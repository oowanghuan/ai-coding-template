#!/usr/bin/env python3
"""Verify only registered protected evidence; never execute candidate tests.

The reviewed operator must pin --trust-sha256 independently of uploaded reports.
Exit codes: 0 passed, 1 failed, 2 unverifiable or invalid invocation.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from framework.quality.gate import verify_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['verify'])
    parser.add_argument('--trust', type=Path, required=True)
    parser.add_argument('--trust-sha256', required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    result = verify_bundle(args.trust, args.trust_sha256, args.run_id)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))
    return {'passed': 0, 'failed': 1, 'unverifiable': 2}[result['status']]


if __name__ == '__main__':
    raise SystemExit(main())
