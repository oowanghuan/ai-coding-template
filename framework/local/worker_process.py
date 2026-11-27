"""Fixed synthetic worker, not an arbitrary command interpreter or model adapter."""
import json
import os
from pathlib import Path
import sys
import time

job = json.loads(sys.stdin.read())
# Python <3.10 on macOS gives monotonic_ns a process-local origin. Query the
# OS clock directly so observations from separate fixed workers are comparable.
started_ns = time.clock_gettime_ns(time.CLOCK_MONOTONIC)
time.sleep(job['delay_seconds'])
path = Path(job['path'])
path.write_text(job['content'])
print(json.dumps({'path': job['path'], 'result': 'synthetic-file-written', 'pid': os.getpid(),
                  'clock': 'CLOCK_MONOTONIC', 'started_ns': started_ns,
                  'finished_ns': time.clock_gettime_ns(time.CLOCK_MONOTONIC)}), flush=True)
