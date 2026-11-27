import json,os,socket,sys
from pathlib import Path
c=json.loads(sys.argv[1]);checks={}
def denied(name,op):
 try:op();checks[name]=False
 except PermissionError:checks[name]=True
 except OSError:checks[name]=False
denied('protected_write',lambda:Path(c['protected']).write_text('forged'))
denied('protected_hardlink',lambda:os.link(c['protected'],str(Path(c['candidate'])/'alias')))
denied('candidate_root_unlink',lambda:os.rmdir(c['candidate']))
denied('target_git_read',lambda:Path(c['target_ref']).read_bytes())
denied('outside_write',lambda:Path(c['outside']).write_text('forged'))
denied('checkout_write',lambda:(Path(c['repo'])/'baseline-probe-canary').write_text('forged'))
def net():
 with socket.socket() as s:s.connect(('127.0.0.1',9))
denied('network',net)
checks['credentials_absent']=not any(k in os.environ for k in ('GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'))
print(json.dumps(checks));sys.exit(0 if all(checks.values()) else 1)
