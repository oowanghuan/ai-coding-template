from pathlib import Path
import hashlib,json,subprocess,datetime
repo=Path('/public/framework');out=Path('/public/experiments/quality-governance-regression-02')
def hashes():
 return {str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest() for group in ['framework','schemas','scripts','tests','examples','templates'] for p in (repo/group).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
before=hashes();env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','HOME':str(out/'home'),'TMPDIR':str(out/'tmp'),'PYTHONPATH':str(repo)+':/public/operator/Library/Python/3.9/lib/python/site-packages','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','V4_OUTER_SEATBELT':'1'}
args=['/usr/bin/sandbox-exec','-f',str(out/'sandbox.sb'),'/usr/bin/python3','-B','-S',str(out/'runner.py'),str(out/'config.json')]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(args,cwd=repo,env=env,capture_output=True,timeout=240)
(out/'stdout.log').write_bytes(r.stdout);(out/'stderr.log').write_bytes(r.stderr);after=hashes()
result={'command':args,'started_at':start,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':r.returncode,'input_hashes':before,'inputs_unchanged':before==after,'changed':[k for k in set(before)|set(after) if before.get(k)!=after.get(k)],'environment':env}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('input_hashes','environment')}));print(r.stdout.decode());print(r.stderr.decode()[-2200:])
