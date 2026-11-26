#!/usr/bin/env python3
"""Check first-round review artifacts, references and evidence integrity.

Run: python3 tests/validate_v4_design.py
This checks consistency, not evidence authenticity or independent acceptance.
"""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs/v4'
NAMES = ['V4_CHARTER.md', 'V3_INVENTORY.md', 'V4_ARCHITECTURE.md',
         'V4_MIGRATION_PLAN.md', 'V4_WORK_PACKAGES.md',
         'V4_ACCEPTANCE_PLAN.md', 'OWNER_DECISIONS.md']
BASELINE = '8ed245f5a5c7adeebd31b3f31272164ee85a1d39'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks, errors = [], []

    def check(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})
        if not condition:
            errors.append(name)

    check('seven formal deliverables exist', all((DOCS / n).is_file() for n in NAMES))
    for n in NAMES:
        path = DOCS / n
        if not path.exists():
            continue
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            rel = unquote(target.split('#')[0])
            resolved = (path.parent / rel).resolve()
            check(n + ' local link ' + rel, resolved.exists() and ROOT in resolved.parents)

    result = json.loads((DOCS / 'evidence/p0/results.json').read_text())
    # Read the recorded shape rather than treating exit zero as successful V3 behavior.
    check('P0 harness fingerprint', sha(ROOT / 'tests/p0_audit.py') == result['harness_sha256'])
    for row in result['cases']:
        check(row['id'] + ' log fingerprint', sha(DOCS / 'evidence/p0' / row['log']) == row['log_sha256'])
        check(row['id'] + ' observation matched', row['observation_matches'])
    manifest = json.loads((DOCS / 'evidence/p0/source-manifest.json').read_text())
    check('156 baseline inputs', len(manifest) == 156)
    for row in manifest:
        check('baseline input ' + row['path'], sha(ROOT / row['path']) == row['sha256'])

    poll = json.loads((DOCS / 'evidence/project-lead-poll.json').read_text())
    check('poller public snapshot fingerprint', sha(DOCS / 'evidence' / poll['public_source_snapshot']) == poll['public_source_sha256'])
    check('real model probe exists', any(r.get('model_probe') == 'passed' and r['status'] == 'success' for r in poll['runs']))
    check('real scheduled invocation exists', any(r['trigger'] == ['scheduled'] and r['status'] == 'success' for r in poll['runs']))
    check('all 12 product scenarios remain explicitly not_run', len(re.findall(r'\| S\d{2} ', (DOCS / 'V4_ACCEPTANCE_PLAN.md').read_text())) == 12 and (DOCS / 'V4_ACCEPTANCE_PLAN.md').read_text().count('**not_run**') == 12)
    wp = (DOCS / 'V4_WORK_PACKAGES.md').read_text()
    defined = set(re.findall(r'\| (WP-\d{3}) /', wp))
    refs = set(re.findall(r'WP-\d{3}', '\n'.join((DOCS / n).read_text() for n in NAMES)))
    check('all explicit work-package IDs defined', refs <= defined)
    original = subprocess.check_output(['git', 'diff', BASELINE, '--name-only'], cwd=ROOT, text=True).splitlines()
    check('no tracked V3 asset modified', all(p.startswith(('docs/v4/', 'tests/')) for p in original))
    # Preserve original captured stdout including blank lines at EOF; do not edit logs to appease Git.
    check('no whitespace errors (raw evidence EOF blank lines allowed)', subprocess.run(
        ['git', '-c', 'core.whitespace=-blank-at-eof', 'diff', '--check', BASELINE],
        cwd=ROOT, capture_output=True).returncode == 0)
    out = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'command': ['python3', 'tests/validate_v4_design.py'],
           'validator_sha256': sha(Path(__file__)), 'inputs': {n: sha(DOCS / n) for n in NAMES},
           'checks': checks, 'passed': len(checks) - len(errors), 'failed': len(errors),
           'limits': 'Author consistency check only. Does not prove test authenticity, full semantic coverage, secret absence, or independent acceptance.'}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
