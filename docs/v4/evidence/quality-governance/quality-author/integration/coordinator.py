"""Finite operator-reviewed coordinator. No candidate imports on the host.
prepare creates immutable inputs; execute requires independently approved hashes.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO = Path('/public/fixture/repository')
DEPS = Path('/public/fixture/dependencies')
STAGE = Path('/public/fixture/history/quality-real-stage')
GUIDE = '# Synthetic quality guide\n\nRequired check: immutable evidence.\n'
PYTHON = '/usr/bin/python3'
GIT = '/usr/bin/git'
SOURCE = r'''import json,os,socket,sys,time
from pathlib import Path
def check_owned_process(pid):
 import ctypes,errno
 lib=ctypes.CDLL(None,use_errno=True)
 lib.sysctl.argtypes=[ctypes.POINTER(ctypes.c_int),ctypes.c_uint,ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),ctypes.c_void_p,ctypes.c_size_t]
 lib.sysctl.restype=ctypes.c_int
 mib=(ctypes.c_int*3)(1,49,pid);buf=ctypes.create_string_buffer(262144);size=ctypes.c_size_t(len(buf))
 rc=lib.sysctl(mib,3,buf,ctypes.byref(size),None,0);err=ctypes.get_errno()
 visible=b'public-harmless-quality-procargs-marker' in buf.raw if rc==0 else False
 print(json.dumps(dict(target='owned synthetic PID only',return_code=rc,errno=err,marker_visible=visible)),file=sys.stderr,flush=True)
 return dict(system_info_denied=rc==-1 and err==errno.EPERM,system_marker_absent=not visible)
r=json.loads(sys.stdin.read()); mode=r['mode']
if mode=='echo': print(r['text'])
elif mode=='document':
 text=Path(__file__).with_name('GUIDE.md').read_text()
 valid=text=='# Synthetic quality guide\n\nRequired check: immutable evidence.\n'
 print('document-ok' if valid else 'document-invalid')
 if not valid:sys.exit(7)
elif mode=='fail': print('rejected');sys.exit(3)
elif mode=='selfreport': print('{"status":"passed","tests":99}');sys.exit(1)
elif mode=='timeout': time.sleep(5)
elif mode=='close-pipes': os.close(1);os.close(2);time.sleep(5)
elif mode=='flood':
 data=b'x'*(1024*1024+1)
 while data:
  n=os.write(1,data);data=data[n:]
elif mode=='fork':
 try:
  pid=os.fork()
 except PermissionError: print('fork-denied')
 else:
  if pid==0: os._exit(0)
  os.waitpid(pid,0);print('fork-allowed');sys.exit(4)
elif mode=='boundary':
 checks=check_owned_process(r['owned_canary_pid'])
 def denied(name,fn):
  try: fn();checks[name]=False
  except PermissionError: checks[name]=True
  except OSError: checks[name]=False
 denied('trusted_write',lambda:Path(r['trusted_target']).write_text('forged'))
 denied('source_hardlink',lambda:os.link(__file__,str(Path.cwd()/'source-alias')))
 denied('outside_read',lambda:Path(r['outside']).read_bytes())
 denied('outside_write',lambda:Path(r['outside']).write_text('changed'))
 denied('scratch_unlink',lambda:os.rmdir(Path.cwd()))
 def network():
  with socket.socket() as s:s.connect(('127.0.0.1',9))
 denied('network',network)
 checks['credentials_absent']=not any(k in os.environ for k in ('GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'))
 Path('forged-report.json').write_text('{"status":"passed","tests":999}')
 import hashlib
 Path('forged-report.sha256').write_text(hashlib.sha256(Path('forged-report.json').read_bytes()).hexdigest())
 print(json.dumps(checks,sort_keys=True,separators=(',',':')))
 if not all(checks.values()):sys.exit(5)
else:sys.exit(6)
'''
GATE_PROBE = r'''import json,os,socket,subprocess,sys
from pathlib import Path
def check_owned_process(pid):
 import ctypes,errno
 lib=ctypes.CDLL(None,use_errno=True)
 lib.sysctl.argtypes=[ctypes.POINTER(ctypes.c_int),ctypes.c_uint,ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),ctypes.c_void_p,ctypes.c_size_t]
 lib.sysctl.restype=ctypes.c_int
 mib=(ctypes.c_int*3)(1,49,pid);buf=ctypes.create_string_buffer(262144);size=ctypes.c_size_t(len(buf))
 rc=lib.sysctl(mib,3,buf,ctypes.byref(size),None,0);err=ctypes.get_errno()
 visible=b'public-harmless-quality-procargs-marker' in buf.raw if rc==0 else False
 print(json.dumps(dict(target='owned synthetic PID only',return_code=rc,errno=err,marker_visible=visible)),file=sys.stderr,flush=True)
 return dict(system_info_denied=rc==-1 and err==errno.EPERM,system_marker_absent=not visible)
c=json.loads(Path(sys.argv[1]).read_text());checks=check_owned_process(c['owned_canary_pid'])
def denied(name,fn):
 try:fn();checks[name]=False
 except PermissionError:checks[name]=True
 except OSError:checks[name]=False
denied('trusted_write',lambda:Path(c['trusted_target']).write_text('forged'))
denied('trusted_hardlink',lambda:os.link(c['trusted_target'],str(Path(c['candidate'])/'alias')))
denied('candidate_root_unlink',lambda:os.rmdir(c['candidate']))
denied('outside_read',lambda:Path(c['outside']).read_bytes())
denied('outside_write',lambda:Path(c['outside']).write_text('changed'))
denied('checkout_write',lambda:(Path(c['repo'])/'quality-forged-canary').write_text('changed'))
def network():
 with socket.socket() as s:s.connect(('127.0.0.1',9))
denied('network',network)
checks['credentials_absent']=not any(k in os.environ for k in ('GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'))
print(json.dumps({'sandbox_canaries':checks}),flush=True)
if not all(checks.values()):sys.exit(8)
args=[sys.executable,'-B','-S',str(Path(c['repo'])/'scripts/v4_quality.py'),'verify','--trust',c['trust'],'--trust-sha256',c['pin'],'--run-id',c['run_id']]
r=subprocess.run(args,capture_output=True,timeout=30)
print(json.dumps({'gate_argv':args,'gate_exit':r.returncode,'gate_stdout':r.stdout.decode(),'gate_stderr':r.stderr.decode()}),flush=True)
sys.exit(r.returncode)
'''

def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def save(path,value):path.write_bytes(canonical(value)+b'\n')
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):return digest(path.read_bytes())
def safe_env(home,tmp):return dict(HOME=str(home),TMPDIR=str(tmp),PATH='/usr/bin:/bin:/usr/sbin:/sbin',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
def check_hash(path,expected):
 if len(expected)!=64 or sha(path)!=expected:raise ValueError('reviewed source hash mismatch: '+str(path))
def invoke(args,env,cwd,timeout=30):return subprocess.run(args,env=env,cwd=cwd,capture_output=True,timeout=timeout,check=False)
def git(args,cwd,env,input=None):
 r=subprocess.run([GIT,'-c','core.hooksPath=/dev/null','-c','commit.gpgsign=false']+args,cwd=cwd,env=env,input=input,capture_output=True,timeout=30)
 if r.returncode:raise RuntimeError('fixture git failed: '+r.stderr.decode())
 return r.stdout

def case(identity,mode,expected=b'',exit=0,required=True,skip=None,**extra):
 return dict(id=identity,required=required,input=canonical(dict(mode=mode,**extra)).decode(),expected_exit=exit,
 expected_stdout_sha256=digest(expected),timeout_seconds=1 if mode in ('timeout','close-pipes') else 5,skip_reason=skip)

def outer_policy(trusted,candidate):
 q=lambda x:json.dumps(str(x))
 reads=['/System','/usr','/bin','/sbin','/Library/Developer','/Library/Apple','/private/var/db/dyld','/private/preboot/Cryptexes',REPO,DEPS,trusted,candidate]
 return '\n'.join(['(version 1)','(deny default)','(allow process*)','(deny process-info* (target others))','(allow file-read-metadata)',
 '(allow file-map-executable)','(allow mach-lookup (global-name "com.apple.system.logger"))',
 '(allow file-read* (literal "/") (literal "/dev/null") (literal "/dev/urandom") '+' '.join('(subpath '+q(p)+')' for p in reads)+')',
 '(allow file-write* (literal "/dev/null") (subpath '+q(candidate)+'))',
 '(deny file-write-unlink (literal '+q(candidate)+'))',
 '(deny mach-lookup (global-name "com.apple.securityd") (global-name "com.apple.security.agent"))',
 '(allow signal (target children))'])+'\n'

def prepare(collector_hash):
 check_hash(REPO/'framework/quality/collector.py',collector_hash)
 if (STAGE/'prepared.json').exists():raise ValueError('prepare manifest already exists; preserve prior experiment')
 root=Path(tempfile.mkdtemp(prefix='v4-quality-real-',dir='/private/tmp')).resolve()
 trusted=root/'T';candidate=root/'C';trusted.mkdir();candidate.mkdir()
 outside=root/'outside-canary';outside.write_text('unchanged-external-canary\n')
 fixture=root/'git-fixture';fixture.mkdir();(fixture/'check.py').write_text(SOURCE);(fixture/'GUIDE.md').write_text(GUIDE)
 env=safe_env(fixture,fixture);env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_NAME='Synthetic Quality Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_NAME='Synthetic Quality Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid',GIT_AUTHOR_DATE='2026-11-27T00:00:00+0000',GIT_COMMITTER_DATE='2026-11-27T00:00:00+0000')
 git(['init','-q'],fixture,env);git(['add','--','check.py','GUIDE.md'],fixture,env);git(['commit','-q','-m','Synthetic quality fixture'],fixture,env)
 commit=git(['rev-parse','HEAD'],fixture,env).decode().strip();tree=git(['rev-parse','HEAD^{tree}'],fixture,env).decode().strip();raw=git(['cat-file','commit','HEAD'],fixture,env).decode()
 manifest={'check.py':{'sha256':digest(SOURCE.encode()),'mode':'100644'},'GUIDE.md':{'sha256':digest(GUIDE.encode()),'mode':'100644'}}
 subject=dict(commit=commit,tree=tree,manifest_sha256=digest(canonical(manifest)))
 version=invoke([PYTHON,'--version'],safe_env(root,root),root).stdout.decode().strip().removeprefix('Python ')
 environment=dict(platform='darwin',python=PYTHON,python_version=version,sandbox='macos-seatbelt')
 boundary_expected=canonical(dict(trusted_write=True,source_hardlink=True,outside_read=True,outside_write=True,scratch_unlink=True,network=True,credentials_absent=True,system_info_denied=True,system_marker_absent=True))+b'\n'
 specs=[('success',[case('unicode','echo','你好，质量\n'.encode(),text='你好，质量'),case('negative','fail',b'rejected\n',exit=3),case('optional','echo',required=False,skip='operator-approved optional fixture')],'passed'),
 ('selfreport',[case('selfreport','selfreport',b'{"status":"passed","tests":99}\n')],'failed'),
 ('timeout',[case('timeout','timeout')],'failed'),('close-pipes',[case('closed','close-pipes')],'failed'),
 ('flood',[case('flood','flood',b'x'*(1024*1024))],'failed'),
 ('requiredskip',[case('required','echo',skip='required check deliberately omitted')],'failed'),
 ('empty',[],'failed'),('document',[case('documentation','document',b'document-ok\n')],'passed'),('fork',[case('fork','fork',b'fork-denied\n')],'passed'),
 ('forged-write',[case('boundary','boundary',boundary_expected,trusted_target=str(trusted/'sentinel'),outside=str(outside),owned_canary_pid='OWNED_CANARY_PID')],'passed'),
 ('no-collector',[case('never-run','echo',b'actual\n',text='actual')],'unverifiable')]
 (trusted/'sentinel').write_text('protected-sentinel\n')
 registrations={};runs=[];inputs={}
 for identity,tests,status in specs:
  t=trusted/identity;c=candidate/identity;t.mkdir();c.mkdir();(t/'subject').mkdir()
  shutil.copyfile(REPO/'framework/quality/collector.py',t/'collector.py');check_hash(t/'collector.py',collector_hash)
  (t/'subject/check.py').write_bytes(SOURCE.encode());(t/'subject/GUIDE.md').write_bytes(GUIDE.encode())
  plan=dict(format='quality-plan/1',run_id=identity,wp_id='WP-201',wp_revision=1,kind='document' if identity=='document' else 'code',trusted_root=str(t),scratch_root=str(c),subject_root=str(t/'subject'),entrypoint='check.py',subject=subject,commit_object=raw,manifest=manifest,collector_sha256=collector_hash,environment=environment,tests=tests)
  save(t/'plan.json',plan);plan_hash=sha(t/'plan.json')
  registrations[identity]=dict(root=str(t),plan_sha256=plan_hash,collector_sha256=collector_hash,wp_id='WP-201',wp_revision=1,subject=subject)
  runs.append(dict(id=identity,root=str(t),scratch=str(c),plan_sha256=plan_hash,expected_gate=status))
  for rel in ('collector.py','subject/check.py','subject/GUIDE.md','plan.json'):inputs[str(t/rel)]=sha(t/rel)
 save(trusted/'trust.json',dict(format='quality-trust/1',runs=registrations))
 (trusted/'gate-probe.py').write_text(GATE_PROBE)
 gate_c=root/'gate-C';gate_c.mkdir();(trusted/'gate.sb').write_text(outer_policy(trusted,gate_c))
 for path in (trusted/'trust.json',trusted/'gate-probe.py',trusted/'gate.sb',trusted/'sentinel',outside):inputs[str(path)]=sha(path)
 for rel in ('framework/quality/gate.py','schemas/evidence.schema.json','scripts/v4_quality.py'):inputs[str(REPO/rel)]=sha(REPO/rel)
 info=dict(format='quality-real-experiment/1',prepared_at=utc(),root=str(root),trusted=str(trusted),candidate=str(candidate),gate_candidate=str(gate_c),outside=str(outside),collector_sha256=collector_hash,coordinator_sha256=sha(Path(__file__)),trust_sha256=sha(trusted/'trust.json'),runs=runs,inputs=inputs)
 save(STAGE/'prepared.json',info);print(json.dumps({'prepared':str(STAGE/'prepared.json'),'root':str(root),'source_commit':commit,'collector_sha256':collector_hash}))

def gate_run(info,run,pin,suffix):
 t=Path(info['trusted']);c=Path(info['gate_candidate'])
 config=t/('gate-config-'+run['id']+'-'+suffix+'.json')
 save(config,dict(trusted_target=str(t/'sentinel'),candidate=str(c),outside=info['outside'],repo=str(REPO),trust=str(t/'trust.json'),pin=pin,run_id=run['id'],owned_canary_pid=info['owned_canary_pid']))
 env=safe_env(c,c);env['PYTHONPATH']=str(REPO)+':'+str(DEPS)
 args=['/usr/bin/sandbox-exec','-f',str(t/'gate.sb'),PYTHON,'-B','-S',str(t/'gate-probe.py'),str(config)]
 start=utc();r=invoke(args,env,c,timeout=45)
 out=STAGE/(run['id']+'-gate-'+suffix);out.with_suffix('.stdout.log').write_bytes(r.stdout);out.with_suffix('.stderr.log').write_bytes(r.stderr)
 rows=[json.loads(line) for line in r.stdout.splitlines()];canaries=rows[0]['sandbox_canaries'];decision=json.loads(rows[1]['gate_stdout']) if len(rows)>1 else None
 record=dict(argv=args,started_at=start,finished_at=utc(),exit_code=r.returncode,canaries=canaries,decision=decision)
 save(out.with_suffix('.json'),record);return record

def execute_batch(info,collector_hash,coordinator_hash,owned):
 results=[]
 for run in info['runs']:
  t=Path(run['root']);c=Path(run['scratch']);check_hash(t/'collector.py',collector_hash)
  args=[PYTHON,'-I','-B','-S',str(t/'collector.py'),'--plan',str(t/'plan.json'),'--plan-sha256',run['plan_sha256']]
  if owned.poll() is not None:raise RuntimeError('owned canary unexpectedly exited; do not query stale PID')
  if run['id']=='no-collector':
   report=(c/'forged-report.json');report.write_bytes(canonical(dict(status='passed',tests=999)))
   (c/'forged-report.sha256').write_text(sha(report))
   gate=gate_run(info,run,info['trust_sha256'],'normal')
   item=dict(id=run['id'],collector_argv=None,collector_exit=None,evidence=None,gate=gate,expected_gate='unverifiable',passed=not (t/'evidence.json').exists() and gate['decision']['status']=='unverifiable' and all(gate['canaries'].values()))
   save(STAGE/(run['id']+'-result.json'),item);results.append(item);continue
  started=utc();r=invoke(args,safe_env(t,c),t,timeout=40)
  if owned.poll() is not None:raise RuntimeError('owned canary unexpectedly exited; do not query stale PID')
  (STAGE/(run['id']+'-collector.stdout.log')).write_bytes(r.stdout);(STAGE/(run['id']+'-collector.stderr.log')).write_bytes(r.stderr)
  actual=json.loads((t/'evidence.json').read_text()) if (t/'evidence.json').exists() else None
  gate=gate_run(info,run,info['trust_sha256'],'normal')
  item=dict(id=run['id'],collector_argv=args,collector_started_at=started,collector_finished_at=utc(),collector_exit=r.returncode,evidence=actual,gate=gate,expected_gate=run['expected_gate'])
  item['passed']=r.returncode==0 and gate['decision'] is not None and gate['decision']['status']==run['expected_gate'] and all(gate['canaries'].values())
  save(STAGE/(run['id']+'-result.json'),item);results.append(item)
 # Replay the exact prior collector operation: exclusive intent must stop it before a new case.
 run=info['runs'][0];t=Path(run['root']);c=Path(run['scratch']);before={str(p):sha(p) for p in t.rglob('*') if p.is_file()}
 args=[PYTHON,'-I','-B','-S',str(t/'collector.py'),'--plan',str(t/'plan.json'),'--plan-sha256',run['plan_sha256']]
 r=invoke(args,safe_env(t,c),t,timeout=10)
 after={str(p):sha(p) for p in t.rglob('*') if p.is_file()}
 (STAGE/'replay.stdout.log').write_bytes(r.stdout);(STAGE/'replay.stderr.log').write_bytes(r.stderr)
 replay=dict(exit_code=r.returncode,inputs_unchanged=before==after,passed=r.returncode!=0 and before==after)
 save(STAGE/'replay.json',replay)
 wrong=gate_run(info,run,'0'*64,'wrong-pin');wrong_ok=wrong['decision']['status']=='unverifiable' and all(wrong['canaries'].values())
 unchanged=all(sha(Path(path))==expected for path,expected in info['inputs'].items())
 summary=dict(completed_at=utc(),collector_sha256=collector_hash,coordinator_sha256=coordinator_hash,runs=[dict(id=r['id'],passed=r['passed'],status=(r['gate']['decision'] or {}).get('status')) for r in results],replay=replay,wrong_pin_rejected=wrong_ok,immutable_inputs_unchanged=unchanged,passed=all(r['passed'] for r in results) and replay['passed'] and wrong_ok and unchanged)
 save(STAGE/'summary.json',summary);print(json.dumps(summary));return 0 if summary['passed'] else 1

def execute(collector_hash,coordinator_hash):
 check_hash(Path(__file__),coordinator_hash)
 info=json.loads((STAGE/'prepared.json').read_text())
 if info['collector_sha256']!=collector_hash or info['coordinator_sha256']!=coordinator_hash:raise ValueError('preparation review binding mismatch')
 for path,expected in info['inputs'].items():check_hash(Path(path),expected)
 fd=os.open(STAGE/'execution-intent.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(canonical(dict(started_at=utc(),collector_sha256=collector_hash,coordinator_sha256=coordinator_hash)))
 root=Path(info['root']);env=safe_env(root,root);env['V4_SYNTHETIC_CANARY']='public-harmless-quality-procargs-marker'
 command=[PYTHON,'-I','-B','-S','-c','import time; time.sleep(180)']
 owned=subprocess.Popen(command,cwd=root,env=env,start_new_session=True,close_fds=True)
 try:
  if owned.poll() is not None:raise RuntimeError('owned canary did not start')
  info['owned_canary_pid']=owned.pid
  # Exactly one approved runtime placeholder changes, before any collector run.
  changes=[];trust_path=Path(info['trusted'])/'trust.json';trust=json.loads(trust_path.read_text())
  for run in info['runs']:
   plan_path=Path(run['root'])/'plan.json';raw=plan_path.read_bytes()
   expected=1 if run['id']=='forged-write' else 0
   if raw.count(b'OWNED_CANARY_PID')!=expected:raise ValueError('unexpected runtime placeholder location')
   if not expected:continue
   plan=json.loads(raw)
   if len(plan['tests'])!=1 or plan['tests'][0]['id']!='boundary':raise ValueError('unexpected runtime binding shape')
   case_input=json.loads(plan['tests'][0]['input'])
   if case_input.get('owned_canary_pid')!='OWNED_CANARY_PID':raise ValueError('runtime placeholder must be owned PID field')
   case_input['owned_canary_pid']=owned.pid;plan['tests'][0]['input']=canonical(case_input).decode()
   save(plan_path,plan);run['plan_sha256']=sha(plan_path);trust['runs'][run['id']]['plan_sha256']=run['plan_sha256'];info['inputs'][str(plan_path)]=sha(plan_path)
   changes.append(dict(run_id=run['id'],field='tests[0].input.owned_canary_pid',value=owned.pid))
  save(trust_path,trust);info['trust_sha256']=sha(trust_path);info['inputs'][str(trust_path)]=sha(trust_path)
  info['runtime_binding_changes']=changes;info['sealed_at']=utc()
  save(STAGE/'sealed-manifest.json',info)
  save(STAGE/'owned-canary.json',dict(command=command,environment=env,pid=owned.pid,scope='This owned synthetic PID only; no unrelated PID query'))
  return execute_batch(info,collector_hash,coordinator_hash,owned)
 finally:
  if owned.poll() is None:
   owned.terminate()
   try:owned.wait(timeout=3)
   except subprocess.TimeoutExpired:owned.kill();owned.wait(timeout=3)
  save(STAGE/'owned-canary-cleanup.json',dict(pid=owned.pid,exit_code=owned.poll(),finished_at=utc(),owned_process_only=True))


def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','execute']);p.add_argument('--reviewed-collector',required=True);p.add_argument('--reviewed-coordinator');a=p.parse_args()
 if a.action=='prepare':prepare(a.reviewed_collector);return 0
 if not a.reviewed_coordinator:raise ValueError('execute requires independently reviewed coordinator hash')
 return execute(a.reviewed_collector,a.reviewed_coordinator)
if __name__=='__main__':sys.exit(main())
