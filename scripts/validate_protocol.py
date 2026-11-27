#!/usr/bin/env python3
"""Validate declared protocol consistency offline; never execute or authorize a task."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from framework.core.protocol import load_json, validate, validate_transition


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--before', type=Path)
    parser.add_argument('--at', default=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    args = parser.parse_args()
    try:
        snapshot = load_json(args.snapshot)
        errors = (validate_transition(load_json(args.before), snapshot, args.at) if args.before
                  else validate(snapshot, args.at))
        print(json.dumps({'valid': not errors, 'observation_time': args.at,
                          'scope': 'declared_consistency_only', 'errors': errors}, indent=2))
        return 2 if errors else 0
    except (ValueError, OSError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
