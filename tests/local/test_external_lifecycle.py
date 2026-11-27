"""Real Store lifecycle with explicitly synthetic driver receipts, never a host driver.

These tests verify negative controller behavior. A fixture PID/log/receipt is not
proof of an actual Worker launch, successful execution, overlap or acceptance.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from framework.local import external
from framework.local.runner import git, prepare, run
from framework.local.storage import canonical
from framework.local.store import Store

ROOT = Path(__file__).resolve().parents[2]
ACTOR = 'principal-implementer'
OWNER = 'principal-owner'


class FastClock:
    """Virtual receipt-wait time only; no product state or lease clocks replaced."""
    def __init__(self): self.value = 0
    def monotonic(self):
        self.value += 1
        return self.value
    def sleep(self, seconds): pass


class ExternalLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.candidate = self.base / 'candidate'; self.candidate.mkdir()
        self.root = self.candidate / 'project'; self.root.mkdir()
        git(self.root, 'init', '-q')
        (self.root / 'src').mkdir(); (self.root / 'src/base.txt').write_text('baseline')
        git(self.root, 'add', 'src')
        git(self.root, '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
            'commit', '-qm', 'synthetic baseline')
        sha = git(self.root, 'rev-parse', 'HEAD').decode().strip()
        snapshot = json.loads((ROOT / 'examples/protocol/in-progress.json').read_text())
        snapshot['assignments'] = []; snapshot['checkpoints'] = []
        snapshot['workers'][0]['state'] = 'available'
        snapshot['work_packages'][0].update(state='planned', assignment_ref=None, checkpoint_ref=None, baseline_sha=sha)
        self.store = Store(self.root); self.store.initialize(snapshot, OWNER)
        self.credentials = self.change('claim', dict(wp_id='WP-DEMO', worker_id='worker-a',
            session_id='session-a', lease_seconds=300))['operation']['result']
        prepare(self.root, self.credentials, ACTOR, self.state()['revision'], 'prepare')
        self.worktree = self.root / self.workspace()['path']
        self.trusted = self.base / 'synthetic-trusted'; self.trusted.mkdir()
        self.requests = self.candidate / 'requests'; self.requests.mkdir()
        self.receipts = self.trusted / 'receipts'; self.receipts.mkdir()
        self.scratch = self.trusted / 'scratch'; self.scratch.mkdir()
        self.config = self.trusted / 'config.json'
        # Client-side config fixture only: no executable, driver or launch capability is invoked.
        self.config_data = dict(format='v4-launch-config/1', trusted_root=str(self.trusted),
            candidate_root=str(self.candidate),
            request_dir=str(self.requests), receipt_dir=str(self.receipts), scratch_root=str(self.scratch),
            jobs=[dict(job_id='fixture-job', operation_id='fixture-run', workspace=str(self.worktree),
                output='src/out.txt', content_sha256=hashlib.sha256(b'fixture output').hexdigest(),
                max_delay_seconds=0, max_runtime_seconds=1)])
        self.config.write_text(json.dumps(self.config_data))

    def state(self): return self.store.inspect()['state']
    def workspace(self): return self.state()['workspaces'][self.credentials['workspace_id']]
    def change(self, action, payload, actor=ACTOR):
        revision = self.state()['revision']
        return self.store.change(action, payload, actor, revision, action + '-' + str(revision))
    def client(self):
        return external.ExternalClient(self.config, 'fixture-job', 'fixture-run', self.worktree,
                                       'src/out.txt', 'fixture output', 0, 1)
    def invoke(self, **changes):
        args = dict(root=self.root, credentials=self.credentials, actor=ACTOR, path='src/out.txt',
            content='fixture output', operation_id='fixture-run', expected_revision=self.state()['revision'],
            config_path=self.config, job_id='fixture-job', timeout=1)
        args.update(changes)
        with patch.object(external, 'time', FastClock()):
            return external.run_external(**args)
    def synthetic_receipt(self, state, exit_code=None, pid=None, corrupt_logs=False):
        # No real process has this fixture identity. Byte-backed logs only exercise validation.
        client = self.client()
        row = dict(format='v4-launch-receipt/1', job_id='fixture-job', operation_id='fixture-run',
            request_sha256=client.request_sha256, config_sha256=client.config_sha256,
            sequence=1, state=state, pid=pid,
            exit_code=exit_code, stdout_sha256=None, stderr_sha256=None)
        if state in ('finished', 'stopped'):
            folder = self.scratch / 'fixture-job'; folder.mkdir(exist_ok=True)
            for name, data in [('stdout', b'explicit synthetic receipt fixture'), ('stderr', b'synthetic failure')]:
                (folder / (name + '.log')).write_bytes(data)
                row[name + '_sha256'] = hashlib.sha256(data).hexdigest()
            if corrupt_logs: row['stdout_sha256'] = '0' * 64
        (self.receipts / 'fixture-job.json').write_bytes(canonical(row) + b'\n')
        return row
    def assert_unresolved(self):
        self.assertIn(self.workspace()['state'], ('launching', 'running', 'unknown'))
        self.assertNotIn(self.workspace()['state'], ('finished', 'stopped'))
        self.assertEqual(self.state()['deliveries'], {})
        self.assertTrue((self.requests / 'fixture-job.cancel.json').exists())
        with self.assertRaises(ValueError): self.change('release', self.credentials)
    def cli(self, extra=()):
        payload = self.base / 'input.json'
        payload.write_text(json.dumps(dict(credentials=self.credentials, path='src/out.txt',
                                          content='fixture output', timeout=1)))
        return [sys.executable, '-B', '-S', str(ROOT / 'scripts/v4_local.py'), 'run-external',
            '--root', str(self.root), '--actor', ACTOR, '--input', str(payload),
            '--expected-revision', str(self.state()['revision']), '--operation-id', 'fixture-run', *extra]

    def test_missing_driver_receipt_stays_unknown_and_blocks_reclaim(self):
        with self.assertRaisesRegex(ValueError, 'receipt timeout'): self.invoke()
        self.assert_unresolved()
        self.change('revoke', dict(assignment_id=self.credentials['assignment_id'], reason='reconcile'), OWNER)
        with self.assertRaisesRegex(ValueError, 'unknown workspace'):
            self.change('claim', dict(wp_id='WP-DEMO', worker_id='worker-a', session_id='session-a', lease_seconds=300))

    def test_explicit_unknown_receipt_is_not_stop_confirmation(self):
        def publish(point):
            if point == 'request_published': self.synthetic_receipt('unknown')
        with self.assertRaisesRegex(ValueError, 'outcome unknown'): self.invoke(fault=publish)
        self.assert_unresolved()
        request = json.loads((self.requests / 'fixture-job.request.json').read_text())
        cancel = json.loads((self.requests / 'fixture-job.cancel.json').read_text())
        self.assertEqual(cancel['request_sha256'], hashlib.sha256(canonical(request)).hexdigest())

    def test_revocation_requests_cancel_without_inventing_stop(self):
        def revoke(point):
            if point == 'request_published':
                self.synthetic_receipt('running', pid=12345)
                self.change('revoke', dict(assignment_id=self.credentials['assignment_id'], reason='owner stop'), OWNER)
        with self.assertRaisesRegex(ValueError, 'fenced'): self.invoke(fault=revoke)
        self.assert_unresolved()
        self.assertEqual(self.state()['snapshot']['assignments'][0]['state'], 'revoked')
        self.assertEqual(json.loads((self.receipts / 'fixture-job.json').read_text())['state'], 'running')

    def test_invalid_terminal_logs_do_not_release_uncertainty(self):
        self.synthetic_receipt('finished', exit_code=9, pid=12345, corrupt_logs=True)
        with self.assertRaisesRegex(ValueError, 'log fingerprint'): self.invoke()
        self.assert_unresolved()

    def test_terminal_failure_cli_replay_is_nonzero_and_does_not_submit_again(self):
        self.synthetic_receipt('finished', exit_code=23, pid=12345)
        args = self.cli(('--launcher-config', str(self.config), '--launcher-job-id', 'fixture-job'))
        first = subprocess.run(args, capture_output=True, timeout=30)
        self.assertNotEqual(first.returncode, 0, first.stdout)
        self.assertEqual(self.workspace()['state'], 'finished')
        self.assertEqual(self.workspace()['run']['exit_code'], 23)
        before = self.store.path.read_bytes()
        second = subprocess.run(args, capture_output=True, timeout=30)
        self.assertNotEqual(second.returncode, 0, second.stdout)
        self.assertEqual(self.store.path.read_bytes(), before)
        with patch.object(external.ExternalClient, 'submit', side_effect=AssertionError('must not republish')) as submit:
            with self.assertRaisesRegex(ValueError, 'failed or unresolved'): self.invoke()
            submit.assert_not_called()
        self.assertEqual(self.state()['deliveries'], {})

    def test_same_operation_cannot_switch_backend_job_or_config(self):
        self.synthetic_receipt('finished', exit_code=23, pid=12345)
        with self.assertRaisesRegex(ValueError, 'failed/stopped'): self.invoke()
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'different intent'):
            run(self.root, self.credentials, ACTOR, 'src/out.txt', 'fixture output',
                'fixture-run', self.state()['revision'], timeout=1)
        alternate = self.trusted / 'alternate.json'
        alternate.write_text(json.dumps(self.config_data, indent=2))  # Same capability, different pinned config bytes.
        with self.assertRaisesRegex(ValueError, 'different intent'): self.invoke(config_path=alternate)
        other = copy.deepcopy(self.config_data); other['jobs'][0]['job_id'] = 'another-job'
        alternate.write_text(json.dumps(other))
        with self.assertRaisesRegex(ValueError, 'different intent'):
            self.invoke(config_path=alternate, job_id='another-job')
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertFalse((self.requests / 'another-job.request.json').exists())

    def test_cli_requires_both_explicit_launcher_arguments(self):
        before = self.store.path.read_bytes()
        for flags in [(), ('--launcher-config', str(self.config)), ('--launcher-job-id', 'fixture-job')]:
            with self.subTest(flags=flags):
                process = subprocess.run(self.cli(flags), capture_output=True, timeout=30)
                self.assertNotEqual(process.returncode, 0, process.stdout)
                self.assertIn('explicit --launcher-config and --launcher-job-id required', json.loads(process.stderr)['error'])
                self.assertEqual(self.store.path.read_bytes(), before)
                self.assertEqual(list(self.requests.iterdir()), [])

    def test_validated_prelaunch_rejection_is_not_success_or_delivery(self):
        self.synthetic_receipt('rejected')
        with self.assertRaisesRegex(ValueError, 'failed/stopped'): self.invoke()
        self.assertEqual(self.workspace()['state'], 'stopped')
        self.assertIsNone(self.workspace()['run']['pid'])
        self.assertIsNone(self.workspace()['run']['exit_code'])
        self.assertEqual(self.state()['deliveries'], {})


if __name__ == '__main__': unittest.main(verbosity=2)
