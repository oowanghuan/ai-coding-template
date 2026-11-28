"""Fixed real processes: runtime authority loss and durable terminal observation.

Synthetic Store events only; no native model or provider quota event.
"""
import json
import subprocess
import threading
import time
import unittest
from unittest.mock import patch

import test_store_binding as helpers
import test_lifecycle as fixtures
from framework.local.storage import atomic_json, authority_lock
from framework.adapters.invocation import AuthorityWatch

PROGRAM = "import time;from pathlib import Path;p=Path('src/a/dirty.txt');p.parent.mkdir(exist_ok=True);p.write_text('unfinished work');Path('ready').touch();time.sleep(10)"


class RuntimeControlTests(unittest.TestCase):
    setUp = helpers.StoreBindingTests.setUp
    initial = helpers.StoreBindingTests.initial
    state = helpers.StoreBindingTests.state
    change = helpers.StoreBindingTests.change
    result = helpers.StoreBindingTests.result
    enable = helpers.StoreBindingTests.enable
    event = helpers.StoreBindingTests.event
    claim = helpers.StoreBindingTests.claim
    stop_owned = helpers.StoreBindingTests.stop_owned
    bound = helpers.StoreBindingTests.bound
    start = helpers.StoreBindingTests.start
    finish = helpers.StoreBindingTests.finish

    def long_job(self):
        job=self.bound(program=PROGRAM);job['request']['timeout_seconds']=10
        return job

    def wait_ready(self,job):
        deadline=time.monotonic()+3
        while not (job['cwd']/'ready').exists() and time.monotonic()<deadline:time.sleep(.01)
        self.assertTrue((job['cwd']/'ready').exists())

    def observed(self,job,record):
        return job['registry'].result('synthetic',record['invocation_id'])

    def test_post_final_guard_revocation_observed_after_real_spawn(self):
        job=self.long_job();real_popen=subprocess.Popen;spawns=[]
        def injected(argv,**kwargs):
            if argv[0]=='/usr/bin/python3':
                self.event('a','quota_limited')  # After final guard, immediately before actual Popen.
                spawns.append(time.monotonic())
            return real_popen(argv,**kwargs)
        with patch('subprocess.Popen',side_effect=injected):record=self.start(job)
        done=self.finish(job,record);elapsed=time.monotonic()-spawns[0]
        self.assertEqual(len(spawns),1);self.assertEqual(done['state'],'stopped')
        self.assertEqual(done['stop_reason'],'authority_revoked');self.assertLess(elapsed,5)
        result=self.observed(job,record)
        self.assertFalse(result['writer_stop_confirmed']);self.assertEqual(result['store_observation']['workspace_state'],'unknown')
        print(json.dumps({'post_final_guard_window':dict(actual_process_starts=1,stop_elapsed_seconds=elapsed,
            declared_test_bound_seconds=5,stop_reason=done['stop_reason'],writer_stop_confirmed=False,
            store_workspace_state='unknown',engineering_accepted=False)}),flush=True)

    def test_running_quota_loss_stops_owned_process_preserves_dirty_and_other_group(self):
        job=self.long_job();other=self.bound('c');record=self.start(job);self.wait_ready(job)
        before=(job['cwd']/'src/a/dirty.txt').read_bytes();start=time.monotonic()
        self.event('b','quota_limited')
        done=self.finish(job,record);self.assertEqual(done['stop_reason'],'authority_revoked')
        self.assertLess(time.monotonic()-start,5)
        self.assertEqual(before,(job['cwd']/'src/a/dirty.txt').read_bytes())
        result=self.observed(job,record)
        self.assertFalse(result['engineering_accepted']);self.assertFalse(result['writer_stop_confirmed'])
        self.assertEqual(self.finish(other,self.start(other))['exit_code'],0)
        with self.assertRaises(ValueError):self.claim('c',wp='WP-A')

    def test_stuck_authority_check_does_not_block_owned_stop_deadline(self):
        job=self.long_job();release=threading.Event();entered=threading.Event()
        def stuck(record):entered.set();release.wait(8);return True
        job['executor'].runtime_guard=stuck
        try:
            started=time.monotonic();record=self.start(job);self.assertTrue(entered.wait(2))
            done=self.finish(job,record)
            self.assertEqual(done['state'],'stopped');self.assertEqual(done['stop_reason'],'authority_check_timeout')
            self.assertLess(time.monotonic()-started,5)
        finally:release.set()

    def test_runtime_check_error_fails_closed(self):
        job=self.long_job()
        def unavailable(record):raise OSError('synthetic Store read failure')
        job['executor'].runtime_guard=unavailable
        done=self.finish(job,self.start(job));self.assertEqual(done['stop_reason'],'authority_check_error')
        self.assertFalse(done['writer_stop_confirmed'])

    def test_busy_store_lock_cannot_hold_the_owned_process_alive(self):
        job=self.long_job();record=self.start(job);self.wait_ready(job)
        # A real competing Store lock, not a mocked callback failure. Supervision
        # must still stop the child while the read-only monitor waits for it.
        with authority_lock(self.root):
            started=time.monotonic();done=self.finish(job,record)
            self.assertEqual(done['stop_reason'],'authority_check_timeout')
            self.assertLess(time.monotonic()-started,5)
        observed=self.observed(job,record)
        self.assertEqual(observed['store_observation']['workspace_state'],'unknown')

    def test_runtime_lease_expiry_stops_without_pmo(self):
        job=self.long_job();record=self.start(job);self.wait_ready(job)
        with patch('framework.adapters.store_binding.now',return_value=fixtures.later(601)):
            done=self.finish(job,record)
        self.assertEqual(done['stop_reason'],'authority_revoked')
        self.assertFalse(done['engineering_accepted'])

    def test_terminal_observation_replay_does_not_release_or_increment_revision(self):
        job=self.bound();record=self.start(job);self.finish(job,record)
        first=self.observed(job,record);before=self.store.path.read_bytes()
        second=self.observed(job,record);self.assertEqual(first,second)
        self.assertEqual(before,self.store.path.read_bytes())
        self.assertEqual(first['store_observation']['workspace_state'],'unknown')
        with self.assertRaises(ValueError):self.result('release',job['authority'],actor='principal-a')

    def test_terminal_store_commit_lost_receipt_replays_without_new_process(self):
        job=self.bound();record=self.start(job);self.finish(job,record);real=atomic_json
        def lost(path,value):real(path,value);raise OSError('lost observation commit receipt')
        with patch('framework.adapters.store_binding.atomic_json',side_effect=lost):
            with self.assertRaises(OSError):self.observed(job,record)
        before=self.store.path.read_bytes();result=self.observed(job,record)
        self.assertEqual(before,self.store.path.read_bytes());self.assertTrue(result['store_observation']['observed'])
        self.assertEqual(len([r for r in self.state()['operations'].values() if r['action']=='provider-process-observed']),1)

    def test_output_tamper_cannot_be_recorded_as_store_result(self):
        job=self.bound();record=self.start(job);self.finish(job,record);before=self.store.path.read_bytes()
        (job['journal']/(record['invocation_id']+'.stdout')).write_bytes(b'forged')
        with self.assertRaises(ValueError):self.observed(job,record)
        self.assertEqual(before,self.store.path.read_bytes())

    def test_late_successful_guard_cannot_restore_freshness(self):
        entered=threading.Event();release=threading.Event()
        def late(record):entered.set();release.wait(2);return True
        with patch.object(AuthorityWatch,'MAX_STALE',.05):
            watch=AuthorityWatch(late,{})
            try:
                self.assertTrue(entered.wait(1));time.sleep(.08);release.set();watch.thread.join(1)
                self.assertEqual(watch.snapshot()['failure'],'authority_check_timeout')
            finally:watch.closed.set();release.set()
