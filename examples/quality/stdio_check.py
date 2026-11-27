"""Synthetic, reviewable stdio fixture; no supplier calls or external services."""
import json
from pathlib import Path
import sys

request = json.loads(sys.stdin.read())
if request['check'] == 'add':
    if type(request['a']) is not int or type(request['b']) is not int:
        print('invalid operands')
        sys.exit(2)
    print(request['a'] + request['b'])
elif request['check'] == 'required_heading':
    lines = (Path(__file__).parent / 'requirements.txt').read_text().splitlines()
    if request['heading'] not in lines:
        print('missing')
        sys.exit(1)
    print('present')
else:
    print('unknown check')
    sys.exit(2)
