import json,subprocess,sys,os
from pathlib import Path
from test_lifecycle import LifecycleTests, later
from test_handoff import HandoffTests
from framework.local import handoff

report={'scope':'actual local frozen-baseline reproduction, synthetic observation, no provider calls'}
case=LifecycleTests();case.setUp()
try:
 case.initial();case.enable();case.event('a','quota_limited',retry_at=later(5))
 probe=case.result('scheduler-tick',{},at=later(5))['probes'][0]
 case.event('b','quota_limited',at=later(6),retry_at=later(100))
 before=case.state()['worker_runtime']['groups']['Q1']
 result=case.event('a','probe-result',at=later(7),probe_id=probe['probe_id'],available=True)
 after=case.state()['worker_runtime']['groups']['Q1']
 report['quota']={'probe':probe,'before_late_success':before,'after_late_success':after,'bug_reproduced':before['limited'] and not after['limited'] and after['retry_at'] is None}
finally:case.doCleanups()
case=HandoffTests();case.setUp()
try:
 original=case.start_old();original.terminate();original.wait(timeout=5)
 writer='import sys;from pathlib import Path;print("ready",flush=True);sys.stdin.readline();Path(sys.argv[1]).write_bytes(b"FINAL-WRITER-BYTES\\n");print("wrote",flush=True)'
 process=subprocess.Popen([sys.executable,'-I','-B','-S','-c',writer,str(case.old_path/'src/a/dirty.txt')],cwd=case.old_path,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 case.processes.append(process);case.process=process
 assert process.stdout.readline()==b'ready\n'
 case.store.workspace_phase(case.old,'principal-a','running','running',run=dict(state='running',pid=process.pid,process_group=process.pid,unknown_operations=[]))
 checkpoint=case.snapshot();old_bytes=(case.old_path/'src/a/dirty.txt').read_bytes()
 process.stdin.write(b'write-final\n');process.stdin.close();assert process.stdout.readline()==b'wrote\n';status=process.wait(timeout=5)
 assert status==0
 final_bytes=(case.old_path/'src/a/dirty.txt').read_bytes()
 case.event('a','quota_limited')
 handoff.confirm_stopped(case.root,case.old,'principal-a',process)
 new=case.new_claim();handoff.prepare_handoff(case.root,new,'principal-c',case.state()['revision'],'baseline-reproduce-final')
 workspace=case.state()['workspaces'][new['workspace_id']];restored=(case.root/workspace['path']/'src/a/dirty.txt').read_bytes()
 report['snapshot']={'actual_writer_pid':process.pid,'actual_writer_exit':status,'checkpoint':checkpoint,'snapshot_bytes':old_bytes.decode(),'final_old_workspace_bytes':final_bytes.decode(),'restored_new_workspace_bytes':restored.decode(),'bug_reproduced':old_bytes!=final_bytes and restored==old_bytes}
finally:case.doCleanups()
report['both_reproduced']=report['quota']['bug_reproduced'] and report['snapshot']['bug_reproduced']
print(json.dumps(report,indent=2),flush=True)
raise SystemExit(0 if report['both_reproduced'] else 1)
