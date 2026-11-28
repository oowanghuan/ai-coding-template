#!/usr/bin/env python3
"""Credential-free synthetic lifecycle demonstration; run only inside reviewed A01.

This is a demo, not the provider launcher. Fixed child code inherits the enclosing
sandbox; no arbitrary command/model input and no CLI authentication are supported.
"""
import argparse
import copy
from datetime import timedelta
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'principal-owner'
A_DRAFT = 'draft from A\n'
A_NOTE = 'untracked note from A\n'
A_FINAL = A_DRAFT + A_NOTE + 'completed by B\n'
B_FINAL = 'B own delivery\n'


def digest(value): return hashlib.sha256(value).hexdigest()
def save(path, value): path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def fixture_worker(mode):
    """Fixed synthetic file writer; no model, subprocess, network or authority API."""
    start = time.clock_gettime_ns(time.CLOCK_MONOTONIC)
    if mode == 'a':
        Path('src/a/tracked.txt').write_text(A_DRAFT)
        Path('src/a/untracked.txt').write_text(A_NOTE)
    elif mode == 'b': Path('src/b/tracked.txt').write_text('B working\n')
    elif mode == 'takeover':
        if Path('src/a/tracked.txt').read_text() != A_DRAFT or Path('src/a/untracked.txt').read_text() != A_NOTE:
            raise ValueError('restored work absent or changed')
    else: raise ValueError('fixed worker mode required')
    print(json.dumps(dict(phase='ready', mode=mode, pid=os.getpid(), process_group=os.getpgrp(),
                         cwd=str(Path.cwd()), started_ns=start, evidence_level='synthetic_fixture')), flush=True)
    if sys.stdin.readline() != 'finish\n': raise ValueError('explicit fixed finish signal required')
    if mode == 'b': Path('src/b/output.txt').write_text(B_FINAL)
    elif mode == 'takeover': Path('src/a/output.txt').write_text(A_FINAL)
    else: raise ValueError('A is intentionally interrupted in this fixture')
    print(json.dumps(dict(phase='finished', mode=mode, pid=os.getpid(),
                         finished_ns=time.clock_gettime_ns(time.CLOCK_MONOTONIC),
                         evidence_level='synthetic_fixture')), flush=True)


def run_demo(root):
    if os.environ.get('V4_OUTER_SEATBELT') != '1':
        raise ValueError('reviewed outer sandbox required; the environment flag alone is not isolation proof')
    root = Path(root)
    if not root.is_absolute() or root.resolve() != root or not root.parent.is_dir():
        raise ValueError('explicit canonical new root and existing parent required')
    if root.exists(): raise FileExistsError('demo root already exists; preserve it and choose a fresh root')
    root.mkdir(mode=0o700)
    sys.path.insert(0, str(ROOT))
    from framework.adapters import default_registry
    from framework.core.protocol import load_json, timestamp
    from framework.local.store import Store, find, now
    from framework.local.runner import git, prepare
    from framework.local.handoff import checkpoint, confirm_stopped, prepare_handoff
    from framework.recovery.checkpoint import load_snapshot
    evidence = root / 'demo-evidence'; evidence.mkdir()
    processes = []; journal = []
    def record(kind, data):
        journal.append(dict(sequence=len(journal)+1, kind=kind, observed_ns=time.clock_gettime_ns(time.CLOCK_MONOTONIC), data=data))
        save(evidence/'journal.json',journal)
    try:
        git(root,'init','-q')
        for letter in ('a','b'):
            (root/'src'/letter).mkdir(parents=True);(root/'src'/letter/'tracked.txt').write_text('baseline '+letter+'\n')
        git(root,'add','--','src');git(root,'-c','user.name=Synthetic Worker Demo','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','-qm','Synthetic worker baseline')
        baseline = git(root,'rev-parse','HEAD').decode().strip()
        snapshot = load_json(ROOT/'examples/protocol/in-progress.json')
        snapshot['assignments']=[];snapshot['checkpoints']=[];snapshot['sessions']=[]
        basewp = snapshot['work_packages'][0];snapshot['work_packages']=[]
        for letter in ('A','B'):
            wp=copy.deepcopy(basewp);wp.update(id='WP-'+letter,state='planned',assignment_ref=None,checkpoint_ref=None,
                baseline_sha=baseline,allowed_paths=['src/'+letter.lower()+'/'],implementer='principal-worker-'+letter.lower(),
                reviewer='principal-worker-c',acceptor='principal-worker-c')
            snapshot['work_packages'].append(wp)
        snapshot['authorizations'][0]['wp_refs']=['WP-A','WP-B']
        snapshot['providers']=[dict(id='provider-synthetic',adapter='synthetic-fixture')]
        snapshot['workers']=[]
        for letter in ('a','b','c'):
            snapshot['workers'].append(dict(id='worker-'+letter,principal='principal-worker-'+letter,
                role_refs=['role-developer' if letter!='c' else 'role-reviewer'],provider_ref='provider-synthetic',
                host_ref='host-local',capabilities=['code' if letter!='c' else 'review'],state='available',slots=1,
                quota='available',authorization_method='synthetic-no-credentials'))
        store=Store(root);store.initialize(snapshot,OWNER)
        def state():return store.inspect()['state']
        def change(action,payload,actor=OWNER,at=None):
            current=state();op='demo-'+action+'-'+str(current['revision'])
            result=store.change(action,payload,actor,current['revision'],op,at=at)
            record(action,result);return result['operation']['result']
        change('enable-lifecycle',dict(workers=[dict(worker_id='worker-'+letter,quota_group='quota-'+letter,
            auth_identity='fixture-identity-'+letter,mode='dedicated',authenticated=True,authorized=True) for letter in ('a','b','c')],
            policy=dict(heartbeat_timeout=120,initial_backoff=1,max_backoff=4,max_probes=3)))
        registry=default_registry();record('adapter',registry.describe('synthetic-fixture'))
        a=change('dispatch-next',dict(lease_seconds=300));b=change('dispatch-next',dict(lease_seconds=300))
        if (a['wp_id'],a['worker_id'],b['wp_id'],b['worker_id']) != ('WP-A','worker-a','WP-B','worker-b'):
            raise ValueError('unexpected deterministic dispatch')
        def actor(credentials):return 'principal-'+credentials['worker_id']
        def directory(credentials):return root/state()['workspaces'][credentials['workspace_id']]['path']
        for label,credentials in [('a',a),('b',b)]:
            prepare(root,credentials,actor(credentials),state()['revision'],'prepare-'+label)
        def launch(credentials,mode,relative,content):
            change('run-begin',dict(credentials,path=relative,content_sha256=digest(content.encode())),actor(credentials))
            work=directory(credentials);env={'HOME':str(work),'TMPDIR':str(work),'PATH':'/usr/bin:/bin',
                'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','V4_OUTER_SEATBELT':'1'}
            error=(evidence/(mode+'.stderr.log')).open('wb')
            argv=[sys.executable,'-I','-B','-S',str(Path(__file__).resolve()),'--fixture-worker',mode]
            proc=subprocess.Popen(argv,cwd=work,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=error,start_new_session=True)
            processes.append((proc,error,mode))
            store.workspace_phase(credentials,actor(credentials),'launching','running',run=dict(state='running',pid=proc.pid,
                process_group=proc.pid,backend='fixed-synthetic-demo',evidence_level='synthetic_fixture',unknown_operations=[]))
            record('process-launched',dict(argv=argv,pid=proc.pid,workspace=str(work),credentials=credentials))
            return proc
        pa=launch(a,'a','src/a/output.txt',A_FINAL);pb=launch(b,'b','src/b/output.txt',B_FINAL)
        def read_ready(proc,label):
            if not select.select([proc.stdout],[],[],10)[0]:raise TimeoutError('fixed child did not report ready')
            line=proc.stdout.readline(65536);(evidence/(label+'.ready.log')).write_bytes(line)
            ready=json.loads(line)
            if ready['pid']!=proc.pid or ready['process_group']!=proc.pid or ready['phase']!='ready':raise ValueError('child identity mismatch')
            record('process-ready',ready);return ready
        ra=read_ready(pa,'a');rb=read_ready(pb,'b')
        parallel=pa.poll() is None and pb.poll() is None and ra['cwd']!=rb['cwd']
        if not parallel:raise ValueError('independent processes were not simultaneously active')
        record('simultaneous-live-processes',dict(a_pid=pa.pid,b_pid=pb.pid,independent_directories=True,observed=True))
        quota=registry.classify('synthetic-fixture',json.dumps(dict(format='synthetic-adapter-result/1',kind='quota_limited',retry_at=None)).encode(),exit_code=None,observed_at=now())
        record('classified-synthetic-quota',quota)
        change('worker-event',dict(worker_id='worker-a',event=quota['kind'],retry_at=quota['retry_at'],source='synthetic_fixture'))
        fenced=state();old=find(fenced['snapshot']['assignments'],a['assignment_id'])
        if old['state']!='revoked' or fenced['workspaces'][a['workspace_id']]['state']!='unknown':raise ValueError('quota did not fence unresolved writer')
        blocked=change('dispatch-next',dict(lease_seconds=300))
        if blocked['assignment_id'] is not None:raise ValueError('unknown writer incorrectly reassigned')
        pa.terminate();exit_a=pa.wait(timeout=5)
        record('actual-wait',dict(pid=pa.pid,exit_code=exit_a,process_group=pa.pid))
        cp=checkpoint(root,a,actor(a),completed=['tracked draft and untracked note preserved'],remaining=['finish delivery'],evidence_refs=[])
        manifest=load_snapshot(root/cp['path'],cp['manifest_sha256'])
        if not manifest['files']['src/a/tracked.txt']['dirty'] or manifest['files']['src/a/untracked.txt']['tracked']:
            raise ValueError('dirty/untracked checkpoint classification mismatch')
        save(evidence/'checkpoint-manifest.json',manifest);record('checkpoint',cp)
        stop=confirm_stopped(root,a,actor(a),pa);record('confirmed-stop',stop)
        def finish(proc,label,credentials):
            proc.stdin.write(b'finish\n');proc.stdin.close();proc.stdin=None
            output,_=proc.communicate(timeout=10);(evidence/(label+'.finished.log')).write_bytes(output)
            if proc.returncode!=0:raise ValueError('fixed synthetic worker failed')
            final=json.loads(output);record('actual-wait',dict(pid=proc.pid,exit_code=proc.returncode,worker_result=final))
            store.workspace_phase(credentials,actor(credentials),'running','finished',run=dict(state='finished',pid=proc.pid,
                process_group=proc.pid,exit_code=proc.returncode,evidence_level='synthetic_fixture',unknown_operations=[]))
        finish(pb,'b',b)
        change('submit',dict(b,path='src/b/output.txt',sha256=digest(B_FINAL.encode())),actor(b))
        change('release',b,actor(b))
        successor=change('dispatch-next',dict(lease_seconds=300))
        if successor.get('worker_id')!='worker-b' or successor.get('wp_id')!='WP-A' or successor['token']<=a['token']:
            raise ValueError('expected B takeover with newer fence')
        prepare_handoff(root,successor,actor(successor),state()['revision'],'prepare-handoff-b')
        if directory(successor)==directory(a):raise ValueError('takeover reused old worktree')
        if (directory(successor)/'src/a/tracked.txt').read_text()!=A_DRAFT or (directory(successor)/'src/a/untracked.txt').read_text()!=A_NOTE:
            raise ValueError('restored source differs')
        resumed=launch(successor,'takeover','src/a/output.txt',A_FINAL);read_ready(resumed,'takeover')
        future=(timestamp(now())+timedelta(seconds=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        tick=change('scheduler-tick',{},at=future)
        probe=next(item for item in tick['probes'] if item['group']=='quota-a')
        change('worker-event',dict(worker_id='worker-a',event='probe-result',probe_id=probe['probe_id'],available=True,source='synthetic_fixture'),at=future)
        recovered=state();current=find(recovered['snapshot']['work_packages'],'WP-A')
        if recovered['worker_runtime']['workers']['worker-a']['status']!='available' or current['assignment_ref']!=successor['assignment_id']:
            raise ValueError('old worker recovery stole assignment')
        no_duplicate=change('dispatch-next',dict(lease_seconds=300))
        if no_duplicate['assignment_id'] is not None:raise ValueError('duplicate dispatch after original worker recovery')
        try:change('submit',dict(a,path='src/a/tracked.txt',sha256=digest(A_DRAFT.encode())),actor(a))
        except ValueError as error:record('old-fence-rejected',dict(error=str(error),assignment_id=a['assignment_id']))
        else:raise ValueError('old fenced writer submitted')
        finish(resumed,'takeover',successor)
        change('submit',dict(successor,path='src/a/output.txt',sha256=digest(A_FINAL.encode())),actor(successor))
        delivered=copy.deepcopy(state()['deliveries'])
        try:change('submit',dict(successor,path='src/a/output.txt',sha256=digest(A_FINAL.encode())),actor(successor))
        except ValueError as error:
            if str(error)!='delivery already exists':raise
            record('duplicate-delivery-rejected',dict(error=str(error),assignment_id=successor['assignment_id']))
        else:raise ValueError('duplicate logical delivery accepted')
        if state()['deliveries']!=delivered:raise ValueError('duplicate attempt altered deliveries')
        change('release',successor,actor(successor))
        final=state();save(evidence/'final-state.json',final)
        deliveries=final['deliveries']
        logical_once=len([v for k,v in deliveries.items() if k=='WP-A'])==1 and deliveries['WP-A']['token']==successor['token']
        if not logical_once or len(deliveries)!=2:raise ValueError('logical delivery invariant failed')
        result=dict(format='synthetic-worker-demo/1',evidence_level='synthetic_fixture',provider_live=False,
            baseline_sha=baseline,parallel_processes_observed=parallel,original_writer_exit=exit_a,
            checkpoint=cp,old_token=a['token'],new_token=successor['token'],new_workspace=directory(successor).as_posix(),
            old_workspace=directory(a).as_posix(),old_worker_recovered_to_pool=True,old_token_rejected=True,
            logical_deliveries={key:1 for key in deliveries},duplicate_delivery_rejected=True,pmo_model_calls=0,actual_model_calls=0,
            states={key:value['status'] for key,value in final['worker_runtime']['workers'].items()},
            engineering_accepted=False,scope='fixed synthetic fixture under enclosing A01; not actual Claude/Codex execution',passed=True)
        save(evidence/'summary.json',result);return result
    except BaseException as error:
        save(evidence/'error.json',dict(type=type(error).__name__,message=str(error),passed=False))
        raise
    finally:
        for proc,stream,label in processes:
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
            if proc.stdin is not None and not proc.stdin.closed:proc.stdin.close()
            if proc.stdout is not None:proc.stdout.close()
            stream.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path)
    parser.add_argument('--fixture-worker',choices=['a','b','takeover'],help=argparse.SUPPRESS)
    args=parser.parse_args()
    if args.fixture_worker:fixture_worker(args.fixture_worker);return 0
    if args.root is None:raise ValueError('--root required')
    print(json.dumps(run_demo(args.root),indent=2));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,TimeoutError) as error:
        print(json.dumps({'error':str(error),'evidence_level':'synthetic_fixture'}),file=sys.stderr);sys.exit(2)
