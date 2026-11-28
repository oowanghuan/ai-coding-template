"""Non-author prepared-workspace recovery integration tests.

Real Git worktrees and local authority run only inside the outer A01 sandbox.
Worker identity/availability are synthetic observations. Deliberate authority
corruption is confined to test-owned fixtures, never a supported recovery step.
No model, provider, external driver, or purported process-stop receipt is used.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import threading
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_lifecycle as shared
from framework.local import handoff
from framework.local.runner import git, prepare
from framework.local.storage import atomic_json
from framework.local.store import find
from framework.local.store import Store
from framework.local.external import ExternalClient
from framework.local.launch_driver import Driver, validate_config


class UnstartedHandoffTests(unittest.TestCase):
    initial = shared.LifecycleTests.initial
    state = shared.LifecycleTests.state
    change = shared.LifecycleTests.change
    result = shared.LifecycleTests.result
    enable = shared.LifecycleTests.enable
    event = shared.LifecycleTests.event
    claim = shared.LifecycleTests.claim

    def setUp(self):
        shared.LifecycleTests.setUp(self)
        for module in ('framework.local.store', 'framework.local.runner', 'framework.local.handoff'):
            clock = patch(module + '.now', return_value=shared.AT)
            clock.start(); self.addCleanup(clock.stop)
        path = self.root / 'src/a'; path.mkdir()
        (path / 'dirty.txt').write_bytes(b'baseline tracked\n')
        (path / 'deleted.txt').write_bytes(b'delete this tracked file\n')
        git(self.root, 'add', 'src/a')
        git(self.root, '-c', 'user.name=Synthetic', '-c', 'user.email=fixture@example.invalid',
            'commit', '-qm', 'unstarted recovery baseline')
        self.sha = git(self.root, 'rev-parse', 'HEAD').decode().strip()
        self.initial(); self.enable()

    def prepared(self, domain='direct-local-only'):
        payload = dict(wp_id='WP-A', worker_id='worker-a', session_id='session-a', lease_seconds=600)
        if domain is not None: payload['execution_domain'] = domain
        self.old = self.result('claim', payload, actor='principal-a')
        prepare(self.root, self.old, 'principal-a', self.state()['revision'], 'prepare-old')
        workspace = self.state()['workspaces'][self.old['workspace_id']]
        self.assertEqual(workspace['state'], 'prepared'); self.assertIsNone(workspace['run'])
        self.old_path = self.root / workspace['path']
        (self.old_path / 'src/a/dirty.txt').write_bytes(b'preserved dirty result\n')
        (self.old_path / 'src/a/dirty.txt').chmod(0o700)
        (self.old_path / 'src/a/deleted.txt').unlink()
        (self.old_path / 'src/a/draft.txt').write_bytes(b'preserved untracked result\n')
        return self.old

    def test_default_domain_cannot_claim_never_launched(self):
        self.prepared(None); self.snapshot()
        self.refused_without_write(self.recover)
        self.assertEqual(self.state()['workspaces'][self.old['workspace_id']]['state'], 'prepared')

    def test_explicit_general_domain_is_rejected_and_unknown_domains_do_not_claim(self):
        for domain in ('external', 'DIRECT-LOCAL-ONLY', True, None, {'name': 'direct-local-only'}):
            with self.subTest(domain=domain):
                self.refused_without_write(lambda: self.result('claim', dict(wp_id='WP-A', worker_id='worker-a',
                    session_id='session-a', lease_seconds=600, execution_domain=domain), actor='principal-a'))
        self.prepared('general'); self.snapshot(); self.refused_without_write(self.recover)

    def snapshot(self):
        return handoff.checkpoint(self.root, self.old, 'principal-a',
            completed=['synthetic local edits'], remaining=['resume actual task'])

    def recover(self, op='recover-old', credentials=None, actor='principal-a', revision=None):
        return handoff.recover_prepared(self.root, credentials or self.old, actor,
            self.state()['revision'] if revision is None else revision, op)

    def refused_without_write(self, call):
        before = self.store.path.read_bytes()
        with self.assertRaises(ValueError): call()
        self.assertEqual(self.store.path.read_bytes(), before)

    def old_files(self):
        return {str(p.relative_to(self.old_path)): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
            'executable': bool(p.stat().st_mode & 0o111)}
            for p in self.old_path.rglob('*') if p.is_file() and '.git' not in p.relative_to(self.old_path).parts}

    def test_real_prepared_handoff_preserves_files_and_delivers_once_at_new_fence(self):
        self.prepared(); checkpoint = self.snapshot(); old_files = self.old_files()
        result = self.recover()
        self.assertFalse(result['replayed'])
        receipt = result['operation']['result']
        self.assertEqual(receipt['execution_observed'], 'never_launched')
        self.assertIs(receipt['process_stop_observed'], False)
        old_state = self.state(); old_workspace = old_state['workspaces'][self.old['workspace_id']]
        self.assertEqual(old_workspace['state'], 'stopped'); self.assertIsNone(old_workspace['run'])
        self.assertEqual(find(old_state['snapshot']['assignments'], self.old['assignment_id'])['state'], 'revoked')
        for action, extra in [('start', {}), ('run-begin', {'path': 'src/a/late.txt', 'content_sha256': 'a' * 64}),
                              ('submit', {'path': 'src/a/draft.txt', 'sha256': hashlib.sha256(b'preserved untracked result\n').hexdigest()})]:
            with self.subTest(old_token_action=action):
                self.refused_without_write(lambda: self.result(action, dict(self.old, **extra), actor='principal-a'))
        new = self.claim('c', wp='WP-A'); self.assertGreater(new['token'], self.old['token'])
        self.refused_without_write(lambda: self.claim('b', wp='WP-A'))
        handoff.prepare_handoff(self.root, new, 'principal-c', self.state()['revision'], 'prepare-new')
        target = self.root / self.state()['workspaces'][new['workspace_id']]['path']
        self.assertNotEqual(target, self.old_path)
        self.assertEqual((target / 'src/a/dirty.txt').read_bytes(), b'preserved dirty result\n')
        self.assertTrue((target / 'src/a/dirty.txt').stat().st_mode & 0o111)
        self.assertEqual((target / 'src/a/draft.txt').read_bytes(), b'preserved untracked result\n')
        self.assertFalse((target / 'src/a/deleted.txt').exists())
        payload = dict(new, path='src/a/draft.txt', sha256=hashlib.sha256(b'preserved untracked result\n').hexdigest())
        first = self.change('submit', payload, actor='principal-c', op='submit-recovered')
        before = self.store.path.read_bytes()
        second = self.change('submit', payload, actor='principal-c', op='submit-recovered')
        self.assertTrue(second['replayed']); self.assertEqual(first['operation'], second['operation'])
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertIs(first['operation']['result']['accepted'], False)
        self.refused_without_write(lambda: self.change('submit', payload, actor='principal-c', op='submit-again'))
        self.assertEqual(len(self.state()['deliveries']), 1); self.assertEqual(self.old_files(), old_files)
        replay = self.recover(revision=0)
        self.assertTrue(replay['replayed']); self.assertEqual(replay['operation'], result['operation'])
        self.assertEqual(self.store.path.read_bytes(), before)
        evidence = {'kind': 'synthetic_fixture', 'no_provider_calls': True, 'actual_git_worktrees': True,
            'checkpoint': checkpoint, 'old_credentials': self.old, 'new_credentials': new,
            'recovery': result, 'delivery': first, 'old_files_unchanged': self.old_files() == old_files,
            'original_files': old_files, 'final_state': self.state()}
        if os.environ.get('V4_UNSTARTED_EVIDENCE'):
            output = Path(os.environ['V4_UNSTARTED_EVIDENCE']); output.mkdir(parents=True, exist_ok=True)
            (output / 'prepared-handoff.json').write_text(json.dumps(evidence, indent=2) + '\n')
        print(json.dumps({'unstarted_handoff': {'old_token': self.old['token'], 'new_token': new['token'],
            'execution_observed': receipt['execution_observed'], 'process_stop_observed': False,
            'delivery_count': 1, 'accepted': False, 'old_files_unchanged': True}}), flush=True)

    def test_quota_fenced_prepared_workspace_uses_same_never_launched_proof(self):
        self.prepared(); self.snapshot(); self.event('a', 'quota_limited')
        result = self.recover()
        self.assertEqual(result['operation']['result']['execution_observed'], 'never_launched')
        self.assertGreater(self.claim('c', wp='WP-A')['token'], self.old['token'])

    def test_missing_checkpoint_and_stale_revision_never_release(self):
        self.prepared(); self.refused_without_write(self.recover)
        self.snapshot(); self.refused_without_write(lambda: self.recover(revision=0))

    def test_prior_launch_receipt_cannot_be_erased_by_run_none(self):
        self.prepared(); self.snapshot()
        self.result('run-begin', dict(self.old, path='src/a/provider.txt', content_sha256='a' * 64), actor='principal-a')
        state = self.state()
        self.assertTrue(any(op['action'] == 'run-begin' and op['result']['workspace_id'] == self.old['workspace_id']
                            for op in state['operations'].values()))
        # Deliberately corrupt only our synthetic authority to mimic a lost run marker.
        state['workspaces'][self.old['workspace_id']].update(state='prepared', run=None)
        atomic_json(self.store.path, state)
        self.refused_without_write(self.recover)

    def test_launching_unknown_without_pid_is_not_never_launched(self):
        self.prepared(); self.snapshot()
        self.result('run-begin', dict(self.old, path='src/a/provider.txt', content_sha256='a' * 64), actor='principal-a')
        self.assertNotIn('pid', self.state()['workspaces'][self.old['workspace_id']]['run'])
        self.refused_without_write(self.recover)
        self.event('a', 'quota_limited')
        self.assertEqual(self.state()['workspaces'][self.old['workspace_id']]['state'], 'unknown')
        self.refused_without_write(self.recover)

    def test_direct_domain_actual_owned_process_requires_real_stop_path(self):
        self.prepared(); self.snapshot()
        self.result('run-begin', dict(self.old, path='src/a/provider.txt', content_sha256='a' * 64), actor='principal-a')
        process = subprocess.Popen([sys.executable, '-B', '-S', '-c', 'import time;time.sleep(60)'],
            cwd=self.old_path, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True)
        try:
            self.assertEqual(os.getpgid(process.pid), process.pid)
            self.store.workspace_phase(self.old, 'principal-a', 'launching', 'running',
                run=dict(state='running', pid=process.pid, process_group=process.pid, unknown_operations=[]))
            self.assertIsNone(process.poll())
            self.refused_without_write(self.recover)
            self.event('a', 'quota_limited'); self.refused_without_write(self.recover)
            process.terminate(); actual_exit = process.wait(timeout=5)
            with self.assertRaises(ProcessLookupError): os.killpg(process.pid, 0)
            stopped = handoff.confirm_stopped(self.root, self.old, 'principal-a', process)
            self.assertEqual(stopped['exit_code'], actual_exit)
            self.assertEqual(self.state()['workspaces'][self.old['workspace_id']]['state'], 'stopped')
            print(json.dumps({'direct_domain_actual_process': {'pid': process.pid,
                'run_begin_persisted_before_spawn': True, 'no_writer_recovery_rejected': True,
                'wait_exit': actual_exit, 'process_group_absent': True}}), flush=True)
        finally:
            if process.poll() is None: process.terminate()
            process.wait(timeout=5)
            process.stdout.close(); process.stderr.close()

    def test_legacy_missing_or_ambiguous_start_proof_rejected(self):
        self.prepared(); self.snapshot(); pristine = self.state()
        for kind in ('missing', 'duplicate', 'wrong-assignment', 'wrong-token', 'wrong-epoch', 'bool-token', 'noncommitted'):
            with self.subTest(kind=kind):
                state = copy.deepcopy(pristine)
                starts = [op for op in state['operations'].values()
                          if op['action'] == 'start' and op['result'].get('workspace_id') == self.old['workspace_id']]
                self.assertEqual(len(starts), 1)
                proof = starts[0]['result']
                self.assertEqual(proof['launch_protocol'], 'persist-before-spawn/1')
                if kind == 'missing': proof.pop('launch_protocol')
                elif kind == 'duplicate': state['operations']['ambiguous-start'] = copy.deepcopy(starts[0])
                elif kind == 'wrong-assignment': proof['assignment_id'] = 'assignment-wrong'
                elif kind == 'wrong-token': proof['token'] += 1
                elif kind == 'wrong-epoch': proof['epoch'] += 1
                elif kind == 'bool-token': proof['token'] = True
                else: starts[0]['status'] = 'unknown'
                atomic_json(self.store.path, state) # Controlled inconsistent authority fixture.
                self.refused_without_write(self.recover)
        atomic_json(self.store.path, pristine)

    def test_same_authorization_reference_changed_or_expired_rejected(self):
        self.prepared(); self.snapshot(); pristine = self.state()
        for kind in ('revoked', 'scope', 'expired'):
            with self.subTest(kind=kind):
                state = copy.deepcopy(pristine)
                auth = state['snapshot']['authorizations'][0]
                if kind == 'revoked': auth['state'] = 'revoked'
                elif kind == 'scope': auth['allowed_paths'] = ['src/a/narrow/']
                else: auth['expires_at'] = '2026-11-28T11:59:59Z'
                atomic_json(self.store.path, state) # Same reference, changed synthetic authority contents.
                self.refused_without_write(self.recover)
                self.assertEqual((self.old_path / 'src/a/draft.txt').read_bytes(), b'preserved untracked result\n')
        atomic_json(self.store.path, pristine)

    def test_terminal_unknown_delivery_and_epoch_change_are_not_unstarted(self):
        self.prepared(); self.snapshot(); pristine = self.state()
        for phase in ('creating', 'launching', 'running', 'unknown', 'finished', 'stopped'):
            with self.subTest(phase=phase):
                state = copy.deepcopy(pristine)
                state['workspaces'][self.old['workspace_id']]['state'] = phase
                atomic_json(self.store.path, state)
                self.refused_without_write(self.recover)
        state = copy.deepcopy(pristine)
        state['snapshot']['project']['authority_epoch'] += 1
        atomic_json(self.store.path, state)
        self.refused_without_write(self.recover)
        atomic_json(self.store.path, pristine)
        self.result('submit', dict(self.old, path='src/a/draft.txt',
            sha256=hashlib.sha256(b'preserved untracked result\n').hexdigest()), actor='principal-a')
        self.refused_without_write(self.recover)

    def test_late_head_change_rejected_without_rewriting_checkpoint_or_original(self):
        self.prepared(); self.snapshot()
        git(self.old_path, '-c', 'user.name=Synthetic', '-c', 'user.email=fixture@example.invalid',
            'commit', '--allow-empty', '-qm', 'late HEAD mutation')
        actual_head = git(self.old_path, 'rev-parse', 'HEAD')
        self.refused_without_write(self.recover)
        self.assertEqual(git(self.old_path, 'rev-parse', 'HEAD'), actual_head)

    def test_actual_authority_lock_serializes_recovery_and_launch_in_both_orders(self):
        self.prepared(); self.snapshot(); pristine = self.state()
        original_apply = Store._apply
        for winner in ('recover-prepared', 'run-begin'):
            with self.subTest(winner=winner):
                atomic_json(self.store.path, copy.deepcopy(pristine))
                entered, release, contender_started = threading.Event(), threading.Event(), threading.Event()
                outputs = {}; failures = {}; threads = []
                revision = pristine['revision']
                launch = dict(self.old, path='src/a/provider.txt', content_sha256='a' * 64)
                def held_apply(store, state, action, payload, actor, at):
                    result = original_apply(store, state, action, payload, actor, at)
                    if action == winner:
                        entered.set()
                        if not release.wait(30): raise AssertionError('test lock release timed out')
                    return result
                def operation(action, contender=False):
                    if contender: contender_started.set()
                    try:
                        outputs[action] = Store(self.root).change(action,
                            self.old if action == 'recover-prepared' else launch,
                            'principal-a', revision, 'race-' + action, at=shared.AT)
                    except BaseException as error:
                        failures[action] = error
                loser = 'run-begin' if winner == 'recover-prepared' else 'recover-prepared'
                with patch.object(Store, '_apply', new=held_apply):
                    first = threading.Thread(target=operation, args=(winner,)); threads.append(first); first.start()
                    try:
                        self.assertTrue(entered.wait(30), failures)
                        second = threading.Thread(target=operation, args=(loser, True)); threads.append(second); second.start()
                        self.assertTrue(contender_started.wait(5))
                        self.assertNotIn(loser, outputs)
                    finally:
                        release.set()
                        for thread in threads: thread.join(timeout=10)
                self.assertTrue(all(not thread.is_alive() for thread in threads))
                self.assertEqual(set(outputs), {winner}); self.assertEqual(set(failures), {loser})
                self.assertIsInstance(failures[loser], ValueError)
                self.assertIn('revision conflict', str(failures[loser]))
                current = self.state(); workspace = current['workspaces'][self.old['workspace_id']]
                self.assertEqual(workspace['state'], 'stopped' if winner == 'recover-prepared' else 'launching')
                # Retry with fresh revision must still fail on the winner's semantic effect.
                self.refused_without_write(lambda: self.change(loser,
                    self.old if loser == 'recover-prepared' else launch, actor='principal-a', op='semantic-retry'))
                print(json.dumps({'actual_lock_order': winner, 'loser_rejected': loser,
                    'process_spawned': False}), flush=True)

    def test_start_bound_scope_cannot_be_reset_by_new_checkpoint(self):
        self.prepared()
        state = self.state()
        original_proof = next(op['result'] for op in state['operations'].values()
            if op['action'] == 'start' and op['result'].get('workspace_id') == self.old['workspace_id'])
        wp = find(state['snapshot']['work_packages'], 'WP-A')
        wp['spec_refs'][0]['version'] = 'changed-after-start-before-snapshot'
        wp['revision'] += 1
        atomic_json(self.store.path, state) # Controlled synthetic authoritative contract revision.
        receipt = self.snapshot() # A real new checkpoint consistent with the modified contract.
        current = self.state(); wp = find(current['snapshot']['work_packages'], 'WP-A')
        workspace = current['workspaces'][self.old['workspace_id']]
        manifest = handoff.checked_checkpoint(self.root, current, wp, workspace)
        self.assertEqual(manifest['context']['spec_refs'], wp['spec_refs'])
        self.assertEqual(receipt['binding'], workspace['checkpoint']['binding'])
        self.assertNotEqual(original_proof['work_binding_sha256'], receipt['binding'])
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'versioned launch-protocol proof'):
            self.recover()
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertEqual(workspace['state'], 'prepared')
        print(json.dumps({'start_bound_scope': {'new_checkpoint_valid': True,
            'contract_changed_after_start': True, 'old_start_proof_rejected': True}}), flush=True)

    def test_stale_latest_pin_late_content_and_scope_changes_rejected(self):
        self.prepared(); first = self.snapshot()
        (self.old_path / 'src/a/draft.txt').write_bytes(b'latest draft\n'); self.snapshot()
        pristine = self.state()
        for kind in ('old-pin', 'spec', 'scope', 'late-content'):
            with self.subTest(kind=kind):
                state = copy.deepcopy(pristine)
                wp = find(state['snapshot']['work_packages'], 'WP-A')
                if kind == 'old-pin': state['workspaces'][self.old['workspace_id']]['checkpoint'] = {
                    k: first[k] for k in ('path', 'manifest_sha256', 'binding', 'unknown_digest')}
                elif kind == 'spec': wp['spec_refs'][0]['version'] = 'new-contract'
                elif kind == 'scope': wp['allowed_paths'] = ['src/a/narrow/']
                else: (self.old_path / 'src/a/draft.txt').write_bytes(b'late bytes after checkpoint\n')
                atomic_json(self.store.path, state)
                self.refused_without_write(self.recover)
                (self.old_path / 'src/a/draft.txt').write_bytes(b'latest draft\n')
        atomic_json(self.store.path, pristine)

    def test_identity_epoch_token_and_operation_conflicts_do_not_mutate(self):
        self.prepared(); self.snapshot()
        self.refused_without_write(lambda: self.recover(actor='principal-c'))
        for field in ('token', 'epoch'):
            for value in (True, self.old[field] + 1):
                with self.subTest(field=field, value=value):
                    bad = dict(self.old); bad[field] = value
                    self.refused_without_write(lambda: self.recover(credentials=bad))
        result = self.recover(); before = self.store.path.read_bytes()
        replay = self.recover(revision=0)
        self.assertTrue(replay['replayed']); self.assertEqual(replay['operation'], result['operation'])
        self.assertEqual(self.store.path.read_bytes(), before)
        self.refused_without_write(lambda: self.recover(op='recover-second-operation'))
        self.refused_without_write(lambda: self.recover(actor='principal-c'))


class ExternalDomainExclusionTests(unittest.TestCase):
    """Filesystem/config validation only; never launch a host driver or process."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.trusted = self.root / 'trusted'; self.candidate = self.root / 'candidate'
        self.requests = self.candidate / 'requests'; self.receipts = self.trusted / 'receipts'
        self.scratch = self.trusted / 'scratch'; self.normal = self.candidate / 'normal'
        for path in (self.requests, self.receipts, self.scratch, self.normal): path.mkdir(parents=True)
        self.worker = self.trusted / 'fixture-worker.py'; self.worker.write_bytes(b'fixture only; never executed\n')
        self.config_path = self.trusted / 'config.json'

    def config(self, workspace, relative):
        return dict(format='v4-launch-config/1', batch_id='synthetic-domain-check',
            trusted_root=str(self.trusted), candidate_root=str(self.candidate), driver_sha256='a' * 64,
            python='/usr/bin/python3', worker_program=str(self.worker),
            worker_sha256=hashlib.sha256(self.worker.read_bytes()).hexdigest(), request_dir=str(self.requests),
            receipt_dir=str(self.receipts), scratch_root=str(self.scratch), deadline_seconds=10,
            jobs=[dict(job_id='job-a', operation_id='run-a', workspace=str(workspace), output=relative,
                content_sha256=hashlib.sha256(b'fixture delivery\n').hexdigest(), max_delay_seconds=2,
                max_runtime_seconds=5)])

    def client(self, workspace, relative):
        return ExternalClient(self.config_path, 'job-a', 'run-a', workspace, relative, 'fixture delivery\n', 0, 5)

    def test_normal_external_configuration_remains_valid_without_spawning(self):
        config = self.config(self.normal, 'result.txt'); self.config_path.write_text(json.dumps(config))
        self.assertEqual(validate_config(config), config)
        client = self.client(self.normal, 'result.txt')
        self.assertEqual(client.request['operation_id'], 'run-a')
        self.assertEqual(list(self.requests.iterdir()), [])

    def test_external_client_refuses_reserved_domain_before_reading_config(self):
        reserved = self.candidate / 'v4-direct-local-missing-config'; reserved.mkdir()
        self.assertFalse(self.config_path.exists())
        with self.assertRaisesRegex(ValueError, 'direct-local-only'):
            self.client(reserved, 'result.txt')
        self.assertEqual(list(self.requests.iterdir()), [])

    def test_reserved_workspace_ancestor_and_output_paths_reject_before_external_launch(self):
        variants = [
            (self.candidate / ('v4-direct-local-' + '1' * 32), 'result.txt'),
            (self.candidate / 'v4-direct-local-ancestor' / 'child', 'result.txt'),
            (self.normal, 'v4-direct-local-output/result.txt'),
            (self.candidate / 'V4-DIRECT-LOCAL-uppercase', 'result.txt'),
            (self.normal, 'V4-DiReCt-LoCaL-output/result.txt'),
        ]
        for workspace, relative in variants:
            with self.subTest(workspace=workspace.name, output=relative):
                workspace.mkdir(parents=True, exist_ok=True)
                (workspace / relative).parent.mkdir(parents=True, exist_ok=True)
                config = self.config(workspace, relative)
                self.config_path.write_text(json.dumps(config))
                # A prepublished mailbox request cannot make an invalid config launch.
                request = self.requests / 'job-a.request.json'
                request.write_text(json.dumps(dict(format='v4-launch-request/1', job_id='job-a',
                    operation_id='run-a', content='fixture delivery\n', delay_seconds=0, timeout=5)))
                before = request.read_bytes()
                with self.assertRaisesRegex(ValueError, 'direct|reserved|domain'):
                    self.client(workspace, relative)
                with self.assertRaisesRegex(ValueError, 'direct|reserved|domain'):
                    validate_config(config)
                with patch('subprocess.Popen', side_effect=AssertionError('no process permitted')) as spawned:
                    with self.assertRaisesRegex(ValueError, 'direct|reserved|domain'):
                        Driver(config, popen=spawned)
                    spawned.assert_not_called()
                self.assertEqual(request.read_bytes(), before)
                self.assertEqual(list(self.receipts.iterdir()), [])
                self.assertEqual(list(self.scratch.iterdir()), [])
                request.unlink()


if __name__ == '__main__':
    unittest.main()
