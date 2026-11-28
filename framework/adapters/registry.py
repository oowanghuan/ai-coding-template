"""N-adapter registry of explicitly registered trusted callables, never imports.

Registration belongs to reviewed application wiring. No JSON file or provider
output can supply a module path, callable, credential, capability or identity.
"""
import copy
import hashlib
import re
from functools import partial

from .results import KINDS, classify_result, strict_json, utc
from .runspec import bounded_run_request, build_run_spec

CAPABILITIES = ('auth', 'availability', 'start', 'status', 'stop', 'result', 'quota',
                'recovery', 'checkpoint', 'native_resume', 'logs', 'evidence')
SUPPORT = {'supported', 'unsupported', 'unknown'}
IDENTIFIER = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$')
SELECTION_FIELDS = ('adapter_id', 'agent_tool', 'model_provider', 'model', 'credential_ref', 'quota_group')


def validate_descriptor(value):
    required = {'format', *SELECTION_FIELDS, 'capabilities', 'validation_level'}
    if not isinstance(value, dict) or set(value) != required or value['format'] != 'adapter-descriptor/1':
        raise ValueError('exact descriptor fields required')
    for field in SELECTION_FIELDS:
        item = value[field]
        if field in ('model', 'credential_ref') and item is None: continue
        if not isinstance(item, str) or not IDENTIFIER.fullmatch(item): raise ValueError('opaque bounded selection identity')
    caps = value['capabilities']
    if not isinstance(caps, dict) or set(caps) != set(CAPABILITIES): raise ValueError('complete capability declaration required')
    if any(not isinstance(v, str) or v not in SUPPORT for v in caps.values()): raise ValueError('tri-state capability required')
    if value['validation_level'] not in ('protocol_only', 'synthetic_fixture', 'provider_live'):
        raise ValueError('validation level')
    return copy.deepcopy(value)


class AdapterRegistry:
    """Closed by default. New reviewed adapters register without changing core."""
    def __init__(self): self._adapters = {}

    def register(self, descriptor, *, planner, classifier, executor=None):
        descriptor = validate_descriptor(descriptor)
        identity = descriptor['adapter_id']
        if identity in self._adapters: raise ValueError('duplicate adapter identity')
        if not callable(planner) or not callable(classifier): raise ValueError('explicit trusted callable required')
        execution = ('start', 'status', 'stop')
        if executor is None and any(descriptor['capabilities'][k] == 'supported' for k in execution):
            raise ValueError('execution capability requires a trusted executor')
        if executor is not None:
            if executor.selection != {k: descriptor[k] for k in SELECTION_FIELDS}:
                raise ValueError('executor selection mismatch')
            if not all(callable(getattr(executor, k, None)) for k in (*execution, 'result')):
                raise ValueError('complete invocation executor required')
        self._adapters[identity] = (descriptor, planner, classifier, executor)

    def _entry(self, identity):
        if not isinstance(identity, str) or identity not in self._adapters: raise ValueError('unregistered adapter')
        return self._adapters[identity]

    def ids(self): return tuple(sorted(self._adapters))
    def describe(self, identity): return copy.deepcopy(self._entry(identity)[0])

    def plan(self, identity, **request):
        descriptor, planner, _, _ = self._entry(identity)
        if 'model' in request and request['model'] != descriptor['model']:
            raise ValueError('model must match registered selection')
        request['model'] = descriptor['model']
        value = planner(**request)
        if not isinstance(value, dict) or value.get('execution_authorized') is not False:
            raise ValueError('planner may only return nonexecuting proposal')
        value = copy.deepcopy(value)
        value['selection'] = {field: descriptor[field] for field in SELECTION_FIELDS}
        value['capabilities'] = copy.deepcopy(descriptor['capabilities'])
        value['validation_level'] = descriptor['validation_level']
        return value

    def classify(self, identity, raw, **observation):
        descriptor, _, classifier, _ = self._entry(identity)
        if descriptor['capabilities']['result'] != 'supported': raise ValueError('result capability unavailable')
        value = classifier(raw, **observation)
        if not isinstance(value, dict) or set(value) != {'kind', 'retry_at', 'provider', 'observed', 'evidence_level'}:
            raise ValueError('classification contract')
        if value['kind'] not in KINDS or not isinstance(value['observed'], dict): raise ValueError('classification kind/observation')
        if value['retry_at'] is not None: utc(value['retry_at'])
        if value['evidence_level'] not in ('untrusted_stdout', 'provider_protocol', 'synthetic_fixture'):
            raise ValueError('classification provenance')
        if descriptor['validation_level'] == 'synthetic_fixture' and value['evidence_level'] != 'synthetic_fixture':
            raise ValueError('synthetic adapter cannot claim live protocol evidence')
        value = copy.deepcopy(value); value['provider'] = descriptor['model_provider']
        value['observed']['selection'] = {field: descriptor[field] for field in SELECTION_FIELDS}
        return value

    def _invoke(self, identity, action, **kwargs):
        descriptor, _, _, executor = self._entry(identity)
        if executor is None or descriptor['capabilities'][action] != 'supported':
            raise ValueError('invocation capability unavailable')
        value = getattr(executor, action)(**kwargs)
        if (not isinstance(value, dict) or value.get('format') != 'provider-invocation/1' or
                value.get('selection') != {k: descriptor[k] for k in SELECTION_FIELDS} or
                value.get('engineering_accepted') is not False):
            raise ValueError('invocation result contract')
        return copy.deepcopy(value)

    def start(self, identity, *, operation_id, authority, **request):
        return self._invoke(identity, 'start', operation_id=operation_id, authority=authority,
                            proposal=self.plan(identity, **request))

    def status(self, identity, invocation_id):
        return self._invoke(identity, 'status', invocation_id=invocation_id)

    def stop(self, identity, invocation_id):
        return self._invoke(identity, 'stop', invocation_id=invocation_id)

    def result(self, identity, invocation_id):
        return self._invoke(identity, 'result', invocation_id=invocation_id)


def synthetic_plan(**request):
    fields = bounded_run_request(**request)
    return dict(fields, format='provider-run-proposal/1', provider='synthetic',
                argv_template=['SYNTHETIC_FIXED_EXECUTOR'], execution_authorized=False,
                compatibility='synthetic_fixture', required_boundary=['reviewed-synthetic-executor'])


def synthetic_classify(raw, *, exit_code, observed_at, evidence_level='synthetic_fixture', **extra):
    """Explicit third adapter fixture; never official or live-provider evidence."""
    if evidence_level != 'synthetic_fixture' or extra: raise ValueError('synthetic fixture interface only')
    utc(observed_at)
    if not isinstance(raw, bytes) or len(raw) > 65536: raise ValueError('fixture byte bounds')
    if exit_code is not None and (type(exit_code) is not int or not -255 <= exit_code <= 255): raise ValueError('exit code')
    observed = dict(at=observed_at, exit_code=exit_code, process_exited=exit_code is not None,
                    stdout_sha256=hashlib.sha256(raw).hexdigest(), signal='synthetic-fixture-invalid')
    out = dict(kind='error', retry_at=None, provider='synthetic', observed=observed, evidence_level='synthetic_fixture')
    try: value = strict_json(raw)
    except (ValueError, UnicodeError, RecursionError): return out
    if not isinstance(value, dict) or set(value) != {'format', 'kind', 'retry_at'} or value['format'] != 'synthetic-adapter-result/1': return out
    if not isinstance(value['kind'], str) or value['kind'] not in KINDS: return out
    if value['retry_at'] is not None:
        try: reset = utc(value['retry_at'])
        except (ValueError, TypeError): return out
        if value['kind'] not in ('rate_limited', 'quota_limited') or reset <= utc(observed_at): return out
    if value['kind'] == 'success' and exit_code != 0: return out
    out.update(kind=value['kind'], retry_at=value['retry_at']); observed['signal'] = 'explicit-synthetic-scenario'
    return out


def descriptor(adapter_id, agent_tool, model_provider, *, model=None, credential_ref=None,
               quota_group, validation_level='protocol_only'):
    caps = {name: 'unknown' for name in CAPABILITIES}
    caps.update(start='unsupported', result='supported', checkpoint='unsupported', native_resume='unsupported',
                evidence='unsupported')
    # Capability values describe the available integration, not vendor marketing.
    return validate_descriptor(dict(format='adapter-descriptor/1', adapter_id=adapter_id, agent_tool=agent_tool,
        model_provider=model_provider, model=model, credential_ref=credential_ref, quota_group=quota_group,
        capabilities=caps, validation_level=validation_level))


def default_registry():
    registry = AdapterRegistry()
    registry.register(descriptor('codex-cli', 'codex-cli', 'openai', quota_group='unconfigured-codex'),
                      planner=partial(build_run_spec, 'codex'), classifier=partial(classify_result, 'codex'))
    registry.register(descriptor('claude-code-cli', 'claude-code-cli', 'anthropic', quota_group='unconfigured-claude'),
                      planner=partial(build_run_spec, 'claude-code'), classifier=partial(classify_result, 'claude-code'))
    registry.register(descriptor('synthetic-fixture', 'synthetic-executor', 'synthetic', quota_group='fixture-quota',
                                 validation_level='synthetic_fixture'), planner=synthetic_plan, classifier=synthetic_classify)
    return registry
