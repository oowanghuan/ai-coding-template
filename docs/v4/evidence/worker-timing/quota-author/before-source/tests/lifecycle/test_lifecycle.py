"""Non-author Store/lifecycle checks. Worker observations are trusted synthetic fixtures.

Real temporary Git/state files are used; no supplier, model, or host driver runs.
"""
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from framework.core.protocol import load_json
from framework.local.storage import atomic_json
from framework.local.store import Store

ROOT=Path(__file__).resolve().parents[2]
OWNER='principal-owner'
AT='2026-11-28T12:00:00Z'


def later(seconds):
    return (datetime.strptime(AT,'%Y-%m-%dT%H:%M:%SZ')+timedelta(seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%SZ')


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve()
        environment=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_NAME='Synthetic Lifecycle',GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_NAME='Synthetic Lifecycle',GIT_COMMITTER_EMAIL='fixture@example.invalid')
        def git(*args):
            result=subprocess.run(['/usr/bin/git','-c','core.hooksPath=/dev/null','-c','commit.gpgsign=false',*args],cwd=self.root,env=environment,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr);return result.stdout.decode().strip()
        git('init','-q');(self.root/'src').mkdir();(self.root/'src/base.txt').write_text('fixture baseline')
        git('add','src');git('commit','-q','-m','fixture baseline');self.sha=git('rev-parse','HEAD')
        self.store=Store(self.root);self.sequence=0
    def initial(self,mutate=None):
        snapshot=load_json(ROOT/'examples/protocol/in-progress.json');snapshot['assignments']=[];snapshot['checkpoints']=[]
        original=copy.deepcopy(snapshot['work_packages'][0]);snapshot['work_packages']=[]
        snapshot['sessions']=[]
        snapshot['providers'].append({'id':'provider-c','adapter':'synthetic'})
        for index,letter in enumerate('abc'):
            worker=copy.deepcopy(snapshot['workers'][0]);worker.update(id='worker-'+letter,principal='principal-'+letter,
                provider_ref='provider-'+letter,state='available',quota='available',capabilities=['code'],role_refs=['role-developer'])
            if index<len(snapshot['workers']):snapshot['workers'][index]=worker
            else:snapshot['workers'].append(worker)
            snapshot['sessions'].append(dict(id='session-'+letter,worker_ref=worker['id'],provider_ref=worker['provider_ref'],host_ref='host-local',context_ref='synthetic-'+letter))
            wp=copy.deepcopy(original);wp.update(id='WP-'+letter.upper(),state='planned',assignment_ref=None,checkpoint_ref=None,
                baseline_sha=self.sha,allowed_paths=['src/'+letter+'/'],implementer=worker['principal'],reviewer=OWNER,acceptor=OWNER)
            snapshot['work_packages'].append(wp)
        snapshot['authorizations'][0]['wp_refs']=[w['id'] for w in snapshot['work_packages']]
        if mutate:mutate(snapshot)
        self.store.initialize(snapshot,OWNER,at=AT)
    def state(self):return self.store.inspect(at=AT)['state']
    def change(self,action,payload,at=AT,actor=OWNER,op=None,fault=None):
        self.sequence+=1
        return self.store.change(action,payload,actor,self.state()['revision'],op or 'operation-'+str(self.sequence),at=at,fault=fault)
    def result(self,action,payload,**kwargs):return self.change(action,payload,**kwargs)['operation']['result']
    def enable(self,policy=None,**extra):
        workers=[dict(worker_id='worker-'+letter,auth_identity='identity-shared' if letter in 'ab' else 'identity-c',quota_group='Q1' if letter in 'ab' else 'Q2',mode='elastic' if letter=='c' else 'dedicated',authenticated=True,authorized=True,**extra) for letter in 'abc']
        return self.result('enable-lifecycle',{'workers':workers,'policy':policy or {'heartbeat_timeout':120,'initial_backoff':5,'max_backoff':10,'max_probes':2}})
    def event(self,letter,event,at=AT,**kwargs):return self.result('worker-event',dict(worker_id='worker-'+letter,event=event,**kwargs),at=at)
    def claim(self,letter,wp=None,at=AT):
        return self.result('claim',dict(wp_id=wp or 'WP-'+letter.upper(),worker_id='worker-'+letter,session_id='session-'+letter,lease_seconds=600),actor='principal-'+letter,at=at)
    def test_enable_preserves_offline_unknown_and_requires_explicit_verified_credentials(self):
        def mutate(s):s['workers'][0]['state']='offline';s['workers'][1]['quota']='unknown'
        self.initial(mutate);self.enable()
        runtime=self.state()['worker_runtime'];self.assertEqual(runtime['workers']['worker-a']['status'],'offline')
        self.assertTrue(runtime['groups']['Q1']['limited']);self.assertNotEqual(runtime['workers']['worker-b']['status'],'available')
        with self.assertRaises(ValueError):self.claim('a')
        with self.assertRaises(ValueError):self.claim('b')
        self.assertEqual(self.claim('c')['token'],1)
    def test_unverified_credentials_do_not_get_live_authority(self):
        self.initial()
        configs=[dict(worker_id='worker-'+x,auth_identity='identity-'+x,quota_group='Q-'+x,mode='restricted') for x in 'abc']
        self.result('enable-lifecycle',{'workers':configs,'policy':{}})
        self.assertTrue(all(w['status']=='authentication_required' for w in self.state()['worker_runtime']['workers'].values()))
        with self.assertRaises(ValueError):self.claim('a')
    def test_only_owner_controller_can_mutate_runtime(self):
        self.initial();self.enable()
        for action,payload in [('worker-event',{'worker_id':'worker-a','event':'heartbeat'}),('scheduler-tick',{}),('dispatch-next',{})]:
            with self.subTest(action=action),self.assertRaisesRegex(ValueError,'owner'):
                self.change(action,payload,actor='principal-a')
    def test_shared_limit_fences_both_and_third_adapter_can_dispatch_without_pmo(self):
        self.initial();self.enable();credentials={letter:self.claim(letter) for letter in 'ab'}
        for letter in 'ab':self.result('start',credentials[letter],actor='principal-'+letter)
        self.event('a','quota_limited',retry_at=later(10))
        state=self.state();assignments=state['snapshot']['assignments']
        self.assertEqual([a['state'] for a in assignments],['revoked','revoked'])
        self.assertTrue(all(w['state']=='unknown' for w in state['workspaces'].values()))
        self.assertEqual(state['worker_runtime']['workers']['worker-c']['status'],'available')
        with patch('subprocess.Popen',side_effect=AssertionError('dispatch must not invoke model/PMO')):
            dispatch=self.result('dispatch-next',{'lease_seconds':300})
        self.assertEqual(dispatch['worker_id'],'worker-c');self.assertEqual(dispatch['wp_id'],'WP-C');self.assertEqual(dispatch['model_calls'],0)
    def test_unknown_workspace_blocks_reassignment_even_after_quota_recovers(self):
        self.initial();self.enable();old=self.claim('a');self.result('start',old,actor='principal-a')
        self.event('a','quota_limited');probe=self.result('scheduler-tick',{},at=later(5))['probes'][0]
        self.event('b','probe-result',at=later(6),probe_id=probe['probe_id'],available=True)
        with self.assertRaisesRegex(ValueError,'unknown workspace'):
            self.claim('c',wp='WP-A',at=later(6))
        self.assertFalse(self.state()['worker_runtime']['workers']['worker-a']['stop_confirmed'])
    def test_heartbeat_rechecked_on_direct_claim_start_submit(self):
        self.initial();self.enable({'heartbeat_timeout':10,'initial_backoff':5,'max_backoff':10,'max_probes':2})
        before=self.state()['revision']
        with self.assertRaisesRegex(ValueError,'heartbeat'):self.claim('b',at=later(11))
        self.assertEqual(self.state()['revision'],before)
        credentials=self.claim('a')
        with self.assertRaisesRegex(ValueError,'heartbeat'):self.result('start',credentials,actor='principal-a',at=later(11))
        self.result('start',credentials,actor='principal-a')
        with self.assertRaisesRegex(ValueError,'heartbeat'):
            self.result('submit',dict(credentials,path='src/a/out.txt',sha256='0'*64),actor='principal-a',at=later(11))
    def test_tick_expires_heartbeat_and_refresh_does_not_restore_old_rights(self):
        self.initial();self.enable({'heartbeat_timeout':10,'initial_backoff':5,'max_backoff':10,'max_probes':2})
        old=self.claim('a');self.result('start',old,actor='principal-a')
        self.result('scheduler-tick',{},at=later(10));self.event('a','heartbeat',at=later(11))
        self.assertEqual(self.state()['snapshot']['assignments'][0]['state'],'revoked')
        self.assertEqual(self.state()['worker_runtime']['workers']['worker-a']['status'],'recovering')
        with self.assertRaisesRegex(ValueError,'fenced'):self.result('start',old,actor='principal-a',at=later(11))
    def test_probe_backoff_durable_unknown_and_attempt_limit(self):
        self.initial();self.enable();self.event('a','rate_limited',retry_at=later(5))
        self.assertEqual(self.result('scheduler-tick',{},at=later(4))['probes'],[])
        first=self.result('scheduler-tick',{},at=later(5))['probes'][0]
        self.store=Store(self.root)
        self.assertEqual(self.result('scheduler-tick',{},at=later(6))['probes'],[])
        self.assertEqual(self.state()['worker_runtime']['groups']['Q1']['pending_probe'],first['probe_id'])
        self.event('a','probe-result',at=later(6),probe_id=first['probe_id'],available=False)
        self.assertEqual(self.result('scheduler-tick',{},at=later(15))['probes'],[])
        second=self.result('scheduler-tick',{},at=later(16))['probes'][0]
        self.event('a','probe-result',at=later(17),probe_id=second['probe_id'],available=False)
        self.assertEqual(self.result('scheduler-tick',{},at=later(27))['probes'],[])
        self.assertEqual(self.state()['worker_runtime']['groups']['Q1']['attempts'],2)
    def test_repeated_limit_does_not_forget_an_unknown_probe_or_reset_budget(self):
        self.initial();self.enable();self.event('a','quota_limited')
        pending=self.result('scheduler-tick',{},at=later(5))['probes'][0]
        before=copy.deepcopy(self.state()['worker_runtime']['groups']['Q1'])
        self.event('b','quota_limited',at=later(6))
        after=self.state()['worker_runtime']['groups']['Q1']
        self.assertEqual(after['pending_probe'],pending['probe_id'])
        self.assertEqual(after['attempts'],before['attempts'])
        self.assertGreater(after['generation'],before['generation'])
        self.assertEqual(self.result('scheduler-tick',{},at=later(20))['probes'],[])
    def test_newer_shared_quota_limit_cannot_be_cleared_by_older_probe_success(self):
        self.initial();self.enable();self.event('a','quota_limited',retry_at=later(5))
        old=self.result('scheduler-tick',{},at=later(5))['probes'][0]
        self.event('b','rate_limited',at=later(6),retry_at=later(30))
        self.assertEqual(self.result('scheduler-tick',{},at=later(30))['probes'],[])
        self.event('a','probe-result',at=later(31),probe_id=old['probe_id'],available=True)
        runtime=self.state()['worker_runtime'];group=runtime['groups']['Q1']
        self.assertTrue(group['limited'])
        self.assertEqual(group['retry_at'],later(30))
        self.assertEqual(group['attempts'],1)
        for worker in ('worker-a','worker-b'):
            self.assertEqual(runtime['workers'][worker]['status'],'quota_limited')
        self.assertEqual(runtime['workers']['worker-c']['status'],'available')
        current=self.result('scheduler-tick',{},at=later(32))['probes'][0]
        self.assertNotEqual(current['probe_id'],old['probe_id'])
        self.event('b','probe-result',at=later(33),probe_id=current['probe_id'],available=True)
        runtime=self.state()['worker_runtime']
        self.assertFalse(runtime['groups']['Q1']['limited'])
        self.assertEqual(runtime['groups']['Q1']['attempts'],2)
        for worker in ('worker-a','worker-b'):
            self.assertEqual(runtime['workers'][worker]['status'],'available')
    def test_new_quota_observation_and_stale_probe_completion_replays_are_idempotent(self):
        self.initial();self.enable();self.event('a','quota_limited')
        old=self.result('scheduler-tick',{},at=later(5))['probes'][0]
        payload=dict(worker_id='worker-b',event='quota_limited',retry_at=later(30))
        self.change('worker-event',payload,at=later(6),op='new-quota-observation')
        before=self.store.path.read_bytes()
        result=self.change('worker-event',payload,at=later(7),op='new-quota-observation')
        self.assertTrue(result['replayed']);self.assertEqual(self.store.path.read_bytes(),before)
        completion=dict(worker_id='worker-a',event='probe-result',probe_id=old['probe_id'],available=True)
        self.change('worker-event',completion,at=later(8),op='old-probe-completion')
        self.assertTrue(self.state()['worker_runtime']['groups']['Q1']['limited'])
        before=self.store.path.read_bytes()
        replay=self.change('worker-event',completion,at=later(9),op='old-probe-completion')
        self.assertTrue(replay['replayed']);self.assertEqual(self.store.path.read_bytes(),before)
        with self.assertRaisesRegex(ValueError,'stale/unknown probe result'):
            self.change('worker-event',completion,at=later(10),op='duplicate-old-completion')
        self.assertEqual(self.store.path.read_bytes(),before)
        self.assertEqual(self.result('scheduler-tick',{},at=later(29))['probes'],[])
    def test_owner_hold_and_budget_precede_recovered_quota(self):
        self.initial();self.enable();self.event('a','quota_limited')
        probe=self.result('scheduler-tick',{},at=later(5))['probes'][0]
        self.event('a','suspend',at=later(6));self.event('a','probe-result',at=later(7),probe_id=probe['probe_id'],available=True)
        self.assertEqual(self.state()['worker_runtime']['workers']['worker-a']['status'],'suspended')
        self.event('b','budget_exhausted',at=later(8),budget_scope='project',source='project-budget-controller')
        self.assertTrue(all(w['status']=='suspended' for w in self.state()['worker_runtime']['workers'].values()))
        self.assertIsNone(self.result('dispatch-next',{},at=later(9))['assignment_id'])
    def test_budget_scope_unknown_and_untrusted_project_source_cannot_stop_project(self):
        self.initial();self.enable();before=self.store.path.read_bytes()
        for payload in ({},{'budget_scope':'unknown'},{'budget_scope':'project','source':'provider-output'}):
            with self.subTest(payload=payload),self.assertRaises(ValueError):
                self.event('a','budget_exhausted',**payload)
            self.assertEqual(self.store.path.read_bytes(),before)
            self.assertEqual(self.state()['snapshot']['project']['budget'],'available')
    def test_invocation_budget_exhaustion_and_context_limit_are_not_account_quota(self):
        self.initial();self.enable();old=self.claim('a');self.result('start',old,actor='principal-a')
        self.event('a','budget_exhausted',budget_scope='invocation',source='trusted-adapter')
        state=self.state();self.assertEqual(state['snapshot']['project']['budget'],'available')
        self.assertFalse(state['worker_runtime']['groups']['Q1']['limited'])
        self.assertEqual(state['worker_runtime']['workers']['worker-b']['status'],'available')
        self.assertEqual(state['worker_runtime']['workers']['worker-c']['status'],'available')
        self.event('b','context_exhausted')
        self.assertFalse(self.state()['worker_runtime']['groups']['Q1']['limited'])
        self.assertEqual(self.claim('c')['token'],1)
    def test_owner_pause_and_project_budget_block_probe_intents(self):
        self.initial();self.enable();self.event('a','quota_limited')
        state=self.state();state['snapshot']['project']['paused']=True;atomic_json(self.store.path,state)
        self.assertEqual(self.result('scheduler-tick',{},at=later(5))['probes'],[])
        state=self.state();state['snapshot']['project'].update(paused=False,budget='exhausted');atomic_json(self.store.path,state)
        self.assertEqual(self.result('scheduler-tick',{},at=later(6))['probes'],[])
        self.assertIsNone(self.state()['worker_runtime']['groups']['Q1']['pending_probe'])
    def test_active_guard_also_rechecks_worker_heartbeat(self):
        self.initial();self.enable({'heartbeat_timeout':10,'initial_backoff':5,'max_backoff':10,'max_probes':2})
        old=self.claim('a');self.result('start',old,actor='principal-a')
        with patch('framework.local.store.now',return_value=later(11)),self.assertRaisesRegex(ValueError,'heartbeat'):
            self.store.guard(old,'principal-a')
    def test_failed_authentication_cannot_be_cleared_by_heartbeat(self):
        self.initial();self.enable();self.event('a','authentication_required');self.event('a','heartbeat',at=later(1))
        self.assertEqual(self.state()['worker_runtime']['workers']['worker-a']['status'],'authentication_required')
        with self.assertRaises(ValueError):self.claim('a',at=later(1))
    def test_tick_commit_response_loss_replays_same_probe_once(self):
        self.initial();self.enable();self.event('a','quota_limited')
        revision=self.state()['revision']
        def crash(point):
            if point=='after_commit':raise RuntimeError('response lost')
        with self.assertRaises(RuntimeError):self.change('scheduler-tick',{},at=later(5),op='probe-stable',fault=crash)
        resumed=Store(self.root).change('scheduler-tick',{},OWNER,revision,'probe-stable',at=later(6))
        self.assertTrue(resumed['replayed']);self.assertEqual(len(resumed['operation']['result']['probes']),1)
        self.assertEqual(self.state()['worker_runtime']['groups']['Q1']['attempts'],1)
        self.assertEqual(self.result('scheduler-tick',{},at=later(7))['probes'],[])
    def test_dispatch_does_not_consume_and_hide_due_probe(self):
        self.initial();self.enable();self.event('a','quota_limited')
        self.result('dispatch-next',{},at=later(5))
        self.assertIsNone(self.state()['worker_runtime']['groups']['Q1']['pending_probe'])
        self.assertEqual(len(self.result('scheduler-tick',{},at=later(5))['probes']),1)
    def test_ambiguous_probe_result_and_changed_replay_payload_rejected(self):
        self.initial();self.enable();self.event('a','quota_limited')
        with self.assertRaisesRegex(ValueError,'probe'):
            self.event('a','probe-result',probe_id='never-registered',available=True)
        payload={'worker_id':'worker-a','event':'heartbeat'}
        self.change('worker-event',payload,op='same-key')
        with self.assertRaisesRegex(ValueError,'different intent'):
            self.change('worker-event',dict(payload,event='resume'),op='same-key')


if __name__=='__main__':unittest.main()
