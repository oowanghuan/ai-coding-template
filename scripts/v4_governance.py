#!/usr/bin/env python3
"""Read-only local governance CLI.

Verify reports verification_scope=locked_baseline and
current_target_status=not_observed. An effective status applies only to the
locked snapshot; it does not validate the live target ref or grant merge authority.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from framework.governance.evaluate import inspect_bundle, verify_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    for name in ('verify','inspect','export','impact','append-proposal'):
        command = sub.add_parser(name, description=__doc__ if name == 'verify' else None)
        command.add_argument('--trust', required=True)
        command.add_argument('--trust-sha256', required=True)
        command.add_argument('--at', required=True)
        if name == 'verify':
            command.add_argument('--signoff', required=True); command.add_argument('--candidate', required=True)
        elif name == 'impact': command.add_argument('--changed-contract', action='append', required=True)
        elif name == 'append-proposal': command.add_argument('--source-id', required=True)
    args = parser.parse_args()
    if args.operation == 'verify':
        result = verify_bundle(args.trust, args.trust_sha256, args.signoff, args.candidate, args.at)
    else:
        result = inspect_bundle(args.trust, args.trust_sha256, args.at, args.operation,
                                getattr(args, 'changed_contract', None), getattr(args, 'source_id', None))
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False))
    return 3 if result['status']=='unverifiable' else (2 if result['status']=='rejected' else 0)


if __name__ == '__main__': sys.exit(main())
