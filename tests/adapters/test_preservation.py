"""Provisional checkpoint integration; real files/processes, no provider calls."""
import json
import os
from pathlib import Path
import shutil
import time
import unittest
from unittest.mock import patch

import test_factory as factory
import test_lifecycle as fixtures
from framework.local import handoff
from framework.local.storage import atomic_json
from framework.recovery.checkpoint import load_snapshot, restore_snapshot

PROGRAM="from pathlib import Path;Path('src/base.txt').write_text('dirty tracked');Path('src/a').mkdir(exist_ok=True);Path('src/a/new.txt').write_text('unfinished untracked')"


class PreservationTests(unittest.TestCase):
    initial = factory.FactoryTests.initial
    state = factory.FactoryTests.state
    change = factory.FactoryTests.change
    result = factory.FactoryTests.result
    enable = factory.FactoryTests.enable
    event = factory.FactoryTests.event
    claim = factory.FactoryTests.claim
    stop_owned = factory.FactoryTests.stop_owned
    bound = factory.FactoryTests.bound
    start = factory.FactoryTests.start
    finish = factory.FactoryTests.finish
    prepare_factory = factory.FactoryTests.prepare_factory
    bind = factory.FactoryTests.bind

    def setUp(self):
        factory.FactoryTests.setUp(self)
        patch('framework.local.handoff.now',return_value=fixtures.AT).start()

    def job(self, program=PROGRAM):
        job,d,opts=self.prepare_factory(program=program)
        return self.bind(job,d,opts)

    def preserve(self,job,record,op='preserve',**kwargs):
        return job['registry'].checkpoint('synthetic',record['invocation_id'],operation_id=op,**kwargs)

    def finished(self):
        job=self.job();record=self.start(job);self.finish(job,record);return job,record

    def test_dirty_and_untracked_restore_as_artifact_but_no_handoff(self):
        job,record=self.finished();result=self.preserve(job,record,remaining=['finish task'])
        cp=self.root/result['path'];manifest=load_snapshot(cp,result['manifest_sha256'])
        self.assertEqual(manifest['context']['unknown_operations'][0]['id'],'provider-'+record['invocation_id'])
        self.assertEqual(manifest['context']['remaining'],['finish task'])
        restored=self.root/'preserved-verification';restore_snapshot(cp,result['manifest_sha256'],restored)
        self.assertEqual((restored/'src/base.txt').read_text(),'dirty tracked')
        self.assertEqual((restored/'src/a/new.txt').read_text(),'unfinished untracked')
        self.assertTrue(result['provisional']);self.assertFalse(result['recovery_ready'])
        with self.assertRaises(ValueError):self.result('release',job['authority'],actor='principal-a')
        with self.assertRaises(ValueError):self.claim('c',wp='WP-A')
        s=self.state();wp=s['snapshot']['work_packages'][0];w=s['workspaces'][job['authority']['workspace_id']]
        self.assertEqual(w['state'],'unknown')
        self.assertEqual(wp['state'],'paused')
        self.assertEqual(s['snapshot']['assignments'][0]['state'],'revoked')
        self.assertEqual(s['worker_runtime']['workers']['worker-a']['status'],'recovering')
        self.assertEqual(s['worker_runtime']['workers']['worker-c']['status'],'available')
        with self.assertRaises(ValueError):self.store.guard(job['authority'],'principal-a')
        with self.assertRaisesRegex(ValueError,'unknown operations'):handoff.checked_checkpoint(self.root,s,wp,w)
        independent=self.bound('c');self.assertEqual(self.finish(independent,self.start(independent))['exit_code'],0)
        exported=Path(os.environ['V4_UNSTARTED_EVIDENCE'])/'provider-preservation'
        exported.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(cp,exported)
        print(json.dumps({'provider_preservation':dict(dirty_tracked_restored=True,untracked_restored=True,
            unknown_operations=len(manifest['context']['unknown_operations']),workspace_state=w['state'],
            work_package_state=wp['state'],assignment_state='revoked',independent_process_exit_code=0,
            exported_manifest_sha256=result['manifest_sha256'],
            recovery_ready=result['recovery_ready'],engineering_accepted=result['engineering_accepted'])}),flush=True)

    def test_replay_has_no_revision_or_snapshot_side_effect(self):
        job,record=self.finished();first=self.preserve(job,record)
        before=self.store.path.read_bytes();paths=set((self.root/'.ai-org/checkpoints').iterdir())
        self.assertEqual(first,self.preserve(job,record));self.assertEqual(before,self.store.path.read_bytes())
        self.assertEqual(paths,set((self.root/'.ai-org/checkpoints').iterdir()))

    def test_checkpoint_commit_lost_receipt_replays_original(self):
        job,record=self.finished()
        def lost(path,value):atomic_json(path,value);raise OSError('lost checkpoint commit response')
        with patch('framework.local.handoff.atomic_json',side_effect=lost):
            with self.assertRaises(OSError):self.preserve(job,record)
        before=self.store.path.read_bytes();paths=set((self.root/'.ai-org/checkpoints').iterdir())
        result=self.preserve(job,record)
        self.assertEqual(before,self.store.path.read_bytes());self.assertEqual(paths,set((self.root/'.ai-org/checkpoints').iterdir()))
        self.assertEqual(len([x for x in self.state()['operations'].values() if x['action']=='provider-checkpoint']),1)
        self.assertFalse(result['recovery_ready'])

    def test_changed_operation_narrative_rejected(self):
        job,record=self.finished();self.preserve(job,record,remaining=['first'])
        before=self.store.path.read_bytes()
        with self.assertRaisesRegex(ValueError,'changed intent'):self.preserve(job,record,remaining=['second'])
        self.assertEqual(before,self.store.path.read_bytes())

    def test_late_bytes_require_new_preservation_without_overwriting_old(self):
        job,record=self.finished();first=self.preserve(job,record)
        (job['cwd']/'src/a/new.txt').write_text('late bytes')
        with self.assertRaises(ValueError):self.preserve(job,record)
        second=self.preserve(job,record,op='later');self.assertNotEqual(first['path'],second['path'])
        self.assertEqual((self.root/first['path']/'data/src/a/new.txt').read_text(),'unfinished untracked')
        self.assertEqual((self.root/second['path']/'data/src/a/new.txt').read_text(),'late bytes')
        self.assertFalse(second['recovery_ready'])

    def test_checkpoint_tampering_rejects_replay(self):
        job,record=self.finished();first=self.preserve(job,record)
        (self.root/first['path']/'data/src/a/new.txt').write_text('forged')
        before=self.store.path.read_bytes()
        with self.assertRaises(ValueError):self.preserve(job,record)
        self.assertEqual(before,self.store.path.read_bytes())

    def test_running_invocation_rejected_without_checkpoint(self):
        job=self.job("import time;time.sleep(10)");job['request']['timeout_seconds']=10;record=self.start(job)
        with self.assertRaises(ValueError):self.preserve(job,record)
        self.assertFalse((self.root/'.ai-org/checkpoints').exists())
        job['registry'].stop('synthetic',record['invocation_id']);self.finish(job,record)

    def test_captured_output_tamper_not_downgraded_to_unknown_snapshot(self):
        job,record=self.finished();(job['journal']/(record['invocation_id']+'.stdout')).write_bytes(b'forged')
        with self.assertRaises(ValueError):self.preserve(job,record)
        self.assertFalse((self.root/'.ai-org/checkpoints').exists())

    def test_initialization_unknown_without_output_can_be_preserved_not_accepted(self):
        job=self.job()
        with patch('framework.adapters.invocation.selectors.DefaultSelector',side_effect=OSError('fixture init failure')):
            record=self.start(job);done=self.finish(job,record)
        self.assertEqual(done['state'],'outcome_unknown')
        self.assertIsNone(done['stdout_sha256']);result=self.preserve(job,record)
        self.assertFalse(result['recovery_ready']);self.assertFalse(result['engineering_accepted'])
        with self.assertRaises(ValueError):self.start(job,operation='restart')

    def test_original_checkpoint_path_still_binds_prepared_state(self):
        job=self.job();before=self.state()['revision']
        cp=handoff.checkpoint(self.root,job['authority'],'principal-a',remaining=['not launched'])
        manifest=load_snapshot(self.root/cp['path'],cp['manifest_sha256'])
        self.assertEqual(manifest['context']['unknown_operations'],[])
        self.assertEqual(manifest['context']['remaining'],['not launched'])
        self.assertEqual(self.state()['revision'],before+1)
        self.assertEqual(self.state()['workspaces'][job['authority']['workspace_id']]['state'],'prepared')

    def test_changed_contract_preserves_workspace_but_no_misbound_checkpoint(self):
        job,record=self.finished();s=self.state();s['snapshot']['work_packages'][0]['forbidden_paths'].append('src/a/new.txt');atomic_json(self.store.path,s)
        with self.assertRaisesRegex(ValueError,'contract changed'):self.preserve(job,record)
        self.assertTrue((job['cwd']/'src/a/new.txt').exists());self.assertFalse((self.root/'.ai-org/checkpoints').exists())
