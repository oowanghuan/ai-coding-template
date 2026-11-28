"""Bounded provider-event classification; provenance is supplied by a trusted caller.

A model can print any JSON. evidence_level must originate in protected supervisor
metadata, never in stdout or a candidate file. Synthetic fixtures do not establish
live provider compatibility. Classifications neither release a lease nor retry.
"""
import hashlib
import json
from datetime import datetime, timezone

PROVIDERS = {'codex', 'claude-code'}
LEVELS = {'untrusted_stdout', 'provider_protocol', 'synthetic_fixture'}
KINDS = {'rate_limited', 'quota_limited', 'context_exhausted', 'authentication_required',
         'network_error', 'budget_exhausted', 'interrupted', 'success', 'error'}
MAX_BYTES = 1024 * 1024
MAX_EVENTS = 256
MAX_LINE_BYTES = 65536
CODEX_CODES = {
    'contextWindowExceeded': 'context_exhausted',
    'sessionBudgetExceeded': 'budget_exhausted',
    'usageLimitExceeded': 'quota_limited',
    'apiKeySpendLimitExceeded': 'quota_limited',
    'projectSpendLimitExceeded': 'quota_limited',
    'organizationSpendLimitExceeded': 'quota_limited',
    'rateLimitExceeded': 'rate_limited',
    'unauthorized': 'authentication_required',
}


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError('duplicate key')
            result[key] = value
        return result
    def bad(_): raise ValueError('nonfinite number')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def utc(value):
    if not isinstance(value, str) or len(value) != 20 or not value.endswith('Z'):
        raise ValueError('explicit UTC second timestamp required')
    parsed = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    if parsed.strftime('%Y-%m-%dT%H:%M:%SZ') != value: raise ValueError('invalid UTC')
    return parsed


def reset_time(value, observed_at):
    # Never infer a reset from prose, wall-clock time, a missing field or a 429.
    if type(value) is not int or not 0 < value < 4102444800: return None
    reset = datetime.fromtimestamp(value, timezone.utc)
    return reset.strftime('%Y-%m-%dT%H:%M:%SZ') if reset > observed_at else None


def parse_events(raw):
    if len(raw) > MAX_BYTES: raise ValueError('output limit')
    lines = [line for line in raw.splitlines() if line.strip()]
    if len(lines) > MAX_EVENTS or any(len(line) > MAX_LINE_BYTES for line in lines):
        raise ValueError('event limit')
    events = [strict_json(line) for line in lines]
    if any(not isinstance(event, dict) for event in events): raise ValueError('object event required')
    return events


def codex_event(event, protocol):
    if protocol == 'codex-exec':
        if event.get('type') == 'turn.completed': return ('success', 'turn.completed', None)
        if event.get('type') in ('turn.failed', 'error'):
            # CLI error.message is prose, even when it says quota/context/reset.
            return ('error', 'exec-error-without-typed-cause', None)
        return None
    method, params = event.get('method'), event.get('params')
    if not isinstance(params, dict): return None
    if method == 'turn/completed':
        turn = params.get('turn')
        if not isinstance(turn, dict): return None
        if turn.get('status') == 'completed': return ('success', 'turn.completed', None)
        if turn.get('status') == 'interrupted': return ('interrupted', 'turn.interrupted', None)
        if turn.get('status') != 'failed': return None
        error = turn.get('error')
    elif method == 'error':
        if params.get('willRetry') is True: return ('error', 'provider-retry-in-progress', None)
        if params.get('willRetry') is not False: return ('error', 'retry-status-unknown', None)
        error = params.get('error')
    else: return None
    if not isinstance(error, dict): return ('error', 'missing-typed-cause', None)
    code = error.get('codexErrorInfo')
    if isinstance(code, str) and code in CODEX_CODES: return (CODEX_CODES[code], code, None)
    if isinstance(code, dict) and set(code) == {'httpConnectionFailed'}:
        detail = code['httpConnectionFailed']
        if isinstance(detail, dict) and set(detail) == {'httpStatusCode'}:
            status = detail['httpStatusCode']
            if status is None: return ('network_error', 'httpConnectionFailed:no-response', None)
            if type(status) is int and status == 401: return ('authentication_required', 'httpConnectionFailed:401', None)
    return ('error', 'unclassified-provider-error', None)


def claude_event(event, observed_at):
    kind = event.get('type')
    if kind == 'rate_limit_event':
        info = event.get('rate_limit_info')
        if not isinstance(info, dict) or info.get('status') != 'rejected': return None
        if info.get('errorCode') == 'credits_required':
            # Buying credits is not automatically authorized; no reset is promised.
            return ('quota_limited', 'credits_required', None)
        if info.get('errorCode') is not None: return ('error', 'unknown-limit-code', None)
        return ('rate_limited', 'rate_limit_rejected', reset_time(info.get('resetsAt'), observed_at))
    if kind == 'assistant':
        code = event.get('error')
        if code == 'authentication_failed': return ('authentication_required', code, None)
        if code == 'rate_limit': return ('rate_limited', code, None)
        if code is not None: return ('error', 'assistant-error-unclassified', None)
        if event.get('aborted') is True: return ('interrupted', 'assistant-aborted', None)
    if kind == 'result':
        subtype = event.get('subtype')
        if subtype == 'success' and event.get('is_error') is False: return ('success', 'result.success', None)
        if subtype == 'error_max_budget_usd' and event.get('is_error') is True:
            return ('budget_exhausted', subtype, None)
        if subtype == 'error_max_turns' and event.get('is_error') is True:
            return ('error', 'invocation-turn-limit', None)
        return ('error', 'result-error-unclassified', None)
    return None


def classify_result(provider, raw, *, exit_code, observed_at, evidence_level='untrusted_stdout',
                    protocol=None, supervisor_reason=None):
    """Return five stable fields. Never chooses a model, retries, pays or grants work.

    Caller-bound exit_code is an observed process outcome, not an output field.
    None means process termination is unconfirmed. Provider protocol provenance
    must be established externally. Unknown/future structures fail conservatively.
    """
    if not isinstance(provider, str) or not isinstance(evidence_level, str) or provider not in PROVIDERS or evidence_level not in LEVELS: raise ValueError('provider/evidence level')
    if not isinstance(raw, bytes): raise ValueError('raw bytes required')
    if exit_code is not None and (type(exit_code) is not int or not -255 <= exit_code <= 255):
        raise ValueError('observed exit code')
    if supervisor_reason not in (None, 'network_error', 'budget_exhausted', 'interrupted'):
        raise ValueError('unsupported supervisor reason')
    when = utc(observed_at)
    protocol = protocol or ('codex-exec' if provider == 'codex' else 'claude-stream-json')
    if protocol not in ({'codex-exec', 'codex-app-server'} if provider == 'codex' else {'claude-stream-json'}):
        raise ValueError('provider/protocol mismatch')
    observed = dict(protocol=protocol, at=observed_at, exit_code=exit_code,
                    process_exited=exit_code is not None, stdout_sha256=hashlib.sha256(raw).hexdigest(),
                    stdout_bytes=len(raw), signal='unclassified', internally_retrying=False, budget_scope=None)
    result = dict(kind='error', retry_at=None, provider=provider, observed=observed, evidence_level=evidence_level)
    if supervisor_reason is not None:
        result['kind'] = supervisor_reason; observed['signal'] = 'supervisor:' + supervisor_reason
        if supervisor_reason == 'budget_exhausted': observed['budget_scope'] = 'supervisor_unspecified'
        return result
    if exit_code is not None and exit_code < 0:
        result['kind'] = 'interrupted'; observed['signal'] = 'observed-process-signal'; return result
    if evidence_level == 'untrusted_stdout':
        observed['signal'] = 'stdout-not-authoritative'; return result
    try: events = parse_events(raw)
    except (ValueError, UnicodeError, RecursionError):
        observed['signal'] = 'malformed-or-unbounded-events'; return result
    signals = []
    for event in events:
        signal = codex_event(event, protocol) if provider == 'codex' else claude_event(event, when)
        if signal: signals.append(signal)
    observed['event_count'] = len(events)
    observed['internally_retrying'] = any(s[1] == 'provider-retry-in-progress' for s in signals)
    failures = [s for s in signals if s[0] != 'success']
    typed = [s for s in failures if s[0] != 'error']
    # A specific credits-required event refines the accompanying generic 429.
    if any(s[1] == 'credits_required' for s in typed): typed = [s for s in typed if s[0] != 'rate_limited']
    if observed['internally_retrying']:
        observed['signal'] = 'provider-retry-in-progress'; return result
    if len({s[0] for s in typed}) > 1:
        observed['signal'] = 'conflicting-provider-signals'; return result
    if typed:
        result['kind'] = typed[-1][0]; observed['signal'] = typed[-1][1]
        if result['kind'] == 'budget_exhausted':
            observed['budget_scope'] = 'session' if typed[-1][1] == 'sessionBudgetExceeded' else 'invocation'
        resets = {s[2] for s in typed if s[2] is not None}
        result['retry_at'] = resets.pop() if len(resets) == 1 else None
        return result
    if failures: observed['signal'] = failures[-1][1]; return result
    if signals and exit_code == 0:
        result['kind'] = 'success'; observed['signal'] = signals[-1][1]
    else: observed['signal'] = 'no-confirmed-terminal-success'
    return result
