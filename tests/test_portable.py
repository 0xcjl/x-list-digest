import sys,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from config import resolve
from run import initialize,finish
from install import install,HOSTS
from feishu_cli import publish,CLIError
from render import render
import test_pipeline as fixtures
ROOT=Path(__file__).resolve().parents[1]
class PortableTest(unittest.TestCase):
    def test_install_all_hosts_and_owned_update(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            result=install(ROOT,home,list(HOSTS))
            self.assertEqual(len(result),4)
            for entry in result:self.assertIn('name: x-list-digest',(Path(entry['path'])/'SKILL.md').read_text())
            self.assertEqual(len(install(ROOT,home,list(HOSTS),update=True)),4)
            with self.assertRaises(ValueError):install(ROOT,home,['codex'])
            (home/HOSTS['codex']/'x-list-digest/.x-list-digest-install.json').unlink()
            with self.assertRaises(ValueError):install(ROOT,home,['codex'],update=True)
    def test_multiple_lists_finish_and_repeat(self):
        fixture=fixtures.PipelineTest();fixture.setUp()
        config={'lists':{'one':{'url':'https://x.com/i/lists/1'},'two':{'url':'https://x.com/i/lists/2'}}}
        with tempfile.TemporaryDirectory() as d:
            jobs=initialize(config,['one','two'],d,end=datetime(2026,10,10,tzinfo=timezone.utc))
            self.assertNotEqual(jobs[0]['run_dir'],jobs[1]['run_dir'])
            directory=Path(jobs[0]['run_dir']);meta=json.loads((directory/'metadata.json').read_text())
            meta.update(coverage='partial',stop_reason='max_tweets')
            (directory/'metadata.json').write_text(json.dumps(meta));(directory/'raw.jsonl').write_text('\n'.join(json.dumps(r) for r in fixture.raw))
            (directory/'analysis.json').write_text(json.dumps(fixture.analysis))
            first=finish(directory);self.assertEqual(first,finish(directory));self.assertEqual(first['tweet_count'],2)
            self.assertIn('partial',Path(first['report_path']).read_text())
    def test_untrusted_text_is_literal(self):
        fixture=fixtures.PipelineTest();fixture.setUp()
        from analyze import enrich
        rows=enrich(fixture.raw,fixture.analysis);rows[0]['text']='![bad](https://malicious.invalid/a) <at id="all">'
        report=render(rows,fixture.meta)
        self.assertNotIn('![bad](',report);self.assertIn('\\<at id=',report)
    def test_cli_checkpoint_readback_and_idempotency(self):
        with tempfile.TemporaryDirectory() as d:
            report=Path(d)/'report.md';report.write_text('# test\n## 顶部摘要\n## 大类分布\n## 元数据')
            state=Path(d)/'publish.json'
            responses=[{'ok':True,'data':{'document':{'document_id':'doc1','url':'https://example.feishu.cn/docx/doc1'}}},
              {'ok':True,'data':{'document':{'document_id':'doc1','content':report.read_text()}}},
              {'ok':True,'data':{'message_id':'msg1'}}]
            with patch('feishu_cli.command',return_value=['local-cli']),patch('feishu_cli.call',side_effect=responses) as call:
                result=publish(report,'title',state,recipient={'type':'chat','id':'oc_example'},identity='user')
                self.assertEqual(result['message_id'],'msg1');self.assertEqual(call.call_count,3)
                self.assertEqual(publish(report,'title',state,recipient={'type':'chat','id':'oc_example'},identity='user'),result)
                self.assertEqual(call.call_count,3)
    def test_unknown_write_does_not_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            report=Path(d)/'report.md';report.write_text('# test');state=Path(d)/'publish.json'
            with patch('feishu_cli.command',return_value=['local-cli']),patch('feishu_cli.call',side_effect=CLIError('timeout')) as call:
                with self.assertRaises(CLIError):publish(report,'title',state,identity='user')
                self.assertEqual(json.loads(state.read_text())['pending'],'document_create')
                with self.assertRaises(CLIError):publish(report,'title',state,identity='user')
                self.assertEqual(call.call_count,1)
if __name__=='__main__':unittest.main()
