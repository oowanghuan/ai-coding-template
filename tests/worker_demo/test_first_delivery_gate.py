"""Non-author first-delivery boundaries; synthetic authority, actual file bytes.

Candidate helper imports and any Git/checker subprocesses run only inside A01.
These checks do not launch the host collector or claim engineering acceptance.
"""
import base64
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('first_delivery_helper',ROOT/'scripts/run_worker_demo.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
EXPECTED=b'B own delivery\n'
ORACLE='28f17b97909760e33a1eed3acdfd6348a9a70c91fb81772a2c9ac4f2027fe07b'
ASSIGNMENT='assignment-'+'1'*32
WORKSPACE='workspace-'+'2'*32
BASELINE='a'*40
REJECT=(ValueError,OSError)


@unittest.skipUnless(os.environ.get('V4_OUTER_SEATBELT')=='1','candidate helpers require reviewed enclosing A01 sandbox')
class FirstDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name).resolve();self.project=self.base/'project'
        self.artifact=self.project/'.ai-org/workspaces'/WORKSPACE/'src/b/output.txt'
        self.artifact.parent.mkdir(parents=True);self.artifact.write_bytes(EXPECTED)
        self.path=self.project/'.ai-org/state.json'
        self.state={
            'format':'local-state/1',
            'deliveries':{'WP-B':dict(assignment_id=ASSIGNMENT,epoch=1,token=1,path='src/b/output.txt',sha256=ORACLE,content_base64=base64.b64encode(EXPECTED).decode(),baseline_sha=BASELINE)},
            'snapshot':{'assignments':[dict(id=ASSIGNMENT,wp_ref='WP-B',worker_ref='worker-b',workspace_id=WORKSPACE,base_sha=BASELINE,authority_epoch=1,fencing_token=1,state='released')],
                        'work_packages':[dict(id='WP-B',revision=4,assignment_ref=ASSIGNMENT,baseline_sha=BASELINE)]},
            'workspaces':{WORKSPACE:dict(id=WORKSPACE,assignment_id=ASSIGNMENT,wp_id='WP-B',baseline_sha=BASELINE,path='.ai-org/workspaces/'+WORKSPACE,state='finished',run=dict(state='finished',exit_code=0,pid=12345,process_group=12345,unknown_operations=[],evidence_level='synthetic_fixture'))},
            'operations':{'submit-first':dict(action='submit',status='committed',revision=5,result=dict(delivery_id='WP-B',sha256=ORACLE,accepted=False))}}
        self.write()
    def write(self):self.path.write_text(json.dumps(self.state,sort_keys=True)+'\n')
    def extract(self):return helper.extract_first_delivery(self.project)
    def malformed(self,mutate):
        prior=copy.deepcopy(self.state);mutate();self.write()
        with self.assertRaises(REJECT):self.extract()
        self.state=prior;self.write()

    def test_interfaces_present(self):
        for name in ('strict_json','extract_first_delivery','make_quality_subject','make_quality_plan'):
            self.assertTrue(callable(getattr(helper,name,None)),name)

    def test_extract_actual_bytes_receipt_and_raw_authority_fingerprint_without_mutation(self):
        before=self.path.read_bytes();result=self.extract();binding=result['binding']
        self.assertEqual(result['delivery_bytes'],EXPECTED)
        self.assertEqual(result['authority_sha256'],hashlib.sha256(before).hexdigest())
        for key,value in dict(wp_id='WP-B',assignment_id=ASSIGNMENT,workspace_id=WORKSPACE,worker_id='worker-b',path='src/b/output.txt',artifact_sha256=ORACLE,baseline_sha=BASELINE,wp_revision=4,epoch=1,token=1,submit_operation_id='submit-first',submit_revision=5,provenance='synthetic_fixture',scope='document-artifact').items():
            self.assertEqual(binding[key],value,key)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(self.artifact.read_bytes(),EXPECTED)

    def test_wrong_but_self_consistent_actual_artifact_is_not_the_oracle(self):
        wrong=b'Incorrect but self-consistent delivery\n';wrong_hash=hashlib.sha256(wrong).hexdigest()
        self.artifact.write_bytes(wrong);self.state['deliveries']['WP-B'].update(content_base64=base64.b64encode(wrong).decode(),sha256=wrong_hash)
        self.state['operations']['submit-first']['result']['sha256']=wrong_hash;self.write()
        result=self.extract();self.assertEqual(result['delivery_bytes'],wrong)
        self.assertNotEqual(result['binding']['artifact_sha256'],ORACLE)
        # Extraction proves provenance consistency only; the independent fixed
        # oracle must reject this in the real collector/Gate integration.

    def test_strict_json_duplicate_keys_and_nonfinite_constants(self):
        self.assertEqual(helper.strict_json(b'{"ok": [1, "text"]}'),{'ok':[1,'text']})
        for raw in (b'{"x":1,"x":2}',b'{"nested":{"x":1,"x":2}}',b'{"n":NaN}',b'{"n":Infinity}',b'{"n":-Infinity}',b'{"x":"\xff"}'):
            with self.subTest(raw=raw),self.assertRaises((ValueError,UnicodeError)):helper.strict_json(raw)

    def test_duplicate_keys_in_real_authority_are_rejected_before_extract(self):
        raw=self.path.read_text().replace('"epoch": 1','"epoch": 2, "epoch": 1')
        self.path.write_text(raw)
        with self.assertRaises(REJECT):self.extract()

    def test_receipt_and_actual_byte_or_hash_mismatch(self):
        for field,value in [('sha256','0'*64),('content_base64',base64.b64encode(b'other').decode()),('content_base64','not valid base64!')]:
            with self.subTest(field=field,value=value):self.malformed(lambda:self.state['deliveries']['WP-B'].__setitem__(field,value))
        self.artifact.write_bytes(b'changed after receipt')
        with self.assertRaises(REJECT):self.extract()

    def test_fixed_path_and_registered_workspace_cannot_escape(self):
        for path in ('../outside','/tmp/output.txt','src/b/../b/output.txt','src/b/other.txt','src/b/output.txt/extra'):
            with self.subTest(path=path):self.malformed(lambda:self.state['deliveries']['WP-B'].__setitem__('path',path))
        for path in ('../outside','.ai-org/workspaces/../other','/tmp/project','.ai-org/workspaces/'+WORKSPACE+'/extra'):
            with self.subTest(workspace_path=path):self.malformed(lambda:self.state['workspaces'][WORKSPACE].__setitem__('path',path))

    def test_exact_assignment_workspace_wp_and_baseline_bindings(self):
        changes=[
            lambda:self.state['snapshot']['assignments'][0].__setitem__('wp_ref','WP-A'),
            lambda:self.state['snapshot']['assignments'][0].__setitem__('worker_ref','worker-other'),
            lambda:self.state['snapshot']['work_packages'][0].__setitem__('assignment_ref','assignment-'+'3'*32),
            lambda:self.state['workspaces'][WORKSPACE].__setitem__('assignment_id','assignment-'+'3'*32),
            lambda:self.state['workspaces'][WORKSPACE].__setitem__('wp_id','WP-A'),
            lambda:self.state['snapshot']['assignments'][0].__setitem__('base_sha','b'*40),
            lambda:self.state['workspaces'][WORKSPACE].__setitem__('baseline_sha','b'*40),
            lambda:self.state['snapshot']['work_packages'][0].__setitem__('baseline_sha','b'*40),
            lambda:self.state['deliveries']['WP-B'].__setitem__('baseline_sha','not-a-sha'),
            lambda:self.state['snapshot']['assignments'].append(copy.deepcopy(self.state['snapshot']['assignments'][0])),
            lambda:self.state['snapshot']['work_packages'].append(copy.deepcopy(self.state['snapshot']['work_packages'][0])),
        ]
        for index,change in enumerate(changes):
            with self.subTest(case=index):self.malformed(change)

    def test_bool_or_nonpositive_execution_identity_revision_and_pid_refused(self):
        positions=[(self.state['deliveries']['WP-B'],'epoch'),(self.state['deliveries']['WP-B'],'token'),
                   (self.state['snapshot']['assignments'][0],'authority_epoch'),(self.state['snapshot']['assignments'][0],'fencing_token'),
                   (self.state['snapshot']['work_packages'][0],'revision'),(self.state['workspaces'][WORKSPACE]['run'],'pid')]
        # Save and restore the exact object to avoid stale references after writes.
        for obj,key in positions:
            original=obj[key]
            for value in (True,False,0,-1,'1'):
                with self.subTest(key=key,value=value):
                    obj[key]=value;self.write()
                    with self.assertRaises(REJECT):self.extract()
            obj[key]=original;self.write()

    def test_only_known_finished_process_and_committed_first_submit_are_accepted(self):
        changes=[
            lambda:self.state['workspaces'][WORKSPACE].__setitem__('state','unknown'),
            lambda:self.state['workspaces'][WORKSPACE]['run'].__setitem__('state','running'),
            lambda:self.state['workspaces'][WORKSPACE]['run'].__setitem__('exit_code',1),
            lambda:self.state['workspaces'][WORKSPACE]['run'].__setitem__('exit_code',False),
            lambda:self.state['workspaces'][WORKSPACE]['run'].__setitem__('unknown_operations',[{'id':'unknown-effect'}]),
            lambda:self.state['workspaces'][WORKSPACE]['run'].__setitem__('evidence_level','provider_live'),
            lambda:self.state['operations']['submit-first'].__setitem__('status','unknown'),
            lambda:self.state['operations']['submit-first']['result'].__setitem__('accepted',True),
            lambda:self.state['operations']['submit-first']['result'].__setitem__('sha256','0'*64),
            lambda:self.state['operations'].__setitem__('duplicate',copy.deepcopy(self.state['operations']['submit-first'])),
            lambda:self.state['operations'].__setitem__('earlier-A',dict(action='submit',status='committed',revision=4,result=dict(delivery_id='WP-A',sha256='f'*64,accepted=False))),
        ]
        for index,change in enumerate(changes):
            with self.subTest(case=index):self.malformed(change)

    def test_symlink_and_hardlink_authority_or_artifact_refused(self):
        for path in (self.path,self.artifact):
            original=path.read_bytes();backup=self.base/('saved-'+path.name);backup.write_bytes(original)
            for kind in ('symlink','hardlink'):
                with self.subTest(path=path.name,kind=kind):
                    path.unlink()
                    if kind=='symlink':path.symlink_to(backup)
                    else:os.link(backup,path)
                    with self.assertRaises(REJECT):self.extract()
                    path.unlink();path.write_bytes(original)
            backup.unlink()

    def test_ancestor_directory_symlink_and_special_leaf_refused(self):
        source=self.artifact.parent;target=self.base/'relocated-b';source.rename(target);source.symlink_to(target,target_is_directory=True)
        with self.assertRaises(REJECT):self.extract()
        source.unlink();target.rename(source)
        self.artifact.unlink();os.mkfifo(self.artifact)
        with self.assertRaises(REJECT):self.extract()

    def test_real_capsule_binds_complete_subject_and_fixed_independent_oracle(self):
        for index,data in enumerate((EXPECTED,b'Incorrect self-consistent delivery\n')):
            with self.subTest(correct=data==EXPECTED):
                self.artifact.write_bytes(data);artifact_hash=hashlib.sha256(data).hexdigest()
                self.state['deliveries']['WP-B'].update(sha256=artifact_hash,content_base64=base64.b64encode(data).decode())
                self.state['operations']['submit-first']['result']['sha256']=artifact_hash;self.write()
                before=self.path.read_bytes();extracted=self.extract()
                trusted=self.base/('T-'+str(index));trusted.mkdir();git_root=self.base/('G-'+str(index))
                capsule=helper.make_quality_subject(trusted,git_root,extracted)
                subject=trusted/'subject';self.assertFalse((subject/'.git').exists());self.assertTrue((git_root/'.git').is_dir())
                self.assertEqual(set(capsule['manifest']),{'artifact.txt','check.py','delivery-binding.json'})
                self.assertEqual({p.name for p in subject.iterdir()},set(capsule['manifest']))
                self.assertEqual((subject/'artifact.txt').read_bytes(),data)
                self.assertEqual(json.loads((subject/'delivery-binding.json').read_bytes())['authority_sha256'],hashlib.sha256(before).hexdigest())
                tree=b''
                for name in sorted(capsule['manifest']):
                    raw=(subject/name).read_bytes();entry=capsule['manifest'][name]
                    self.assertEqual(entry,{'sha256':hashlib.sha256(raw).hexdigest(),'mode':'100644'})
                    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).digest()
                    tree+=b'100644 '+name.encode()+b'\0'+blob
                actual_tree=hashlib.sha1(b'tree '+str(len(tree)).encode()+b'\0'+tree).hexdigest()
                self.assertEqual(capsule['subject']['tree'],actual_tree)
                commit=capsule['commit_object'].encode()
                self.assertEqual(hashlib.sha1(b'commit '+str(len(commit)).encode()+b'\0'+commit).hexdigest(),capsule['subject']['commit'])
                self.assertIn('tree '+actual_tree,capsule['commit_object'].splitlines())
                self.assertNotEqual(capsule['subject']['commit'],BASELINE)
                manifest=json.dumps(capsule['manifest'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
                self.assertEqual(capsule['subject']['manifest_sha256'],hashlib.sha256(manifest).hexdigest())
                plan=helper.make_quality_plan(trusted,self.base/('Q-'+str(index)),capsule,extracted,'synthetic-version')
                self.assertEqual(plan['kind'],'document');self.assertEqual(plan['wp_id'],'WP-B');self.assertEqual(plan['wp_revision'],4)
                self.assertEqual(plan['subject'],capsule['subject']);self.assertEqual(plan['entrypoint'],'check.py')
                self.assertEqual(len(plan['tests']),1);case=plan['tests'][0]
                self.assertIs(case['required'],True);self.assertEqual(case['expected_exit'],0);self.assertIsNone(case['skip_reason'])
                self.assertEqual(case['expected_stdout_sha256'],ORACLE)
                if data!=EXPECTED:self.assertNotEqual(case['expected_stdout_sha256'],artifact_hash)
                self.assertEqual(self.path.read_bytes(),before)

    def test_fake_passed_report_is_not_a_delivery_receipt(self):
        self.path.write_text(json.dumps({'passed':True,'sha256':ORACLE,'tests':{'passed':1}}))
        with self.assertRaises((ValueError,KeyError)):self.extract()


if __name__=='__main__':unittest.main()
