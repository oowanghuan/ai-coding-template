import json,os,runpy,socket,sys
from pathlib import Path
config=json.loads(Path(sys.argv[1]).read_text())
c=Path(config['candidate']);t=Path(config['trusted']);source=t/'source'
checks={}
def denied(name, action):
    try: action()
    except PermissionError: checks[name]=True
    else: checks[name]=False
# Empty C root must remain anchored. Do this before creating home/tmp/work files.
denied('candidate_root_unlink',lambda:os.rmdir(c))
denied('trusted_write',lambda:(t/'marker').write_text('forged'))
denied('source_write',lambda:(source/'scripts/v4_worker_demo.py').write_text('forged'))
denied('trusted_hardlink_alias',lambda:os.link(t/'marker',c/'alias'))
denied('outside_read',lambda:Path(config['forbidden']).read_bytes())
denied('outside_write',lambda:Path(config['forbidden']).write_text('forged'))
s=socket.socket()
try: denied('network_connect',lambda:s.connect(('127.0.0.1',9)))
finally:s.close()
checks['credential_environment_absent']=not any(k in os.environ for k in
 ['GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'])
print(json.dumps({'sandbox_canaries':checks}),flush=True)
if not all(checks.values()):raise SystemExit(3)
(c/'home').mkdir();(c/'tmp').mkdir()
os.environ.update(HOME=str(c/'home'),TMPDIR=str(c/'tmp'),V4_OUTER_SEATBELT='1')
# -I -S suppresses user site, .pth, current directory imports and Python env paths.
sys.path[:0]=[str(source),str(t/'dependencies')]
sys.argv=[str(source/'scripts/v4_worker_demo.py'),'--root',str(c/'project')]
runpy.run_path(sys.argv[0],run_name='__main__')
