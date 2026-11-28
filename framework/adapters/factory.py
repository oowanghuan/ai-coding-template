"""Explicit trusted application wiring, not a deployment or plugin loader.

Only a reviewed host controller may supply these callables, paths and settings.
No model output or project JSON can register an executor or attest its boundary.
The native recipes reuse locally inspected CLI proposals; live admission remains
the responsibility of an independently validated execution environment.
"""
import copy
from pathlib import PurePosixPath

from .invocation import ProcessExecutor, canonical_sha
from .registry import SELECTION_FIELDS, validate_descriptor
from .runspec import build_run_spec
from .store_binding import StoreBinding


def native_argv(tool, *, binary, model=None):
    """Fixed recipes for the first two tools, outside the N-provider scheduler.

    No extra flags, shell interpolation, prompt arguments or session resume.
    Produces data only; neither a boundary proof nor permission to invoke a CLI.
    Other reviewed tools can provide their own fixed argv to the same factory.
    """
    if (not isinstance(binary, str) or '\0' in binary or
            not PurePosixPath(binary).is_absolute() or
            PurePosixPath(binary).as_posix() != binary or '..' in PurePosixPath(binary).parts):
        raise ValueError('fixed absolute executable path required')
    proposal = build_run_spec(tool, work_package_id='recipe', assignment_id='recipe',
                              baseline_sha='0' * 40, prompt='recipe', model=model)
    return (binary, *proposal['argv_template'][1:])


def bind_native_store_adapter(registry, adapter, *, tool, binary, **settings):
    """First two concrete recipes; selection model cannot drift from argv.

    Tools and model providers are distinct: no provider/model identity is
    inferred from the tool name. The Store must match the explicit selection.
    This installs wiring only, and requires the same trusted boundary checker.
    """
    adapter = validate_descriptor(adapter)
    tools = {'codex': 'codex-cli', 'claude-code': 'claude-code-cli'}
    if tool not in tools or adapter['agent_tool'] != tools[tool]:
        raise ValueError('concrete tool recipe does not match registered agent tool')
    argv = native_argv(tool, binary=binary, model=adapter['model'])
    return bind_store_adapter(registry, adapter, argv=argv, **settings)


class _FactoryStoreBinding(StoreBinding):
    def __init__(self, *, boundary_check, **kwargs):
        self._boundary_check = boundary_check
        self._factory_manifest = None
        super().__init__(**kwargs)

    def boundary_valid(self):
        if self._factory_manifest is None: return False
        # Exceptions fail closed. The runtime watch also bounds a stuck check.
        return self._boundary_check(copy.deepcopy(self._factory_manifest)) is True

    def authorize(self, authority, proposal):
        return self.boundary_valid() and super().authorize(authority, proposal)


def bind_store_adapter(registry, adapter, *, planner, classifier, argv, environment,
                       pinned_files, project_root, reservation_root, journal_root,
                       actor, authority, cwd, boundary_check):
    """Bind one fixed selection and prepared workspace; does not start anything.

    boundary_check must be trusted supervisor code checking actual immutable
    deployment/isolation, configuration, credential/network and spending scope.
    It receives a detached content-bound manifest, not candidate assertions.
    Its True is an admission observation, not task authority; Store authorization
    is still required at every start. No built-in always-allow/live deployment.
    Never pass secrets in argv or pins; environment content is only hashed here.
    """
    if not all(callable(x) for x in (planner, classifier, boundary_check)):
        raise ValueError('explicit trusted planner/classifier/boundary checker required')
    adapter = validate_descriptor(adapter)
    if adapter['adapter_id'] in registry.ids(): raise ValueError('duplicate adapter identity')
    selection = {k: adapter[k] for k in SELECTION_FIELDS}
    bridge = _FactoryStoreBinding(project_root=project_root, reservation_root=reservation_root,
        actor=actor, authority=authority, selection=selection, cwd=cwd, boundary_check=boundary_check)
    executor = ProcessExecutor(selection=selection, argv=argv, cwd=cwd, environment=environment,
        journal_root=journal_root, pinned_files=pinned_files, authorize=bridge.authorize,
        launch_reservations=bridge)
    bridge._factory_manifest = dict(format='fixed-adapter-binding/1',
        execution_binding_sha256=executor.binding, selection=copy.deepcopy(selection),
        store_id=bridge.store_id, authority=copy.deepcopy(bridge.authority),
        contract_sha256=bridge.contract, authorization_sha256=bridge.authorization,
        scope=copy.deepcopy(bridge.scope), cwd=str(executor.cwd),
        reservation_root=executor.launch_domain, journal_root=str(executor.root),
        argv=list(executor.argv), environment_sha256=canonical_sha(executor.environment),
        environment_keys=sorted(executor.environment), pinned_files=copy.deepcopy(executor.pins))
    if not bridge.boundary_valid(): raise ValueError('execution boundary not admitted')
    # Factory claims only the implemented invocation operations; it never
    # promotes validation_level or asserts authentication/native recovery.
    for name in ('start', 'status', 'stop', 'result', 'checkpoint'):
        adapter['capabilities'][name] = 'supported'
    registry.register(adapter, planner=planner, classifier=classifier, executor=executor)
    return executor
