import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from framework.quality import collector as c


class CollectorContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve(); self.t = self.base / 'trusted'; self.t.mkdir()
        self.s = self.base / 'scratch'; self.s.mkdir(); self.source = self.t / 'subject'; self.source.mkdir()
        code = b'print("ok")\n'; (self.source / 'main.py').write_bytes(code)
        manifest = {'main.py': {'mode': '100644', 'sha256': c.digest(code)}}
        tree = c.tree_hash({'main.py': ('100644', c.git_object('blob', code))})
        commit = 'tree ' + tree + '\nauthor Synthetic <test@example.invalid> 1 +0000\ncommitter Synthetic <test@example.invalid> 1 +0000\n\nfixture\n'
        self.plan = dict(format='quality-plan/1', run_id='run-a', wp_id='WP-201', wp_revision=1,
            kind='code', trusted_root=str(self.t), scratch_root=str(self.s), subject_root=str(self.source),
            entrypoint='main.py', subject=dict(commit=c.git_object('commit', commit.encode()), tree=tree,
            manifest_sha256=c.digest(c.canonical(manifest))), commit_object=commit, manifest=manifest,
            collector_sha256='1' * 64, environment=dict(platform='darwin', python='/usr/bin/python3',
            python_version='3.9.6', sandbox='macos-seatbelt'), tests=[dict(id='basic', required=True,
            input='', expected_exit=0, expected_stdout_sha256=c.digest(b'ok\n'), timeout_seconds=2, skip_reason=None)])

    def test_snapshot_is_bound_to_real_git_object_encoding(self):
        self.assertEqual(c.validate(self.plan), self.plan)
        self.assertEqual(c.git_object('tree', b''), '4b825dc642cb6eb9a060e54bf8d69288fbee4904')

    def test_source_changes_and_extra_files_are_rejected(self):
        (self.source / 'main.py').write_text('changed')
        with self.assertRaises(ValueError): c.validate(self.plan)
        (self.source / 'main.py').write_text('print("ok")\n'); (self.source / 'extra').write_text('extra')
        with self.assertRaises(ValueError): c.validate(self.plan)

    def test_commit_and_tree_cannot_be_self_reported(self):
        for key in ('commit', 'tree', 'manifest_sha256'):
            p = copy.deepcopy(self.plan); p['subject'][key] = '0' * len(p['subject'][key])
            with self.assertRaises(ValueError): c.validate(p)

    def test_mode_change_is_not_silently_accepted(self):
        (self.source / 'main.py').chmod(0o755)
        with self.assertRaises(ValueError): c.validate(self.plan)

    def test_expected_exit_bool_signal_and_large_value_rejected(self):
        for value in (True, -15, 256, '0'):
            p = copy.deepcopy(self.plan); p['tests'][0]['expected_exit'] = value
            with self.assertRaises(ValueError): c.validate(p)

    def test_duplicate_cases_and_timeout_budget_rejected(self):
        p = copy.deepcopy(self.plan); p['tests'] *= 2
        with self.assertRaises(ValueError): c.validate(p)
        p['tests'] = [dict(self.plan['tests'][0], id='case-' + str(i), timeout_seconds=30) for i in range(5)]
        with self.assertRaises(ValueError): c.validate(p)

    def test_trust_and_candidate_roots_cannot_overlap(self):
        for path in (self.t, self.source, self.base):
            p = copy.deepcopy(self.plan); p['scratch_root'] = str(path)
            with self.assertRaises(ValueError): c.validate(p)

    def test_source_symlink_and_hardlink_are_rejected(self):
        target = self.source / 'main.py'; data = target.read_bytes(); target.unlink()
        other = self.base / 'other'; other.write_bytes(data); target.symlink_to(other)
        with self.assertRaises(ValueError): c.validate(self.plan)
        target.unlink(); os.link(other, target)
        with self.assertRaises(ValueError): c.validate(self.plan)

    def test_ancestor_swap_is_rejected(self):
        root = self.base / 'victim'; root.mkdir(); file = root / 'data'; file.write_bytes(b'original')
        outside = self.base / 'outside'; outside.mkdir(); (outside / 'data').write_bytes(b'outside')
        original = os.open; swapped = [False]
        def swap(path, flags, *args, **kwargs):
            if not swapped[0]:
                swapped[0] = True; root.rename(self.base / 'saved'); root.symlink_to(outside)
            return original(path, flags, *args, **kwargs)
        with patch.object(c.os, 'open', swap):
            with self.assertRaises((ValueError, OSError)): c.regular(file)

    def test_strict_json_rejects_duplicates_and_nan(self):
        for data in ('{"a":1,"a":2}', '{"a":NaN}'):
            with self.assertRaises(ValueError): c.strict_json(data)

    def test_intent_is_exclusive_and_preserved(self):
        path = self.t / 'intent.json'; c.save_new(path, {'state': 'unknown'})
        before = path.read_bytes()
        with self.assertRaises(FileExistsError): c.save_new(path, {'state': 'retry'})
        self.assertEqual(path.read_bytes(), before)

    def test_skipping_does_not_spawn_or_claim_exit(self):
        with patch.object(c.subprocess, 'Popen') as spawn:
            result = c.run_case(self.plan, dict(self.plan['tests'][0], skip_reason='optional example'))
        spawn.assert_not_called(); self.assertEqual(result['status'], 'skipped')
        self.assertIsNone(result['exit_code']); self.assertIsNone(result['pid']); self.assertIsNone(result['stdout'])

    def test_policy_does_not_grant_fork_or_trusted_write(self):
        policy = c.policy(self.source, self.s / 'basic', self.s)
        self.assertIn('(deny process-fork)', policy); self.assertNotIn('(allow process*)', policy)
        self.assertIn('(deny process-info* (target others))', policy)
        self.assertNotIn('(allow sysctl-read)', policy)
        self.assertNotIn('network', policy)
        write = next(line for line in policy.splitlines() if line.startswith('(allow file-write'))
        self.assertNotIn(str(self.t), write)


if __name__ == '__main__': unittest.main()
