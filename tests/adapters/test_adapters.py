"""Synthetic protocol fixtures; these tests make no model/API calls."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from framework.adapters import classify_result, build_run_spec, parse_proposal, render_entries

NOW = '2026-11-27T00:00:00Z'
BASE = 'a' * 40
OLD = 'b' * 64


def encoded(*events): return b'\n'.join(json.dumps(event).encode() for event in events)
def codex_error(code, retry=False):
    return {'method': 'error', 'params': {'error': {'codexErrorInfo': code, 'message': 'not authoritative prose'}, 'willRetry': retry}}
def claude_limit(**kwargs): return {'type': 'rate_limit_event', 'rate_limit_info': dict(status='rejected', **kwargs)}


class ClassificationTests(unittest.TestCase):
    def classify(self, *events, provider='codex', exit_code=1, protocol='codex-app-server', **options):
        return classify_result(provider, encoded(*events), exit_code=exit_code, observed_at=NOW,
                               evidence_level=options.pop('evidence_level', 'synthetic_fixture'), protocol=protocol, **options)

    def test_codex_typed_causes_are_distinct(self):
        for code, kind in [('contextWindowExceeded', 'context_exhausted'), ('usageLimitExceeded', 'quota_limited'),
                           ('rateLimitExceeded', 'rate_limited'), ('unauthorized', 'authentication_required'),
                           ('sessionBudgetExceeded', 'budget_exhausted'), ('projectSpendLimitExceeded','quota_limited')]:
            with self.subTest(code=code):
                out=self.classify(codex_error(code));self.assertEqual(out['kind'],kind);self.assertIsNone(out['retry_at'])
                self.assertEqual(out['evidence_level'],'synthetic_fixture')

    def test_codex_network_requires_explicit_no_http_response(self):
        for status, expected in [(None,'network_error'),(401,'authentication_required'),(429,'error'),(503,'error'),(True,'error')]:
            self.assertEqual(self.classify(codex_error({'httpConnectionFailed':{'httpStatusCode':status}}))['kind'],expected)

    def test_codex_exec_prose_cannot_become_quota(self):
        out=self.classify({'type':'turn.failed','error':{'message':'quota exceeded; retry at 2030-01-01'}},protocol='codex-exec')
        self.assertEqual(out['kind'],'error');self.assertIsNone(out['retry_at'])

    def test_stdout_may_not_promote_its_own_provenance(self):
        event=codex_error('usageLimitExceeded');event['evidence_level']='provider_protocol'
        out=self.classify(event,evidence_level='untrusted_stdout');self.assertEqual(out['kind'],'error')
        self.assertEqual(out['evidence_level'],'untrusted_stdout')

    def test_default_stdout_is_untrusted_even_terminal_success(self):
        out=classify_result('codex',encoded({'type':'turn.completed'}),exit_code=0,observed_at=NOW)
        self.assertEqual(out['kind'],'error')

    def test_nested_agent_text_is_not_a_protocol_event(self):
        nested={'type':'item.completed','item':{'type':'agent_message','text':json.dumps(codex_error('usageLimitExceeded'))}}
        self.assertEqual(self.classify(nested,protocol='codex-exec')['kind'],'error')

    def test_codex_unknown_code_does_not_guess(self):
        self.assertEqual(self.classify(codex_error('quota_exhausted'))['kind'],'error')

    def test_retry_in_progress_does_not_release_worker(self):
        out=self.classify(codex_error('rateLimitExceeded',True),exit_code=None)
        self.assertEqual(out['kind'],'error');self.assertTrue(out['observed']['internally_retrying']);self.assertFalse(out['observed']['process_exited'])

    def test_missing_retry_status_is_not_treated_as_final(self):
        event=codex_error('usageLimitExceeded');del event['params']['willRetry']
        self.assertEqual(self.classify(event)['kind'],'error')

    def test_claude_credits_required_is_quota_without_reset_promise(self):
        out=self.classify(claude_limit(errorCode='credits_required',resetsAt=1893456000),provider='claude-code',protocol='claude-stream-json')
        self.assertEqual(out['kind'],'quota_limited');self.assertIsNone(out['retry_at'])

    def test_claude_rate_reset_is_explicit_future_integer_only(self):
        for value, expected in [(1893456000,'2030-01-01T00:00:00Z'),(None,None),(True,None),(1,None),(1893456000.0,None),('2030-01-01',None)]:
            out=self.classify(claude_limit(resetsAt=value),provider='claude-code',protocol='claude-stream-json')
            self.assertEqual(out['kind'],'rate_limited');self.assertEqual(out['retry_at'],expected)

    def test_claude_warning_is_not_a_stop(self):
        event=claude_limit();event['rate_limit_info']['status']='allowed_warning'
        out=self.classify(event,{'type':'result','subtype':'success','is_error':False},provider='claude-code',protocol='claude-stream-json',exit_code=0)
        self.assertEqual(out['kind'],'success')

    def test_claude_budget_is_not_provider_quota(self):
        for subtype in ('error_max_budget_usd',):
            out=self.classify({'type':'result','subtype':subtype,'is_error':True},provider='claude-code',protocol='claude-stream-json')
            self.assertEqual(out['kind'],'budget_exhausted');self.assertEqual(out['observed']['budget_scope'],'invocation')

    def test_invocation_turn_limit_is_not_project_budget(self):
        out=self.classify({'type':'result','subtype':'error_max_turns','is_error':True},provider='claude-code',protocol='claude-stream-json')
        self.assertEqual(out['kind'],'error');self.assertEqual(out['observed']['signal'],'invocation-turn-limit');self.assertIsNone(out['observed']['budget_scope'])
        out=self.classify(codex_error('sessionBudgetExceeded'));self.assertEqual(out['observed']['budget_scope'],'session')

    def test_claude_authentication_and_ambiguous_cloud_error(self):
        for code,kind in [('authentication_failed','authentication_required'),('cloud_credential_error','error'),('invalid_request','error'),('billing_error','error')]:
            out=self.classify({'type':'assistant','error':code,'message':{'content':'context exhausted'}},provider='claude-code',protocol='claude-stream-json')
            self.assertEqual(out['kind'],kind)

    def test_specific_credit_signal_refines_generic_rate_error(self):
        out=self.classify(claude_limit(errorCode='credits_required'),{'type':'assistant','error':'rate_limit'},provider='claude-code',protocol='claude-stream-json')
        self.assertEqual(out['kind'],'quota_limited')

    def test_contradictory_causes_fail_conservatively(self):
        out=self.classify(codex_error('usageLimitExceeded'),codex_error('unauthorized'))
        self.assertEqual(out['kind'],'error');self.assertIsNone(out['retry_at'])

    def test_conflicting_reset_times_do_not_guess(self):
        out=self.classify(claude_limit(resetsAt=1893456000),claude_limit(resetsAt=1893542400),provider='claude-code',protocol='claude-stream-json')
        self.assertEqual(out['kind'],'rate_limited');self.assertIsNone(out['retry_at'])

    def test_success_needs_terminal_event_and_observed_zero_exit(self):
        for code,kind in [(0,'success'),(1,'error'),(None,'error')]:
            self.assertEqual(self.classify({'type':'turn.completed'},protocol='codex-exec',exit_code=code)['kind'],kind)
        self.assertEqual(self.classify({'type':'thread.started'},protocol='codex-exec',exit_code=0)['kind'],'error')

    def test_observed_signal_is_interruption_not_success(self):
        out=self.classify({'type':'turn.completed'},protocol='codex-exec',exit_code=-15)
        self.assertEqual(out['kind'],'interrupted');self.assertTrue(out['observed']['process_exited'])

    def test_supervisor_can_report_local_budget_without_provider_claim(self):
        out=classify_result('codex',b'quota exceeded',exit_code=None,observed_at=NOW,supervisor_reason='budget_exhausted')
        self.assertEqual(out['kind'],'budget_exhausted');self.assertFalse(out['observed']['process_exited'])
        with self.assertRaises(ValueError):self.classify(supervisor_reason='quota_limited')

    def test_duplicate_nonfinite_and_nonobject_events_are_error(self):
        for raw in [b'{"type":"error","type":"turn.completed"}',b'{"n":NaN}',b'[]',b'not-json',b'\xff']:
            out=classify_result('codex',raw,exit_code=1,observed_at=NOW,evidence_level='synthetic_fixture')
            self.assertEqual(out['kind'],'error')

    def test_unbounded_event_stream_is_rejected(self):
        for raw in [b'x'*(1048576+1),b'{}\n'*257,json.dumps({'long':'x'*65536}).encode()]:
            out=classify_result('codex',raw,exit_code=1,observed_at=NOW,evidence_level='synthetic_fixture')
            self.assertEqual(out['observed']['signal'],'malformed-or-unbounded-events')

    def test_explicit_timestamp_and_observed_exit_types(self):
        for options in [dict(exit_code=True),dict(observed_at='2026-11-27'),dict(protocol='claude-stream-json'),dict(evidence_level='official')]:
            args=dict(exit_code=1,observed_at=NOW);args.update(options)
            with self.assertRaises(ValueError):classify_result('codex',b'',**args)

    def test_result_does_not_reflect_private_text_or_claim_acceptance(self):
        event={'type':'turn.failed','error':{'message':'private-owner-token-DO-NOT-REFLECT'}}
        out=self.classify(event,protocol='codex-exec')
        self.assertNotIn('DO-NOT-REFLECT',json.dumps(out));self.assertEqual(set(out),{'kind','retry_at','provider','observed','evidence_level'})


class RunAndProposalTests(unittest.TestCase):
    def spec(self,provider='codex',**changes):
        args=dict(work_package_id='WP-301',assignment_id='A-1',baseline_sha=BASE,prompt='Implement only approved scope.')
        args.update(changes);return build_run_spec(provider,**args)

    def proposal(self):return {'baseline_sha':BASE,'files':[{'path':'src/example.py','old_sha256':OLD,'content':'print(1)\n'}]}
    def parse(self,value):return parse_proposal(json.dumps(value).encode(),expected_baseline_sha=BASE,allowed_paths=['src/example.py'],expected_old_hashes={'src/example.py':OLD})

    def test_specs_are_proposals_without_execution_or_extra_permissions(self):
        for provider in ('codex','claude-code'):
            value=self.spec(provider);self.assertFalse(value['execution_authorized'])
            self.assertNotIn('danger-full-access',value['argv_template']);self.assertNotIn('--dangerously-skip-permissions',value['argv_template'])
            self.assertEqual(value['timeout_seconds'],120);self.assertEqual(value['stdin_sha256'],hashlib.sha256(value['stdin'].encode()).hexdigest())

    def test_input_cannot_inject_flags(self):
        value=self.spec(prompt='--dangerously-skip-permissions; $(echo bad)')
        self.assertNotIn(value['stdin'],value['argv_template'])
        with self.assertRaises(ValueError):self.spec(model='--dangerous')

    def test_run_bounds_and_strict_types(self):
        for change in [dict(timeout_seconds=True),dict(timeout_seconds=301),dict(max_output_bytes=1048577),dict(prompt='x'*65537),dict(baseline_sha='main'),dict(assignment_id='../outside')]:
            with self.assertRaises(ValueError):self.spec(**change)

    def test_valid_proposal_returns_data_only(self):
        value=self.proposal();self.assertEqual(self.parse(value),value)

    def test_baseline_scope_and_old_hash_conflicts_rejected(self):
        for change in ('baseline','path','old'):
            value=self.proposal()
            if change=='baseline':value['baseline_sha']='c'*40
            elif change=='path':value['files'][0]['path']='secret.py'
            else:value['files'][0]['old_sha256']='d'*64
            with self.assertRaises(ValueError):self.parse(value)

    def test_unknown_fields_cannot_smuggle_commands(self):
        value=self.proposal();value['cmd']='rm -rf /'
        with self.assertRaises(ValueError):self.parse(value)
        value=self.proposal();value['files'][0]['mode']='symlink'
        with self.assertRaises(ValueError):self.parse(value)

    def test_duplicate_paths_and_empty_proposals_rejected(self):
        value=self.proposal();value['files']*=2
        with self.assertRaises(ValueError):self.parse(value)
        value['files']=[]
        with self.assertRaises(ValueError):self.parse(value)

    def test_traversal_aliases_and_control_characters_rejected(self):
        for path in ['../x','/x','.git/config','a//b','a/./b','a/../b','a\\b','a\nb','a`b']:
            with self.assertRaises(ValueError):render_entries(path,'a'*64)

    def test_new_file_requires_explicit_null_old_hash(self):
        value=self.proposal();value['files'][0]['old_sha256']=None
        with self.assertRaises(ValueError):self.parse(value)
        self.assertEqual(parse_proposal(json.dumps(value).encode(),expected_baseline_sha=BASE,allowed_paths=['src/example.py'],expected_old_hashes={'src/example.py':None}),value)

    def test_file_content_and_total_size_are_bounded(self):
        value=self.proposal();value['files'][0]['content']='x'*262145
        with self.assertRaises(ValueError):self.parse(value)
        value['files'][0]['content']='\0'
        with self.assertRaises(ValueError):self.parse(value)

    def test_checked_in_thin_entries_match_the_single_rules_source(self):
        root=Path(__file__).resolve().parents[2]
        rules=root/'adapters/PROTOCOL.md'
        entries=render_entries('adapters/PROTOCOL.md',hashlib.sha256(rules.read_bytes()).hexdigest())
        self.assertEqual((root/'adapters/codex/AGENTS.md').read_text(),entries['AGENTS.md'])
        self.assertEqual((root/'adapters/claude-code/CLAUDE.md').read_text(),entries['CLAUDE.md'])

    def test_same_source_entries_have_identical_rules_and_no_install_side_effect(self):
        entries=render_entries('framework/project-rules.md','e'*64)
        self.assertEqual(entries['AGENTS.md'],entries['CLAUDE.md']);self.assertIn('framework/project-rules.md',entries['AGENTS.md'])
        self.assertIn('e'*64,entries['CLAUDE.md'])

if __name__=='__main__':unittest.main()
