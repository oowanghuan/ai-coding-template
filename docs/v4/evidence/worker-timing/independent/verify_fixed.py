import json,subprocess,sys,os
from pathlib import Path
from test_lifecycle import LifecycleTests, later
from test_handoff import HandoffTests
from framework.local import handoff

report={'scope':'independent fixed-version timing verification, real local fixed writer, injected quota observations, no provider calls'}
case=LifecycleTests();case.setUp()
try:
 case.initial();case.enable();case.event('a','quota_limited',retry_at=later(5))
 old=case.result('scheduler-tick',{},at=later(5))['probes'][0]
 case.event('b','quota_limited',at=later(6),retry_at=later(100))
 newer=case.state()['worker_runtime']['groups']['Q1']
 while_unknown=case.result('scheduler-tick',{},at=later(100))
 assert while_unknown['probes']==[],'unknown old probe must prevent another launch'
 assert case.state()['worker_runtime']['groups']['Q1']['pending_probe']==old['probe_id']
 stale_result=case.event('a','probe-result',at=later(101),probe_id=old['probe_id'],available=True)
 after_old=case.state()['worker_runtime']['groups']['Q1']
 assert after_old['limited'] is True and after_old['retry_at']==later(100)
 assert after_old['attempts']==newer['attempts'] and after_old['pending_probe'] is None
 new=case.result('scheduler-tick',{},at=later(101))['probes'][0]
 assert new['probe_id']!=old['probe_id']
 case.event('b','probe-result',at=later(102),probe_id=new['probe_id'],available=True)
 after_new=case.state()['worker_runtime']['groups']['Q1']
 assert after_new['limited'] is False
 report['quota']={'old_probe':old,'new_limit':newer,'unknown_probe_tick':while_unknown,'stale_success_receipt':stale_result,'after_old_success':after_old,'new_probe':new,'after_new_success':after_new,'old_success_cannot_clear_new_limit':True,'unknown_probe_blocks_new_launch':True,'only_current_generation_recovers':True}
finally:case.doCleanups()
case=HandoffTests();case.setUp()
try:
 original=case.start_old();original.terminate();original.wait(timeout=5)
 writer='import sys;from pathlib import Path;print("ready",flush=True);sys.stdin.readline();Path(sys.argv[1]).write_bytes(b"FINAL-WRITER-BYTES\\n");print("wrote",flush=True)'
 process=subprocess.Popen([sys.executable,'-I','-B','-S','-c',writer,str(case.old_path/'src/a/dirty.txt')],cwd=case.old_path,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 case.processes.append(process);case.process=process
 assert process.stdout.readline()==b'ready\n'
 case.store.workspace_phase(case.old,'principal-a','running','running',run=dict(state='running',pid=process.pid,process_group=process.pid,unknown_operations=[]))
 checkpoint=case.snapshot();snapshot_bytes=(case.old_path/'src/a/dirty.txt').read_bytes()
 process.stdin.write(b'write-final\n');process.stdin.close();assert process.stdout.readline()==b'wrote\n';status=process.wait(timeout=5);assert status==0
 final_bytes=(case.old_path/'src/a/dirty.txt').read_bytes();case.event('a','quota_limited');state_before=case.store.path.read_bytes()
 try:handoff.confirm_stopped(case.root,case.old,'principal-a',process)
 except ValueError as error:stop_error=str(error)
 else:raise AssertionError('stale pre-exit snapshot must not confirm stopped')
 assert case.store.path.read_bytes()==state_before
 try:case.new_claim()
 except ValueError as error:claim_error=str(error)
 else:raise AssertionError('handoff must remain blocked until final snapshot')
 assert (case.old_path/'src/a/dirty.txt').read_bytes()==final_bytes
 final_checkpoint=case.snapshot();handoff.confirm_stopped(case.root,case.old,'principal-a',process)
 new=case.new_claim();handoff.prepare_handoff(case.root,new,'principal-c',case.state()['revision'],'independent-final-restore')
 workspace=case.state()['workspaces'][new['workspace_id']];restored=(case.root/workspace['path']/'src/a/dirty.txt').read_bytes()
 assert restored==final_bytes and restored!=snapshot_bytes
 report['snapshot']={'actual_writer_pid':process.pid,'actual_writer_exit':status,'initial_checkpoint':checkpoint,'final_checkpoint':final_checkpoint,'snapshot_bytes':snapshot_bytes.decode(),'final_old_bytes':final_bytes.decode(),'restored_bytes':restored.decode(),'stale_stop_error':stop_error,'stale_claim_error':claim_error,'failed_stop_preserved_authority':True,'final_bytes_restored':True}
finally:case.doCleanups()
report['passed']=True
print(json.dumps(report,indent=2),flush=True)
