"""Actual fixed Python processes inside A01; no model/credential/provider calls."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from framework.adapters.registry import AdapterRegistry, descriptor, synthetic_plan, synthetic_classify
from framework.adapters.invocation import ProcessExecutor, LaunchReservations
from framework.local.launch_driver import atomic


class InvocationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(); self.work = self.root / 'work'; self.work.mkdir()
        self.journal = self.root / 'journal'; self.journal.mkdir(); self.executors = []
        self.reservations = self.root / 'launches'; self.reservations.mkdir()
        self.addCleanup(self.stop_owned)
        self.authority = dict(assignment_id='assign-a', workspace_id='workspace-a', epoch=1, token=1)
        self.request = dict(work_package_id='WP-A', assignment_id='assign-a', baseline_sha='a'*40,
                            prompt='fixed task input', timeout_seconds=3, max_output_bytes=1024)

    def stop_owned(self):
        for executor in self.executors:
            for identity, live in list(executor._live.items()):
                live['stop'].set(); live['thread'].join(timeout=8)
                self.assertFalse(live['thread'].is_alive())

    def configured(self, program="import sys;print(sys.stdin.read());print('stderr-record',file=sys.stderr)",
                   authorize=None, name='tool-x', journal=None):
        desc = descriptor(name, 'agent-tool-' + name, 'model-provider-' + name,
                          quota_group='shared', validation_level='synthetic_fixture')
        for field in ('start', 'status', 'stop', 'result'): desc['capabilities'][field] = 'supported'
        selection = {k: desc[k] for k in ('adapter_id', 'agent_tool', 'model_provider', 'model', 'credential_ref', 'quota_group')}
        executor = ProcessExecutor(selection=selection, argv=['/usr/bin/python3', '-I', '-B', '-S', '-c', program],
            cwd=str(self.work), environment=dict(PATH='/usr/bin:/bin', HOME=str(self.work), LC_ALL='C'),
            journal_root=str(journal or self.journal),
            launch_reservations=LaunchReservations(self.reservations),
            pinned_files={'/usr/bin/python3':hashlib.sha256(Path('/usr/bin/python3').read_bytes()).hexdigest()},
            authorize=authorize or (lambda a,p:a==self.authority))
        self.executors.append(executor); registry = AdapterRegistry()
        registry.register(desc, planner=synthetic_plan, classifier=synthetic_classify, executor=executor)
        return registry, executor, desc

    def launch(self, registry, name='tool-x', operation='op-a', **changes):
        request = dict(self.request, **changes)
        return registry.start(name, operation_id=operation, authority=self.authority, **request)

    def finished(self, registry, identity, name='tool-x'):
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            value = registry.status(name, identity)
            if value['state'] not in ('launch_intent', 'running'): return value
            time.sleep(0.02)
        self.fail('bounded process did not settle')

    def test_real_process_input_output_exit_and_no_engineering_acceptance(self):
        r, e, d = self.configured(); value = self.launch(r); done = self.finished(r, value['invocation_id'])
        self.assertEqual(done['state'], 'exited'); self.assertEqual(done['exit_code'], 0)
        out = r.result('tool-x', value['invocation_id'])
        self.assertEqual(out['stdout'], b'fixed task input\n'); self.assertIn(b'stderr-record', out['stderr'])
        self.assertFalse(out['engineering_accepted']); self.assertFalse(out['writer_stop_confirmed'])
        self.assertEqual(out['evidence_level'], 'untrusted_stdout')
        self.assertEqual(out['baseline_sha'], self.request['baseline_sha'])
        self.assertEqual(out['stdin_sha256'], hashlib.sha256(self.request['prompt'].encode()).hexdigest())

    def test_n_adapters_execute_through_same_interface_without_provider_branches(self):
        for name in ('first', 'second', 'third'):
            self.work = self.root / ('work-' + name); self.work.mkdir()
            self.authority = dict(assignment_id='assign-' + name, workspace_id='workspace-' + name, epoch=1, token=1)
            self.request['assignment_id'] = self.authority['assignment_id']
            journal = self.root / name; journal.mkdir()
            r, e, d = self.configured(name=name, journal=journal)
            v = self.launch(r, name=name); self.assertEqual(self.finished(r, v['invocation_id'], name)['exit_code'], 0)
            self.assertEqual(r.result(name, v['invocation_id'])['selection']['model_provider'], 'model-provider-' + name)

    def test_proposal_argv_cannot_select_program_or_environment(self):
        r,e,d = self.configured("import os;print(os.environ.get('INHERITED_SECRET','absent'))")
        p=r.plan('tool-x',**self.request);p['argv_template']=['/arbitrary/program'];p['environment']={'INHERITED_SECRET':'forged'}
        with patch.dict(os.environ, {'INHERITED_SECRET':'host-only'}):
            v=e.start(operation_id='fixed',authority=self.authority,proposal=p)
        self.finished(r,v['invocation_id']);self.assertEqual(r.result('tool-x',v['invocation_id'])['stdout'],b'absent\n')

    def test_replay_after_lost_response_does_not_launch_twice(self):
        r,e,d=self.configured("from pathlib import Path;p=Path('count');p.write_text(p.read_text()+'x' if p.exists() else 'x')")
        v=self.launch(r);self.finished(r,v['invocation_id']);self.assertEqual(self.launch(r)['invocation_id'],v['invocation_id'])
        self.assertEqual((self.work/'count').read_text(),'x')
        with self.assertRaisesRegex(ValueError,'different intent'):self.launch(r,prompt='different')

    def test_unknown_launch_intent_never_replays_and_does_not_kill_by_pid(self):
        r,e,d=self.configured();p=r.plan('tool-x',**self.request)
        calls=[]
        def deny_second(a,p):calls.append(1);return len(calls)==1
        e.authorize=deny_second;v=e.start(operation_id='unknown',authority=self.authority,proposal=p)
        self.assertEqual(v['state'],'outcome_unknown')
        with patch('subprocess.Popen',side_effect=AssertionError('must not launch')):
            self.assertEqual(e.start(operation_id='unknown',authority=self.authority,proposal=p)['state'],'outcome_unknown')
        self.assertEqual(e.stop(invocation_id=v['invocation_id'])['state'],'outcome_unknown')

    def test_restarted_controller_cannot_treat_running_record_as_stopped_or_restart(self):
        program='import time;time.sleep(2)';r,e,d=self.configured(program);v=self.launch(r)
        r2,e2,d2=self.configured(program)
        self.assertEqual(r2.status('tool-x',v['invocation_id'])['state'],'outcome_unknown')
        self.assertEqual(self.launch(r2)['state'],'outcome_unknown')
        self.assertEqual(r2.stop('tool-x',v['invocation_id'])['state'],'outcome_unknown')
        r.stop('tool-x',v['invocation_id']);self.assertEqual(self.finished(r,v['invocation_id'])['state'],'stopped')

    def test_timeout_and_output_bound_are_distinct_and_never_accepted(self):
        for program,changes,expected in [('import time;time.sleep(5)',{'timeout_seconds':1},'timed_out'),
                                         ("print('x'*10000)",{},'output_limited')]:
            self.work = self.root / ('work-' + expected); self.work.mkdir()
            self.authority = dict(assignment_id='assign-' + expected, workspace_id='workspace-' + expected, epoch=1, token=1)
            self.request['assignment_id'] = self.authority['assignment_id']
            journal=self.root/expected;journal.mkdir();r,e,d=self.configured(program,journal=journal)
            v=self.launch(r,**changes);done=self.finished(r,v['invocation_id']);self.assertEqual(done['state'],expected)
            out=r.result('tool-x',v['invocation_id']);self.assertLessEqual(len(out['stdout'])+len(out['stderr']),1024)
            self.assertFalse(done['writer_stop_confirmed'])

    def test_stop_is_request_then_owned_exit_not_claimed_descendant_stop(self):
        r,e,d=self.configured('import time;time.sleep(5)');v=self.launch(r)
        requested=r.stop('tool-x',v['invocation_id']);self.assertEqual(requested['state'],'running')
        done=self.finished(r,v['invocation_id']);self.assertEqual(done['state'],'stopped');self.assertIsNotNone(done['exit_code'])
        self.assertFalse(done['writer_stop_confirmed'])

    def test_denied_authority_or_boolean_token_does_not_launch(self):
        r,e,d=self.configured(authorize=lambda a,p:False)
        with self.assertRaises(ValueError):self.launch(r)
        self.assertEqual(list(self.journal.glob('inv-*.json')),[])
        self.authority['token']=True
        with self.assertRaises(ValueError):self.launch(r)

    def test_output_tampering_and_binding_change_are_rejected(self):
        r,e,d=self.configured();v=self.launch(r);self.finished(r,v['invocation_id'])
        (self.journal/(v['invocation_id']+'.stdout')).write_bytes(b'forged')
        with self.assertRaisesRegex(ValueError,'changed'):r.result('tool-x',v['invocation_id'])
        r2,e2,d2=self.configured("print('different binding')")
        with self.assertRaisesRegex(ValueError,'binding'):r2.status('tool-x',v['invocation_id'])

    def test_unknown_capability_and_unbound_executor_cannot_start(self):
        r,e,d=self.configured();d['adapter_id']='unbound'
        with self.assertRaises(ValueError):AdapterRegistry().register(d,planner=synthetic_plan,classifier=synthetic_classify)
        r._adapters['tool-x'][0]['capabilities']['start']='unknown'
        with self.assertRaisesRegex(ValueError,'capability'):self.launch(r)

    def test_failure_exit_is_observed_not_promoted_to_success(self):
        r,e,d=self.configured('import sys;sys.exit(7)');v=self.launch(r)
        done=self.finished(r,v['invocation_id']);self.assertEqual(done['exit_code'],7);self.assertFalse(done['engineering_accepted'])

    def test_concurrent_duplicate_start_creates_one_actual_process(self):
        r,e,d=self.configured("from pathlib import Path;p=Path('once');p.write_text(p.read_text()+'x' if p.exists() else 'x')")
        barrier=threading.Barrier(3);values=[];errors=[]
        def launch():
            try:barrier.wait(timeout=3);values.append(self.launch(r))
            except BaseException as error:errors.append(error)
        threads=[threading.Thread(target=launch) for _ in range(3)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(timeout=5);self.assertFalse(thread.is_alive())
        self.assertEqual(errors,[]);self.assertEqual(len({v['invocation_id'] for v in values}),1)
        self.finished(r,values[0]['invocation_id']);self.assertEqual((self.work/'once').read_text(),'x')

    def test_stop_still_observed_after_child_closes_output_pipes(self):
        r,e,d=self.configured("import os,time;from pathlib import Path;os.close(1);os.close(2);Path('closed').touch();time.sleep(5)")
        v=self.launch(r);deadline=time.monotonic()+2
        while not (self.work/'closed').exists() and time.monotonic()<deadline:time.sleep(0.01)
        self.assertTrue((self.work/'closed').exists());r.stop('tool-x',v['invocation_id'])
        self.assertEqual(self.finished(r,v['invocation_id'])['state'],'stopped')

    def test_changed_pinned_input_prevents_spawn(self):
        r,e,d=self.configured();e.pins['/usr/bin/python3']='0'*64
        with patch('subprocess.Popen',side_effect=AssertionError('must not spawn')):
            with self.assertRaisesRegex(ValueError,'pin changed'):self.launch(r)
        self.assertEqual(list(self.journal.glob('inv-*.json')),[])

    def test_new_operation_cannot_repeat_same_authority_or_workspace(self):
        r,e,d=self.configured();v=self.launch(r);self.finished(r,v['invocation_id'])
        with self.assertRaisesRegex(ValueError,'already bound'):self.launch(r,operation='different-key')
        self.authority['token']=2
        with self.assertRaisesRegex(ValueError,'already bound'):self.launch(r,operation='new-token-same-workspace')

    def test_unknown_launch_cannot_be_retried_with_new_operation_id(self):
        r,e,d=self.configured();calls=[]
        def deny_second(a,p):calls.append(1);return len(calls)==1
        e.authorize=deny_second;v=self.launch(r);self.assertEqual(v['state'],'outcome_unknown')
        e.authorize=lambda a,p:True
        with patch('subprocess.Popen',side_effect=AssertionError('unknown result must not repeat')):
            with self.assertRaisesRegex(ValueError,'already bound'):self.launch(r,operation='replacement-key')

    def test_direct_only_namespace_cannot_gain_an_external_launch_path(self):
        parent=self.root/'V4-DIRECT-LOCAL-fixture';parent.mkdir();self.work=parent/'nested';self.work.mkdir()
        with self.assertRaisesRegex(ValueError,'direct-local-only'):self.configured()
        self.work=self.root/'work'
        with self.assertRaisesRegex(ValueError,'direct-local-only'):
            self.configured("print('/tmp/v4-direct-local-output')")

    def test_cross_adapter_lost_receipt_restarted_controller_and_independent_work(self):
        program = "import os,time;f=os.open('starts',os.O_CREAT|os.O_APPEND|os.O_WRONLY,0o600);os.write(f,b'x');os.close(f);time.sleep(1)"
        a, executor, _ = self.configured(program)
        first = self.launch(a)
        deadline = time.monotonic() + 2
        while not (self.work/'starts').exists() and time.monotonic() < deadline: time.sleep(0.01)
        self.assertEqual((self.work/'starts').read_bytes(), b'x')
        # Discard the caller's receipt. A replacement controller owns no handle.
        restored, _, _ = self.configured(program)
        unknown = restored.status('tool-x', first['invocation_id'])
        self.assertEqual(unknown['state'], 'outcome_unknown')
        journal_b = self.root/'journal-b'; journal_b.mkdir()
        b, _, _ = self.configured(program, name='tool-b', journal=journal_b)
        rejected = False
        try:
            second = self.launch(b, name='tool-b', operation='changed-key')
            self.finished(b, second['invocation_id'], 'tool-b')
        except ValueError: rejected = True
        self.finished(a, first['invocation_id'])
        original_count = len((self.work/'starts').read_bytes())
        # Another workspace/authority must not be blocked by A's observation.
        self.work = self.root/'independent'; self.work.mkdir()
        self.authority = dict(assignment_id='assign-b', workspace_id='workspace-b', epoch=1, token=1)
        self.request.update(assignment_id='assign-b', work_package_id='WP-B')
        journal_c = self.root/'journal-c'; journal_c.mkdir()
        c, _, _ = self.configured(program, name='tool-b', journal=journal_c)
        third = self.launch(c, name='tool-b', operation='independent-key')
        independent = self.finished(c, third['invocation_id'], 'tool-b')
        independent_count = len((self.work/'starts').read_bytes())
        print(json.dumps(dict(cross_adapter_receipt_loss=dict(original_process_starts=original_count,
            replacement_rejected=rejected, restored_state=unknown['state'],
            independent_process_starts=independent_count, independent_state=independent['state']))), flush=True)
        reservations = json.loads((self.reservations/'launches.json').read_text())
        print(json.dumps({'cross_adapter_reservations': [dict(authority=row['authority'],
            selection=row['selection'], state=row['state']) for row in reservations['intents']]}), flush=True)
        self.assertTrue(rejected)
        self.assertEqual(original_count, 1)
        self.assertEqual(independent_count, 1)
        self.assertEqual(independent['exit_code'], 0)

    def test_cross_adapter_concurrent_starts_share_persistent_lock(self):
        program = "import os;f=os.open('starts',os.O_CREAT|os.O_APPEND|os.O_WRONLY,0o600);os.write(f,b'x');os.close(f)"
        a, _, _ = self.configured(program)
        other = self.root/'other-journal'; other.mkdir()
        b, _, _ = self.configured(program, name='tool-b', journal=other)
        barrier = threading.Barrier(2); results = []; rejected = []
        def launch(registry, name):
            try:
                barrier.wait(timeout=3)
                results.append((registry, name, self.launch(registry, name=name, operation=name)))
            except ValueError as error: rejected.append(str(error))
        threads = [threading.Thread(target=launch, args=(r,n)) for r,n in ((a,'tool-x'),(b,'tool-b'))]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=5); self.assertFalse(thread.is_alive())
        self.assertEqual(len(results),1); self.assertEqual(len(rejected),1)
        r,n,v = results[0]; self.finished(r,v['invocation_id'],n)
        self.assertEqual((self.work/'starts').read_bytes(),b'x')

    def test_reservation_commit_then_local_journal_failure_never_rearms(self):
        r,e,_ = self.configured()
        real_atomic = atomic
        def fail_local(path, value):
            if path.parent == self.journal: raise OSError('injected lost local write')
            return real_atomic(path,value)
        with patch('framework.adapters.invocation.atomic', side_effect=fail_local):
            with patch('subprocess.Popen',side_effect=AssertionError('must not spawn')):
                with self.assertRaises(OSError): self.launch(r)
        self.assertEqual(list(self.journal.glob('inv-*.json')), [])
        before = (self.reservations/'launches.json').read_bytes()
        other = self.root/'replacement'; other.mkdir()
        self.authority['token'] = 2
        b,_,_ = self.configured(name='tool-b',journal=other)
        with patch('subprocess.Popen',side_effect=AssertionError('must not retry uncertain reservation')):
            with self.assertRaisesRegex(ValueError,'already bound'):
                self.launch(b,name='tool-b',operation='replacement')
        self.assertEqual(before,(self.reservations/'launches.json').read_bytes())

    def test_same_path_with_changed_workspace_identity_cannot_bypass_fence(self):
        r,_,_ = self.configured(); v = self.launch(r); self.finished(r,v['invocation_id'])
        self.authority.update(assignment_id='assign-other',workspace_id='workspace-other',token=2)
        self.request['assignment_id'] = 'assign-other'
        other = self.root/'other'; other.mkdir()
        b,_,_ = self.configured(name='tool-b',journal=other)
        with self.assertRaisesRegex(ValueError,'already bound'): self.launch(b,name='tool-b',operation='new-ids')

    def test_shared_output_journal_allows_independent_binding_and_same_operation(self):
        r,_,_ = self.configured(); v = self.launch(r); self.finished(r,v['invocation_id'])
        self.work = self.root/'work-b'; self.work.mkdir()
        self.authority.update(assignment_id='assign-b',workspace_id='workspace-b')
        self.request.update(assignment_id='assign-b',work_package_id='WP-B')
        b,e,d = self.configured(name='tool-b')
        r.register(d,planner=synthetic_plan,classifier=synthetic_classify,executor=e)
        other = self.launch(r,name='tool-b')
        self.assertNotEqual(v['invocation_id'],other['invocation_id'])
        self.assertEqual(self.finished(r,other['invocation_id'],'tool-b')['exit_code'],0)

    def test_registry_refuses_mixed_launch_domains(self):
        r,_,_ = self.configured()
        self.reservations = self.root/'wrong-domain'; self.reservations.mkdir()
        b,e,d = self.configured(name='tool-b')
        with self.assertRaisesRegex(ValueError,'share a launch domain'):
            r.register(d,planner=synthetic_plan,classifier=synthetic_classify,executor=e)


if __name__ == '__main__': unittest.main()
