"""Actual fixed processes and Store handoff, only inside an enclosing A01 sandbox."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('worker_demo',ROOT/'scripts/v4_worker_demo.py')
demo=importlib.util.module_from_spec(spec);spec.loader.exec_module(demo)


@unittest.skipUnless(os.environ.get('V4_OUTER_SEATBELT')=='1','actual synthetic workers require reviewed enclosing sandbox')
class WorkerDemoTests(unittest.TestCase):
    def test_real_parallel_quota_checkpoint_takeover_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve()/'new-project';result=demo.run_demo(root)
            self.assertTrue(result['passed']);self.assertEqual(result['evidence_level'],'synthetic_fixture')
            self.assertFalse(result['provider_live']);self.assertFalse(result['engineering_accepted'])
            self.assertEqual(result['pmo_model_calls'],0);self.assertEqual(result['actual_model_calls'],0)
            self.assertGreater(result['new_token'],result['old_token']);self.assertNotEqual(result['old_workspace'],result['new_workspace'])
            self.assertEqual(result['logical_deliveries'],{'WP-A':1,'WP-B':1})
            self.assertTrue(result['duplicate_delivery_rejected'])
            self.assertTrue(result['parallel_processes_observed']);self.assertTrue(result['old_token_rejected'])
            checkpoint=json.loads((root/'demo-evidence/checkpoint-manifest.json').read_text())
            self.assertTrue(checkpoint['files']['src/a/tracked.txt']['dirty']);self.assertFalse(checkpoint['files']['src/a/untracked.txt']['tracked'])
            before=(root/'.ai-org/state.json').read_bytes()
            with self.assertRaises(FileExistsError):demo.run_demo(root)
            self.assertEqual((root/'.ai-org/state.json').read_bytes(),before)

    def test_existing_root_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve();(root/'keep').write_text('work')
            with self.assertRaises(FileExistsError):demo.run_demo(root)
            self.assertEqual((root/'keep').read_text(),'work')

if __name__=='__main__':unittest.main()
