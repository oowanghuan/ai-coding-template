"""Non-executing run proposals and bounded output payload validation.

These are not launcher capabilities. A trusted launcher must independently bind
its reviewed binary/config/argv/credential boundary. No subprocess is invoked.
"""
import hashlib
import re
from pathlib import PurePosixPath

from .results import PROVIDERS, strict_json

ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$')
SHA1 = re.compile(r'^[a-f0-9]{40}$')
SHA256 = re.compile(r'^[a-f0-9]{64}$')
MODEL = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$')


def bounded_run_request(*, work_package_id, assignment_id, baseline_sha, prompt,
                        timeout_seconds=120, max_output_bytes=1048576, model=None):
    """Provider-neutral bounds only; not authority or provider capability."""
    if not isinstance(work_package_id, str) or not isinstance(assignment_id, str) or not ID.fullmatch(work_package_id) or not ID.fullmatch(assignment_id): raise ValueError('identity')
    if not isinstance(baseline_sha, str) or not SHA1.fullmatch(baseline_sha): raise ValueError('baseline SHA')
    if not isinstance(prompt, str) or not prompt or '\0' in prompt or len(prompt.encode()) > 65536: raise ValueError('prompt bounds')
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 300: raise ValueError('timeout bounds')
    if type(max_output_bytes) is not int or not 1024 <= max_output_bytes <= 1048576: raise ValueError('output bounds')
    if model is not None and (not isinstance(model, str) or not MODEL.fullmatch(model)): raise ValueError('explicit model identifier')
    return dict(work_package_id=work_package_id, assignment_id=assignment_id, baseline_sha=baseline_sha,
                stdin=prompt, stdin_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                timeout_seconds=timeout_seconds, max_output_bytes=max_output_bytes, model=model)


def build_run_spec(provider, **request):
    """Two concrete CLI proposal adapters. Use AdapterRegistry for N tools/providers."""
    if not isinstance(provider, str) or provider not in PROVIDERS: raise ValueError('unsupported concrete CLI adapter')
    fields = bounded_run_request(**request)
    if provider == 'codex':
        args = ['CODEX_FIXED_BINARY', '--ask-for-approval', 'never', 'exec', '--json', '--sandbox', 'read-only']
    else:
        args = ['CLAUDE_FIXED_BINARY', '--print', '--verbose', '--output-format', 'stream-json',
                '--restricted', '--safe-mode', '--tools', '', '--disallowedTools', 'mcp__*',
                '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--setting-sources', '', '--max-turns', '1']
    if fields['model'] is not None: args.extend(['--model', fields['model']])
    if provider == 'codex': args.append('-')
    return dict(fields, format='provider-run-proposal/1', provider=provider, argv_template=args,
                execution_authorized=False, compatibility='local-cli-help-verified-live-boundary-unverified',
                required_boundary=['fixed-reviewed-binary-and-config', 'no-unreviewed-managed-customizations',
                                   'tools-hooks-mcp-disabled-and-verified', 'candidate-cannot-access-credentials',
                                   'authorized-provider-connection-only', 'owned-process-lifecycle',
                                   'protected-output-provenance', 'operator-billing-authorization'])


def safe_relative(name):
    if not isinstance(name, str) or not name or len(name.encode()) > 512 or '\\' in name or any(ord(ch) < 32 or ch == '`' for ch in name):
        raise ValueError('relative file path')
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or any(part in ('', '.', '..', '.git') for part in name.split('/')):
        raise ValueError('unsafe relative path')
    return name


def parse_proposal(raw, *, expected_baseline_sha, allowed_paths, expected_old_hashes):
    """Validate data only. Never writes files or executes a patch/command.

    All allowlists and old hashes come from protected assignment state. Applying
    validated data still requires independent lease/baseline/conflict rechecks.
    """
    if not isinstance(raw, bytes) or len(raw) > 1048576: raise ValueError('proposal bounds')
    if not isinstance(expected_baseline_sha, str) or not SHA1.fullmatch(expected_baseline_sha): raise ValueError('baseline')
    if not isinstance(allowed_paths, (list, tuple)) or len(allowed_paths) > 64: raise ValueError('scope bounds')
    allowed = {safe_relative(path) for path in allowed_paths}
    if len(allowed) != len(allowed_paths) or set(expected_old_hashes) != allowed: raise ValueError('exact assignment hash scope')
    if any(v is not None and (not isinstance(v, str) or not SHA256.fullmatch(v)) for v in expected_old_hashes.values()):
        raise ValueError('old hash binding')
    try: value = strict_json(raw)
    except (ValueError, UnicodeError, RecursionError) as error: raise ValueError('invalid proposal JSON') from error
    if not isinstance(value, dict) or set(value) != {'baseline_sha', 'files'}: raise ValueError('exact proposal fields')
    if value['baseline_sha'] != expected_baseline_sha: raise ValueError('baseline mismatch')
    files = value['files']
    if not isinstance(files, list) or not 1 <= len(files) <= 64: raise ValueError('file count')
    seen = set(); total = 0
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {'path', 'old_sha256', 'content'}: raise ValueError('exact file fields')
        path = safe_relative(entry['path'])
        if path not in allowed or path in seen: raise ValueError('outside scope or duplicate path')
        if entry['old_sha256'] != expected_old_hashes[path]: raise ValueError('old content conflict')
        content = entry['content']
        if not isinstance(content, str) or '\0' in content or len(content.encode()) > 262144: raise ValueError('text content bounds')
        total += len(content.encode()); seen.add(path)
    if total > 524288: raise ValueError('aggregate content limit')
    return value
