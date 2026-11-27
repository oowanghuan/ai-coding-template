#!/usr/bin/env python3
"""Plan/apply/rollback a minimal neutral project; never initializes Git implicitly."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from framework.core.protocol import load_json
from framework.local.bootstrap import plan, apply, rollback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan-init', 'plan-import', 'plan-upgrade', 'apply', 'rollback'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--owner')
    parser.add_argument('--project-id')
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--plan-sha256')
    parser.add_argument('--operation-id')
    args = parser.parse_args()
    if args.action.startswith('plan-'):
        return plan(args.root, args.action[5:], args.project_id, args.owner)
    if args.action == 'apply':
        if args.plan is None or not args.plan_sha256: raise ValueError('exact --plan and --plan-sha256 required')
        return apply(args.root, load_json(args.plan), args.plan_sha256)
    return rollback(args.root, args.operation_id or '')


if __name__ == '__main__':
    try:
        print(json.dumps(main(), indent=2))
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        sys.exit(2)
