import copy
import hashlib
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

from framework.local.bootstrap import apply, inventory, plan, rollback
from framework.local.storage import atomic_json, fingerprint
from framework.local.store import Store
from framework.local.runner import git


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def plan(self, mode='init', **kw):
        return plan(self.root, mode, 'demo', 'owner', **kw)

    def install(self, proposed=None):
        p = proposed or self.plan()
        return apply(self.root, p, p['plan_sha256'])

    def test_dry_run_writes_nothing_and_initial_state_is_honest(self):
        before = inventory(self.root)
        p = self.plan(); self.plan()
        self.assertEqual(inventory(self.root), before)
        self.install(p)
        result = Store(self.root).inspect()
        self.assertEqual(result['consistency_errors'], [])
        snapshot = result['state']['snapshot']
        self.assertEqual(snapshot['workers'], [])
        self.assertEqual(snapshot['authorizations'], [])
        self.assertEqual(snapshot['work_packages'][0]['state'], 'planned')
        self.assertIsNone(snapshot['work_packages'][0]['baseline_sha'])
        self.assertFalse((self.root / '.git').exists())

    def test_dirty_import_preserves_git_files_and_custom_rules(self):
        git(self.root, 'init', '-q')
        (self.root / 'code.txt').write_text('old')
        git(self.root, 'add', 'code.txt')
        git(self.root, '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid', 'commit', '-qm', 'base')
        (self.root / 'code.txt').write_text('dirty')
        (self.root / 'CLAUDE.md').write_text('custom rules')
        (self.root / 'untracked.txt').write_text('uncommitted')
        before = inventory(self.root)
        self.install(self.plan('import'))
        after = inventory(self.root)
        self.assertTrue(all(after[k] == v for k, v in before.items()))
        self.assertEqual(Store(self.root).inspect()['state']['snapshot']['work_packages'][0]['baseline_sha'], before['git-head'])

    def test_repeat_apply_and_rollback_are_safe(self):
        p = self.plan(); receipt = self.install(p)
        before = inventory(self.root)
        self.assertTrue(self.install(p)['replayed'])
        self.assertEqual(inventory(self.root), before)
        rollback(self.root, receipt['transaction_id'])
        again = inventory(self.root)
        rollback(self.root, receipt['transaction_id'])
        self.assertEqual(inventory(self.root), again)
        self.assertFalse((self.root / 'BOOTSTRAP.md').exists())

    def test_stale_plan_and_wrong_hash_rejected(self):
        p = self.plan()
        with self.assertRaisesRegex(ValueError, 'fingerprint'): apply(self.root, p, 'a'*64)
        (self.root / 'new.txt').write_text('preserve')
        with self.assertRaisesRegex(ValueError, 'stale'): self.install(p)
        self.assertEqual((self.root / 'new.txt').read_text(), 'preserve')
        self.assertFalse((self.root / '.ai-org/state.json').exists())

    def test_custom_bootstrap_conflict(self):
        (self.root / 'BOOTSTRAP.md').write_text('custom')
        p = self.plan('import')
        self.assertTrue(any(r['action'] == 'conflict' for r in p['files']))
        with self.assertRaisesRegex(ValueError, 'conflicting'): self.install(p)
        self.assertEqual((self.root / 'BOOTSTRAP.md').read_text(), 'custom')

    def test_symlink_destination_refused(self):
        outside = self.root / 'outside'; outside.mkdir()
        (self.root / '.ai-org').symlink_to(outside)
        with self.assertRaises(ValueError): self.plan('import')
        self.assertEqual(list(outside.iterdir()), [])

    def test_upgrade_and_rollback_preserve_task_authority(self):
        self.install()
        state = (self.root / '.ai-org/state.json').read_bytes()
        p = self.plan('upgrade', version='0.3-preview', guide_bytes=b'next immutable guide')
        receipt = self.install(p)
        self.assertEqual((self.root / '.ai-org/state.json').read_bytes(), state)
        self.assertTrue((self.root / receipt['guide']).exists())
        rollback(self.root, receipt['transaction_id'])
        self.assertEqual((self.root / '.ai-org/state.json').read_bytes(), state)
        self.assertFalse((self.root / receipt['guide']).exists())
        self.assertEqual(Store(self.root).inspect()['consistency_errors'], [])

    def test_edited_file_blocks_rollback_before_any_deletion(self):
        receipt = self.install()
        (self.root / 'BOOTSTRAP.md').write_text('user edit')
        before = inventory(self.root)
        with self.assertRaisesRegex(ValueError, 'edited'): rollback(self.root, receipt['transaction_id'])
        self.assertEqual(inventory(self.root), before)

    def test_state_progress_is_not_rewound_by_rollback(self):
        receipt = self.install()
        path = self.root / '.ai-org/state.json'; state = json.loads(path.read_text())
        state['revision'] += 1; atomic_json(path, state)
        with self.assertRaisesRegex(ValueError, 'edited'): rollback(self.root, receipt['transaction_id'])
        self.assertEqual(json.loads(path.read_text())['revision'], 1)

    def test_old_receipt_cannot_delete_new_installation(self):
        old = self.install()
        self.install(self.plan('upgrade', version='next', guide_bytes=b'new'))
        before = inventory(self.root)
        with self.assertRaisesRegex(ValueError, 'newer'): rollback(self.root, old['transaction_id'])
        self.assertEqual(inventory(self.root), before)

    def test_fault_after_unrecorded_write_preserves_unknown_and_blocks_store(self):
        p = self.plan()
        def crash(point):
            if point == 'file_written': raise RuntimeError('crash')
        with self.assertRaises(RuntimeError): apply(self.root, p, p['plan_sha256'], fault=crash)
        before = inventory(self.root)
        with self.assertRaises(ValueError): self.install(p)
        with self.assertRaisesRegex(ValueError, 'Unknown interrupted'): rollback(self.root, p['operation_id'])
        with self.assertRaisesRegex(ValueError, 'outcome unknown'): Store(self.root).inspect()
        self.assertEqual(inventory(self.root), before)

    def test_committed_receipt_can_reconcile_lost_final_response(self):
        p = self.plan()
        def crash(point):
            if point == 'receipt_committed': raise RuntimeError('crash')
        with self.assertRaises(RuntimeError): apply(self.root, p, p['plan_sha256'], fault=crash)
        with self.assertRaises(ValueError): Store(self.root).inspect()
        self.assertTrue(self.install(p)['replayed'])
        self.assertEqual(Store(self.root).inspect()['consistency_errors'], [])

    def test_unknown_execution_blocks_upgrade(self):
        self.install()
        path = self.root / '.ai-org/state.json'; state = json.loads(path.read_text())
        state['workspaces']['synthetic'] = dict(state='unknown')
        atomic_json(path, state)
        with self.assertRaisesRegex(ValueError, 'unknown execution|invalid local state'): self.plan('upgrade')

    def test_authority_reference_blocks_asset_removal(self):
        self.install()
        receipt = self.install(self.plan('upgrade', version='next', guide_bytes=b'new'))
        path = self.root / '.ai-org/state.json'; state = json.loads(path.read_text())
        state['snapshot']['work_packages'][0]['spec_refs'][0]['path'] = receipt['guide']
        atomic_json(path, state)
        with self.assertRaisesRegex(ValueError, 'still references'): rollback(self.root, receipt['transaction_id'])

    def test_plan_cannot_select_arbitrary_files(self):
        p = self.plan()
        p['payloads']['.git/config'] = p['payloads']['BOOTSTRAP.md']
        p['plan_sha256'] = fingerprint({k:v for k,v in p.items() if k != 'plan_sha256'})
        with self.assertRaisesRegex(ValueError, 'paths'): self.install(p)

    def test_rollback_lost_response_can_reconcile(self):
        receipt = self.install()
        def crash(point):
            if point == 'rollback_recorded': raise RuntimeError('crash')
        with self.assertRaises(RuntimeError): rollback(self.root, receipt['transaction_id'], fault=crash)
        result = rollback(self.root, receipt['transaction_id'])
        self.assertEqual(result['state'], 'rolled_back')
        self.assertEqual(json.loads((self.root / '.ai-org/install-journal.json').read_text())['state'], 'rolled_back')

    def test_reinstall_after_rollback_preserves_newer_ownership(self):
        old = self.install(); rollback(self.root, old['transaction_id'])
        new = self.install(self.plan('import'))
        before = inventory(self.root)
        rollback(self.root, old['transaction_id'])
        self.assertEqual(inventory(self.root), before)
        self.assertEqual(Store(self.root).inspect()['consistency_errors'], [])

    def crash_between_journal_and_receipt(self):
        (self.root / 'user.txt').write_text('preserved user work')
        p = self.plan('import')
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / 'plan.json'; path.write_text(json.dumps(p))
            code = '''import os,sys
from framework.local import bootstrap as b
from framework.core.protocol import load_json
original=b.atomic_json
def crash(path,value):
 original(path,value)
 if path.name == 'install-journal.json' and value['state'] == 'preparing': os._exit(23)
b.atomic_json=crash
p=load_json(sys.argv[2]); b.apply(sys.argv[1],p,p['plan_sha256'])
'''
            result = subprocess.run([sys.executable, '-B', '-S', '-c', code, str(self.root), str(path)], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertFalse((self.root / '.ai-org/installations' / (p['operation_id'] + '.json')).exists())
        return p

    def rollback_cli(self, p):
        cli = Path(__file__).resolve().parents[2] / 'scripts/v4_project.py'
        return subprocess.run([sys.executable, '-B', '-S', str(cli), 'rollback', '--root', str(self.root),
            '--operation-id', p['operation_id']], capture_output=True, timeout=30)

    def test_journal_only_crash_recovers_via_new_process_cli(self):
        p = self.crash_between_journal_and_receipt()
        result = self.rollback_cli(p)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['state'], 'rolled_back')
        self.assertEqual((self.root / 'user.txt').read_text(), 'preserved user work')
        self.install(self.plan('import'))
        self.assertEqual(Store(self.root).inspect()['consistency_errors'], [])

    def test_journal_only_recovery_preserves_unknown_file(self):
        p = self.crash_between_journal_and_receipt()
        (self.root / 'BOOTSTRAP.md').write_text('unknown writer result')
        before = inventory(self.root)
        result = self.rollback_cli(p)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(inventory(self.root), before)


if __name__ == '__main__':
    unittest.main()
