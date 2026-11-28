"""Author-run real Store/Git + fixed-process bridge checks, no model calls."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import time
import unittest
from unittest.mock import patch

import test_lifecycle as fixtures
from framework.adapters.invocation import ProcessExecutor, LaunchReservations
from framework.adapters.registry import AdapterRegistry, descriptor, synthetic_plan, synthetic_classify
from framework.adapters.store_binding import StoreBinding
from framework.local.runner import prepare
from framework.local.storage import atomic_json


class StoreBindingTests(unittest.TestCase):
    initial = fixtures.LifecycleTests.initial
    state = fixtures.LifecycleTests.state
    change = fixtures.LifecycleTests.change
    result = fixtures.LifecycleTests.result
    enable = fixtures.LifecycleTests.enable
    event = fixtures.LifecycleTests.event
    claim = fixtures.LifecycleTests.claim

    def setUp(self):
        fixtures.LifecycleTests.setUp(self)
        self.addCleanup(patch.stopall)
        patch('framework.local.store.now', return_value=fixtures.AT).start()
        patch('framework.adapters.store_binding.now', return_value=fixtures.AT).start()
        self.initial()
        self.enable(resource=dict(agent_tool='fixture-tool',model_provider='fixture-model',model=None,credential_ref='opaque-reference'))
        self.fence = self.root/'shared-launches'; self.fence.mkdir()
        self.executors = []; self.addCleanup(self.stop_owned)

    def stop_owned(self):
        for e in self.executors:
            for live in list(e._live.values()):
                live['stop'].set(); live['thread'].join(8)
                self.assertFalse(live['thread'].is_alive())

    def bound(self, letter='a', credentials=None, journal_name=None, program=None):
        if credentials is None:
            credentials = self.claim(letter)
            prepare(self.root, credentials, 'principal-'+letter, self.state()['revision'], 'prepare-'+letter)
        authority = {k:credentials[k] for k in ('assignment_id','workspace_id','epoch','token')}
        workspace = self.state()['workspaces'][authority['workspace_id']]
        cwd = self.root/workspace['path']
        d = descriptor('synthetic','fixture-tool','fixture-model',credential_ref='opaque-reference',
                       quota_group='Q2' if letter=='c' else 'Q1',validation_level='synthetic_fixture')
        for k in ('start','status','stop','result'): d['capabilities'][k]='supported'
        selection = {k:d[k] for k in ('adapter_id','agent_tool','model_provider','model','credential_ref','quota_group')}
        bridge = StoreBinding(project_root=self.root,reservation_root=self.fence,actor='principal-'+letter,
                              authority=authority,selection=selection,cwd=cwd)
        journal = self.root/(journal_name or 'journal-'+letter); journal.mkdir()
        program = program or "from pathlib import Path;p=Path('src/%s/out.txt');p.parent.mkdir(exist_ok=True);p.write_text('fixed result')" % letter
        e = ProcessExecutor(selection=selection,argv=['/usr/bin/python3','-I','-B','-S','-c',program],
            cwd=cwd,environment={'PATH':'/usr/bin:/bin'},journal_root=journal,
            pinned_files={'/usr/bin/python3':hashlib.sha256(Path('/usr/bin/python3').read_bytes()).hexdigest()},
            authorize=bridge.authorize,launch_reservations=bridge)
        self.executors.append(e); r=AdapterRegistry()
        r.register(d,planner=synthetic_plan,classifier=synthetic_classify,executor=e)
        request=dict(work_package_id='WP-'+letter.upper(),assignment_id=authority['assignment_id'],
                     baseline_sha=self.sha,prompt='fixed task',timeout_seconds=3,max_output_bytes=1024)
        return dict(registry=r,executor=e,bridge=bridge,authority=authority,request=request,cwd=cwd,journal=journal,letter=letter)

    def start(self, job, operation='run'):
        return job['registry'].start('synthetic',operation_id=operation,authority=job['authority'],**job['request'])

    def finish(self, job, record):
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            result=job['registry'].status('synthetic',record['invocation_id'])
            if result['state'] not in ('launch_intent','running'): return result
            time.sleep(.02)
        self.fail('fixed process did not finish')

    def assert_not_launched(self, job):
        self.assertFalse((job['cwd']/('src/'+job['letter']+'/out.txt')).exists())
        self.assertEqual(list(job['journal'].glob('inv-*.json')), [])

    def test_store_intent_precedes_spawn_and_exit_does_not_release_authority(self):
        job=self.bound(); original_popen=subprocess.Popen; observations=[]
        def observed_popen(argv, **kwargs):
            if argv[0]=='/usr/bin/python3':
                state=self.state();workspace=state['workspaces'][job['authority']['workspace_id']]
                observations.append(dict(workspace_state=workspace['state'],
                    launch_operations=len([r for r in state['operations'].values() if r['action']=='provider-run-begin']),
                    writer_stop_confirmed=state['worker_runtime']['workers']['worker-a']['stop_confirmed']))
            return original_popen(argv,**kwargs)
        with patch('subprocess.Popen',side_effect=observed_popen): record=self.start(job)
        done=self.finish(job,record)
        self.assertEqual(observations,[dict(workspace_state='launching',launch_operations=1,writer_stop_confirmed=False)])
        self.assertEqual(done['exit_code'],0)
        s=self.state();w=s['workspaces'][job['authority']['workspace_id']]
        self.assertEqual(w['state'],'launching')
        self.assertEqual(w['run']['invocation_id'],record['invocation_id'])
        self.assertFalse(s['worker_runtime']['workers']['worker-a']['stop_confirmed'])
        self.assertEqual(s['snapshot']['work_packages'][0]['state'],'in_progress')
        with self.assertRaisesRegex(ValueError,'unresolved'):
            self.result('release',job['authority'],actor='principal-a')
        self.assertEqual(len([r for r in s['operations'].values() if r['action']=='provider-run-begin']),1)
        print(json.dumps({'store_bridge':{'actual_exit_code':done['exit_code'],'workspace_state':w['state'],
            'writer_stop_confirmed':False,'launch_operations':1,'task_state':'in_progress','engineering_accepted':False,
            'observed_before_actual_spawn':observations}}),flush=True)

    def test_wrong_token_baseline_package_or_selection_never_launches(self):
        job=self.bound()
        for key,value in [('token',2),('epoch',True),('workspace_id','unrelated')]:
            old=job['authority'][key];job['authority'][key]=value
            with self.assertRaises(ValueError):self.start(job)
            job['authority'][key]=old
        for key,value in [('baseline_sha','f'*40),('work_package_id','WP-B')]:
            old=job['request'][key];job['request'][key]=value
            with self.assertRaises(ValueError):self.start(job)
            job['request'][key]=old
        job['bridge'].selection['model_provider']='other'
        with self.assertRaises(ValueError):self.start(job)
        self.assert_not_launched(job)

    def test_live_quota_fences_one_group_and_independent_worker_continues(self):
        a=self.bound('a');c=self.bound('c')
        self.event('b','quota_limited')
        with self.assertRaises(ValueError):self.start(a)
        self.assert_not_launched(a)
        result=self.finish(c,self.start(c));self.assertEqual(result['exit_code'],0)
        self.assertFalse(self.state()['worker_runtime']['groups']['Q2']['limited'])

    def test_expired_lease_and_heartbeat_rechecked_at_launch(self):
        job=self.bound()
        for later in (121,601):
            with patch('framework.adapters.store_binding.now',return_value=fixtures.later(later)):
                with self.assertRaises(ValueError):self.start(job)
        self.assert_not_launched(job)

    def test_owner_budget_pause_contract_and_auth_changes_block_existing_binding(self):
        job=self.bound();original=self.state()
        for change in ('budget','paused','authorization','contract','host','authentication'):
            s=copy.deepcopy(original)
            if change=='budget':s['snapshot']['project']['budget']='unknown'
            elif change=='paused':s['snapshot']['project']['paused']=True
            elif change=='authorization':s['snapshot']['authorizations'][0]['state']='revoked'
            elif change=='contract':s['snapshot']['work_packages'][0]['forbidden_paths'].append('src/a/protected')
            elif change=='host':s['worker_runtime']['workers']['worker-a']['host_available']=False
            else:s['worker_runtime']['workers']['worker-a']['authenticated']=False
            atomic_json(self.store.path,s)  # Explicit fault injection, never a production input.
            with self.subTest(change=change),self.assertRaises(ValueError):self.start(job)
            self.assert_not_launched(job)
        atomic_json(self.store.path,original)

    def test_revoke_between_reservation_and_final_guard_prevents_spawn(self):
        job=self.bound();authorize=job['bridge'].authorize;calls=[]
        def guarded(a,p):
            calls.append(1)
            if len(calls)==2:self.event('a','quota_limited')
            return authorize(a,p)
        job['executor'].authorize=guarded
        record=self.start(job)
        self.assertEqual(record['state'],'outcome_unknown')
        self.assertFalse((job['cwd']/'src/a/out.txt').exists())
        w=self.state()['workspaces'][job['authority']['workspace_id']]
        self.assertEqual(w['state'],'unknown')
        self.assertFalse(self.state()['worker_runtime']['workers']['worker-a']['stop_confirmed'])

    def test_store_commit_then_shared_fence_failure_blocks_replacement(self):
        job=self.bound()
        with patch.object(LaunchReservations,'reserve',side_effect=OSError('injected fence unavailable')):
            with self.assertRaises(OSError):self.start(job)
        self.assert_not_launched(job)
        self.assertEqual(self.state()['workspaces'][job['authority']['workspace_id']]['state'],'launching')
        replacement=self.bound(credentials=job['authority'],journal_name='replacement-journal')
        with self.assertRaises(ValueError):self.start(replacement,operation='different-key')
        self.assert_not_launched(replacement)

    def test_store_write_failure_before_commit_has_no_partial_launch(self):
        job=self.bound();before=self.store.path.read_bytes()
        with patch('framework.adapters.store_binding.atomic_json',side_effect=OSError('injected before commit')):
            with self.assertRaises(OSError):self.start(job)
        self.assertEqual(before,self.store.path.read_bytes());self.assert_not_launched(job)
        self.assertFalse((self.fence/'launches.json').exists())

    def test_new_controller_cannot_replay_an_already_launched_workspace(self):
        job=self.bound();self.finish(job,self.start(job))
        before=self.store.path.read_bytes()
        self.fence=self.root/'misconfigured-new-fence';self.fence.mkdir()
        other=self.bound(credentials=job['authority'],journal_name='other-journal')
        with self.assertRaises(ValueError):self.start(other,operation='replacement')
        self.assertEqual(before,self.store.path.read_bytes())
        self.assertEqual(list(other['journal'].glob('inv-*.json')),[])

    def test_store_commit_lost_response_is_not_retried(self):
        job=self.bound();real_atomic=atomic_json
        def lost_receipt(path,value):
            real_atomic(path,value)
            raise OSError('injected lost commit receipt')
        with patch('framework.adapters.store_binding.atomic_json',side_effect=lost_receipt):
            with self.assertRaises(OSError):self.start(job)
        self.assert_not_launched(job)
        self.assertEqual(self.state()['workspaces'][job['authority']['workspace_id']]['state'],'launching')
        with self.assertRaises(ValueError):self.start(job,operation='retry-after-lost-receipt')
        self.assert_not_launched(job)

    def test_wrong_registered_cwd_and_unrestored_handoff_block_start(self):
        job=self.bound();job['bridge'].cwd=self.root
        with self.assertRaises(ValueError):self.start(job)
        job['bridge'].cwd=job['cwd']
        s=self.state();s['workspaces'][job['authority']['workspace_id']]['recovery_source']='old-workspace'
        atomic_json(self.store.path,s)
        with self.assertRaises(ValueError):self.start(job)
        self.assert_not_launched(job)
