import json,sys
from pathlib import Path
request=json.loads(sys.stdin.read())
data=json.loads(Path(__file__).with_name('data.json').read_text())
value=data[request['key']]
print(value)
if value=='fail':sys.exit(1)
