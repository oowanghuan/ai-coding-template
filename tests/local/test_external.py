"""Synthetic client contracts; actual sandboxed launches have separate evidence."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from framework.local.external import ExternalClient, immutable_json
from framework.local.storage import canonical


class ExternalClientTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.trusted = self.root / 'trusted'; self.trusted.mkdir()
        self.candidate = self.root / 'candidate'; self.candidate.mkdir()
        self.workspace = self.candidate / 'workspace'; self.workspace.mkdir()
        self.requests = self.candidate / 'requests'; self.requests.mkdir()
        self.receipts = self.trusted / 'receipts'; self.receipts.mkdir()
        self.scratch = self.trusted / 'scratch'; self.scratch.mkdir()
        self.config = self.trusted / 'config.json'
        self.data = dict(format='v4-launch-config/1', trusted_root=str(self.trusted), candidate_root=str(self.candidate),
                         request_dir=str(self.requests), receipt_dir=str(self.receipts), scratch_root=str(self.scratch),
                         jobs=[dict(job_id='job-a', operation_id='run-a', workspace=str(self.workspace),
                                    output='result.txt', content_sha256=hashlib.sha256('合成'.encode()).hexdigest(),
                                    max_delay_seconds=2, max_runtime_seconds=5)])
        self.config.write_text(json.dumps(self.data))

    def client(self, **changes):
        args = dict(config_path=self.config, job_id='job-a', operation_id='run-a', workspace=self.workspace,
                    path='result.txt', content='合成', delay_seconds=0, timeout=5)
        args.update(changes)
        return ExternalClient(**args)

    def receipt(self, client, **changes):
        row = dict(format='v4-launch-receipt/1', job_id='job-a', operation_id='run-a',
                   request_sha256=client.request_sha256, config_sha256=client.config_sha256,
                   sequence=1, state='running', pid=12345,
                   exit_code=None, stdout_sha256=None, stderr_sha256=None)
        row.update(changes)
        (self.receipts / 'job-a.json').write_bytes(canonical(row) + b'\n')
        return row

    def test_request_replay_is_immutable_and_unicode_hash_is_utf8(self):
        c = self.client(); c.submit(); p = self.requests / 'job-a.request.json'; before = p.read_bytes()
        c.submit(); self.assertEqual(p.read_bytes(), before)
        self.assertEqual(c.request_sha256, hashlib.sha256(canonical(json.loads(before))).hexdigest())
        with self.assertRaisesRegex(ValueError, 'another intent'):
            immutable_json(p, dict(c.request, content='different'))
        self.assertEqual(p.read_bytes(), before)

    def test_provisioned_identity_scope_content_and_limits_are_enforced(self):
        for change in [dict(job_id='../job'), dict(operation_id='other'), dict(path='elsewhere'),
                       dict(content='other'), dict(workspace=self.root), dict(delay_seconds=3), dict(timeout=6),
                       dict(delay_seconds=0.5), dict(timeout=True)]:
            with self.subTest(change=change), self.assertRaises(ValueError): self.client(**change)
        self.assertEqual(list(self.requests.iterdir()), [])

    def test_absent_receipt_never_means_success(self):
        c = self.client(); c.submit(); self.assertIsNone(c.status())

    def test_receipt_binds_job_operation_and_request(self):
        for key in ('job_id', 'operation_id', 'request_sha256', 'config_sha256'):
            c = self.client(); self.receipt(c, **{key: 'different'})
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'binding mismatch'): c.status()

    def test_receipt_cannot_be_reused_for_another_workspace_capability(self):
        c = self.client(); self.receipt(c)
        another = self.candidate / 'another-workspace'; another.mkdir()
        self.data['jobs'][0]['workspace'] = str(another)
        changed = self.trusted / 'changed-config.json'; changed.write_text(json.dumps(self.data))
        other = self.client(config_path=changed, workspace=another)
        self.assertEqual(other.request_sha256, c.request_sha256)
        self.assertNotEqual(other.config_sha256, c.config_sha256)
        with self.assertRaisesRegex(ValueError, 'binding mismatch'): other.status()

    def test_writable_request_tree_cannot_contain_trusted_storage(self):
        self.data['request_dir'] = str(self.root)
        self.config.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError, 'outside candidate root'): self.client()

    def test_receipt_cannot_regress_or_change_same_sequence(self):
        c = self.client(); self.receipt(c, sequence=2); c.status()
        self.receipt(c, sequence=1)
        with self.assertRaisesRegex(ValueError, 'sequence'): c.status()
        self.receipt(c, sequence=2, pid=54321)
        with self.assertRaisesRegex(ValueError, 'sequence'): c.status()

    def test_pid_is_immutable_across_receipts(self):
        c = self.client(); self.receipt(c); c.status(); self.receipt(c, sequence=2, pid=54321)
        with self.assertRaisesRegex(ValueError, 'process identity'): c.status()

    def test_terminal_needs_real_exit_and_matching_log_bytes(self):
        c = self.client(); p = self.scratch / 'job-a'; p.mkdir()
        (p / 'stdout.log').write_bytes(b'actual output'); (p / 'stderr.log').write_bytes(b'')
        hashes = {name + '_sha256': hashlib.sha256((p / (name + '.log')).read_bytes()).hexdigest()
                  for name in ('stdout', 'stderr')}
        self.receipt(c, state='finished', **hashes)
        with self.assertRaisesRegex(ValueError, 'exit code'): c.status()
        self.receipt(c, state='finished', exit_code=0, **hashes)
        self.assertEqual(c.status()['exit_code'], 0)
        (p / 'stdout.log').write_bytes(b'forged')
        with self.assertRaisesRegex(ValueError, 'fingerprint'): c.status()

    def test_rejected_cannot_assert_a_spawned_process(self):
        c = self.client(); self.receipt(c, state='rejected')
        with self.assertRaisesRegex(ValueError, 'prelaunch'): c.status()
        self.receipt(c, state='rejected', pid=None)
        self.assertEqual(c.status()['state'], 'rejected')

    def test_cancel_is_bound_idempotent_and_does_not_assert_stopped(self):
        c = self.client(); c.submit(); c.cancel(); p = self.requests / 'job-a.cancel.json'; before = p.read_bytes()
        c.cancel(); self.assertEqual(before, p.read_bytes())
        self.assertEqual(json.loads(before)['request_sha256'], c.request_sha256)
        self.assertIsNone(c.status())

    def test_receipt_symlink_and_hardlink_are_refused(self):
        c = self.client(); target = self.root / 'fake.json'; target.write_text('{}')
        receipt = self.receipts / 'job-a.json'; receipt.symlink_to(target)
        with self.assertRaises(ValueError): c.status()
        receipt.unlink(); os.link(target, receipt)
        with self.assertRaisesRegex(ValueError, 'single-link'): c.status()

    def test_request_and_lock_aliases_do_not_overwrite_other_files(self):
        c = self.client(); target = self.root / 'kept'; target.write_text('keep')
        request = self.requests / 'job-a.request.json'; request.symlink_to(target)
        with self.assertRaises(ValueError): c.submit()
        request.unlink(); lock = self.requests / 'job-a.request.json.lock'; lock.unlink(); os.link(target, lock)
        with self.assertRaisesRegex(ValueError, 'lock'): c.submit()
        self.assertEqual(target.read_text(), 'keep')


if __name__ == '__main__': unittest.main(verbosity=2)
