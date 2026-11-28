"""Real local file operations in the outer A01 sandbox; identities are fixtures."""
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from framework.recovery import checkpoint as cp
from framework.recovery.admission import evaluate_takeover


def context():
    return dict(wp_ref='WP-302',assignment_ref='assignment-old',authority_epoch=1,fencing_token=7,
                baseline_sha='1'*40,last_valid_commit='2'*40,completed=['write first draft'],
                remaining=['finish review'],unknown_operations=[],role_ref='implementer',
                authorization_ref='authorization-1',next_actions=['recheck authority'])


def current():
    return dict(wp_ref='WP-302',old_assignment_ref='assignment-old',old_writer_status='confirmed_stopped',
                old_fencing_token=7,authority_epoch=1,new_assignment_ref='assignment-new',new_fencing_token=8,
                authorization_valid=True,budget_available=True,owner_status='active',work_package_status='paused',
                new_lease_expires_at='2026-12-01T01:00:00Z',reconciled_operations={})


class Checkpoints(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve()
        self.work=self.root/'work';self.work.mkdir();self.destination=self.root/'checkpoint';self.restore=self.root/'restore'
        (self.work/'unchanged.txt').write_bytes(b'unchanged\n');(self.work/'dirty.txt').write_bytes(b'edited\n')
        (self.work/'new').mkdir();(self.work/'new'/'draft.txt').write_bytes(b'untracked\x00binary\n');(self.work/'empty').mkdir()
        (self.work/'run.py').write_bytes(b'print(1)\n');(self.work/'run.py').chmod(0o755)
        (self.work/'.git').write_text('gitdir: /never/follow/this/path\n')
        self.baseline={'unchanged.txt':{'sha256':cp.digest(b'unchanged\n'),'mode':'100644'},
                       'dirty.txt':{'sha256':cp.digest(b'original\n'),'mode':'100644'},
                       'deleted.txt':{'sha256':cp.digest(b'deleted\n'),'mode':'100644'}}
    def create(self):return cp.create_snapshot(self.work,self.destination,context(),self.baseline)
    def test_roundtrip_preserves_dirty_untracked_empty_directory_and_exec(self):
        before={str(p.relative_to(self.work)):p.read_bytes() for p in self.work.rglob('*') if p.is_file()}
        receipt=self.create();manifest=cp.load_snapshot(self.destination,receipt['manifest_sha256'])
        self.assertEqual(receipt['tracked_count'],2);self.assertEqual(receipt['untracked_count'],2)
        self.assertFalse(manifest['files']['unchanged.txt']['dirty']);self.assertTrue(manifest['files']['dirty.txt']['dirty'])
        self.assertEqual(manifest['deleted_tracked'],['deleted.txt']);self.assertIn('empty',manifest['directories'])
        restored=cp.restore_snapshot(self.destination,receipt['manifest_sha256'],self.restore)
        self.assertFalse(restored['execution_authorized']);self.assertFalse((self.restore/'.git').exists())
        for name,raw in before.items():
            self.assertEqual((self.work/name).read_bytes(),raw)
            if name!='.git':self.assertEqual((self.restore/name).read_bytes(),raw)
        self.assertTrue((self.restore/'run.py').stat().st_mode & stat.S_IXUSR)
        self.assertEqual(manifest['context'],context())
    def test_explicit_git_metadata_exclusion_never_follows_worktree_pointer(self):
        receipt=self.create()
        self.assertTrue(cp.load_snapshot(self.destination,receipt['manifest_sha256'])['excluded_git_metadata'])
        self.assertFalse((self.destination/'data/.git').exists())
    def test_source_symlink_and_hardlink_refused(self):
        for kind in ('symlink','hardlink'):
            with self.subTest(kind=kind):
                output=self.root/('checkpoint-'+kind);link=self.work/'linked'
                if kind=='symlink':link.symlink_to(self.work/'unchanged.txt')
                else:os.link(self.work/'unchanged.txt',link)
                with self.assertRaises((ValueError,OSError)):cp.create_snapshot(self.work,output,context(),self.baseline)
                self.assertFalse(output.exists());link.unlink()
    def test_git_symlink_is_refused_even_when_excluded(self):
        (self.work/'.git').unlink();(self.work/'.git').symlink_to(self.work/'unchanged.txt')
        with self.assertRaises(ValueError):self.create()
        self.assertFalse(self.destination.exists())
    def test_fifo_refused_without_blocking(self):
        os.mkfifo(self.work/'fifo')
        with self.assertRaises(ValueError):self.create()
        self.assertFalse(self.destination.exists())
    def test_symlink_ancestor_and_path_escape_refused(self):
        alias=self.root/'alias';alias.symlink_to(self.work,target_is_directory=True)
        with self.assertRaises(OSError):cp.create_snapshot(alias,self.destination,context(),self.baseline)
        with self.assertRaises(ValueError):cp.create_snapshot(str(self.work)+'/../work',self.destination,context(),self.baseline)
        for name in ('../outside','/absolute','a//b','a/./b','a\\b'):
            with self.subTest(path=name),self.assertRaises(ValueError):cp.create_snapshot(self.work,self.destination,context(),{name:{'sha256':'a'*64,'mode':'100644'}})
    def test_nested_destination_and_missing_parent_refused(self):
        with self.assertRaises(ValueError):cp.create_snapshot(self.work,self.work/'checkpoint',context(),self.baseline)
        with self.assertRaises(FileNotFoundError):cp.create_snapshot(self.work,self.root/'missing'/'checkpoint',context(),self.baseline)
    def test_existing_destination_preserved_for_create_and_restore(self):
        receipt=self.create();original=(self.destination/'manifest.json').read_bytes()
        with self.assertRaises(FileExistsError):self.create()
        self.assertEqual((self.destination/'manifest.json').read_bytes(),original)
        self.restore.mkdir();(self.restore/'sentinel').write_bytes(b'keep')
        with self.assertRaises(FileExistsError):cp.restore_snapshot(self.destination,receipt['manifest_sha256'],self.restore)
        self.assertEqual((self.restore/'sentinel').read_bytes(),b'keep')
    def test_wrong_pin_and_corrupt_content_refused(self):
        receipt=self.create()
        with self.assertRaises(ValueError):cp.load_snapshot(self.destination,'f'*64)
        (self.destination/'data/dirty.txt').write_bytes(b'corrupt')
        with self.assertRaises(ValueError):cp.restore_snapshot(self.destination,receipt['manifest_sha256'],self.restore)
        self.assertFalse(self.restore.exists())
    def test_manifest_tampering_and_extra_files_refused(self):
        receipt=self.create();path=self.destination/'manifest.json';raw=path.read_bytes()
        value=json.loads(raw);value['context']['fencing_token']=999;path.write_bytes(cp.canonical(value)+b'\n')
        with self.assertRaises(ValueError):cp.load_snapshot(self.destination,receipt['manifest_sha256'])
        path.write_bytes(raw);(self.destination/'extra').write_text('not registered')
        with self.assertRaises(ValueError):cp.load_snapshot(self.destination,receipt['manifest_sha256'])
    def test_checkpoint_links_refused(self):
        receipt=self.create();data=self.destination/'data/dirty.txt';raw=data.read_bytes();data.unlink();data.symlink_to(self.work/'dirty.txt')
        with self.assertRaises(ValueError):cp.load_snapshot(self.destination,receipt['manifest_sha256'])
        data.unlink();data.write_bytes(raw);os.link(data,self.root/'alias-data')
        with self.assertRaises(ValueError):cp.load_snapshot(self.destination,receipt['manifest_sha256'])
    def test_changed_source_aborts_and_preserves_partial_staging(self):
        original=cp.read_regular;changed=[False]
        def altering(parent,name,limit=cp.MAX_FILE):
            result=original(parent,name,limit)
            if name=='dirty.txt' and not changed[0]:
                changed[0]=True;(self.work/'dirty.txt').write_bytes(b'new work to retain\n')
            return result
        with patch.object(cp,'read_regular',side_effect=altering),self.assertRaises(ValueError):self.create()
        self.assertFalse(self.destination.exists());self.assertEqual((self.work/'dirty.txt').read_bytes(),b'new work to retain\n')
        self.assertTrue(list(self.root.glob('.checkpoint-staging-*')))
    def test_size_bound_fails_before_publication(self):
        with patch.object(cp,'MAX_TOTAL',1),self.assertRaises(ValueError):self.create()
        self.assertFalse(self.destination.exists())
    def test_empty_checkpoint_and_unique_successive_checkpoints(self):
        empty=self.root/'emptywork';empty.mkdir()
        first=cp.create_snapshot(empty,self.destination,context(),{})
        (empty/'later').write_bytes(b'work')
        second=cp.create_snapshot(empty,self.root/'second',context(),{})
        self.assertNotEqual(first['manifest_sha256'],second['manifest_sha256'])
        self.assertEqual(cp.load_snapshot(self.destination,first['manifest_sha256'])['files'],{})
    def test_two_actual_processes_publish_once_without_overwrite(self):
        argsfile=self.root/'args.json';argsfile.write_text(json.dumps({'work':str(self.work),'destination':str(self.destination),'context':context(),'baseline':self.baseline}))
        ready=self.root/'go';script=self.root/'worker.py'
        script.write_text("import json,sys,time\nfrom pathlib import Path\nfrom framework.recovery.checkpoint import create_snapshot\na=json.loads(Path(sys.argv[1]).read_text())\nwhile not Path(sys.argv[2]).exists():time.sleep(.01)\ntry:\n r=create_snapshot(a['work'],a['destination'],a['context'],a['baseline']);print(json.dumps(r))\nexcept FileExistsError:\n sys.exit(4)\n")
        processes=[subprocess.Popen([sys.executable,'-B','-S',str(script),str(argsfile),str(ready)],stdout=subprocess.PIPE,stderr=subprocess.PIPE) for _ in range(2)]
        ready.write_text('go');outputs=[p.communicate(timeout=15) for p in processes]
        self.assertEqual(sorted(p.returncode for p in processes),[0,4],outputs)
        winner=next(json.loads(out) for p,(out,err) in zip(processes,outputs) if p.returncode==0)
        self.assertEqual(cp.load_snapshot(self.destination,winner['manifest_sha256'])['context'],context())
    def test_real_git_dirty_state_and_untracked_content_preserved(self):
        (self.work/'.git').unlink()
        environment=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',
            GIT_AUTHOR_NAME='Synthetic Recovery Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',
            GIT_COMMITTER_NAME='Synthetic Recovery Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
        def git(*args):
            result=subprocess.run(['/usr/bin/git','-c','core.hooksPath=/dev/null','-c','commit.gpgsign=false',*args],cwd=self.work,env=environment,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr);return result.stdout
        git('init','-q');git('add','unchanged.txt','dirty.txt','run.py');git('commit','-q','-m','fixture baseline')
        commit=git('rev-parse','HEAD').decode().strip()
        baseline={name:{'sha256':cp.digest((self.work/name).read_bytes()),'mode':'100755' if name=='run.py' else '100644'} for name in ('unchanged.txt','dirty.txt','run.py')}
        (self.work/'dirty.txt').write_bytes(b'new dirty result\n');(self.work/'run.py').unlink()
        before=git('status','--porcelain=v1','-z');value=context();value.update(baseline_sha=commit,last_valid_commit=commit)
        receipt=cp.create_snapshot(self.work,self.destination,value,baseline)
        self.assertEqual(git('status','--porcelain=v1','-z'),before)
        manifest=cp.load_snapshot(self.destination,receipt['manifest_sha256'])
        self.assertEqual(manifest['context']['baseline_sha'],commit)
        self.assertTrue(manifest['files']['dirty.txt']['dirty']);self.assertFalse(manifest['files']['new/draft.txt']['tracked'])
        self.assertEqual(manifest['deleted_tracked'],['run.py'])
        cp.restore_snapshot(self.destination,receipt['manifest_sha256'],self.restore)
        self.assertEqual((self.restore/'dirty.txt').read_bytes(),b'new dirty result\n')
        self.assertEqual((self.restore/'new/draft.txt').read_bytes(),(self.work/'new/draft.txt').read_bytes())
    def test_publication_failure_leaves_source_and_incomplete_stage(self):
        with patch.object(cp,'publish',side_effect=OSError('simulated crash before publication')):
            with self.assertRaises(OSError):self.create()
        self.assertFalse(self.destination.exists());self.assertTrue((self.work/'dirty.txt').exists())
        self.assertTrue(list(self.root.glob('.checkpoint-staging-*')))
        # A new explicit attempt has its own stage, retaining the failed attempt.
        receipt=self.create();self.assertEqual(cp.load_snapshot(self.destination,receipt['manifest_sha256'])['context'],context())
    def test_restore_source_mutation_between_validation_and_copy_is_refused(self):
        receipt=self.create();original=cp.scan;changed=[False]
        def altering(root,target=None,exclude_git=False):
            if target is not None and not changed[0]:
                changed[0]=True;(self.destination/'data/dirty.txt').write_bytes(b'tampered during restore')
            return original(root,target,exclude_git)
        with patch.object(cp,'scan',side_effect=altering),self.assertRaises(ValueError):
            cp.restore_snapshot(self.destination,receipt['manifest_sha256'],self.restore)
        self.assertFalse(self.restore.exists());self.assertEqual((self.work/'dirty.txt').read_bytes(),b'edited\n')
    def test_staging_corruption_is_not_published(self):
        original=cp.write_file;changed=[False]
        def corrupt(parent,name,raw,executable=False):
            if name=='dirty.txt' and not changed[0]:raw=b'wrong bytes';changed[0]=True
            return original(parent,name,raw,executable)
        with patch.object(cp,'write_file',side_effect=corrupt),self.assertRaises(ValueError):self.create()
        self.assertFalse(self.destination.exists())
    def test_three_adapter_contexts_share_checkpoint_and_takeover_protocol(self):
        # No model process or real credential: three synthetic adapter identities.
        workspace=self.work;previous=None
        for index,name in enumerate(('adapter-A','adapter-B','adapter-C')):
            value=context();value.update(assignment_ref='assignment-'+name,fencing_token=7+index,
                worker_ref='worker-'+name,provider_ref='tool-provider-'+name,
                model_provider_ref='model-provider-shared',model_ref='synthetic-model-'+str(index),
                credential_ref='protected-credential-reference-'+str(index))
            if previous is not None:
                old=previous['manifest']['context'];observed=current()
                observed.update(old_assignment_ref=old['assignment_ref'],old_fencing_token=old['fencing_token'],
                    new_assignment_ref=value['assignment_ref'],new_fencing_token=value['fencing_token'])
                admission=evaluate_takeover(previous['manifest'],observed,'2026-12-01T00:00:00Z')
                self.assertTrue(admission['admissible']);self.assertFalse(admission['execution_authorized'])
                workspace=self.root/('restored-'+name)
                cp.restore_snapshot(previous['receipt']['path'],previous['receipt']['manifest_sha256'],workspace)
            (workspace/(name+'.txt')).write_text('synthetic adapter artifact '+name)
            receipt=cp.create_snapshot(workspace,self.root/('checkpoint-'+name),value,self.baseline)
            manifest=cp.load_snapshot(receipt['path'],receipt['manifest_sha256'])
            self.assertEqual(manifest['context']['provider_ref'],'tool-provider-'+name)
            self.assertNotEqual(manifest['context']['provider_ref'],manifest['context']['model_provider_ref'])
            self.assertEqual(manifest['context']['credential_ref'],'protected-credential-reference-'+str(index))
            previous={'receipt':receipt,'manifest':manifest}
        self.assertTrue(all(name+'.txt' in manifest['files'] for name in ('adapter-A','adapter-B','adapter-C')))
    def test_source_does_not_infer_facts_from_model_completed_text(self):
        value=context();value['completed']=['Model claims all tests passed']
        receipt=cp.create_snapshot(self.work,self.destination,value,self.baseline)
        manifest=cp.load_snapshot(self.destination,receipt['manifest_sha256'])
        self.assertNotIn('accepted',manifest);self.assertNotIn('execution_authorized',manifest)


class Admission(unittest.TestCase):
    def setUp(self):self.manifest={'context':context()};self.observations=current();self.at='2026-12-01T00:00:00Z'
    def decide(self):return evaluate_takeover(self.manifest,self.observations,self.at)
    def test_positive_is_not_execution_authority(self):
        result=self.decide();self.assertTrue(result['admissible']);self.assertFalse(result['execution_authorized']);self.assertTrue(result['requires_atomic_authority_recheck'])
    def test_stop_owner_authorization_budget_and_task_precedence(self):
        for field,value,reason in [('old_writer_status','unknown','old-writer-not-confirmed-stopped'),('old_writer_status','model_says_stopped','old-writer-not-confirmed-stopped'),('authorization_valid',False,'authorization-not-valid'),('budget_available',False,'budget-not-available'),('owner_status','paused','owner-not-active'),('work_package_status','completed','task-not-recoverable')]:
            with self.subTest(field=field,value=value):
                self.observations=current();self.observations[field]=value
                result=self.decide();self.assertFalse(result['admissible']);self.assertIn(reason,result['reasons'])
    def test_old_fence_same_assignment_epoch_and_expiry_block(self):
        for field,value in [('new_fencing_token',7),('new_fencing_token',True),('old_fencing_token',6),('new_assignment_ref','assignment-old'),('authority_epoch',2),('new_lease_expires_at',self.at),('wp_ref','other'),('old_assignment_ref','other')]:
            with self.subTest(field=field):
                self.observations=current();self.observations[field]=value;self.assertFalse(self.decide()['admissible'])
    def test_unknown_operation_requires_actual_reconciliation_reference(self):
        self.manifest['context']['unknown_operations']=[{'id':'op-1','intent':'write external artifact','reconciliation':'read operation key'}]
        self.assertFalse(self.decide()['admissible'])
        self.observations['reconciled_operations']={'op-1':{'outcome':'planned','evidence_ref':'plan'}};self.assertFalse(self.decide()['admissible'])
        self.observations['reconciled_operations']={'op-1':{'outcome':'confirmed_applied','evidence_ref':'receipt-1'}};self.assertTrue(self.decide()['admissible'])
    def test_missing_or_invalid_inputs_fail_closed(self):
        del self.observations['owner_status'];self.assertFalse(self.decide()['admissible'])
        self.assertFalse(evaluate_takeover({},current(),self.at)['admissible'])
        self.assertFalse(evaluate_takeover(self.manifest,current(),'yesterday')['admissible'])


if __name__=='__main__':unittest.main()
