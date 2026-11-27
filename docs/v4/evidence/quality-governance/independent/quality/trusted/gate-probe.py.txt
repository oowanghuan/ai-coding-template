import json,os,socket,subprocess,sys
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
