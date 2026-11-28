import subprocess,hashlib,json,datetime
from pathlib import Path
base=Path(__file__).resolve().parent.parent;repo=Path('<REPOSITORY>');deps='<INSTALLED_DEPENDENCIES>'
def inputs():
 result={}
 for name in ('framework','schemas','tests','examples','manifests','templates','adapters','scripts'):
  directory=repo/name
  if directory.exists():
   for p in directory.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts:result[str(p.relative_to(repo))]=hashlib.sha256(p.read_bytes()).hexdigest()
 return result
start=inputs();results=[]
env={'HOME':str(base/'C/home'),'TMPDIR':str(base/'C/tmp'),'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','PYTHONPATH':str(repo)+':'+deps,'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','V4_OUTER_SEATBELT':'1'}
for group in ('install','protocol','local','bootstrap','quality','governance','adapters','recovery','lifecycle','worker_demo'):
 argv=['/usr/bin/sandbox-exec','-f',str(base/'T/profile.sb'),'/usr/bin/python3','-B','-S',str(base/'T/run_group.py'),str(repo),group,str(base/'T')]
 begun=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (base/'T'/ (group+'.stdout.log')).open('wb') as out,(base/'T'/(group+'.stderr.log')).open('wb') as err:
  try:run=subprocess.run(argv,cwd=repo,env=env,stdout=out,stderr=err,timeout=600);code=run.returncode
  except subprocess.TimeoutExpired:code='timeout'
 record={'group':group,'argv':argv,'started_at':begun,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':code}
 lines=(base/'T'/(group+'.stdout.log')).read_text().splitlines()
 record['results']=[json.loads(x) for x in lines if x.startswith('{') and x.endswith('}')]
 results.append(record);print(json.dumps(record),flush=True)
 (base/'T/progress.json').write_text(json.dumps(results,indent=2))
end=inputs();summary={'before':start,'after':end,'inputs_unchanged':start==end,'runs':results,'environment':env,'profile_sha256':hashlib.sha256((base/'T/profile.sb').read_bytes()).hexdigest(),'passed':all(r['exit_code']==0 for r in results)}
(base/'T/result.json').write_text(json.dumps(summary,indent=2));print(json.dumps({'result':str(base/'T/result.json'),'passed':summary['passed'],'inputs_unchanged':start==end}),flush=True)
