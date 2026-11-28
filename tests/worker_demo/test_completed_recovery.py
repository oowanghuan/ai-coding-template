"""Completed synthetic deliveries survive duplicate recovery notifications.

This observes fixed local writer calls/artifacts, not exactly-once external APIs.
Real provider/API calls remain zero and unverified.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('completed_worker_demo', ROOT/'scripts/v4_worker_demo.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


@unittest.skipUnless(os.environ.get('V4_OUTER_SEATBELT') == '1', 'reviewed enclosing A01 required')
class CompletedRecoveryTests(unittest.TestCase):
    def test_completed_delivery_recovery_replay_twice_and_new_id_rejected(self):
        from framework.local.store import Store
        from framework.local.storage import fingerprint
        # Retain success/failure artifacts; never overwrite or resume an old root.
        stage = Path(tempfile.mkdtemp(prefix='completed-recovery-')).resolve()
        root = stage/'project'
        print('completed recovery evidence: ' + str(stage), flush=True)
        summary = demo.run_demo(root)
        self.assertTrue(summary['passed'])
        store = Store(root)
        state = store.inspect()['state']
        journal_path = root/'demo-evidence/journal.json'
        journal_bytes = journal_path.read_bytes()
        journal = json.loads(journal_bytes)
        receipt = next(row['data']['operation'] for row in reversed(journal)
                       if row['kind'] == 'worker-event' and
                       row['data']['operation']['result']['status'] == 'available')
        operations = [key for key,value in state['operations'].items() if value == receipt]
        self.assertEqual(len(operations), 1)
        operation_id = operations[0]
        probes = [probe for row in journal if row['kind'] == 'scheduler-tick'
                  for probe in row['data']['operation']['result']['probes'] if probe['group'] == 'quota-a']
        self.assertEqual(len(probes), 1)
        payload = dict(worker_id='worker-a', event='probe-result',
                       probe_id=probes[0]['probe_id'], available=True, source='synthetic_fixture')
        actor = receipt['actor']
        self.assertEqual(fingerprint(dict(action='worker-event',payload=payload,actor=actor)), receipt['intent'])
        self.assertEqual(set(state['deliveries']), {'WP-A', 'WP-B'})
        self.assertTrue(all(a['state'] not in ('active','reserved') for a in state['snapshot']['assignments']))
        state_bytes = (root/'.ai-org/state.json').read_bytes()
        def outputs():
            return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted((root/'.ai-org/workspaces').rglob('*')) if p.is_file()}
        artifacts = outputs()
        launch_count = sum(row['kind'] == 'process-launched' for row in journal)
        self.assertEqual(launch_count, 3)  # A, B's own task, B's takeover; actual prior Popen calls.
        replays = []
        # Guard only the post-completion window. No fake process replaces the
        # three actual preceding writers; any attempted new launch fails this test.
        with patch('subprocess.Popen', side_effect=AssertionError('unexpected post-completion process launch')) as popen:
            for _ in range(2):
                result = store.change('worker-event',payload,actor,state['revision'],operation_id)
                self.assertTrue(result['replayed'])
                self.assertEqual(result['operation'], receipt)
                self.assertEqual((root/'.ai-org/state.json').read_bytes(), state_bytes)
                self.assertEqual(outputs(), artifacts)
                self.assertEqual(journal_path.read_bytes(), journal_bytes)
                replays.append(result)
            with self.assertRaisesRegex(ValueError, '^stale/unknown probe result$'):
                store.change('worker-event',payload,actor,state['revision'],'post-completion-new-operation')
            popen.assert_not_called()
        final = store.inspect()['state']
        self.assertEqual(final, state)
        self.assertEqual((root/'.ai-org/state.json').read_bytes(), state_bytes)
        self.assertEqual(outputs(), artifacts)
        self.assertEqual(journal_path.read_bytes(), journal_bytes)
        report = dict(format='completed-recovery-replay/1',evidence_level='synthetic_fixture',
                      operation_id=operation_id,payload=payload,actor=actor,replays=replays,
                      new_operation_same_probe_rejected=True,authority_unchanged=True,
                      assignments_unchanged=True,logical_deliveries_unchanged=True,
                      artifact_sha256=artifacts,prior_actual_fixed_writer_starts=launch_count,
                      post_completion_process_start_attempts=0,actual_external_api_calls=0,
                      external_exactly_once_verified=False,provider_live=False,
                      state_sha256=hashlib.sha256(state_bytes).hexdigest(),passed=True)
        (stage/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')


if __name__ == '__main__':
    unittest.main()
