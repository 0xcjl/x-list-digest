"""Install the same Agent Skills package for supported hosts on the machine running this CLI."""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path
HOSTS={'codex':'.agents/skills','hermes':'.hermes/skills','claude-code':'.claude/skills','openclaw':'.openclaw/skills'}
MARKER='.x-list-digest-install.json'
def install(source, home, agents, update=False, dependencies=False):
    installed=[]
    for agent in agents:
        target=home/HOSTS[agent]/'x-list-digest'
        if target.exists() and not update:raise ValueError(f'{target} exists; use --update')
        if target.exists() and not (target/MARKER).exists():raise ValueError(f'{target} not owned by this installer; refusing overwrite')
        target.parent.mkdir(parents=True,exist_ok=True)
        stage=Path(tempfile.mkdtemp(prefix='.x-list-digest-',dir=target.parent))
        try:
            shutil.copytree(source,stage,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.venv','__pycache__','demo-output','integration','tools','.git','*.zip',MARKER))
            (stage/MARKER).write_text(json.dumps({'name':'x-list-digest','agent':agent,'format':1})+'\n')
            if target.exists():
                backup=target.with_name('x-list-digest.previous')
                if backup.exists():raise ValueError(f'{backup} already exists; inspect before updating')
                # Preserve an existing working venv when updating owned skill files.
                if (target/'.venv').exists():shutil.move(str(target/'.venv'),str(stage/'.venv'))
                target.rename(backup)
                try:stage.rename(target)
                except Exception:backup.rename(target);raise
                shutil.rmtree(backup)
            else:stage.rename(target)
            if dependencies:
                if not (target/'.venv').exists():subprocess.run([sys.executable,'-m','venv',str(target/'.venv')],check=True)
                subprocess.run([str(target/'.venv/bin/python'),'-m','pip','install','-r',str(target/'requirements.txt')],check=True,stdout=subprocess.DEVNULL)
            installed.append({'agent':agent,'path':str(target)})
        finally:
            if stage.exists():shutil.rmtree(stage)
    return installed
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--agents',nargs='+',choices=['all',*HOSTS],default=['all']);p.add_argument('--home',type=Path,default=Path.home());p.add_argument('--update',action='store_true');p.add_argument('--install-deps',action='store_true');a=p.parse_args()
    agents=list(HOSTS) if 'all' in a.agents else list(dict.fromkeys(a.agents))
    try:print(json.dumps(install(Path(__file__).resolve().parents[1],a.home.expanduser(),agents,a.update,a.install_deps),ensure_ascii=False,indent=2))
    except ValueError as e:p.exit(2,str(e)+'\n')
