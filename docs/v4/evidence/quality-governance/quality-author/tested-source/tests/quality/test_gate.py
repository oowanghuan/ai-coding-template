"""Gate logic tests use synthetic protected-bundle fixtures, not collector evidence.

Actual OS protection and collector execution are independently validated elsewhere.
No fixture report is presented as a real passing engineering run.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from framework.quality.gate import canonical, digest, verify_bundle

ROOT = Path(__file__).resolve().parents[2]


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.trusted = self.base / 'trusted'; self.trusted.mkdir()
        self.scratch = self.base / 'scratch'; self.scratch.mkdir()
        self.subject_root = self.trusted / 'subject'; self.subject_root.mkdir()
        (self.trusted / 'logs').mkdir(); (self.trusted / 'policies').mkdir()
        source = b"print('ok')\n"; (self.subject_root / 'check.py').write_bytes(source)
        manifest = {'check.py': {'sha256': digest(source), 'mode': '100644'}}
        env = {'HOME': str(self.base), 'TMPDIR': str(self.base), 'PATH': '/usr/bin:/bin', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'}
        def git_hash(kind, data):
            return subprocess.check_output(['/usr/bin/git', 'hash-object', '-t', kind, '--stdin'], input=data, env=env).decode().strip()
        blob = git_hash('blob', source)
        tree = git_hash('tree', b'100644 check.py\0' + bytes.fromhex(blob))
        commit = 'tree ' + tree + '\nauthor Synthetic <test@example.invalid> 0 +0000\ncommitter Synthetic <test@example.invalid> 0 +0000\n\nfixture\n'
        subject = {'commit': git_hash('commit', commit.encode()), 'tree': tree, 'manifest_sha256': digest(canonical(manifest))}
        environment = dict(platform='darwin', python='/usr/bin/python3', python_version='3.9.6', sandbox='macos-seatbelt')
        self.plan = dict(format='quality-plan/1', run_id='run-a', wp_id='WP-201', wp_revision=1, kind='code',
            trusted_root=str(self.trusted), scratch_root=str(self.scratch), subject_root=str(self.subject_root), entrypoint='check.py',
            subject=subject, commit_object=commit, manifest=manifest, collector_sha256='a'*64, environment=environment,
            tests=[dict(id='check-a', required=True, input='', expected_exit=0,
                        expected_stdout_sha256=digest(b'ok\n'), timeout_seconds=2, skip_reason=None)])
        self.case = dict(id='check-a', required=True, status='passed', exit_code=0, signal=None, timed_out=False,
            output_limit_exceeded=False, collection_error=None,
            command=['/usr/bin/python3','-I','-B','-S',str(self.subject_root/'check.py')], input_sha256=digest(b''),
            expected_exit=0, expected_stdout_sha256=digest(b'ok\n'),
            stdout=dict(path='logs/check-a.stdout',sha256=digest(b'ok\n'),size=3),
            stderr=dict(path='logs/check-a.stderr',sha256=digest(b''),size=0),
            policy_sha256=digest(b'synthetic-policy\n'),skip_reason=None,
            started_at='2026-11-27T00:00:01Z',finished_at='2026-11-27T00:00:02Z',pid=123,cwd=str(self.scratch/'check-a'))
        self.evidence = dict(format='quality-evidence/1', evidence_id='run-a',wp_id='WP-201',wp_revision=1,kind='code',
            subject=copy.deepcopy(subject),plan_sha256='0'*64,collector_sha256='a'*64,adapter='python-stdio/1',state='complete',
            started_at='2026-11-27T00:00:00Z',finished_at='2026-11-27T00:00:03Z',environment=environment,
            source_unchanged=True,cases=[self.case],counts=dict(passed=1,failed=0,skipped=0,not_run=0))
        (self.trusted/'logs/check-a.stdout').write_bytes(b'ok\n'); (self.trusted/'logs/check-a.stderr').write_bytes(b'')
        (self.trusted/'policies/check-a.sb').write_bytes(b'synthetic-policy\n')
        self.trust_path = self.base/'trust.json'
        self.save_plan()

    def save_evidence(self):
        (self.trusted/'evidence.json').write_bytes(canonical(self.evidence))

    def save_plan(self):
        raw = canonical(self.plan); (self.trusted/'plan.json').write_bytes(raw)
        self.evidence['plan_sha256'] = digest(raw)
        self.trust = dict(format='quality-trust/1',runs={'run-a':dict(root=str(self.trusted),plan_sha256=digest(raw),
            collector_sha256=self.plan['collector_sha256'],wp_id=self.plan['wp_id'],wp_revision=self.plan['wp_revision'],subject=self.plan['subject'])})
        self.trust_path.write_bytes(canonical(self.trust)); self.pin=digest(self.trust_path.read_bytes())
        self.save_evidence()

    def gate(self):
        return verify_bundle(self.trust_path,self.pin,'run-a')

    def check(self,status,reason=None):
        result=self.gate();self.assertEqual(result['status'],status,result)
        if reason:self.assertTrue(any(reason in row for row in result['reasons']),result)
        return result

    def counts(self):
        self.evidence['counts']={status:sum(c['status']==status for c in self.evidence['cases']) for status in ('passed','failed','skipped','not_run')}

    def not_executed(self,status):
        self.case['status']=status
        for key in ('pid','exit_code','signal','stdout','stderr','policy_sha256','started_at','finished_at'):self.case[key]=None
        self.counts()

    def test_valid_fixture_is_deterministic_and_read_only(self):
        before={str(p.relative_to(self.base)):p.read_bytes() for p in self.base.rglob('*') if p.is_file()}
        first=self.check('passed');self.assertEqual(self.gate(),first)
        after={str(p.relative_to(self.base)):p.read_bytes() for p in self.base.rglob('*') if p.is_file()}
        self.assertEqual(before,after);self.assertNotIn('accepted',first);self.assertNotIn('business_validated',first)

    def test_handwritten_report_and_matching_hash_without_registered_receipt(self):
        (self.trusted/'evidence.json').unlink()
        report=canonical(dict(status='passed',tests=99));(self.scratch/'report.json').write_bytes(report)
        (self.scratch/'report.sha256').write_text(digest(report))
        self.check('unverifiable','receipt:')

    def test_forged_trust_plus_own_hash_cannot_replace_operator_pin(self):
        forged=copy.deepcopy(self.trust);forged['runs']['run-a']['root']=str(self.scratch)
        self.trust_path.write_bytes(canonical(forged));(self.scratch/'own-hash').write_text(digest(canonical(forged)))
        self.check('unverifiable','pin-mismatch')

    def test_unregistered_run_and_wrong_pin_fail_closed(self):
        self.assertEqual(verify_bundle(self.trust_path,self.pin,'other')['status'],'unverifiable')
        self.assertEqual(verify_bundle(self.trust_path,'b'*64,'run-a')['status'],'unverifiable')

    def test_declared_trusted_flag_is_not_source_proof(self):
        self.evidence['protected']=True;self.save_evidence();self.check('unverifiable','schema:evidence')

    def test_wrong_receipt_identity_and_subject(self):
        original=copy.deepcopy(self.evidence)
        for field,value in [('subject',dict(self.plan['subject'],tree='f'*40)),('wp_revision',2),('wp_id','WP-OTHER'),('collector_sha256','b'*64),('plan_sha256','b'*64),('evidence_id','other')]:
            with self.subTest(field=field):
                self.evidence=copy.deepcopy(original);self.evidence[field]=value;self.save_evidence();self.check('unverifiable','binding-mismatch')

    def test_plan_replacement_and_matching_self_hash_still_rejected(self):
        self.plan['tests'][0]['required']=False
        data=canonical(self.plan);(self.trusted/'plan.json').write_bytes(data)
        self.evidence['plan_sha256']=digest(data);self.save_evidence();self.check('unverifiable','registered-hash-mismatch')

    def test_wrong_commit_object_rejected(self):
        self.plan['commit_object']+='tampered';self.save_plan();self.check('unverifiable','commit-object')

    def test_manifest_fingerprint_rejected(self):
        self.plan['subject']['manifest_sha256']='b'*64;self.save_plan();self.check('unverifiable','manifest-fingerprint')

    def test_source_changed_or_extra_file_rejected(self):
        (self.subject_root/'extra.py').write_text('extra');self.check('unverifiable','plan:')
        (self.subject_root/'extra.py').unlink();(self.subject_root/'check.py').write_text('changed');self.check('unverifiable','plan:')

    def test_source_mode_change_rejected(self):
        (self.subject_root/'check.py').chmod(0o755);self.check('unverifiable','plan:')

    def test_source_changed_flag_rejected(self):
        self.evidence['source_unchanged']=False;self.save_evidence();self.check('unverifiable','source-changed')

    def test_missing_extra_and_duplicate_case_ids_rejected(self):
        original=copy.deepcopy(self.evidence['cases'])
        for cases in [[],original+original,[dict(original[0],id='extra')]]:
            with self.subTest(cases=len(cases)):
                self.evidence['cases']=cases;self.save_evidence();self.check('unverifiable','check-set-mismatch')

    def test_duplicate_plan_case_ids_rejected(self):
        self.plan['tests']*=2;self.save_plan();self.check('unverifiable','duplicate-check-id')

    def test_changed_input_command_cwd_or_expected_result_rejected(self):
        original=copy.deepcopy(self.case)
        for field,value in [('input_sha256','b'*64),('command',['/bin/sh']),('cwd',str(self.scratch)),('expected_exit',2),('expected_stdout_sha256','b'*64),('required',False)]:
            with self.subTest(field=field):
                self.case=copy.deepcopy(original);self.case[field]=value;self.evidence['cases']=[self.case];self.save_evidence();self.check('unverifiable','plan-binding-mismatch')

    def test_missing_or_changed_log_rejected(self):
        path=self.trusted/'logs/check-a.stdout';path.unlink();self.check('unverifiable','case:check-a:')
        path.write_bytes(b'bad');self.check('unverifiable','fingerprint-mismatch')

    def test_changed_log_and_paired_hash_cannot_fake_expected_result(self):
        data=b'failed';(self.trusted/'logs/check-a.stdout').write_bytes(data)
        self.case['stdout'].update(sha256=digest(data),size=len(data));self.save_evidence()
        self.check('unverifiable','reported-outcome-mismatch')

    def test_log_descriptor_cannot_select_another_path(self):
        self.case['stdout']['path']='../outside';self.save_evidence();self.check('unverifiable','unexpected-stdout-path')

    def test_policy_missing_and_tampered_rejected(self):
        path=self.trusted/'policies/check-a.sb';path.unlink();self.check('unverifiable','case:')
        path.write_bytes(b'changed');self.check('unverifiable','policy-fingerprint-mismatch')

    def test_log_aliases_rejected(self):
        path=self.trusted/'logs/check-a.stdout';saved=self.base/'saved';saved.write_bytes(path.read_bytes());path.unlink();path.symlink_to(saved)
        self.check('unverifiable','case:');path.unlink();os.link(saved,path);self.check('unverifiable','case:')

    def test_trust_hardlink_rejected(self):
        os.link(self.trust_path,self.base/'trust-alias');self.check('unverifiable','trust:')

    def test_required_skip_is_failed(self):
        self.plan['tests'][0]['skip_reason']='maintenance';self.case['skip_reason']='maintenance'
        self.not_executed('skipped');self.save_plan();self.check('failed','required-skip')

    def test_optional_approved_skip_with_actual_check_passes(self):
        expected=dict(self.plan['tests'][0],id='optional',required=False,skip_reason='explicit approved optional skip')
        self.plan['tests'].append(expected)
        row=dict(self.case,id='optional',required=False,status='skipped',skip_reason=expected['skip_reason'],cwd=str(self.scratch/'optional'))
        for key in ('pid','exit_code','signal','stdout','stderr','policy_sha256','started_at','finished_at'):row[key]=None
        self.evidence['cases'].append(row);self.counts();self.save_plan();self.check('passed')

    def test_unapproved_skip_rejected(self):
        self.plan['tests'][0]['required']=False;self.case['required']=False;self.not_executed('skipped');self.save_plan();self.check('unverifiable','unapproved-skip')

    def test_not_run_is_failed_even_if_optional(self):
        self.plan['tests'][0]['required']=False;self.case['required']=False;self.not_executed('not_run');self.save_plan();self.check('failed','not-run')

    def test_empty_code_and_document_are_not_passed(self):
        for kind in ['code','document']:
            with self.subTest(kind=kind):
                self.plan['kind']=kind;self.plan['tests']=[];self.evidence['kind']=kind;self.evidence['cases']=[];self.counts();self.save_plan();self.check('failed','no-executed-checks')

    def test_actual_document_check_and_expected_nonzero_exit_can_pass(self):
        self.plan['kind']='document';self.evidence['kind']='document';self.plan['tests'][0]['expected_exit']=2
        self.case.update(expected_exit=2,exit_code=2);self.save_plan();self.check('passed')

    def test_genuine_failure_is_failed_without_baseline_waiver(self):
        self.case.update(status='failed',exit_code=1);self.counts();self.save_evidence();self.check('failed','observed-check-failed')

    def test_failed_exit_reported_passed_is_unverifiable(self):
        self.case['exit_code']=1;self.save_evidence();self.check('unverifiable','reported-outcome-mismatch')

    def test_timeout_signal_and_output_limit_never_pass(self):
        original=copy.deepcopy(self.case)
        for change in [dict(timed_out=True,exit_code=-9,signal=9),dict(exit_code=-15,signal=15),dict(output_limit_exceeded=True)]:
            with self.subTest(change=change):
                self.case=copy.deepcopy(original);self.case.update(status='failed',**change);self.evidence['cases']=[self.case];self.counts();self.save_evidence();self.check('failed')

    def test_collection_error_and_unknown_are_unverifiable(self):
        self.case.update(status='failed',collection_error='capture failed');self.counts();self.save_evidence();self.check('unverifiable','collection-error')
        self.case.update(status='passed',collection_error=None);self.counts();self.evidence['state']='unknown';self.save_evidence();self.check('unverifiable','unknown-outcome')

    def test_environment_and_signal_binding_rejected(self):
        self.case.update(exit_code=0,signal=9);self.save_evidence();self.check('unverifiable','signal-exit')
        self.case['signal']=None;self.evidence['environment']=dict(self.plan['environment'],python_version='other');self.save_evidence();self.check('unverifiable','binding-mismatch')

    def test_missing_pid_and_invalid_time_rejected(self):
        self.case['pid']=None;self.save_evidence();self.check('unverifiable','missing-execution-identity')
        self.case['pid']=123;self.case['finished_at']='2026-11-27T00:00:09Z';self.save_evidence();self.check('unverifiable','time-order')

    def test_counts_and_boolean_numbers_rejected(self):
        self.evidence['counts']['passed']=0;self.save_evidence();self.check('unverifiable','counts-mismatch')
        self.evidence['counts']['passed']=True;self.save_evidence();self.check('unverifiable','schema:evidence')

    def test_duplicate_json_key_and_nonfinite_rejected(self):
        path=self.trusted/'evidence.json';path.write_text('{"format":"quality-evidence/1","format":"quality-evidence/1"}')
        self.check('unverifiable','receipt:')
        path.write_text('{"value":NaN}');self.check('unverifiable','receipt:')

    def test_oversized_log_is_unverifiable(self):
        (self.trusted/'logs/check-a.stdout').write_bytes(b'x'*(1048576+1));self.check('unverifiable','case:')

    def test_float_in_integer_field_is_rejected(self):
        self.case['pid']=123.0;self.save_evidence();self.check('unverifiable','schema:')

    def test_ancestor_symlink_is_rejected(self):
        logs=self.trusted/'logs';moved=self.trusted/'moved-logs'
        logs.rename(moved);logs.symlink_to(moved,target_is_directory=True)
        self.check('unverifiable','case:')

    def test_source_requires_fixed_subject_path(self):
        new=self.trusted/'alternative';self.subject_root.rename(new)
        self.plan['subject_root']=str(new);self.save_plan()
        self.check('unverifiable','subject-not-fixed-path')

    def test_group_execute_bit_does_not_change_git_mode(self):
        (self.subject_root/'check.py').chmod(0o654)
        self.check('passed')

    def test_cli_uses_registered_bundle_and_status_exit_codes(self):
        args=[sys.executable,'-B','-S',str(ROOT/'scripts/v4_quality.py'),'verify','--trust',str(self.trust_path),'--trust-sha256',self.pin,'--run-id','run-a']
        for status,expected_code in [('passed',0),('failed',1),('unverifiable',2)]:
            if status=='failed':self.case.update(status='failed',exit_code=1);self.counts();self.save_evidence()
            if status=='unverifiable':(self.trusted/'evidence.json').unlink()
            out=subprocess.run(args,capture_output=True,timeout=30)
            self.assertEqual(out.returncode,expected_code,out.stderr);self.assertEqual(json.loads(out.stdout)['status'],status)


if __name__=='__main__':unittest.main()
