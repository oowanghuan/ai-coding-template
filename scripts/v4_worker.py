#!/usr/bin/env python3
"""Local lifecycle controller. Fixed observations only; no model or shell execution.

Run only from a reviewed installation. Owner actor denotes a trusted local
controller, not remote authentication. --cycles drives persistent scheduling
without an AI PMO; returned probe intents need an approved provider observer.
"""
import argparse
import json
from pathlib import Path
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from framework.local.store import Store
from framework.core.protocol import load_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['inspect', 'enable-lifecycle', 'worker-event', 'scheduler-tick', 'dispatch-next', 'cycle'])
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--actor')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--operation-id')
    parser.add_argument('--expected-revision', type=int)
    parser.add_argument('--cycles', type=int, default=1)
    parser.add_argument('--interval', type=float, default=15)
    args = parser.parse_args()
    store = Store(args.root)
    if args.action == 'inspect':
        return store.inspect()
    if not args.actor:
        raise ValueError('trusted --actor required')
    payload = load_json(args.input) if args.input else {}
    if args.action != 'cycle':
        if args.expected_revision is None or not args.operation_id:
            raise ValueError('exact revision and operation ID required')
        return store.change(args.action, payload, args.actor, args.expected_revision, args.operation_id)
    if not 1 <= args.cycles <= 1000 or not 0 <= args.interval <= 60:
        raise ValueError('bounded cycles/interval required')
    for index in range(args.cycles):
        for action in ('scheduler-tick', 'dispatch-next'):
            state = store.inspect()['state']
            try:
                result = store.change(action, {}, args.actor, state['revision'], 'cycle-' + uuid.uuid4().hex)
            except ValueError as error:
                if str(error) != 'revision conflict':
                    raise
                result = {'conflict': True, 'recompute_next_cycle': True}
            print(json.dumps({'action': action, 'result': result}), flush=True)
        if index + 1 < args.cycles:
            time.sleep(args.interval)
    return {'cycles': args.cycles, 'model_calls': 0, 'provider_execution': 'not_implemented'}


if __name__ == '__main__':
    try:
        print(json.dumps(main(), indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        sys.exit(2)
