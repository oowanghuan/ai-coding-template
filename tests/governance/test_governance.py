"""Synthetic identity/Gate fixtures test governance logic, NOT real engineering acceptance."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

from framework.governance.core import (ZERO, append_proposal, canonical, chain_errors,
    derive, evaluate_loaded, fingerprint, impact, schema_errors)
from framework.governance.evaluate import load, read_bytes, verify_bundle

AT = '2026-11-27T20:00:00Z'


def subject(tree='1'*40, message='reviewed', manifest=None):
    body = 'tree '+tree+'\nauthor Fixture <fixture@example.invalid> 0 +0000\ncommitter Fixture <fixture@example.invalid> 0 +0000\n\n'+message+'\n'
    data = body.encode(); commit = hashlib.sha1(b'commit '+str(len(data)).encode()+b'\0'+data).hexdigest()
    return {'commit':commit,'tree':tree,'manifest_sha256':fingerprint(manifest or {'main.py':{'sha256':'2'*64,'mode':'100644'}})}, body


class Fixture:
    def __init__(self):
        self.subject, self.body = subject()
        work = dict(revision=1,risk='high',author_principals=['author'],author_contexts=['author-session'],
                    author_groups=['author-group'],required_paths=['main.py'],target_base_sha='3'*40,
                    allow_same_tree_commit=True,separate_acceptor=True,required_contracts=['API'],mechanical_changes={})
        self.trust = dict(format='governance-trust/1',trusted_root='/T',candidate_root='/C',project_id='demo',
            ledger=dict(path='/T/ledger.json',sha256='0'*64,sequence=0,head_sha256=ZERO),sources={},
            work_packages={'WP-203':work},contracts={'API':{'depends_on':[]}},graph_complete=True,
            quality={'trust_path':'/T/quality.json','trust_sha256':'4'*64})
        self.ledger = dict(format='governance-ledger/1',project_id='demo',entries=[]); self.records={}
        self.gate = dict(status='passed',gate_id='5'*64,evidence_id='run-1',evidence_sha256='6'*64,
                         subject=self.subject,wp_id='WP-203',wp_revision=1)
        self.quality = {'review':{'gate':self.gate,'plan':{'manifest':{'main.py':{'sha256':'2'*64,'mode':'100644'}}}}}
        self.add('contract',dict(id='API',path='api.md',version='1',sha256='7'*64,depends_on=[]),'contract_owner')
        self.review = dict(id='R1',wp_id='WP-203',wp_revision=1,subject=self.subject,commit_object=self.body,
                          target_base_sha='3'*40,paths=['main.py'],contract_refs=[dict(id='API',version='1',sha256='7'*64)],
                          quality_run_id='run-1',conclusion='approved',summary='Synthetic review only.',deviation_refs=[],policy_sha256=fingerprint(work))
        self.add('review', self.review, 'reviewer')
        self.add('signoff',dict(id='S1',review_id='R1',gate_id='5'*64,evidence_sha256='6'*64),'acceptor')
        self.candidate = dict(format='governance-candidate/1',wp_id='WP-203',wp_revision=1,subject=self.subject,
                              commit_object=self.body,target_base_sha='3'*40,paths=['main.py'],quality_run_id=None)

    def add(self, kind, payload, role):
        key='src-'+str(len(self.records)+1)
        record=dict(format='governance-record/1',kind=kind,issued_at='2026-11-27T19:00:00Z',payload=payload)
        digest=fingerprint(record); self.records[key]=record
        self.trust['sources'][key]=dict(path='/T/'+key+'.json',sha256=digest,principal=role,role=role,
                                       context_id=role+'-session',independence_group=role+'-group')
        proposal=append_proposal(self.ledger,key,digest);self.ledger=proposal['proposal']
        self.trust['ledger'].update(proposal['tip']);self.trust['ledger']['sha256']=fingerprint(self.ledger)
        return key

    def run(self): return evaluate_loaded(self.trust,self.ledger,self.records,'S1',self.candidate,AT,self.quality)
    def deviation(self, **updates):
        value=dict(id='D1',revision=1,wp_id='WP-203',wp_revision=1,subject_commit=self.subject['commit'],
                   scope_paths=['main.py'],reason='Synthetic known issue',expires_at='2026-12-01T00:00:00Z',
                   status='open',closure=None,baseline=None)
        value.update(updates); self.review['deviation_refs']=['D1']; self.add('deviation',value,'owner');return value


class GovernanceLogic(unittest.TestCase):
    def setUp(self): self.f=Fixture()
    def rejected(self, reason):
        result=self.f.run();self.assertNotEqual(result['status'],'effective');self.assertIn(reason,result['reasons'])
    def test_schema_valid_fixture_and_positive_synthetic_decision(self):
        for value,kind in [(self.f.trust,'trust'),(self.f.ledger,'ledger'),(self.f.candidate,'candidate')]+[(r,'record') for r in self.f.records.values()]:
            self.assertEqual(schema_errors(value,kind),[])
        self.assertEqual(self.f.run()['status'],'effective')
    def test_high_risk_author_cannot_review_despite_model_label(self):
        self.f.trust['sources']['src-2']['principal']='author';self.rejected('high-risk-reviewer-not-independent')
    def test_same_author_group_is_not_independent(self):
        self.f.trust['sources']['src-3']['independence_group']='author-group';self.rejected('high-risk-acceptor-not-independent')
    def test_wrong_role_source_rejected(self):
        self.f.trust['sources']['src-2']['role']='owner';self.rejected('source-role-not-authorized:src-2')
    def test_wrong_sha_and_tree(self):
        self.f.candidate['subject']=dict(self.f.subject,commit='8'*40);self.rejected('commit-object-sha-mismatch')
        self.f.candidate['subject']=dict(self.f.subject,tree='9'*40);self.rejected('commit-object-tree-mismatch')
    def test_scope_is_explicit_for_each_decision_status(self):
        for gate_status,decision_status in [('passed','effective'),('failed','rejected'),('unverifiable','unverifiable')]:
            with self.subTest(status=decision_status):
                self.f.gate['status']=gate_status
                result=self.f.run()
                self.assertEqual(result['status'],decision_status)
                self.assertEqual(result['verification_scope'],'locked_baseline')
                self.assertEqual(result['current_target_status'],'not_observed')
    def test_actual_git_ref_advance_does_not_turn_snapshot_into_live_observation(self):
        # Real local Git movement; review and Gate identities remain synthetic.
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve()
            environment=dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
                GIT_AUTHOR_NAME='Synthetic Fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid',
                GIT_COMMITTER_NAME='Synthetic Fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid')
            def git(*args):
                process=subprocess.run(['/usr/bin/git','-c','core.hooksPath=/dev/null','-c','commit.gpgsign=false',*args],
                    cwd=root,env=environment,capture_output=True,text=True)
                self.assertEqual(process.returncode,0,process.stderr)
                return process.stdout.strip()
            git('init','-q')
            (root/'target.txt').write_text('baseline\n');git('add','target.txt');git('commit','-q','-m','baseline')
            baseline=git('rev-parse','HEAD')
            work=self.f.trust['work_packages']['WP-203'];work['target_base_sha']=baseline
            self.f.review['target_base_sha']=baseline;self.f.review['policy_sha256']=fingerprint(work)
            self.f.candidate['target_base_sha']=baseline
            before=self.f.run()
            (root/'target.txt').write_text('advanced\n');git('add','target.txt');git('commit','-q','-m','advance target')
            self.assertNotEqual(git('rev-parse','HEAD'),baseline)
            after=self.f.run()
            self.assertEqual(before,after)
            self.assertEqual(after['status'],'effective')
            self.assertEqual(after['target_base_sha'],baseline)
            self.assertEqual(after['verification_scope'],'locked_baseline')
            self.assertEqual(after['current_target_status'],'not_observed')
    def test_target_base_recheck(self):
        self.f.candidate['target_base_sha']='9'*40;self.rejected('target-base-changed-recheck-required')
    def test_same_tree_new_commit_exact_binding(self):
        self.f.candidate['subject'],self.f.candidate['commit_object']=subject(message='new metadata')
        result=self.f.run();self.assertEqual(result['status'],'effective');self.assertEqual(result['equivalence'],'same_tree_commit')
        self.assertNotEqual(result['reviewed_subject']['commit'],result['candidate_subject']['commit'])
    def test_same_tree_needs_prepinned_policy(self):
        self.f.candidate['subject'],self.f.candidate['commit_object']=subject(message='new metadata')
        self.f.trust['work_packages']['WP-203']['allow_same_tree_commit']=False
        self.rejected('different-commit-not-preauthorized');self.rejected('review-policy-fingerprint-mismatch')
    def test_contract_change_then_restore_does_not_resurrect(self):
        old=copy.deepcopy(self.f.records['src-1']['payload'])
        self.f.add('contract',dict(old,version='2',sha256='9'*64),'contract_owner')
        self.f.add('contract',old,'contract_owner');self.rejected('signoff-invalidated-by-history')
    def test_review_before_change_cannot_be_signed_after_restore(self):
        self.f.ledger['entries'].pop();self.f.records.pop('src-3');self.f.trust['sources'].pop('src-3')
        old=copy.deepcopy(self.f.records['src-1']['payload'])
        self.f.add('contract',dict(old,version='2',sha256='9'*64),'contract_owner');self.f.add('contract',old,'contract_owner')
        self.f.add('signoff',dict(id='S1',review_id='R1',gate_id='5'*64,evidence_sha256='6'*64),'acceptor')
        self.rejected('signoff-invalidated-by-history')
    def test_revoke_survives_content_restore_and_old_history_fails_tip(self):
        old=copy.deepcopy(self.f.ledger);self.f.add('revoke',dict(signoff_id='S1',reason='withdrawn'),'owner')
        self.rejected('signoff-revoked');self.assertIn('protected-history-tip-mismatch',chain_errors(old,self.f.trust['ledger']))
    def test_missing_impact_relation(self):
        self.f.trust['contracts']['API']['depends_on']=['missing'];self.rejected('impact-relation-missing-or-changed:API')
    def test_transitive_impact(self):
        graph={'A':{'depends_on':[]},'B':{'depends_on':['A']},'C':{'depends_on':['B']}}
        self.assertEqual(impact(graph,['A'])['affected'],['A','B','C'])
    def test_required_contract_binding(self):
        self.f.trust['work_packages']['WP-203']['required_contracts']=['missing'];self.rejected('required-contract-bindings-missing')
    def test_expired_deviation(self):
        self.f.deviation(expires_at=AT);self.rejected('expired-deviation:D1')
    def test_plan_does_not_close_and_failed_gate_stays_failed(self):
        self.f.deviation(status='remediation_planned');self.f.gate['status']='failed'
        self.rejected('quality-gate-not-passed');self.assertEqual(self.f.run()['active_deviations'],['D1'])
    def test_closure_requires_exact_passed_gate(self):
        closure=dict(quality_run_id='closure-1',gate_id='a'*64,subject=self.f.subject,scope_paths=['main.py'])
        self.f.deviation(status='closed',closure=closure)
        self.rejected('deviation-closure-gate-not-passed:D1')
        self.f.quality['closures']={'D1':{'gate':dict(self.f.gate,gate_id='a'*64,evidence_id='closure-1')}}
        self.assertEqual(self.f.run()['status'],'effective')
        closure['scope_paths']=['other.py'];self.rejected('deviation-closure-binding-mismatch:D1')
    def test_exact_mechanical_delta_requires_candidate_gate_and_no_other_change(self):
        old=self.f.quality['review']['plan']['manifest'];new={'main.py':{'sha256':'a'*64,'mode':'100644'}}
        work=self.f.trust['work_packages']['WP-203'];work['mechanical_changes']={'main.py':{'old':old['main.py'],'new':new['main.py']}}
        self.f.review['policy_sha256']=fingerprint(work)
        self.f.candidate['subject'],self.f.candidate['commit_object']=subject(tree='a'*40,manifest=new)
        self.f.candidate['quality_run_id']='mechanical-1'
        self.rejected('candidate-quality-gate-not-passed')
        self.f.quality['candidate']={'gate':dict(self.f.gate,subject=self.f.candidate['subject'],evidence_id='mechanical-1'), 'plan':{'manifest':new}}
        self.assertEqual(self.f.run()['status'],'effective')
        work['mechanical_changes']['main.py']['new']={'sha256':'b'*64,'mode':'100644'}
        self.f.review['policy_sha256']=fingerprint(work);self.rejected('mechanical-transform-outside-exact-policy')
    def test_baseline_known_vs_new_failures_not_a_waiver(self):
        deviation=self.f.deviation(baseline={'quality_run_id':'baseline-1','subject':self.f.subject})
        manifest={'main.py':{'sha256':'2'*64,'mode':'100644'}}
        plan={'entrypoint':'main.py','manifest':manifest,'tests':[{'id':'known'},{'id':'new'}]}
        failed=lambda ident,digest:dict(id=ident,status='failed',exit_code=1,signal=None,timed_out=False,
            stdout={'sha256':digest,'size':10},stderr=None)
        current={'environment':{'sandbox':'synthetic'},'cases':[failed('known','a'*64),failed('new','b'*64)]}
        baseline={'environment':{'sandbox':'synthetic'},'cases':[failed('known','a'*64)]}
        self.f.gate['status']='failed';self.f.quality['review'].update(plan=plan,evidence=current)
        self.f.quality['baselines']={'D1':{'gate':dict(self.f.gate,evidence_id='baseline-1'),'plan':plan,'evidence':baseline}}
        result=self.f.run();self.assertEqual(result['status'],'rejected')
        self.assertEqual(result['failure_analysis'][0]['known_failures'],['known'])
        self.assertEqual(result['failure_analysis'][0]['new_failures'],['new'])
        current['cases'][0]['stdout']['sha256']='c'*64
        self.assertEqual(self.f.run()['failure_analysis'][0]['known_failures'],[])
    def test_integer_json_type_is_strict(self):
        self.f.candidate['wp_revision']=1.0
        self.assertTrue(schema_errors(self.f.candidate,'candidate'))
    def test_empty_review_or_fake_actor_schema(self):
        self.f.review['summary']=' ';self.rejected('review-not-approved')
        self.f.records['src-2']['actor']='owner';self.assertTrue(schema_errors(self.f.records['src-2'],'record'))


class ProtectedInputs(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve()
        self.t=self.root/'trusted';self.c=self.root/'candidate';self.t.mkdir();self.c.mkdir();self.f=Fixture()
        self.f.trust.update(trusted_root=str(self.t),candidate_root=str(self.c))
        self.f.trust['quality']['trust_path']=str(self.t/'quality.json')
        for key,binding in self.f.trust['sources'].items():
            binding['path']=str(self.t/(key+'.json'));Path(binding['path']).write_bytes(canonical(self.f.records[key]))
        self.f.trust['ledger']['path']=str(self.t/'ledger.json');(self.t/'ledger.json').write_bytes(canonical(self.f.ledger))
        self.path=self.t/'trust.json';self.path.write_bytes(canonical(self.f.trust));self.pin=fingerprint(self.f.trust)
        self.cp=self.c/'candidate.json';self.cp.write_bytes(canonical(self.f.candidate))
    def test_valid_load_and_forged_source_rejected(self):
        self.assertEqual(load(self.path,self.pin,AT)[0],self.f.trust)
        (self.t/'src-2.json').write_text('{}')
        self.assertEqual(verify_bundle(self.path,self.pin,'S1',self.cp,AT)['status'],'unverifiable')
    def test_protected_verifier_scope_survives_success_rejection_and_load_error(self):
        # Only this test substitutes the Gate fixture; the public CLI has no such input.
        with patch('framework.governance.evaluate.quality_details', return_value=self.f.quality['review']):
            for gate_status,expected in [('passed','effective'),('failed','rejected'),('unverifiable','unverifiable')]:
                self.f.gate['status']=gate_status
                result=verify_bundle(self.path,self.pin,'S1',self.cp,AT)
                self.assertEqual(result['status'],expected)
                self.assertEqual(result['verification_scope'],'locked_baseline')
                self.assertEqual(result['current_target_status'],'not_observed')
                body={key:value for key,value in result.items() if key!='decision_id'}
                self.assertEqual(result['decision_id'],fingerprint(body))
        result=verify_bundle(self.path,'a'*64,'S1',self.cp,AT)
        self.assertEqual(result['status'],'unverifiable')
        self.assertEqual(result['verification_scope'],'locked_baseline')
        self.assertEqual(result['current_target_status'],'not_observed')
    def test_cli_help_and_unverifiable_output_expose_snapshot_scope(self):
        cli=Path(__file__).resolve().parents[2]/'scripts/v4_governance.py'
        for args in [[],['verify']]:
            process=subprocess.run([sys.executable,'-B','-S',str(cli),*args,'--help'],capture_output=True,text=True)
            self.assertEqual(process.returncode,0,process.stderr)
            for text in ('locked_baseline','not_observed','live target ref'):
                self.assertIn(text,process.stdout)
        process=subprocess.run([sys.executable,'-B','-S',str(cli),'verify','--trust',str(self.path),
            '--trust-sha256','a'*64,'--at',AT,'--signoff','S1','--candidate',str(self.cp)],capture_output=True,text=True)
        self.assertEqual(process.returncode,3,process.stderr)
        result=json.loads(process.stdout)
        self.assertEqual(result['verification_scope'],'locked_baseline')
        self.assertEqual(result['current_target_status'],'not_observed')
    def test_wrong_trust_pin(self):
        self.assertEqual(verify_bundle(self.path,'a'*64,'S1',self.cp,AT)['status'],'unverifiable')
    def test_symlink_ancestor_and_hardlink_rejected(self):
        alias=self.root/'alias';alias.symlink_to(self.t,target_is_directory=True)
        with self.assertRaises(OSError):read_bytes(alias/'trust.json')
        hard=self.c/'hard';os.link(self.path,hard)
        with self.assertRaises(ValueError):read_bytes(self.path)
    def test_duplicate_json_key(self):
        self.cp.write_text('{"format":"x","format":"y"}')
        self.assertEqual(verify_bundle(self.path,self.pin,'S1',self.cp,AT)['status'],'unverifiable')
    def test_external_passed_json_not_consumed(self):
        self.cp.write_text(json.dumps(dict(self.f.candidate,gate={'status':'passed'})))
        self.assertEqual(verify_bundle(self.path,self.pin,'S1',self.cp,AT)['status'],'unverifiable')
    def test_cli_inspect_export_impact_proposal_and_no_authority_write(self):
        cli=Path(__file__).resolve().parents[2]/'scripts/v4_governance.py'
        before={p.name:p.read_bytes() for p in self.t.iterdir()}
        for command,extra in [('inspect',[]),('export',[]),('impact',['--changed-contract','API'])]:
            result=subprocess.run([sys.executable,'-B','-S',str(cli),command,'--trust',str(self.path),
                '--trust-sha256',self.pin,'--at',AT]+extra,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            parsed=json.loads(result.stdout)
            if command=='impact':self.assertEqual(parsed['affected'],['API'])
        result=subprocess.run([sys.executable,'-B','-S',str(cli),'append-proposal','--trust',str(self.path),
            '--trust-sha256',self.pin,'--at',AT,'--source-id','src-1'],capture_output=True,text=True)
        self.assertEqual(result.returncode,3) # duplicate source cannot be appended
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.t.iterdir()})
    def test_real_quality_verifier_is_called_fail_closed_missing_trust(self):
        result=verify_bundle(self.path,self.pin,'S1',self.cp,AT)
        self.assertEqual(result['status'],'unverifiable')
        self.assertTrue(any('quality' in item for item in result['reasons']))


if __name__=='__main__':unittest.main()
