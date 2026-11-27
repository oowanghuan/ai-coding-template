import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from framework.core.protocol import load_json, validate
from framework.local.storage import atomic_json, safe_path
from framework.local.store import Store, now
from framework.local.runner import git, prepare, run, sandbox_policy

ROOT = Path(__file__).resolve().parents[2]
ACTOR = 'principal-implementer'
OWNER = 'principal-owner'


def fixture(sha):
    s = load_json(ROOT / 'examples/protocol/in-progress.json')
    s['assignments'] = []
    s['checkpoints'] = []
    w = s['work_packages'][0]
    w.update(state='planned', assignment_ref=None, checkpoint_ref=None, baseline_sha=sha)
    s['workers'][0]['state'] = 'available'
    return s


class LocalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        git(self.root, 'init', '-q')
        (self.root / 'src').mkdir()
        (self.root / 'src/base.txt').write_text('baseline')
        git(self.root, 'add', 'src')
        git(self.root, '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
            'commit', '-qm', 'synthetic baseline')
        self.sha = git(self.root, 'rev-parse', 'HEAD').decode().strip()
        self.store = Store(self.root)

    def init(self, mutate=None):
        s = fixture(self.sha)
        if mutate:
            mutate(s)
        return self.store.initialize(s, OWNER)

    def state(self):
        return self.store.inspect()['state']

    def change(self, action, payload, actor=ACTOR, op=None, **kw):
        return self.store.change(action, payload, actor, self.state()['revision'],
                                 op or action + str(self.state()['revision']), **kw)

    def claim(self, wp='WP-DEMO', worker='worker-a', session='session-a', actor=ACTOR, **kw):
        return self.change('claim', dict(wp_id=wp, worker_id=worker, session_id=session, lease_seconds=300),
                           actor=actor, **kw)['operation']['result']

    def start(self, credentials, **kw):
        return prepare(self.root, credentials, ACTOR, self.state()['revision'], 'start', **kw)

    @unittest.skipIf(os.environ.get('V4_OUTER_SEATBELT') == '1', 'nested Seatbelt unavailable; full runner integration requires independent isolated host')
    def test_reserved_start_and_controlled_delivery(self):
        self.init()
        c = self.claim()
        self.assertEqual(self.state()['snapshot']['work_packages'][0]['state'], 'ready')
        self.start(c)
        r = run(self.root, c, ACTOR, 'src/out.txt', 'synthetic', 'run', self.state()['revision'])
        self.assertEqual(r['exit_code'], 0)
        self.assertEqual(run(self.root, c, ACTOR, 'src/out.txt', 'synthetic', 'run', 0), r)
        with self.assertRaisesRegex(ValueError, 'different intent'):
            run(self.root, c, ACTOR, 'src/out.txt', 'changed', 'run', 0)
        delivered = self.change('submit', dict(c, path='src/out.txt', sha256=hashlib.sha256(b'synthetic').hexdigest()))
        self.assertFalse(delivered['operation']['result']['accepted'])
        self.assertFalse((self.root / 'src/out.txt').exists())
        self.assertEqual(self.state()['snapshot']['work_packages'][0]['state'], 'in_progress')

    def test_real_process_race_has_one_winner(self):
        self.init()
        code = '''import sys,json
from framework.local.store import Store
sys.stdin.readline()
try:
 r=Store(sys.argv[1]).change('claim',dict(wp_id='WP-DEMO',worker_id='worker-a',session_id='session-a',lease_seconds=300),'principal-implementer',0,sys.argv[2])
 print(json.dumps(r))
except ValueError as e:
 print(str(e));sys.exit(2)
'''
        processes = [subprocess.Popen([sys.executable, '-B', '-S', '-c', code, str(self.root), 'race' + str(i)],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for i in range(2)]
        for p in processes:
            p.stdin.write(b'go\n'); p.stdin.flush()
        outputs = [p.communicate(timeout=30) for p in processes]
        self.assertEqual(sorted(p.returncode for p in processes), [0, 2], outputs)
        self.assertEqual(len(self.state()['snapshot']['assignments']), 1)

    def test_commit_crash_replay_and_payload_mismatch(self):
        self.init()
        def fault(point):
            if point == 'after_commit':
                raise RuntimeError('lost response')
        with self.assertRaises(RuntimeError):
            self.claim(op='stable', fault=fault)
        p = dict(wp_id='WP-DEMO', worker_id='worker-a', session_id='session-a', lease_seconds=300)
        replay = self.store.change('claim', p, ACTOR, 0, 'stable')
        self.assertTrue(replay['replayed'])
        with self.assertRaisesRegex(ValueError, 'different intent'):
            self.store.change('claim', dict(p, lease_seconds=50), ACTOR, 0, 'stable')
        self.assertEqual(len(self.state()['snapshot']['assignments']), 1)

    def test_before_commit_preserves_authority(self):
        self.init()
        before = self.store.path.read_bytes()
        def fault(point):
            if point == 'before_commit':
                raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):
            self.claim(fault=fault)
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_unauthorized_actor_cannot_claim_or_revoke(self):
        self.init()
        with self.assertRaises(ValueError):
            self.claim(actor='intruder')
        c = self.claim()
        with self.assertRaisesRegex(ValueError, 'owner'):
            self.change('revoke', dict(assignment_id=c['assignment_id'], reason='test'))

    def test_authorization_budget_quota_and_pause_block_claim(self):
        for field, value in [('authorization', 'revoked'), ('budget', 'unknown'), ('quota', 'exhausted'), ('paused', True)]:
            with self.subTest(field=field):
                self.init()
                state = self.state()
                s = state['snapshot']
                if field == 'authorization': s['authorizations'][0]['state'] = value
                elif field == 'quota': s['workers'][0]['quota'] = value
                else: s['project'][field] = value
                atomic_json(self.store.path, state)  # Trusted fixture setup only.
                with self.assertRaises(ValueError): self.claim()
                self.store.path.unlink()

    def test_wrong_epoch_token_and_expired_lease(self):
        self.init()
        c = self.claim()
        for changed in [dict(c, epoch=2), dict(c, token=0)]:
            with self.assertRaisesRegex(ValueError, 'fenced'):
                self.change('heartbeat', dict(changed, lease_seconds=20))
        with self.assertRaisesRegex(ValueError, 'fenced'):
            self.change('heartbeat', dict(c, lease_seconds=20), at='2031-01-01T00:00:00Z')

    def test_expired_reservation_reclaims_with_new_token(self):
        self.init()
        old = self.claim(at='2026-01-01T00:00:00Z')
        current = self.claim()
        self.assertGreater(current['token'], old['token'])
        self.assertEqual(self.state()['snapshot']['assignments'][0]['state'], 'expired')
        with self.assertRaises(ValueError): self.change('heartbeat', dict(old, lease_seconds=30))

    def test_real_crash_after_atomic_write_reconciles_on_restart(self):
        self.init()
        code = '''import os,sys
from framework.local.store import Store
def crash(point):
 if point == 'after_commit': os._exit(19)
Store(sys.argv[1]).change('claim',dict(wp_id='WP-DEMO',worker_id='worker-a',session_id='session-a',lease_seconds=300),'principal-implementer',0,'crash-claim',fault=crash)
'''
        p = subprocess.run([sys.executable, '-B', '-S', '-c', code, str(self.root)], capture_output=True, timeout=30)
        self.assertEqual(p.returncode, 19, p.stderr)
        payload = dict(wp_id='WP-DEMO', worker_id='worker-a', session_id='session-a', lease_seconds=300)
        result = Store(self.root).change('claim', payload, ACTOR, 0, 'crash-claim')
        self.assertTrue(result['replayed'])
        self.assertEqual(len(self.state()['snapshot']['assignments']), 1)

    def test_protocol_01_stays_strict_and_02_requires_known_execution_baseline(self):
        s = fixture(self.sha); s['providers'] = []; s['hosts'] = []; s['workers'] = []; s['sessions'] = []
        s['authorizations'] = []
        w = s['work_packages'][0]
        w.update(baseline_sha=None, authorization_ref=None, implementer=None, reviewer=None, acceptor=None)
        self.assertTrue(validate(s, now()))
        s['schema_version'] = '0.2'
        self.assertEqual(validate(s, now()), [])
        w['state'] = 'ready'
        self.assertTrue(any('unknown-baseline' in e for e in validate(s, now())))

    def test_revoke_fences_old_delivery_and_preserves_workspace(self):
        self.init(); c = self.claim(); self.start(c)
        path = self.root / self.state()['workspaces'][c['workspace_id']]['path']
        (path / 'src/out.txt').write_text('kept')
        self.change('revoke', dict(assignment_id=c['assignment_id'], reason='owner stop'), OWNER)
        with self.assertRaisesRegex(ValueError, 'fenced'):
            self.change('submit', dict(c, path='src/out.txt', sha256=hashlib.sha256(b'kept').hexdigest()))
        new = self.claim()
        self.assertGreater(new['token'], c['token'])
        self.assertNotEqual(new['workspace_id'], c['workspace_id'])
        self.assertEqual((path / 'src/out.txt').read_text(), 'kept')

    def test_unknown_worktree_intent_blocks_reassignment(self):
        self.init(); c = self.claim()
        def fault(point):
            if point == 'intent_saved': raise RuntimeError('crash')
        with self.assertRaises(RuntimeError): self.start(c, fault=fault)
        self.change('revoke', dict(assignment_id=c['assignment_id'], reason='stop'), OWNER)
        with self.assertRaisesRegex(ValueError, 'unknown workspace'): self.claim()
        with self.assertRaises(ValueError): self.start(c)

    def test_created_worktree_can_reconcile_without_duplicate(self):
        self.init(); c = self.claim()
        def fault(point):
            if point == 'workspace_created': raise RuntimeError('crash')
        with self.assertRaises(RuntimeError): self.start(c, fault=fault)
        self.change('reconcile', dict(workspace_id=c['workspace_id'], resolution='workspace-present'), OWNER)
        self.assertTrue(self.start(c)['replayed'])
        self.assertEqual(len(self.state()['workspaces']), 1)

    def test_partial_worktree_cannot_be_reconciled_as_complete(self):
        self.init(); c = self.claim()
        def fault(point):
            if point == 'workspace_created': raise RuntimeError('crash')
        with self.assertRaises(RuntimeError): self.start(c, fault=fault)
        p = self.root / self.state()['workspaces'][c['workspace_id']]['path'] / 'src/base.txt'
        p.write_text('partial')
        with self.assertRaisesRegex(ValueError, 'materialization'):
            self.change('reconcile', dict(workspace_id=c['workspace_id'], resolution='workspace-present'), OWNER)
        self.assertEqual(p.read_text(), 'partial')

    def test_launch_intent_is_not_retried(self):
        self.init(); c = self.claim(); self.start(c)
        def fault(point):
            if point == 'launch_intent_saved': raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):
            run(self.root, c, ACTOR, 'src/out.txt', 'x', 'run', self.state()['revision'], fault=fault)
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            run(self.root, c, ACTOR, 'src/out.txt', 'x', 'run', 0)
        with self.assertRaisesRegex(ValueError, 'unresolved'): self.change('release', c)

    def test_process_started_failure_is_stopped_not_accepted(self):
        self.init(); c = self.claim(); self.start(c)
        def fault(point):
            if point == 'process_started': raise RuntimeError('controlled interruption')
        with self.assertRaises(RuntimeError):
            run(self.root, c, ACTOR, 'src/out.txt', 'x', 'run', self.state()['revision'], delay_seconds=5, fault=fault)
        self.assertEqual(self.state()['workspaces'][c['workspace_id']]['state'], 'stopped')
        self.assertEqual(self.state()['deliveries'], {})

    @unittest.skipIf(os.environ.get('V4_OUTER_SEATBELT') == '1', 'nested Seatbelt unavailable; policy/worker is separately tested by trusted outer harness')
    def test_sandbox_denies_network_host_read_write_and_credentials(self):
        # Actual OS sandbox with a malicious probe, independent of the fixed worker's behavior.
        workspace = self.root / 'sandbox'; workspace.mkdir()
        scratch = self.root / 'scratch'; scratch.mkdir()
        canary = self.root / 'outside'; canary.write_text('kept')
        policy = scratch / 'probe.sb'
        policy.write_text(sandbox_policy(workspace, ROOT / 'framework/local', workspace / 'allowed', scratch))
        probe = '''import os,socket,sys
from pathlib import Path
for action in [lambda:Path(sys.argv[1]).read_text(),lambda:Path(sys.argv[1]).write_text('bad'),lambda:socket.create_connection(('127.0.0.1',9))]:
 try:action()
 except PermissionError:continue
 else:raise AssertionError('sandbox escape')
assert not any(k in os.environ for k in ['GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','SSH_AUTH_SOCK'])
Path('allowed').write_text('ok')
'''
        p = subprocess.run(['/usr/bin/sandbox-exec', '-f', str(policy), sys.executable, '-B', '-S', '-c', probe, str(canary)],
                           cwd=workspace, env={'PATH': '/usr/bin:/bin', 'HOME': str(scratch)}, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr.decode())
        self.assertEqual(canary.read_text(), 'kept')
        self.assertEqual((workspace / 'allowed').read_text(), 'ok')

    def test_path_escape_symlink_and_hardlink_refused(self):
        self.init(); c = self.claim(); self.start(c)
        path = self.root / self.state()['workspaces'][c['workspace_id']]['path']
        (path / 'src/link').symlink_to(self.root / 'src/base.txt')
        os.link(path / 'src/base.txt', path / 'src/hard')
        for name in ['../outside', '/outside', 'src/link', 'src/hard', 'secrets/private']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.change('submit', dict(c, path=name, sha256='a'*64))

    def test_worker_registration_owner_only_and_immutable(self):
        self.init()
        s = self.state()['snapshot']
        p = dict(worker=s['workers'][0], provider=s['providers'][0], host=s['hosts'][0], session=s['sessions'][0])
        with self.assertRaises(ValueError): self.change('register-worker', p)
        self.change('register-worker', p, OWNER)
        q = copy.deepcopy(p); q['worker']['slots'] = 2
        with self.assertRaisesRegex(ValueError, 'immutable'): self.change('register-worker', q, OWNER)

    def two_tasks(self, same_scope=False, same_worker=False):
        def mutate(s):
            w = s['work_packages'][0]; w['allowed_paths'] = ['src/a/']
            second = copy.deepcopy(w); second.update(id='WP-SECOND', allowed_paths=['src/a/' if same_scope else 'src/b/'])
            s['work_packages'].append(second)
            s['authorizations'][0]['wp_refs'].append('WP-SECOND')
            if not same_worker:
                s['workers'][1].update(role_refs=['role-developer'], capabilities=['code'], quota='available')
                s['sessions'].append(dict(id='session-b', worker_ref='worker-b', provider_ref='provider-b',
                                          host_ref='host-local', context_ref='synthetic-b'))
        self.init(mutate)

    def test_scope_conflict_and_capacity(self):
        for same_worker in [False, True]:
            with self.subTest(same_worker=same_worker):
                self.two_tasks(same_scope=not same_worker, same_worker=same_worker)
                self.claim()
                with self.assertRaisesRegex(ValueError, 'worker-capacity' if same_worker else 'scope-conflict'):
                    self.claim(wp='WP-SECOND', worker='worker-a' if same_worker else 'worker-b',
                               session='session-a' if same_worker else 'session-b', actor=ACTOR if same_worker else 'principal-reviewer')
                self.store.path.unlink()

    def test_unmet_dependency(self):
        self.two_tasks()
        s = self.state()
        s['snapshot']['work_packages'][0]['dependencies'] = [dict(wp_id='WP-SECOND', required_milestone='merged', artifact_revision=self.sha)]
        atomic_json(self.store.path, s)
        with self.assertRaisesRegex(ValueError, 'dependency-not-ready'): self.claim()

    @unittest.skipIf(os.environ.get('V4_OUTER_SEATBELT') == '1', 'nested Seatbelt unavailable; not counted as end-to-end runner acceptance')
    def test_two_isolated_runners_capture_distinct_deliveries(self):
        # Concurrent controller calls alone do not prove Worker execution overlap.
        # The fixed Worker has no start/end handshake; overlap needs separate evidence.
        self.two_tasks()
        a = self.claim()
        b = self.claim(wp='WP-SECOND', worker='worker-b', session='session-b', actor='principal-reviewer')
        self.start(a)
        prepare(self.root, b, 'principal-reviewer', self.state()['revision'], 'start-b')
        workspaces = self.state()['workspaces']
        self.assertNotEqual(workspaces[a['workspace_id']]['path'], workspaces[b['workspace_id']]['path'])
        errors = []; outcomes = []
        def launch(c, actor, path, key):
            try:
                for attempt in range(10):
                    try:
                        outcomes.append(run(self.root, c, actor, path, key, key, self.state()['revision'], delay_seconds=1))
                        return
                    except ValueError as error:
                        if str(error) != 'revision conflict': raise
                raise AssertionError('too many conflicts')
            except BaseException as error: errors.append(str(error))
        threads = [threading.Thread(target=launch, args=(a, ACTOR, 'src/a/out', 'run-a')),
                   threading.Thread(target=launch, args=(b, 'principal-reviewer', 'src/b/out', 'run-b'))]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=30)
        self.assertTrue(all(not thread.is_alive() for thread in threads), 'Runner calls did not terminate')
        self.assertFalse(errors, errors)
        self.assertEqual(len(outcomes), 2)
        self.assertNotEqual(outcomes[0]['pid'], outcomes[1]['pid'])
        self.assertTrue(all(outcome['exit_code'] == 0 for outcome in outcomes))
        for c, actor, wp_id, path, content in [
                (a, ACTOR, 'WP-DEMO', 'src/a/out', b'run-a'),
                (b, 'principal-reviewer', 'WP-SECOND', 'src/b/out', b'run-b')]:
            digest = hashlib.sha256(content).hexdigest()
            result = self.change('submit', dict(c, path=path, sha256=digest), actor)['operation']['result']
            self.assertEqual(result, dict(delivery_id=wp_id, sha256=digest, accepted=False))
            delivery = self.state()['deliveries'][wp_id]
            self.assertEqual(delivery['assignment_id'], c['assignment_id'])
            self.assertEqual((delivery['epoch'], delivery['token']), (c['epoch'], c['token']))
            self.assertEqual(delivery['path'], path)
            self.assertEqual(delivery['baseline_sha'], self.sha)
            self.assertEqual(delivery['sha256'], digest)
            self.assertEqual(base64.b64decode(delivery['content_base64']), content)
            self.assertFalse((self.root / path).exists())
        self.assertEqual(set(self.state()['deliveries']), {'WP-DEMO', 'WP-SECOND'})
        self.assertEqual(self.store.inspect()['consistency_errors'], [])
        self.assertEqual(git(self.root, 'rev-parse', 'HEAD').decode().strip(), self.sha)
        self.assertEqual((self.root / 'src/base.txt').read_text(), 'baseline')

    def test_no_sandbox_fallback_on_nested_launch_failure(self):
        if os.environ.get('V4_OUTER_SEATBELT') != '1':
            self.skipTest('specific to outer Seatbelt test environment')
        self.init(); c = self.claim(); self.start(c)
        with self.assertRaisesRegex(ValueError, 'synthetic process failed'):
            run(self.root, c, ACTOR, 'src/out.txt', 'x', 'nested', self.state()['revision'])
        state = self.state()
        self.assertEqual(state['workspaces'][c['workspace_id']]['run']['exit_code'], 71)
        self.assertEqual(state['deliveries'], {})
        self.assertFalse((self.root / state['workspaces'][c['workspace_id']]['path'] / 'src/out.txt').exists())

    def test_cli_failed_run_replay_stays_failed_and_does_not_launch(self):
        if os.environ.get('V4_OUTER_SEATBELT') != '1':
            self.skipTest('reproduces the actual nested Seatbelt failure')
        self.init(); c = self.claim(); self.start(c)
        payload = self.root / 'run-input.json'
        payload.write_text(json.dumps(dict(credentials=c, path='src/out.txt', content='x')))
        args = [sys.executable, '-B', '-S', str(ROOT / 'scripts/v4_local.py'), 'run', '--root', str(self.root),
                '--actor', ACTOR, '--input', str(payload), '--operation-id', 'cli-failure',
                '--expected-revision', str(self.state()['revision'])]
        first = subprocess.run(args, capture_output=True, timeout=30)
        self.assertNotEqual(first.returncode, 0)
        state = self.state()
        self.assertEqual(state['workspaces'][c['workspace_id']]['run']['exit_code'], 71)
        before = self.store.path.read_bytes()
        logs = self.root / '.ai-org/runner' / c['workspace_id']
        saved = {p.name:p.read_bytes() for p in logs.iterdir()}
        second = subprocess.run(args, capture_output=True, timeout=30)
        self.assertNotEqual(second.returncode, 0, second.stdout.decode())
        self.assertEqual(first.stderr, second.stderr)
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertEqual({p.name:p.read_bytes() for p in logs.iterdir()}, saved)
        self.assertEqual(self.state()['deliveries'], {})

    def test_cli_success_receipt_replay_preserves_result(self):
        # Synthetic committed result, not evidence of a successful nested launch.
        self.init(); c = self.claim(); self.start(c)
        p = dict(c, path='src/out.txt', content_sha256=hashlib.sha256(b'x').hexdigest(), delay_seconds=0, timeout=20)
        self.change('run-begin', p, op='success-replay')
        self.store.workspace_phase(c, ACTOR, 'launching', 'finished', run=dict(state='finished', exit_code=0, synthetic=True))
        payload = self.root / 'run-input.json'
        payload.write_text(json.dumps(dict(credentials=c, path='src/out.txt', content='x')))
        before = self.store.path.read_bytes()
        p = subprocess.run([sys.executable, '-B', '-S', str(ROOT / 'scripts/v4_local.py'), 'run', '--root', str(self.root),
            '--actor', ACTOR, '--input', str(payload), '--operation-id', 'success-replay', '--expected-revision', '0'],
            capture_output=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)['exit_code'], 0)
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_two_actual_workers_inherit_outer_sandbox_and_submit(self):
        # Tests actual process/worktree isolation and delivery, NOT the nested launcher.
        self.two_tasks(); a = self.claim()
        b = self.claim(wp='WP-SECOND', worker='worker-b', session='session-b', actor='principal-reviewer')
        self.start(a); prepare(self.root, b, 'principal-reviewer', self.state()['revision'], 'start-b')
        processes = []
        for c, relative in [(a, 'src/a/out'), (b, 'src/b/out')]:
            directory = self.root / self.state()['workspaces'][c['workspace_id']]['path']
            (directory / relative).parent.mkdir(parents=True)
            process = subprocess.Popen([sys.executable, '-B', '-S', str(ROOT / 'framework/local/worker_process.py')],
                cwd=directory, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.stdin.write(json.dumps(dict(path=relative, content='isolated', delay_seconds=1)).encode())
            process.stdin.flush(); processes.append(process)
        self.assertTrue(all(p.poll() is None for p in processes))
        for p in processes:
            out, err = p.communicate(timeout=15)
            self.assertEqual(p.returncode, 0, err)
        for c, actor, relative in [(a, ACTOR, 'src/a/out'), (b, 'principal-reviewer', 'src/b/out')]:
            result = self.change('submit', dict(c, path=relative, sha256=hashlib.sha256(b'isolated').hexdigest()), actor)
            self.assertFalse(result['operation']['result']['accepted'])
        self.assertEqual(len(self.state()['deliveries']), 2)
        self.assertFalse((self.root / 'src/a/out').exists())


if __name__ == '__main__':
    unittest.main()
