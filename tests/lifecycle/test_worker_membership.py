"""Atomic hot enrollment with synthetic controller observations and real Git/state.

No provider authentication is inferred from these fixtures.
"""
import copy
import threading
import unittest

import test_lifecycle as fixtures


class MembershipTests(unittest.TestCase):
    setUp = fixtures.LifecycleTests.setUp
    initial = fixtures.LifecycleTests.initial
    state = fixtures.LifecycleTests.state
    change = fixtures.LifecycleTests.change
    result = fixtures.LifecycleTests.result
    enable = fixtures.LifecycleTests.enable
    event = fixtures.LifecycleTests.event
    claim = fixtures.LifecycleTests.claim

    def member(self, identity='d', group='Q3'):
        s = self.state()['snapshot']
        worker = copy.deepcopy(s['workers'][2])
        worker.update(id='worker-' + identity, principal='principal-' + identity,
                      state='available', quota='available')
        return dict(worker=worker, provider=copy.deepcopy(s['providers'][2]),
                    host=copy.deepcopy(s['hosts'][0]),
                    session=dict(id='session-' + identity, worker_ref=worker['id'],
                                 provider_ref=worker['provider_ref'], host_ref=worker['host_ref'],
                                 context_ref='synthetic-' + identity),
                    runtime=dict(worker_id=worker['id'], quota_group=group,
                                 auth_identity='identity-' + identity, mode='elastic',
                                 authenticated=True, authorized=True,
                                 resource=dict(agent_tool='synthetic-tool', model_provider='synthetic-model',
                                               model=None, credential_ref='credential-ref-only')))

    def boot(self):
        self.initial(); self.enable()

    def reject_unchanged(self, payload, **kwargs):
        before = self.store.path.read_bytes()
        with self.assertRaises((ValueError, KeyError)):
            self.change('register-worker', payload, **kwargs)
        self.assertEqual(before, self.store.path.read_bytes())

    def test_live_pool_add_preserves_active_rights_and_claims_other_task(self):
        self.boot(); old = self.claim('a'); self.result('start', old, actor='principal-a')
        before = self.state(); payload = self.member()
        result = self.result('register-worker', payload)
        self.assertEqual(result, dict(worker_id='worker-d', status='available', execution_started=False))
        after = self.state()
        for key in ('assignments', 'work_packages', 'authorizations'):
            self.assertEqual(before['snapshot'][key], after['snapshot'][key])
        for key in ('workspaces', 'tokens', 'deliveries'):
            self.assertEqual(before[key], after[key])
        for identity in before['worker_runtime']['workers']:
            self.assertEqual(before['worker_runtime']['workers'][identity], after['worker_runtime']['workers'][identity])
        for group in before['worker_runtime']['groups']:
            self.assertEqual(before['worker_runtime']['groups'][group], after['worker_runtime']['groups'][group])
        new = self.claim('d', wp='WP-B')
        self.assertEqual(new['token'], 1)
        self.assertNotEqual(old['workspace_id'], new['workspace_id'])

    def test_operation_replay_after_claim_does_not_reset_runtime_or_rights(self):
        self.boot(); payload = self.member(); revision = self.state()['revision']
        self.store.change('register-worker', payload, fixtures.OWNER, revision, 'admit', at=fixtures.AT)
        self.claim('d', wp='WP-B'); before = self.store.path.read_bytes()
        replay = self.store.change('register-worker', payload, fixtures.OWNER, revision, 'admit', at=fixtures.AT)
        self.assertTrue(replay['replayed']); self.assertEqual(before, self.store.path.read_bytes())
        changed = copy.deepcopy(payload); changed['runtime']['quota_group'] = 'replacement'
        self.reject_unchanged(changed, op='admit')
        self.reject_unchanged(payload, op='different-operation')

    def test_shared_limit_pending_probe_and_generation_preserved(self):
        self.boot(); self.event('a', 'quota_limited', retry_at=fixtures.later(5))
        self.result('scheduler-tick', {}, at=fixtures.later(5))
        group = copy.deepcopy(self.state()['worker_runtime']['groups']['Q1'])
        self.assertIsNotNone(group['pending_probe'])
        result = self.result('register-worker', self.member(group='Q1'), at=fixtures.later(6))
        self.assertEqual(result['status'], 'quota_limited')
        self.assertEqual(group, self.state()['worker_runtime']['groups']['Q1'])
        with self.assertRaises(ValueError): self.claim('d', wp='WP-B', at=fixtures.later(6))
        self.assertEqual(self.claim('c', at=fixtures.later(6))['token'], 1)

    def test_unknown_credentials_cannot_claim(self):
        self.boot()
        for index, field in enumerate(('authenticated', 'authorized')):
            payload = self.member(identity='d' + str(index)); del payload['runtime'][field]
            result = self.result('register-worker', payload)
            self.assertEqual(result['status'], 'authentication_required' if field == 'authenticated' else 'suspended')
            with self.assertRaises(ValueError): self.claim('d' + str(index), wp='WP-B')

    def test_owner_only_missing_runtime_and_wrong_bindings_rollback(self):
        self.boot(); payload = self.member()
        self.reject_unchanged(payload, actor='principal-a')
        missing = copy.deepcopy(payload); del missing['runtime']; self.reject_unchanged(missing)
        for field, key in (('worker', 'host_ref'), ('worker', 'provider_ref'),
                           ('session', 'worker_ref'), ('session', 'host_ref'),
                           ('session', 'provider_ref'), ('runtime', 'worker_id')):
            with self.subTest(field=field, key=key):
                altered = copy.deepcopy(payload); altered[field][key] = 'wrong'
                self.reject_unchanged(altered)

    def test_existing_provider_host_and_session_cannot_be_redefined(self):
        self.boot(); payload = self.member()
        changed = copy.deepcopy(payload); changed['provider']['adapter'] = 'replacement'; self.reject_unchanged(changed)
        changed = copy.deepcopy(payload); changed['host']['label'] = 'replacement'; self.reject_unchanged(changed)
        changed = copy.deepcopy(payload); changed['session']['id'] = 'session-a'; self.reject_unchanged(changed)

    def test_invalid_resource_or_runtime_never_partially_adds_member(self):
        self.boot(); payload = self.member()
        variants = [('quota_group', ''), ('auth_identity', None), ('mode', 'invalid'),
                    ('resource', {'credential_ref': '/private/credential'}),
                    ('pending_probe', None)]
        for field, value in variants:
            with self.subTest(field=field):
                changed = copy.deepcopy(payload); changed['runtime'][field] = value
                self.reject_unchanged(changed)

    def test_unknown_new_quota_and_conflicting_shared_quota_fail_closed(self):
        self.boot(); payload = self.member(); payload['worker']['quota'] = 'unknown'
        self.assertEqual(self.result('register-worker', payload)['status'], 'quota_limited')
        with self.assertRaises(ValueError): self.claim('d', wp='WP-B')
        conflict = self.member('e', 'Q1'); conflict['worker']['quota'] = 'exhausted'
        self.reject_unchanged(conflict)

    def test_new_host_registration_does_not_grant_task_environment_authority(self):
        self.boot(); payload = self.member(); payload['host']['id'] = 'host-new'
        payload['worker']['host_ref'] = payload['session']['host_ref'] = 'host-new'
        self.result('register-worker', payload)
        before = self.store.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'host-not-authorized'): self.claim('d', wp='WP-B')
        self.assertEqual(before, self.store.path.read_bytes())

    def test_capability_budget_and_offline_restrictions_still_apply(self):
        self.boot(); payload = self.member(); payload['worker']['capabilities'] = ['review']
        self.result('register-worker', payload)
        with self.assertRaises(ValueError): self.claim('d', wp='WP-B')
        offline = self.member('e'); offline['worker']['state'] = 'offline'
        self.assertEqual(self.result('register-worker', offline)['status'], 'offline')
        with self.assertRaises(ValueError): self.claim('e', wp='WP-B')
        self.event('a', 'budget_exhausted', budget_scope='project', source='project-budget-controller')
        self.assertEqual(self.result('register-worker', self.member('f'))['status'], 'suspended')
        with self.assertRaises(ValueError): self.claim('f', wp='WP-B')

    def test_same_revision_concurrent_admissions_have_one_winner(self):
        self.boot(); revision = self.state()['revision']; barrier = threading.Barrier(2); results = []
        payloads = [self.member('d'), self.member('e')]
        def attempt(index):
            barrier.wait(timeout=10)
            try:
                self.store.change('register-worker', payloads[index], fixtures.OWNER, revision,
                                  'concurrent-' + str(index), at=fixtures.AT)
                results.append('committed')
            except ValueError as error: results.append(str(error))
        threads = [threading.Thread(target=attempt, args=(i,)) for i in range(2)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=30); self.assertFalse(thread.is_alive())
        self.assertCountEqual(results, ['committed', 'revision conflict'])
        state = self.state(); self.assertEqual(len(state['worker_runtime']['workers']), 4)
        self.assertEqual(len(state['snapshot']['workers']), 4)

    def test_commit_fault_reconciliation_and_legacy_registration(self):
        self.initial(); payload = self.member(); del payload['runtime']
        self.result('register-worker', payload)
        self.result('register-worker', payload)  # Legacy unchanged-identity registration.
        self.assertNotIn('worker_runtime', self.state())

    def test_before_and_after_commit_faults_preserve_atomicity_and_replay(self):
        self.boot(); payload = self.member(); before = self.store.path.read_bytes()
        def fail_before(point):
            if point == 'before_commit': raise RuntimeError('synthetic before commit')
        def fail_after(point):
            if point == 'after_commit': raise RuntimeError('synthetic lost response')
        with self.assertRaises(RuntimeError):
            self.change('register-worker', payload, op='atomic-admit', fault=fail_before)
        self.assertEqual(before, self.store.path.read_bytes())
        with self.assertRaises(RuntimeError):
            self.change('register-worker', payload, op='atomic-admit', fault=fail_after)
        committed = self.store.path.read_bytes()
        self.assertTrue(self.change('register-worker', payload, op='atomic-admit')['replayed'])
        self.assertEqual(committed, self.store.path.read_bytes())


if __name__ == '__main__': unittest.main()
