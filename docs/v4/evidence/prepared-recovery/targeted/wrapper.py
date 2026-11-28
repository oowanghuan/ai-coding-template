import json,os,socket,sys,unittest
from pathlib import Path
t=Path(sys.argv[1]);c=Path(sys.argv[2]);checks={}
def denied(name,action):
    try:action()
    except PermissionError:checks[name]=True
    except OSError:checks[name]=False
    else:checks[name]=False
checks['empty_candidate_anchor']=not list(c.iterdir())
denied('candidate_anchor_unlink',lambda:os.rmdir(c))
denied('trusted_write',lambda:(t/'marker').write_text('forged'))
denied('source_write',lambda:(t/'source/framework/local/handoff.py').write_text('forged'))
denied('trusted_hardlink',lambda:os.link(t/'marker',c/'alias'))
denied('outside_read',lambda:(t.parent/'outside').read_bytes())
denied('outside_write',lambda:(t.parent/'outside').write_text('forged'))
s=socket.socket()
try:denied('network',lambda:s.connect(('127.0.0.1',9)))
finally:s.close()
checks['credentials_absent']=not any(k in os.environ for k in ['GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'])
print(json.dumps({'sandbox_canaries':checks}),flush=True)
if not all(checks.values()):raise SystemExit(3)
(c/'home').mkdir();(c/'tmp').mkdir()
os.environ.update(HOME=str(c/'home'),TMPDIR=str(c/'tmp'),V4_OUTER_SEATBELT='1',V4_UNSTARTED_EVIDENCE=str(c/'evidence'))
sys.path[:0]=[str(t/'source'),str(t/'deps')]
sys.path.insert(0,str(t/'source/tests/lifecycle'))
suite=unittest.TestLoader().loadTestsFromNames([
    'test_unstarted_handoff.UnstartedHandoffTests.test_actual_authority_lock_serializes_recovery_and_launch_in_both_orders',
    'test_unstarted_handoff.UnstartedHandoffTests.test_start_bound_scope_cannot_be_reset_by_new_checkpoint'])
r=unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'run':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped)}),flush=True)
raise SystemExit(0 if r.wasSuccessful() else 1)
