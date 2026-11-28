import os,socket,json,sys
from pathlib import Path
a=json.loads(sys.argv[1]);out={}
def denied(k,fn):
 try:fn();out[k]=False
 except PermissionError:out[k]=True
 except OSError:out[k]=False
denied('trusted_write',lambda:Path(a['t']).write_text('bad'))
denied('outside_read',lambda:Path(a['outside']).read_bytes())
denied('checkout_write',lambda:Path(a['repo']).write_text('bad'))
denied('hardlink_to_T',lambda:os.link(a['t'],a['alias']))
def net():
 with socket.socket() as s:s.connect(('127.0.0.1',9))
denied('network',net)
out['credential_env_absent']=not any(k in os.environ for k in ['GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'])
print(json.dumps(out));sys.exit(0 if all(out.values()) else 1)
