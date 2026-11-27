import json,os,socket,sys,unittest
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text())
checks={}
for name,operation in [
 ('outside_file_read',lambda:Path(c['canary']).read_text()),
 ('outside_file_write',lambda:Path(c['canary']).write_text('changed')),
 ('checkout_write',lambda:(Path(c['repo'])/'sandbox-write-canary').write_text('unexpected'))]:
 try:
  operation();checks[name]=False
 except PermissionError:
  checks[name]=True
try:
 with socket.socket() as s:
  s.connect(('127.0.0.1',9))
 checks['network_connect']=False
except PermissionError:
 checks['network_connect']=True
except OSError as e:
 checks['network_connect']=False
checks['credentials_removed']=not any(k in os.environ for k in ['GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'])
print(json.dumps({'sandbox_canaries':checks}),flush=True)
if not all(checks.values()):sys.exit(3)
result={}
ok=True
for group in ['quality']:
 suite=unittest.TestLoader().discover(str(Path(c['repo'])/'tests'/group),pattern='test_gate.py')
 r=unittest.TextTestRunner(verbosity=2).run(suite)
 result[group]={'run':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped),'passed':r.testsRun-len(r.failures)-len(r.errors)-len(r.skipped)}
 ok &= r.wasSuccessful()
print(json.dumps({'tests':result}),flush=True)
sys.exit(0 if ok else 1)
