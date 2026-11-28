"""Registry extension and synthetic third-adapter contracts, not provider-live tests."""
import json
import unittest

from framework.adapters import AdapterRegistry, CAPABILITIES, default_registry, descriptor
from framework.adapters.registry import synthetic_classify, synthetic_plan

BASE='a'*40
NOW='2026-11-27T00:00:00Z'


def request():return dict(work_package_id='WP-301',assignment_id='ASSIGN-3',baseline_sha=BASE,prompt='approved bounded fixture task')
def event(kind='success',retry_at=None):return json.dumps(dict(format='synthetic-adapter-result/1',kind=kind,retry_at=retry_at)).encode()


class RegistryTests(unittest.TestCase):
    def test_three_builtin_adapters_and_generic_capabilities(self):
        registry=default_registry();self.assertEqual(registry.ids(),('claude-code-cli','codex-cli','synthetic-fixture'))
        for identity in registry.ids():
            d=registry.describe(identity);self.assertEqual(set(d['capabilities']),set(CAPABILITIES))
            self.assertTrue(set(d['capabilities'].values())<={'supported','unsupported','unknown'})
            self.assertEqual(d['capabilities']['start'],'unsupported')

    def test_third_adapter_uses_identical_plan_and_result_interface(self):
        registry=default_registry()
        for identity in registry.ids():
            p=registry.plan(identity,**request());self.assertFalse(p['execution_authorized'])
            self.assertEqual(p['selection']['adapter_id'],identity)
        p=registry.plan('synthetic-fixture',**request());self.assertEqual(p['validation_level'],'synthetic_fixture')
        out=registry.classify('synthetic-fixture',event(),exit_code=0,observed_at=NOW)
        self.assertEqual(out['kind'],'success');self.assertEqual(out['provider'],'synthetic')
        self.assertEqual(out['evidence_level'],'synthetic_fixture')

    def test_nth_adapter_registration_needs_no_core_provider_branch(self):
        registry=default_registry();d=descriptor('fourth','other-agent','other-model-vendor',model='model-z',credential_ref='credential-ref-z',quota_group='shared-team-quota',validation_level='synthetic_fixture')
        registry.register(d,planner=synthetic_plan,classifier=synthetic_classify)
        p=registry.plan('fourth',**request());self.assertEqual(p['selection']['agent_tool'],'other-agent')
        out=registry.classify('fourth',event('quota_limited'),exit_code=1,observed_at=NOW)
        self.assertEqual(out['provider'],'other-model-vendor');self.assertEqual(out['kind'],'quota_limited')
        self.assertEqual(out['observed']['selection']['credential_ref'],'credential-ref-z')

    def test_selection_axes_are_independent(self):
        first=descriptor('a','tool-a','vendor-a',model='model-a',credential_ref='cred-a',quota_group='shared')
        second=descriptor('b','tool-b','vendor-a',model='model-b',credential_ref='cred-b',quota_group='shared')
        self.assertNotEqual(first['agent_tool'],second['agent_tool']);self.assertEqual(first['model_provider'],second['model_provider'])
        self.assertNotEqual(first['credential_ref'],second['credential_ref']);self.assertEqual(first['quota_group'],second['quota_group'])

    def test_describe_and_registration_are_defensive_copies(self):
        r=AdapterRegistry();d=descriptor('x','tool','vendor',quota_group='q')
        r.register(d,planner=synthetic_plan,classifier=synthetic_classify);d['quota_group']='wrong'
        clone=r.describe('x');clone['capabilities']['start']='supported'
        self.assertEqual(r.describe('x')['quota_group'],'q');self.assertEqual(r.describe('x')['capabilities']['start'],'unsupported')

    def test_unknown_adapter_is_rejected(self):
        r=default_registry()
        for op in (lambda:r.describe('arbitrary'),lambda:r.plan('arbitrary',**request()),lambda:r.classify('arbitrary',event(),exit_code=0,observed_at=NOW)):
            with self.assertRaises(ValueError):op()

    def test_duplicate_adapter_rejected(self):
        r=default_registry()
        with self.assertRaises(ValueError):r.register(r.describe('synthetic-fixture'),planner=synthetic_plan,classifier=synthetic_classify)

    def test_json_module_paths_cannot_register_handlers(self):
        r=AdapterRegistry();d=descriptor('x','tool','vendor',quota_group='q')
        with self.assertRaises(ValueError):r.register(d,planner='arbitrary.module.run',classifier='eval')
        d['module']='arbitrary'
        with self.assertRaises(ValueError):r.register(d,planner=synthetic_plan,classifier=synthetic_classify)

    def test_missing_or_boolean_capability_rejected(self):
        for kind in ('missing','boolean'):
            d=descriptor('x','tool','vendor',quota_group='q')
            if kind=='missing':del d['capabilities']['quota']
            else:d['capabilities']['quota']=True
            with self.assertRaises(ValueError):AdapterRegistry().register(d,planner=synthetic_plan,classifier=synthetic_classify)

    def test_absent_result_capability_fails_closed(self):
        r=AdapterRegistry();d=descriptor('x','tool','vendor',quota_group='q');d['capabilities']['result']='unknown'
        r.register(d,planner=synthetic_plan,classifier=synthetic_classify)
        with self.assertRaises(ValueError):r.classify('x',event(),exit_code=0,observed_at=NOW)

    def test_opaque_credential_reference_is_not_path_or_environment(self):
        for ref in ('/home/auth.json','TOKEN=secret','https://credentials.invalid'):
            with self.assertRaises(ValueError):descriptor('x','tool','vendor',credential_ref=ref,quota_group='q')

    def test_caller_cannot_silently_change_registered_model(self):
        r=default_registry()
        with self.assertRaises(ValueError):r.plan('codex-cli',model='unregistered-model',**request())

    def test_synthetic_adapter_cannot_claim_provider_protocol_or_live(self):
        r=default_registry()
        for level in ('provider_protocol','provider_live','untrusted_stdout'):
            with self.assertRaises(ValueError):r.classify('synthetic-fixture',event(),exit_code=0,observed_at=NOW,evidence_level=level)

    def test_synthetic_quota_has_no_implicit_reset(self):
        r=default_registry();out=r.classify('synthetic-fixture',event('quota_limited'),exit_code=1,observed_at=NOW)
        self.assertIsNone(out['retry_at']);self.assertEqual(out['evidence_level'],'synthetic_fixture')
        out=r.classify('synthetic-fixture',event('rate_limited','2030-01-01T00:00:00Z'),exit_code=1,observed_at=NOW)
        self.assertEqual(out['retry_at'],'2030-01-01T00:00:00Z')

    def test_synthetic_wrong_exit_no_success_or_implicit_stop(self):
        r=default_registry();out=r.classify('synthetic-fixture',event(),exit_code=None,observed_at=NOW)
        self.assertEqual(out['kind'],'error');self.assertFalse(out['observed']['process_exited'])

    def test_registry_rejects_malicious_handler_contract(self):
        r=AdapterRegistry();d=descriptor('x','tool','vendor',quota_group='q')
        r.register(d,planner=lambda **kw:{'execution_authorized':True},classifier=lambda *a,**k:{'kind':'accepted'})
        with self.assertRaises(ValueError):r.plan('x',**request())
        with self.assertRaises(ValueError):r.classify('x',event(),exit_code=0,observed_at=NOW)

if __name__=='__main__':unittest.main()
