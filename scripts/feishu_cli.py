"""Publish through official lark-cli using its local auth; never extract tokens."""
import argparse,hashlib,json,shutil,subprocess,uuid
from pathlib import Path
from common import write
class CLIError(RuntimeError):pass
def command(executable,profile=None):
    resolved=shutil.which(executable)
    if not resolved:raise CLIError('local lark-cli executable is not reachable in this environment')
    return [resolved]+(['--profile',profile] if profile else [])
def call(prefix,args,stdin=None):
    try:r=subprocess.run(prefix+args,input=stdin,text=True,capture_output=True,timeout=180,check=False)
    except subprocess.TimeoutExpired:raise CLIError('CLI timed out; remote write outcome may be unknown') from None
    try:data=json.loads(r.stdout if r.stdout.strip() else r.stderr)
    except json.JSONDecodeError:raise CLIError('CLI returned non-JSON output; inspect locally without sharing credentials') from None
    if r.returncode or data.get('ok') is False:
        err=data.get('error',{});raise CLIError(f"CLI error: {err.get('type','unknown')}/{err.get('subtype','unknown')}")
    return data

def auth_check(executable='lark-cli',profile=None):
    return call(command(executable,profile),['auth','status','--json'])

def publish(report,title,state_path,executable='lark-cli',profile=None,parent_token=None,recipient=None,identity=None,dry_run=False):
    prefix=command(executable,profile);report=Path(report).resolve();state_path=Path(state_path)
    content=report.read_text();fingerprint=hashlib.sha256(json.dumps({'content':content,'title':title,'profile':profile,
      'parent_token':parent_token,'recipient':recipient,'identity':identity},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    if identity not in ('user','bot'):raise ValueError('choose sending identity user or bot from the configured local profile')
    if recipient and (recipient.get('type') not in ('chat','user') or not recipient.get('id')):raise ValueError('recipient must have type chat/user and ID')
    state=json.loads(state_path.read_text()) if state_path.exists() else {}
    if state and state.get('fingerprint')!=fingerprint:raise ValueError('content/destination changed; create a new publish state')
    if state.get('pending'):raise CLIError('previous write outcome unknown; reconcile remote result before resuming')
    create=['docs','+create','--title',title,'--doc-format','markdown','--content','-','--as',identity]
    create+=['--parent-token',parent_token] if parent_token else ['--parent-position','my_library']
    if dry_run:
        result=call(prefix,create+['--dry-run'],content)
        return {'status':'dry-run','document_request':result,'message_requested':bool(recipient)}
    if not state:
        state={'fingerprint':fingerprint,'message_uuid':str(uuid.uuid4())};write(state_path,state)
    if not state.get('document_id'):
        state['pending']='document_create';write(state_path,state)
        result=call(prefix,create,content)
        doc=result.get('data',{}).get('document',{})
        if not doc.get('document_id') or not doc.get('url'):raise CLIError('create response missing document ID/URL; reconcile pending write')
        state.update(document_id=doc['document_id'],doc_url=doc['url'],warnings=result.get('data',{}).get('warnings',[]),pending=None);write(state_path,state)
    # Read-back must succeed before sending a link to the recipient.
    if not state.get('verified'):
        fetched=call(prefix,['docs','+fetch','--doc',state['document_id'],'--doc-format','markdown','--as',identity])
        remote=fetched.get('data',{}).get('document',{})
        if remote.get('document_id')!=state['document_id'] or not remote.get('content'):raise CLIError('document read-back returned wrong ID or no content')
        expected_sections=('顶部摘要','大类分布','元数据')
        if not all(section in remote['content'] for section in expected_sections if section in content):raise CLIError('document read-back missing report sections')
        state['verified']=True;write(state_path,state)
    if recipient and not state.get('message_id'):
        summary=content.split('## 大类分布')[0][:1600]+'\n完整报告：'+state['doc_url']
        args=['im','+messages-send','--'+recipient['type']+'-id',recipient['id'],'--text','-',
          '--as',identity,'--idempotency-key',state['message_uuid']]
        state['pending']='message_send';write(state_path,state)
        result=call(prefix,args,summary)
        msg=result.get('data',{})
        if not msg.get('message_id'):raise CLIError('message response missing ID; reconcile pending send')
        state.update(message_id=msg['message_id'],pending=None);write(state_path,state)
    return state
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--title',required=True);p.add_argument('--state',required=True)
    p.add_argument('--cli',default='lark-cli');p.add_argument('--profile');p.add_argument('--folder-token');p.add_argument('--as',dest='identity',choices=['user','bot'],required=True)
    g=p.add_mutually_exclusive_group();g.add_argument('--chat-id');g.add_argument('--user-id');p.add_argument('--dry-run',action='store_true');p.add_argument('--db');p.add_argument('--digest-id',type=int);a=p.parse_args()
    recipient={'type':'chat','id':a.chat_id} if a.chat_id else {'type':'user','id':a.user_id} if a.user_id else None
    try:
        r=publish(a.report,a.title,a.state,a.cli,a.profile,a.folder_token,recipient,a.identity,a.dry_run)
        if a.db and a.digest_id and not a.dry_run:
            import sqlite3
            with sqlite3.connect(a.db) as c:c.execute('UPDATE digests SET feishu_doc_url=?,feishu_msg_id=? WHERE id=?',(r['doc_url'],r.get('message_id'),a.digest_id))
        print(json.dumps(r,ensure_ascii=False,indent=2))
    except (CLIError,ValueError) as e:p.exit(2,str(e)+'\n')
