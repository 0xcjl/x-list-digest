"""Report observable readiness on the execution machine; no credential output."""
import argparse,json,shutil,sys
from pathlib import Path
from config import load
from feishu_cli import auth_check,CLIError
from install import HOSTS
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',default=str(Path(__file__).resolve().parents[1]/'config.yaml'));p.add_argument('--cli');p.add_argument('--profile');a=p.parse_args()
    config=load(a.config);exe=a.cli or config.get('feishu',{}).get('executable','lark-cli')
    readiness={'execution_machine':sys.platform,'lists':config['lists'],'agents':{k:(Path.home()/v/'x-list-digest/SKILL.md').exists() for k,v in HOSTS.items()},
      'browser':{'backend':config.get('browser',{}).get('backend','host'),'status':'requires_host_tool_check'},
      'feishu_cli':{'found':bool(shutil.which(exe)),'auth':'unknown'},'network':'requires_host_policy_check'}
    if readiness['feishu_cli']['found']:
        try:
            result=auth_check(exe,a.profile or config.get('feishu',{}).get('profile'))
            # Command success alone is not proof that the API token has been verified.
            readiness['feishu_cli']['auth']='status_readable_not_api_verified'
        except CLIError as e:readiness['feishu_cli']['auth']=str(e)
    print(json.dumps(readiness,ensure_ascii=False,indent=2))
