"""User-facing CLI paths, executed from the target without importing product APIs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def fingerprints(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*') if path.is_file()}


class ProjectCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.target = self.base / 'project'; self.target.mkdir()

    def command(self, script, *args, expected=0):
        process = subprocess.run([sys.executable, '-B', '-S', str(ROOT / 'scripts' / script),
                                  *args, '--root', str(self.target)],
                                 cwd=self.target, capture_output=True, timeout=30)
        self.assertEqual(process.returncode, expected, process.stderr.decode())
        return json.loads(process.stdout if process.returncode == 0 else process.stderr)

    def plan(self, mode):
        proposed = self.command('v4_project.py', 'plan-' + mode,
                                '--owner', 'cli-owner', '--project-id', 'cli-project')
        path = self.base / 'reviewed-plan.json'
        path.write_text(json.dumps(proposed))
        return proposed, path

    def apply(self, proposed, path, expected=0):
        return self.command('v4_project.py', 'apply', '--plan', str(path),
                            '--plan-sha256', proposed['plan_sha256'], expected=expected)

    def test_empty_target_can_use_reviewed_cli_from_target_directory(self):
        proposed, path = self.plan('init')
        self.assertEqual(list(self.target.iterdir()), [])
        receipt = self.apply(proposed, path)
        self.assertFalse((self.target / 'scripts').exists())
        result = self.command('v4_local.py', 'inspect')
        self.assertEqual(result['consistency_errors'], [])
        self.assertEqual(result['state']['snapshot']['work_packages'][0]['state'], 'planned')
        self.assertEqual(result['state']['snapshot']['authorizations'], [])
        before = fingerprints(self.target)
        self.assertTrue(self.apply(proposed, path)['replayed'])
        self.assertEqual(fingerprints(self.target), before)
        self.command('v4_project.py', 'rollback', '--operation-id', receipt['transaction_id'])
        self.assertFalse((self.target / '.ai-org/state.json').exists())

    def test_stale_public_plan_preserves_work_then_imports_after_replanning(self):
        proposed, path = self.plan('init')
        original = {'app.txt': 'existing work', 'AGENTS.md': 'existing rules', 'CLAUDE.md': 'existing Claude rules'}
        for name, text in original.items(): (self.target / name).write_text(text)
        error = self.apply(proposed, path, expected=2)
        self.assertIn('stale plan', error['error'])
        self.assertFalse((self.target / '.ai-org/state.json').exists())
        proposed, path = self.plan('import')
        self.apply(proposed, path)
        self.assertEqual(self.command('v4_local.py', 'inspect')['consistency_errors'], [])
        for name, text in original.items(): self.assertEqual((self.target / name).read_text(), text)


if __name__ == '__main__':
    unittest.main()
