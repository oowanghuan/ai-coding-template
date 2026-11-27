import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from framework.core.protocol import load_json, validate, validate_transition

ROOT = Path(__file__).resolve().parents[2]
AT = '2026-11-27T10:00:00Z'


class Protocol(unittest.TestCase):
    def setUp(self):
        self.data = load_json(ROOT / 'examples/protocol/in-progress.json')
        self.wp = self.data['work_packages'][0]

    def reject(self, code):
        errors = validate(self.data, AT)
        self.assertTrue(any(e.startswith(code) for e in errors), errors)

    def delivered(self, state='accepted', kind='code'):
        from framework.core.protocol import MINIMUM
        self.wp.update(state=state, kind=kind, submitted_sha='d' * 40,
                       evidence_refs=['synthetic-evidence'], review_refs=['synthetic-review'],
                       required_milestones=sorted(MINIMUM[kind]))
        self.wp['milestones'] = {k: {'status': 'passed', 'subject_sha': 'd' * 40,
                                    'evidence_refs': ['synthetic-evidence'], 'signer': 'principal-reviewer',
                                    'reason': None} for k in MINIMUM[kind]}
        if 'merged' in self.wp['milestones']:
            self.wp['milestones']['merged']['signer'] = 'principal-owner'
        self.data['assignments'][0]['state'] = 'released'

    def test_example_valid_and_validation_is_pure_deterministic(self):
        before = copy.deepcopy(self.data)
        self.assertEqual(validate(self.data, AT), [])
        self.assertEqual(validate(self.data, AT), [])
        self.assertEqual(self.data, before)

    def test_each_kind_has_distinct_acceptance(self):
        for kind in ('code', 'spec', 'review', 'release', 'business-validation'):
            self.delivered(kind=kind)
            with self.subTest(kind=kind):
                self.assertEqual(validate(self.data, AT), [])

    def test_required_field_and_unknown_parallel_state_rejected(self):
        self.wp['done'] = True
        self.reject('schema:')
        del self.wp['done']
        del self.wp['negative_criteria']
        self.reject('schema:')

    def test_missing_and_duplicate_identifiers(self):
        self.wp['accountable_role'] = 'missing'
        self.reject('missing-reference:')
        self.data['workers'][1]['id'] = self.data['workers'][0]['id']
        self.reject('duplicate-id:')

    def test_self_and_two_node_dependency_cycles(self):
        dep = dict(wp_id=self.wp['id'], required_milestone='merged', artifact_revision='a' * 40)
        self.wp['dependencies'] = [dep]
        self.reject('dependency-cycle:')
        other = copy.deepcopy(self.wp)
        other.update(id='WP-OTHER', state='planned', assignment_ref=None, checkpoint_ref=None)
        self.data['work_packages'].append(other)
        self.wp['dependencies'][0]['wp_id'] = 'WP-OTHER'
        self.reject('dependency-cycle:')

    def test_dependency_must_pass_exact_required_revision(self):
        other = copy.deepcopy(self.wp)
        other.update(id='WP-OTHER', state='planned', assignment_ref=None, checkpoint_ref=None)
        self.data['work_packages'].append(other)
        self.wp['dependencies'] = [dict(wp_id='WP-OTHER', required_milestone='merged', artifact_revision='d' * 40)]
        self.reject('dependency-not-ready:')
        other['milestones']['merged'].update(status='passed', subject_sha='e' * 40, signer='principal-owner', evidence_refs=['synthetic'])
        other['submitted_sha'] = 'e' * 40
        self.reject('dependency-not-ready:')

    def test_proposed_revoked_missing_and_expired_authorization(self):
        for state in ('proposed', 'revoked'):
            self.data['authorizations'][0]['state'] = state
            self.reject('not-authorized:')
        self.data['authorizations'][0].update(state='granted', expires_at='2026-01-01T00:00:00Z')
        self.reject('not-authorized:')
        self.wp['authorization_ref'] = None
        self.reject('not-authorized:')

    def test_authorization_scope_and_host(self):
        self.data['authorizations'][0]['allowed_paths'] = ['other/']
        self.reject('authorization-scope:')
        self.data['authorizations'][0]['environment_refs'] = ['missing-host']
        self.reject('host-not-authorized:')

    def test_pause_budget_and_unknown_quota_are_not_permission(self):
        self.data['project']['paused'] = True
        self.reject('project-or-task-blocked:')
        self.data['project'].update(paused=False, budget='unknown')
        self.reject('project-or-task-blocked:')
        self.data['workers'][0]['quota'] = 'unknown'
        self.reject('worker-unavailable:')

    def test_expired_lease_and_epoch(self):
        self.data['assignments'][0]['lease_expires_at'] = AT
        self.reject('inactive-lease:')
        self.data['assignments'][0]['lease_expires_at'] = '2030-01-01T00:00:00Z'
        self.data['assignments'][0]['authority_epoch'] = 2
        self.reject('inactive-lease:')

    def test_double_assignment_and_capacity(self):
        other = copy.deepcopy(self.data['assignments'][0])
        other['id'] = 'assignment-other'
        self.data['assignments'].append(other)
        self.reject('double-assignment:')
        self.reject('worker-capacity:')
        self.reject('shared-workspace:')

    def test_scope_conflict_and_forbidden_scope(self):
        other = copy.deepcopy(self.data['assignments'][0])
        other.update(id='assignment-other', allowed_paths=['src/a.py'])
        self.data['assignments'].append(other)
        self.reject('scope-conflict:')
        self.wp['forbidden_paths'] = ['src/a.py']
        self.reject('assignment-scope:')

    def test_unsafe_scope_paths(self):
        for path in ('../escape', '/absolute', 'src/../escape', 'src//file', 'src\\file', 'src/*'):
            self.wp['allowed_paths'] = [path]
            with self.subTest(path=path):
                self.reject('schema:')

    def test_provider_session_binding(self):
        self.data['sessions'][0]['provider_ref'] = 'provider-b'
        self.reject('session-environment:')

    def test_high_risk_self_acceptance_rejected_across_models(self):
        self.wp.update(risk='high', acceptor='principal-implementer')
        self.reject('independence:')

    def test_merged_is_not_engineering_or_business_acceptance(self):
        self.delivered()
        self.wp['milestones']['engineering_accepted']['status'] = 'pending'
        self.reject('unmet-acceptance:')
        self.wp['kind'] = 'business-validation'
        self.reject('missing-kind-milestones:')

    def test_empty_or_wrong_sha_signoff_rejected(self):
        self.delivered()
        self.wp['milestones']['review_passed']['evidence_refs'] = []
        self.reject('empty-signoff:')
        self.wp['milestones']['review_passed']['subject_sha'] = 'e' * 40
        self.reject('milestone-sha:')

    def test_unstarted_task_cannot_also_be_complete(self):
        self.delivered(state='planned')
        self.reject('unstarted-with-completion:')

    def test_required_milestone_cannot_be_not_applicable(self):
        self.delivered()
        self.wp['milestones']['engineering_accepted'].update(status='not_applicable', reason='Skip')
        self.reject('required-not-applicable:')

    def test_satisfied_dependency_requires_the_exact_artifact(self):
        other = copy.deepcopy(self.wp)
        other.update(id='WP-OTHER', state='submitted', assignment_ref=None, checkpoint_ref=None,
                     submitted_sha='d' * 40, evidence_refs=['synthetic'])
        other['milestones']['merged'].update(status='passed', subject_sha='d' * 40,
                                            signer='principal-owner', evidence_refs=['synthetic'])
        self.data['work_packages'].append(other)
        self.wp['dependencies'] = [dict(wp_id='WP-OTHER', required_milestone='merged', artifact_revision='d' * 40)]
        self.assertEqual(validate(self.data, AT), [])
        self.wp['dependencies'][0]['artifact_revision'] = 'e' * 40
        self.reject('dependency-not-ready:')

    def test_checkpoint_unknown_operation_blocks_start(self):
        self.data['checkpoints'][0]['unknown_operations'] = [dict(id='operation-unknown', intent='Synthetic write', reconciliation='Read remote result first')]
        self.reject('unknown-operation:')

    def test_checkpoint_stale_spec_and_cross_assignment(self):
        self.data['checkpoints'][0]['spec_refs'][0]['version'] = 'stale'
        self.reject('stale-checkpoint-contract:')
        self.data['checkpoints'][0]['wp_revision'] = 100
        self.reject('checkpoint-binding:')

    def test_invalid_date_and_empty_recovery_location(self):
        self.data['checkpoints'][0]['created_at'] = '2026-02-30T10:00:00Z'
        self.reject('schema:')
        self.data['checkpoints'][0]['uncommitted'][0]['location'] = ''
        self.reject('schema:')

    def test_transition_legal_submission_and_illegal_close(self):
        before = copy.deepcopy(self.data)
        self.delivered(state='submitted')
        self.wp['revision'] += 1
        self.data['project']['revision'] += 1
        self.assertEqual(validate_transition(before, self.data, AT), [])
        self.wp['state'] = 'closed'
        self.assertIn('illegal-transition:WP-DEMO', validate_transition(before, self.data, AT))

    def test_signed_contract_change_requires_rework_and_invalidation(self):
        self.delivered()
        before = copy.deepcopy(self.data)
        self.wp['spec_refs'][0]['sha256'] = 'f' * 64
        self.wp['revision'] += 1
        self.data['project']['revision'] += 1
        self.assertIn('signature-invalidation-required:WP-DEMO', validate_transition(before, self.data, AT))
        self.wp.update(state='in_progress', change_reason='Contract revised')
        for milestone in self.wp['milestones'].values():
            milestone['status'] = 'invalidated'
        self.data['assignments'][0]['state'] = 'active'
        self.data['checkpoints'][0]['spec_refs'] = copy.deepcopy(self.wp['spec_refs'])
        # Rework needs a fresh assignment, not reactivating an already released lease.
        self.data['assignments'][0].update(id='assignment-rework', fencing_token=2)
        self.wp['assignment_ref'] = 'assignment-rework'
        self.data['checkpoints'][0]['assignment_ref'] = 'assignment-rework'
        self.assertEqual(validate_transition(before, self.data, AT), [])

    def test_expired_snapshot_can_be_safely_paused(self):
        self.data['assignments'][0]['lease_expires_at'] = '2026-11-27T09:30:00Z'
        before = copy.deepcopy(self.data)
        self.wp.update(state='paused', revision=2)
        self.data['assignments'][0]['state'] = 'expired'
        self.data['project']['revision'] += 1
        self.assertEqual(validate_transition(before, self.data, AT), [])

    def test_assignment_identity_and_tokens_cannot_be_reused(self):
        before = copy.deepcopy(self.data)
        self.data['project']['revision'] += 1
        self.data['assignments'][0]['workspace_id'] = 'other-worktree'
        self.assertIn('assignment-identity-changed:assignment-demo', validate_transition(before, self.data, AT))
        self.data['assignments'][0]['id'] = 'assignment-replacement'
        self.wp.update(assignment_ref='assignment-replacement', revision=2)
        self.data['checkpoints'][0]['assignment_ref'] = 'assignment-replacement'
        self.assertIn('fencing-token-not-increased:assignment-replacement', validate_transition(before, self.data, AT))

    def test_revision_and_deletion_cannot_silently_overwrite(self):
        before = copy.deepcopy(self.data)
        self.wp['title'] = 'Changed'
        self.assertIn('project-revision', validate_transition(before, self.data, AT))
        self.assertIn('work-package-revision:WP-DEMO', validate_transition(before, self.data, AT))

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'bad.json'
            p.write_text('{"state":"planned","state":"closed"}')
            with self.assertRaises(ValueError):
                load_json(p)

    def test_cli_returns_deterministic_json_and_nonzero_for_invalid(self):
        command = [sys.executable, '-B', str(ROOT / 'scripts/validate_protocol.py')]
        result = subprocess.run(command + [str(ROOT / 'examples/protocol/in-progress.json'), '--at', AT], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['scope'], 'declared_consistency_only')
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'bad.json'
            p.write_text('{}')
            result = subprocess.run(command + [str(p), '--at', AT], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
