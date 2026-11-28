"""Non-author handoff tests with actual Git worktrees and owned process groups.

Only synthetic authority fixtures are modified for negative cases. Child processes
sleep; test-created dirty files are not attributed to a model or real provider.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_lifecycle as shared
from framework.local import handoff
from framework.local.runner import git, prepare
from framework.local.storage import atomic_json
from framework.local.store import find


class HandoffTests(unittest.TestCase):
    initial=shared.LifecycleTests.initial
    state=shared.LifecycleTests.state
    change=shared.LifecycleTests.change
    result=shared.LifecycleTests.result
    enable=shared.LifecycleTests.enable
    event=shared.LifecycleTests.event
    claim=shared.LifecycleTests.claim

    def setUp(self):
        shared.LifecycleTests.setUp(self)
        self.clock=shared.AT
        for module in ('framework.local.store','framework.local.runner','framework.local.handoff'):
            clock=patch(module+'.now',side_effect=lambda:self.clock);clock.start();self.addCleanup(clock.stop)
        path=self.root/'src/a';path.mkdir();(path/'dirty.txt').write_bytes(b'baseline dirty\n');(path/'deleted.txt').write_bytes(b'baseline deletion\n')
        git(self.root,'add','src/a')
        git(self.root,'-c','user.name=Synthetic','-c','user.email=fixture@example.invalid','commit','-qm','handoff baseline')
        self.sha=git(self.root,'rev-parse','HEAD').decode().strip()
        self.initial();self.enable()
        self.processes=[];self.addCleanup(self.cleanup_processes)
    def cleanup_processes(self):
        for process in self.processes:
            if process.poll() is None:process.terminate()
            process.wait(timeout=5)
            if process.stdout:process.stdout.close()
            if process.stderr:process.stderr.close()
    def start_old(self):
        self.old=self.claim('a')
        prepare(self.root,self.old,'principal-a',self.state()['revision'],'prepare-old')
        self.old_workspace=self.state()['workspaces'][self.old['workspace_id']]
        self.old_path=self.root/self.old_workspace['path']
        (self.old_path/'src/a/dirty.txt').write_bytes(b'dirty checkpoint result\n')
        (self.old_path/'src/a/deleted.txt').unlink()
        (self.old_path/'src/a/draft.txt').write_bytes(b'untracked checkpoint result\n')
        self.result('run-begin',dict(self.old,path='src/a/provider-output.txt',content_sha256='a'*64),actor='principal-a')
        process=subprocess.Popen([sys.executable,'-B','-S','-c','import time;time.sleep(60)'],cwd=self.old_path,
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        self.processes.append(process);self.process=process
        self.assertEqual(os.getpgid(process.pid),process.pid)
        self.store.workspace_phase(self.old,'principal-a','launching','running',run=dict(state='running',pid=process.pid,process_group=process.pid,unknown_operations=[]))
        return process
    def snapshot(self):
        return handoff.checkpoint(self.root,self.old,'principal-a',completed=['synthetic dirty draft'],remaining=['final validation'])
    def stop(self):
        self.event('a','quota_limited')
        self.process.terminate();status=self.process.wait(timeout=5)
        with self.assertRaises(ProcessLookupError):os.killpg(self.process.pid,0)
        result=handoff.confirm_stopped(self.root,self.old,'principal-a',self.process)
        self.assertEqual(result['exit_code'],status)
        print(json.dumps({'owned_handoff_stop':{'pid':self.process.pid,'registered_group':self.process.pid,'wait_exit':status,'group_absent':True}}))
        return result
    def ready_for_takeover(self):
        self.start_old();self.snapshot();self.stop()
    def new_claim(self):
        new=self.claim('c',wp='WP-A');self.assertGreater(new['token'],self.old['token'])
        self.assertEqual(self.state()['workspaces'][new['workspace_id']]['recovery_source'],self.old['workspace_id'])
        return new
    def submit_forbidden(self,new):
        state=self.state();workspace=state['workspaces'][new['workspace_id']]
        self.assertEqual(workspace['state'],'creating')
        with self.assertRaises(ValueError):
            self.result('submit',dict(new,path='src/a/dirty.txt',sha256=hashlib.sha256(b'baseline dirty\n').hexdigest()),actor='principal-c')
        self.assertNotIn('WP-A',self.state()['deliveries'])

    def test_actual_stop_then_higher_fence_handoff_preserves_dirty_and_untracked(self):
        self.ready_for_takeover();before={str(p.relative_to(self.old_path)):p.read_bytes() for p in self.old_path.rglob('*') if p.is_file()}
        new=self.new_claim();handoff.prepare_handoff(self.root,new,'principal-c',self.state()['revision'],'prepare-new')
        workspace=self.state()['workspaces'][new['workspace_id']];target=self.root/workspace['path']
        self.assertEqual(workspace['state'],'prepared');self.assertIn('restored',workspace)
        self.assertEqual((target/'src/a/dirty.txt').read_bytes(),b'dirty checkpoint result\n')
        self.assertEqual((target/'src/a/draft.txt').read_bytes(),b'untracked checkpoint result\n')
        self.assertFalse((target/'src/a/deleted.txt').exists())
        self.assertEqual({str(p.relative_to(self.old_path)):p.read_bytes() for p in self.old_path.rglob('*') if p.is_file()},before)
        delivery=self.result('submit',dict(new,path='src/a/draft.txt',sha256=hashlib.sha256(b'untracked checkpoint result\n').hexdigest()),actor='principal-c')
        self.assertFalse(delivery['accepted']);self.assertEqual(len(self.state()['deliveries']),1)
    def test_running_or_unregistered_owned_process_cannot_confirm_stopped(self):
        self.start_old();self.snapshot()
        with self.assertRaisesRegex(ValueError,'still running'):handoff.confirm_stopped(self.root,self.old,'principal-a',self.process)
        other=subprocess.Popen([sys.executable,'-B','-S','-c','pass'],start_new_session=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.processes.append(other);other.wait(timeout=5)
        with self.assertRaisesRegex(ValueError,'not registered'):handoff.confirm_stopped(self.root,self.old,'principal-a',other)
        self.assertNotEqual(self.state()['workspaces'][self.old['workspace_id']]['state'],'stopped')
    def test_stop_without_checkpoint_cannot_release_unknown_workspace(self):
        self.start_old();self.event('a','quota_limited');self.process.terminate();self.process.wait(timeout=5)
        with self.assertRaisesRegex(ValueError,'checkpoint'):handoff.confirm_stopped(self.root,self.old,'principal-a',self.process)
        self.assertEqual(self.state()['workspaces'][self.old['workspace_id']]['state'],'unknown')
        with self.assertRaises(ValueError):self.claim('c',wp='WP-A')
    def test_stale_checkpoint_pin_rejected_against_latest_registered_checkpoint(self):
        self.start_old();old=self.snapshot();(self.old_path/'src/a/draft.txt').write_bytes(b'later preserved draft\n');self.snapshot();self.stop()
        state=self.state();record={key:old[key] for key in ('path','manifest_sha256','binding','unknown_digest')}
        state['workspaces'][self.old['workspace_id']]['checkpoint']=record
        atomic_json(self.store.path,state) # Deliberately corrupt only the synthetic authority pointer.
        with self.assertRaisesRegex(ValueError,'latest checkpoint'):self.claim('c',wp='WP-A')
        self.assertEqual((self.old_path/'src/a/draft.txt').read_bytes(),b'later preserved draft\n')
    def test_corrupt_checkpoint_artifact_rejected_before_new_claim(self):
        self.ready_for_takeover();state=self.state();record=state['workspaces'][self.old['workspace_id']]['checkpoint']
        (self.root/record['path']/'data/src/a/draft.txt').write_bytes(b'corrupt snapshot')
        with self.assertRaisesRegex(ValueError,'checkpoint'):self.claim('c',wp='WP-A')
        self.assertEqual(len(self.state()['snapshot']['assignments']),1)
    def test_spec_baseline_and_new_unknown_after_checkpoint_block_claim(self):
        self.ready_for_takeover();pristine=self.state()
        for kind in ('spec','baseline','unknown'):
            with self.subTest(kind=kind):
                state=copy.deepcopy(pristine);wp=find(state['snapshot']['work_packages'],'WP-A')
                if kind=='spec':wp['spec_refs'][0]['version']='changed-after-snapshot'
                elif kind=='baseline':wp['baseline_sha']='f'*40
                else:state['workspaces'][self.old['workspace_id']]['run']['unknown_operations']=[dict(id='late-op',intent='unknown late effect',reconciliation='read trusted receipt')]
                atomic_json(self.store.path,state) # Synthetic post-snapshot authority mutation.
                with self.assertRaisesRegex(ValueError,'changed since|unknown operation'):self.claim('c',wp='WP-A')
                self.assertEqual(len(self.state()['snapshot']['assignments']),1)
        atomic_json(self.store.path,pristine)
    def test_recovered_old_worker_cannot_steal_new_assignment(self):
        self.ready_for_takeover();new=self.new_claim()
        probe=self.result('scheduler-tick',{},at=shared.later(5))['probes'][0]
        self.event('a','probe-result',at=shared.later(6),probe_id=probe['probe_id'],available=True)
        self.assertEqual(self.state()['worker_runtime']['workers']['worker-a']['status'],'available')
        with self.assertRaisesRegex(ValueError,'claimed'):self.claim('a',at=shared.later(6))
        with self.assertRaisesRegex(ValueError,'fenced'):self.result('start',self.old,actor='principal-a',at=shared.later(6))
        wp=find(self.state()['snapshot']['work_packages'],'WP-A');self.assertEqual(wp['assignment_ref'],new['assignment_id'])
    def test_restore_error_leaves_creating_and_forbids_submit(self):
        self.ready_for_takeover();new=self.new_claim()
        with patch('framework.local.handoff.restore_snapshot',side_effect=OSError('injected restore failure')):
            with self.assertRaises(OSError):handoff.prepare_handoff(self.root,new,'principal-c',self.state()['revision'],'prepare-error')
        self.submit_forbidden(new)
    def test_partial_restore_write_cannot_be_submitted_or_replayed(self):
        self.ready_for_takeover();new=self.new_claim();original=Path.write_bytes;changed=[False]
        def failing(path,content):
            if str(new['workspace_id']) in str(path) and path.name=='draft.txt' and not changed[0]:
                changed[0]=True;raise OSError('injected partial file restore')
            return original(path,content)
        with patch('pathlib.Path.write_bytes',new=failing):
            with self.assertRaises(OSError):handoff.prepare_handoff(self.root,new,'principal-c',self.state()['revision'],'prepare-partial')
        self.assertTrue(changed[0]);self.submit_forbidden(new)
        before=self.store.path.read_bytes()
        with self.assertRaises(ValueError):handoff.prepare_handoff(self.root,new,'principal-c',0,'prepare-partial')
        self.assertEqual(self.store.path.read_bytes(),before)


    def test_final_prepared_or_finished_output_without_checkpoint_blocks_reassignment(self):
        old=self.claim('a');prepare(self.root,old,'principal-a',self.state()['revision'],'prepare-unsnapshotted')
        pristine=self.state();workspace=pristine['workspaces'][old['workspace_id']]
        artifact=self.root/workspace['path']/'src/a/unsubmitted.txt';artifact.write_bytes(b'preserve unsubmitted result\n')
        for phase in ('prepared','finished'):
            with self.subTest(phase=phase):
                state=copy.deepcopy(pristine)
                # Trusted synthetic state fixture for this negative regression;
                # finished here is not evidence that a model/runner executed.
                state['workspaces'][old['workspace_id']]['state']=phase
                if phase=='finished':state['workspaces'][old['workspace_id']]['run']={'state':'finished','exit_code':0}
                atomic_json(self.store.path,state)
                self.event('a','quota_limited')
                fenced=self.state();saved=fenced['workspaces'][old['workspace_id']]
                self.assertEqual(saved['state'],phase)
                self.assertTrue(saved['handoff_required']);self.assertNotIn('checkpoint',saved)
                before=self.store.path.read_bytes()
                with self.assertRaisesRegex(ValueError,'checkpointed before reassignment'):
                    self.claim('c',wp='WP-A')
                self.assertEqual(self.store.path.read_bytes(),before)
                self.assertEqual(len(self.state()['snapshot']['assignments']),1)
                self.assertEqual(artifact.read_bytes(),b'preserve unsubmitted result\n')
    def test_final_boolean_epoch_and_token_cannot_alias_integer_execution_rights(self):
        old=self.claim('a');prepare(self.root,old,'principal-a',self.state()['revision'],'prepare-bool-binding')
        self.assertEqual(old['token'],1);self.assertEqual(old['epoch'],1)
        before=self.store.path.read_bytes()
        for field in ('token','epoch'):
            for value in (True,False):
                with self.subTest(field=field,value=value),self.assertRaisesRegex(ValueError,'must be integers'):
                    handoff.checkpoint(self.root,dict(old,**{field:value}),'principal-a',completed=['synthetic'],remaining=['continue'])
                self.assertEqual(self.store.path.read_bytes(),before)
        self.assertFalse((self.root/'.ai-org/checkpoints').exists())


if __name__=='__main__':unittest.main()
