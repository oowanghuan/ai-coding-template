import json,os,socket,sys,time
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
