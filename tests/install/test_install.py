import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((ROOT / 'manifests/v3-tools.json').read_text())


def tree(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}


class Installation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / 'target'
        self.target.mkdir()

    def run_installer(self, *args, root=ROOT, expected=0):
        p = subprocess.run([sys.executable, '-B', str(root / 'scripts/install_claude_tools.py'),
                            '--target', str(self.target), *args], capture_output=True, text=True)
        self.assertEqual(p.returncode, expected, p.stdout + p.stderr)
        return json.loads(p.stdout or p.stderr)

    def fixture(self):
        root = Path(self.temp.name) / 'source'
        files = {'scripts/install_claude_tools.py', 'manifests/v3-tools.json'}
        files.update(r['source'] for r in MANIFEST['tools'] + MANIFEST['resources'])
        files.update(r['path'] for r in MANIFEST['preserved_copies'])
        for file in files:
            dest = root / file
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / file, dest)
        return root

    def test_empty_install_copies_exact_declared_assets(self):
        result = self.run_installer()
        rows = MANIFEST['tools'] + MANIFEST['resources']
        self.assertEqual(result['created'], len(rows))
        for row in rows:
            self.assertEqual(hashlib.sha256((self.target / row['target']).read_bytes()).hexdigest(), row['sha256'])
        self.assertEqual(len(MANIFEST['tools']), 52)
        self.assertFalse((self.target / '.claude/settings.json').exists())
        self.assertFalse((self.target / '_backup').exists())

    def test_dry_run_and_repeat_are_non_destructive(self):
        self.run_installer('--dry-run')
        self.assertEqual(list(self.target.iterdir()), [])
        self.run_installer()
        before = tree(self.target)
        self.assertEqual(self.run_installer()['state'], 'unchanged')
        self.assertEqual(tree(self.target), before)

    def test_conflict_aborts_before_any_write(self):
        p = self.target / '.claude/commands/ai-pm.md'
        p.parent.mkdir(parents=True)
        p.write_text('custom content')
        before = tree(self.target)
        self.run_installer(expected=2)
        self.assertEqual(tree(self.target), before)
        self.assertFalse((self.target / '.ai-coding-template').exists())

    def test_existing_git_dirty_and_untracked_preserved(self):
        for name in ['.git/config', 'app.txt', 'untracked.txt']:
            p = self.target / name
            p.parent.mkdir(exist_ok=True)
            p.write_text('existing work')
        before = tree(self.target)
        self.run_installer()
        after = tree(self.target)
        self.assertTrue(all(after[k] == v for k, v in before.items()))

    def test_rollback_preserves_preexisting_files(self):
        (self.target / 'custom.txt').write_text('preserve')
        transaction = self.run_installer()['transaction_id']
        self.run_installer('--rollback', transaction)
        self.assertEqual((self.target / 'custom.txt').read_text(), 'preserve')
        self.assertFalse((self.target / '.claude').exists())
        self.assertFalse((self.target / 'CC_COLLABORATION').exists())
        self.run_installer('--rollback', transaction)  # idempotent receipt

    def test_rollback_refuses_edited_file_without_partial_deletion(self):
        transaction = self.run_installer()['transaction_id']
        (self.target / '.claude/commands/ai-pm.md').write_text('new user edit')
        before = tree(self.target)
        self.run_installer('--rollback', transaction, expected=2)
        self.assertEqual(tree(self.target), before)

    def test_old_rollback_cannot_delete_a_later_install(self):
        first = self.run_installer()['transaction_id']
        self.run_installer('--rollback', first)
        self.run_installer()
        before = tree(self.target)
        self.run_installer('--rollback', first)
        self.assertEqual(tree(self.target), before)

    def test_committed_old_receipt_cannot_delete_later_repair(self):
        first = self.run_installer()['transaction_id']
        victim = self.target / '.claude/commands/ai-pm.md'
        original = victim.read_bytes()
        victim.unlink()  # A remains committed; B recreates the missing same-content file.
        second = self.run_installer()['transaction_id']
        self.assertNotEqual(first, second)
        self.assertEqual(victim.read_bytes(), original)
        before = tree(self.target)
        result = self.run_installer('--rollback', first, expected=2)
        self.assertIn('ownership', result['error'])
        self.assertEqual(tree(self.target), before)  # No partial removal of A or B.
        self.run_installer('--rollback', second)
        self.assertFalse(victim.exists())
        self.run_installer('--rollback', first)
        self.run_installer('--rollback', first)
        self.assertFalse((self.target / '.claude').exists())

    def test_legacy_receipt_cannot_delete_new_repair_and_ambiguous_history_stops(self):
        first = self.run_installer()['transaction_id']
        directory = self.target / '.ai-coding-template/transactions'
        def legacy(transaction):
            path = directory / (transaction + '.json')
            receipt = json.loads(path.read_text())
            receipt['version'] = 1
            receipt.pop('predecessors', None)
            path.write_text(json.dumps(receipt))
        legacy(first)
        victim = self.target / '.claude/commands/ai-pm.md'
        victim.unlink()
        second = self.run_installer()['transaction_id']
        before = tree(self.target)
        self.run_installer('--rollback', first, expected=2)
        self.assertEqual(tree(self.target), before)
        legacy(second)  # Two old receipts have no ordering proof: neither may guess.
        before = tree(self.target)
        self.run_installer('--rollback', second, expected=2)
        self.assertEqual(tree(self.target), before)

    def test_unknown_later_write_blocks_old_receipt(self):
        first = self.run_installer()['transaction_id']
        victim = self.target / '.claude/commands/ai-pm.md'
        victim.unlink()
        second = self.run_installer()['transaction_id']
        path = self.target / ('.ai-coding-template/transactions/' + second + '.json')
        receipt = json.loads(path.read_text())
        receipt.update(state='needs_recovery', created=[])
        path.write_text(json.dumps(receipt))  # B wrote the file; its result is unknown.
        before = tree(self.target)
        self.run_installer('--rollback', first, expected=2)
        self.assertEqual(tree(self.target), before)

    def test_single_legacy_receipt_can_still_rollback(self):
        first = self.run_installer()['transaction_id']
        path = self.target / ('.ai-coding-template/transactions/' + first + '.json')
        receipt = json.loads(path.read_text())
        receipt['version'] = 1
        receipt.pop('predecessors', None)
        path.write_text(json.dumps(receipt))
        self.run_installer('--rollback', first)
        self.run_installer('--rollback', first)
        self.assertFalse((self.target / '.claude').exists())

    def test_unknown_interrupted_write_preserved(self):
        transaction = self.run_installer()['transaction_id']
        path = self.target / ('.ai-coding-template/transactions/' + transaction + '.json')
        receipt = json.loads(path.read_text())
        receipt['state'] = 'needs_recovery'
        receipt['created'].pop()  # Crash after write, before its receipt was persisted.
        path.write_text(json.dumps(receipt))
        before = tree(self.target)
        self.run_installer('--rollback', transaction, expected=2)
        self.assertEqual(tree(self.target), before)

    def test_symlink_destination_refused(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (self.target / '.claude').symlink_to(outside)
        self.run_installer(expected=2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_non_directory_ancestor_refused(self):
        (self.target / '.claude').write_text('preserve')
        self.run_installer(expected=2)
        self.assertEqual(list(self.target.iterdir()), [self.target / '.claude'])

    def test_missing_or_changed_source_fails_list_and_install(self):
        source = self.fixture()
        p = source / MANIFEST['tools'][0]['source']
        p.write_text('tampered')
        self.run_installer('--list', root=source, expected=2)
        p.unlink()
        self.run_installer(root=source, expected=2)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_symlink_source_refused_even_when_content_matches(self):
        source = self.fixture()
        path = source / MANIFEST['tools'][0]['source']
        content = Path(self.temp.name) / 'same-content'
        content.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(content)
        self.run_installer(root=source, expected=2)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_manifest_path_escape_and_duplicate_rejected(self):
        source = self.fixture()
        manifest_path = source / 'manifests/v3-tools.json'
        for target in ['../escape', '/tmp/escape', '.git', '.git/config', '.ai-coding-template', MANIFEST['tools'][1]['target']]:
            manifest = json.loads(json.dumps(MANIFEST))
            manifest['tools'][0]['target'] = target
            manifest_path.write_text(json.dumps(manifest))
            self.run_installer(root=source, expected=2)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_missing_dependency_rejected(self):
        source = self.fixture()
        manifest = json.loads(json.dumps(MANIFEST))
        manifest['tools'][0]['requires'] = ['skills:missing']
        (source / 'manifests/v3-tools.json').write_text(json.dumps(manifest))
        self.run_installer(root=source, expected=2)

    def test_selection_includes_declared_dependencies(self):
        result = self.run_installer('--only', 'commands', '--list')
        self.assertEqual(sum(x.startswith('commands:') for x in result['tools']), 26)
        self.assertIn('skills:gate_checker', result['tools'])
        self.assertFalse(result['native_loading_verified'])
        self.run_installer('--only', 'invalid', expected=2)

    def test_incomplete_transaction_blocks_new_install(self):
        receipts = self.target / '.ai-coding-template/transactions'
        receipts.mkdir(parents=True)
        (receipts / ('0' * 32 + '.json')).write_text(json.dumps({'state': 'needs_recovery'}))
        self.run_installer(expected=2)
        self.assertFalse((self.target / '.claude').exists())

    def test_cooperative_single_instance(self):
        state = self.target / '.ai-coding-template'
        state.mkdir()
        with (state / 'install.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            self.run_installer(expected=2)
        self.assertFalse((self.target / '.claude').exists())

    def test_legacy_shell_entry_point(self):
        p = subprocess.run(['/bin/bash', str(ROOT / 'scripts/init-claude-tools.sh'), '--list'],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(json.loads(p.stdout)['tools']), 52)

    def test_manifest_coverage_and_preserved_legacy_variants(self):
        source_commands = {p.stem for p in (ROOT / 'CC_COLLABORATION/05_tools/slash-commands').glob('*.md') if p.stem != 'README'}
        self.assertEqual(source_commands, {r['id'].split(':')[1] for r in MANIFEST['tools'] if r['kind'] == 'commands'})
        self.assertEqual(len(MANIFEST['preserved_copies']), 5)
        self.assertEqual(sum(r['kind'] == 'skills' and r['source'].startswith('.claude/') for r in MANIFEST['tools']), 15)
        for kind in ('skills', 'subagents'):
            existing = {p.stem for p in (ROOT / '.claude' / kind).glob('*.md') if p.stem != 'README'}
            existing |= {p.stem for p in (ROOT / 'CC_COLLABORATION/05_tools' / kind).glob('*.md') if p.stem != 'README'}
            self.assertEqual(existing, {r['id'].split(':')[1] for r in MANIFEST['tools'] if r['kind'] == kind})
        self.run_installer('--list')  # verifies every source and preserved-copy hash


if __name__ == '__main__':
    unittest.main()
