#!/usr/bin/env python3
"""Trusted local controller; operate only in a reviewed installation, not candidate trees."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from framework.core.protocol import load_json
from framework.local.store import Store
from framework.local.runner import prepare, run
from framework.local.external import run_external


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'inspect', 'register-worker', 'claim', 'start', 'heartbeat',
                                         'release', 'revoke', 'reconcile', 'submit', 'run', 'run-external'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--actor')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--expected-revision', type=int)
    parser.add_argument('--operation-id')
    parser.add_argument('--launcher-config', type=Path)
    parser.add_argument('--launcher-job-id')
    args = parser.parse_args()
    store = Store(args.root)
    if args.action == 'inspect':
        return store.inspect()
    if not args.actor or args.input is None:
        raise ValueError('--actor and --input required')
    payload = load_json(args.input)
    if args.action == 'init':
        return store.initialize(payload, args.actor)
    if args.expected_revision is None or not args.operation_id:
        raise ValueError('--expected-revision and --operation-id required')
    if args.action == 'start':
        return prepare(args.root, payload, args.actor, args.expected_revision, args.operation_id)
    if args.action == 'run':
        # No arbitrary command option; this adapter only supports a fixed synthetic worker.
        return run(args.root, payload['credentials'], args.actor, payload['path'], payload['content'],
                   args.operation_id, args.expected_revision, payload.get('delay_seconds', 0))
    if args.action == 'run-external':
        if args.launcher_config is None or not args.launcher_job_id:
            raise ValueError('explicit --launcher-config and --launcher-job-id required')
        return run_external(args.root, payload['credentials'], args.actor, payload['path'], payload['content'],
                            args.operation_id, args.expected_revision, args.launcher_config, args.launcher_job_id,
                            payload.get('delay_seconds', 0), payload.get('timeout', 20))
    return store.change(args.action, payload, args.actor, args.expected_revision, args.operation_id)


if __name__ == '__main__':
    try:
        print(json.dumps(main(), indent=2))
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        sys.exit(2)
