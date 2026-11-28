import json,unittest,sys,socket,os
from pathlib import Path
repo=Path(sys.argv[1]);group=sys.argv[2];T=Path(sys.argv[3]);checks={}
for key,path,mode in [('checkout_write',repo/'a01-canary','write'),('trusted_write',T/'a01-canary','write'),('private_read',Path('<PRIVATE_CANARY>'),'read')]:
 try:
  path.write_text('denied') if mode=='write' else path.read_bytes();checks[key]=False
 except PermissionError:checks[key]=True
try:
 with socket.socket() as s:s.connect(('127.0.0.1',9))
 checks['network']=False
except PermissionError:checks['network']=True
except OSError:checks['network']=False
checks['no_credential_environment']=not any(k in os.environ for k in ('GH_TOKEN','GITHUB_TOKEN','ANTHROPIC_API_KEY','OPENAI_API_KEY','CLAUDE_CODE_OAUTH_TOKEN','SSH_AUTH_SOCK'))
print(json.dumps({'canaries':checks}),flush=True)
if not all(checks.values()):sys.exit(3)
suite=unittest.TestLoader().discover(str(repo/'tests'/group))
r=unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'group':group,'run':r.testsRun,'passed':r.testsRun-len(r.failures)-len(r.errors)-len(r.skipped),'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped)}),flush=True)
sys.exit(0 if r.wasSuccessful() else 1)
