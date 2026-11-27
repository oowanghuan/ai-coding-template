"""Fixed synthetic worker, not an arbitrary command interpreter or model adapter."""
import json
from pathlib import Path
import sys
import time

job = json.loads(sys.stdin.read())
time.sleep(job['delay_seconds'])
path = Path(job['path'])
path.write_text(job['content'])
print(json.dumps({'path': job['path'], 'result': 'synthetic-file-written'}), flush=True)
