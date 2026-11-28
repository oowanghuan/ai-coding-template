"""Factory contracts with fixed real executables; native recipes never run."""
import json
import time
import unittest
from unittest.mock import patch

import test_store_binding as helpers
from framework.adapters.factory import bind_store_adapter, bind_native_store_adapter, native_argv
from framework.adapters.registry import AdapterRegistry, synthetic_plan, synthetic_classify, descriptor


class FactoryTests(unittest.TestCase):
    setUp = helpers.StoreBindingTests.setUp
    initial = helpers.StoreBindingTests.initial
    state = helpers.StoreBindingTests.state
    change = helpers.StoreBindingTests.change
    result = helpers.StoreBindingTests.result
    enable = helpers.StoreBindingTests.enable
    event = helpers.StoreBindingTests.event
    claim = helpers.StoreBindingTests.claim
    stop_owned = helpers.StoreBindingTests.stop_owned
    bound = helpers.StoreBindingTests.bound
    start = helpers.StoreBindingTests.start
    finish = helpers.StoreBindingTests.finish

    def prepare_factory(self, *, check=None, program=None):
        job = self.bound(program=program)
        old = job['executor']
        adapter = job['registry'].describe('synthetic')
        job['registry'] = AdapterRegistry()
        options = dict(planner=synthetic_plan, classifier=synthetic_classify,
            argv=list(old.argv), environment=dict(old.environment), pinned_files=dict(old.pins),
            project_root=self.root, reservation_root=self.fence, journal_root=job['journal'],
            actor='principal-a', authority=job['authority'], cwd=job['cwd'],
            boundary_check=check if check is not None else lambda manifest: True)
        return job, adapter, options

    def bind(self, job, adapter, options):
        job['executor'] = bind_store_adapter(job['registry'], adapter, **options)
        self.executors.append(job['executor'])
        return job

    def test_native_recipes_are_nonexecuting_fixed_arguments(self):
        codex = native_argv('codex', binary='/fixed/codex', model='model-a')
        claude = native_argv('claude-code', binary='/fixed/claude', model='model-b')
        self.assertEqual(codex, ('/fixed/codex','--ask-for-approval','never','exec','--json',
                                '--sandbox','read-only','--model','model-a','-'))
        self.assertIn('--restricted', claude);self.assertIn('--safe-mode', claude)
        self.assertEqual(claude[claude.index('--tools')+1], '')
        self.assertEqual(claude[-2:], ('--model','model-b'))
        for binary in ['relative', '/fixed/../cli', '/fixed//cli', '/fixed/cli\0']:
            with self.assertRaises(ValueError): native_argv('codex',binary=binary)
        with self.assertRaises(ValueError): native_argv('unregistered',binary='/fixed/cli')
        with self.assertRaises(ValueError): native_argv('codex',binary='/fixed/cli',model='x --unsafe')

    def test_factory_registration_does_not_launch_or_write_authority(self):
        observations=[]
        job,d,opts=self.prepare_factory(check=lambda m: observations.append(m) or True)
        before=self.store.path.read_bytes();self.bind(job,d,opts)
        self.assertEqual(before,self.store.path.read_bytes());self.assertEqual(len(observations),1)
        self.assertFalse(list(job['journal'].glob('inv-*.json')))
        m=observations[0]
        self.assertEqual(m['execution_binding_sha256'],job['executor'].binding)
        self.assertEqual(m['selection'],job['executor'].selection)
        self.assertNotIn('environment',m)
        self.assertEqual(job['registry'].describe('synthetic')['validation_level'],'synthetic_fixture')
        self.assertEqual(job['registry'].describe('synthetic')['capabilities']['native_resume'],'unsupported')

    def test_native_factory_binds_selection_model_without_assuming_provider(self):
        for tool,agent in [('codex','codex-cli'),('claude-code','claude-code-cli')]:
            d=descriptor('custom-entry',agent,'enterprise-provider',model='selected-model',quota_group='shared')
            # Native assembly only; never execute either CLI in this evidence.
            with patch('framework.adapters.factory.bind_store_adapter') as bind:
                bind_native_store_adapter(AdapterRegistry(),d,tool=tool,binary='/fixed/tool',
                                          boundary_check=lambda m:False)
                args=bind.call_args.kwargs['argv']
                self.assertEqual(args[args.index('--model')+1],d['model'])
                self.assertEqual(bind.call_args.args[1]['model_provider'],'enterprise-provider')
            d['agent_tool']='other-tool'
            with self.assertRaises(ValueError):
                bind_native_store_adapter(AdapterRegistry(),d,tool=tool,binary='/fixed/tool')

    def test_third_tool_fixed_process_roundtrip_and_replay(self):
        job,d,opts=self.prepare_factory();self.bind(job,d,opts)
        first=self.start(job);done=self.finish(job,first)
        result=job['registry'].result('synthetic',first['invocation_id'])
        self.assertEqual(done['exit_code'],0);self.assertFalse(result['engineering_accepted'])
        self.assertTrue(result['store_observation']['observed'])
        again=self.start(job);self.assertEqual(first['invocation_id'],again['invocation_id'])
        self.assertEqual((job['cwd']/'src/a/out.txt').read_text(),'fixed result')
        self.assertEqual(len(list(job['journal'].glob('inv-*.json'))),1)
        print(json.dumps({'fixed_factory':dict(selection=result['selection'],state=done['state'],
            actual_exit_code=done['exit_code'],store_observed=True,invocation_records=1,
            native_model_calls=0,engineering_accepted=False)}),flush=True)

    def test_missing_false_unknown_or_throwing_boundary_never_registers(self):
        job,d,opts=self.prepare_factory();before=self.store.path.read_bytes()
        def fail(m):raise OSError('boundary unavailable')
        for check in [None, lambda m:False, lambda m:None, lambda m:1, fail]:
            opts['boundary_check']=check
            with self.subTest(check=check),self.assertRaises((ValueError,OSError)):
                self.bind(job,d,opts)
            self.assertEqual(job['registry'].ids(),())
        self.assertEqual(before,self.store.path.read_bytes())

    def test_boundary_revoked_after_binding_rejects_before_launch(self):
        allowed=[True];job,d,opts=self.prepare_factory(check=lambda m:allowed[0])
        self.bind(job,d,opts);allowed[0]=False;before=self.store.path.read_bytes()
        with self.assertRaises(ValueError):self.start(job)
        self.assertEqual(before,self.store.path.read_bytes())
        self.assertFalse(list(job['journal'].glob('inv-*.json')))

    def test_boundary_revoked_while_running_stops_owned_process(self):
        allowed=[True];job,d,opts=self.prepare_factory(check=lambda m:allowed[0],
            program="from pathlib import Path;import time;Path('ready').touch();time.sleep(10)")
        self.bind(job,d,opts);job['request']['timeout_seconds']=10;record=self.start(job)
        deadline=time.monotonic()+3
        while not (job['cwd']/'ready').exists() and time.monotonic()<deadline:time.sleep(.01)
        self.assertTrue((job['cwd']/'ready').exists());allowed[0]=False
        done=self.finish(job,record);self.assertEqual(done['stop_reason'],'authority_revoked')
        self.assertFalse(done['writer_stop_confirmed'])

    def test_detached_configuration_and_boundary_manifest(self):
        def observed(m):m['argv'][0]='/bad/program';m['selection']['model_provider']='bad';return True
        job,d,opts=self.prepare_factory(check=observed);self.bind(job,d,opts)
        opts['argv'][0]='/bad/program';opts['environment']['INJECT']='yes';d['model_provider']='bad'
        self.assertEqual(job['executor'].argv[0],'/usr/bin/python3')
        self.assertNotIn('INJECT',job['executor'].environment)
        self.assertEqual(self.finish(job,self.start(job))['exit_code'],0)

    def test_model_or_registry_selection_cannot_override_fixed_resource(self):
        job,d,opts=self.prepare_factory();self.bind(job,d,opts)
        with self.assertRaises(ValueError):job['registry'].start('synthetic',operation_id='bad',
            authority=job['authority'],model='different-model',**job['request'])
        with self.assertRaises(ValueError):self.bind(job,d,opts)
        self.assertFalse(list(job['journal'].glob('inv-*.json')))

    def test_pinned_config_changed_after_binding_blocks_start(self):
        job,d,opts=self.prepare_factory();config=self.root/'trusted-config';config.write_text('fixed')
        import hashlib
        opts['pinned_files'][str(config)]=hashlib.sha256(config.read_bytes()).hexdigest()
        self.bind(job,d,opts);config.write_text('changed');before=self.store.path.read_bytes()
        with self.assertRaises(ValueError):self.start(job)
        self.assertEqual(before,self.store.path.read_bytes())

    def test_valid_boundary_does_not_override_store_quota(self):
        job,d,opts=self.prepare_factory();self.bind(job,d,opts);self.event('a','quota_limited')
        with self.assertRaises(ValueError):self.start(job)
        self.assertFalse(list(job['journal'].glob('inv-*.json')))
