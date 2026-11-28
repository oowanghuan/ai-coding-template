#!/usr/bin/env python3
"""Reviewed, macOS-only launch helper for the fixed synthetic Worker demo.

Run the independently reviewed exact bytes with Python -I -S. This script never
imports project/dependency code on the host. It creates a fresh private fixture,
freezes inputs, checks isolation in the sandbox, and retains all run evidence.
It is neither a provider launcher nor an installer/background service.
On timeout it terminates only its owned process group, preserves the fixture,
and reports unknown: descendant-session termination is not proven. Never
resume/replay that fixture automatically or infer complete process-tree recovery.
"""
import argparse
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import tempfile

PYTHON = '/usr/bin/python3'
SANDBOX = '/usr/bin/sandbox-exec'
LIMIT = 64 * 1024 * 1024
DEPENDENCIES = ('jsonschema', 'jsonschema_specifications', 'referencing', 'rpds',
                'attrs', 'attr', 'typing_extensions.py')
COLLECTOR_SHA256 = 'f4ad7874c7dc9415f4dc0d1d26f2d4d095b42ef7580b786152f0886452d9ab6f'
FIRST_DELIVERY_ORACLE = b'B own delivery\n'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def regular(path, limit=LIMIT):
    """Bounded no-link reading, including every ancestor, without importing code."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute paths without parent traversal required')
    access = 0x40000000 if sys.platform == 'darwin' else getattr(os, 'O_PATH', os.O_RDONLY)
    fd = os.open('/', access | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, access | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = child
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            info = os.fstat(leaf)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
                raise ValueError('input must be bounded single-link regular file: ' + str(path))
            with os.fdopen(os.dup(leaf), 'rb') as stream:
                data = stream.read(limit + 1)
            if len(data) > limit:
                raise ValueError('input exceeds read limit')
            return data
        finally:
            os.close(leaf)
    finally:
        os.close(fd)


def canonical_directory(value):
    path = Path(value)
    if not path.is_absolute() or path.resolve() != path or not path.is_dir():
        raise ValueError('existing canonical absolute directory required: ' + str(path))
    current = Path('/')
    for part in path.parts[1:]:
        current /= part
        if not stat.S_ISDIR(current.lstat().st_mode):
            raise ValueError('linked directory refused')
    return path


def files_under(path, suffixes=None):
    if not path.is_dir() or path.is_symlink():
        raise ValueError('required input directory absent or linked: ' + str(path))
    for base, dirs, names in os.walk(path, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d != '__pycache__')
        for directory in dirs:
            if (Path(base) / directory).is_symlink():
                raise ValueError('linked input directory refused')
        for name in sorted(names):
            file = Path(base) / name
            if suffixes is None or file.suffix in suffixes:
                yield file


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def nonfinite(_): raise ValueError('nonfinite JSON number')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=nonfinite)


def positive(value):
    return type(value) is int and value > 0


def extract_first_delivery(project):
    """Read the fixed fixture result, never use candidate paths as commands.

    This is same-host fixture provenance, not authentication of hostile workers.
    Every file read rejects links; an unchanged reread detects concurrent edits.
    The Gate will attest the frozen bytes, not a claim of live C immutability.
    """
    project = canonical_directory(project)
    raw = regular(project/'.ai-org/state.json', 4 * 1024 * 1024)
    state = strict_json(raw)
    if state['format'] != 'local-state/1': raise ValueError('unsupported authority')
    delivery = state['deliveries']['WP-B']
    if (set(delivery) != {'assignment_id','epoch','token','path','sha256','content_base64','baseline_sha'}
            or delivery['path'] != 'src/b/output.txt'
            or not positive(delivery['epoch']) or not positive(delivery['token'])
            or type(delivery['assignment_id']) is not str
            or not re.fullmatch(r'assignment-[0-9a-f]{32}', delivery['assignment_id'])
            or type(delivery['baseline_sha']) is not str
            or not re.fullmatch(r'[0-9a-f]{40}', delivery['baseline_sha'])
            or type(delivery['sha256']) is not str or not re.fullmatch(r'[0-9a-f]{64}', delivery['sha256'])
            or type(delivery['content_base64']) is not str or len(delivery['content_base64']) > 90000):
        raise ValueError('invalid fixed delivery binding')
    data = base64.b64decode(delivery['content_base64'], validate=True)
    if len(data) > 65536 or sha(data) != delivery['sha256']:
        raise ValueError('delivery bytes/hash mismatch')
    def one(rows, identity):
        matches = [row for row in rows if row['id'] == identity]
        if len(matches) != 1: raise ValueError('ambiguous/missing fixture identity')
        return matches[0]
    assignment = one(state['snapshot']['assignments'], delivery['assignment_id'])
    wp = one(state['snapshot']['work_packages'], 'WP-B')
    workspace_id = assignment['workspace_id']
    if type(workspace_id) is not str or not re.fullmatch(r'workspace-[0-9a-f]{32}', workspace_id):
        raise ValueError('invalid workspace identifier')
    workspace = state['workspaces'][workspace_id]
    relative_workspace = '.ai-org/workspaces/' + workspace_id
    if (assignment['wp_ref'] != 'WP-B' or assignment['worker_ref'] != 'worker-b'
            or assignment['state'] != 'released' or assignment['base_sha'] != delivery['baseline_sha']
            or type(assignment['authority_epoch']) is not int or assignment['authority_epoch'] != delivery['epoch']
            or type(assignment['fencing_token']) is not int or assignment['fencing_token'] != delivery['token']
            or wp['assignment_ref'] != assignment['id'] or wp['baseline_sha'] != delivery['baseline_sha']
            or not positive(wp['revision']) or workspace['id'] != workspace_id
            or workspace['assignment_id'] != assignment['id'] or workspace['wp_id'] != 'WP-B'
            or workspace['baseline_sha'] != delivery['baseline_sha'] or workspace['path'] != relative_workspace
            or workspace['state'] != 'finished' or workspace['run']['state'] != 'finished'
            or type(workspace['run']['exit_code']) is not int or workspace['run']['exit_code'] != 0
            or not positive(workspace['run']['pid'])
            or workspace['run'].get('unknown_operations') != []
            or workspace['run'].get('evidence_level') != 'synthetic_fixture'):
        raise ValueError('authority/assignment/workspace binding mismatch')
    submissions = [(key, row) for key,row in state['operations'].items()
                   if row.get('action') == 'submit' and row.get('status') == 'committed']
    if not submissions or any(not positive(row.get('revision')) for _,row in submissions):
        raise ValueError('missing/invalid submission receipts')
    first_id, first = min(submissions, key=lambda item:item[1]['revision'])
    if (sum(row['result'].get('delivery_id') == 'WP-B' for _,row in submissions) != 1
            or len({row['revision'] for _,row in submissions}) != len(submissions)
            or first['result'].get('delivery_id') != 'WP-B'
            or first['result'].get('sha256') != sha(data) or first['result'].get('accepted') is not False):
        raise ValueError('first submission is not the bound WP-B delivery')
    artifact = project/relative_workspace/'src/b/output.txt'
    if regular(artifact, 65536) != data:
        raise ValueError('workspace artifact differs from captured delivery')
    if regular(project/'.ai-org/state.json', 4 * 1024 * 1024) != raw or regular(artifact, 65536) != data:
        raise ValueError('candidate delivery changed during capture')
    binding = dict(format='worker-delivery-binding/1',wp_id='WP-B',wp_revision=wp['revision'],
        assignment_id=assignment['id'],worker_id='worker-b',workspace_id=workspace_id,
        epoch=delivery['epoch'],token=delivery['token'],path='src/b/output.txt',
        artifact_sha256=sha(data),baseline_sha=delivery['baseline_sha'],authority_sha256=sha(raw),
        submit_operation_id=first_id,submit_revision=first['revision'],
        provenance='synthetic_fixture',scope='document-artifact')
    return dict(delivery_bytes=data,binding=binding,authority_sha256=sha(raw))


QUALITY_CHECKER = r'''import json,os,socket,sys
from pathlib import Path
subject=Path(__file__).parent
checks={}
def denied(name,action):
    try:action()
    except PermissionError:checks[name]=True
    else:checks[name]=False
denied('case_root_unlink',lambda:os.rmdir(Path.cwd()))
denied('trusted_plan_write',lambda:(subject.parent/'plan.json').write_text('forged'))
denied('subject_hardlink_alias',lambda:os.link(subject/'artifact.txt',Path.cwd()/'alias'))
s=socket.socket()
try:denied('network_connect',lambda:s.connect(('127.0.0.1',9)))
finally:s.close()
checks['credential_environment_absent']=not any(k in os.environ for k in
 ['GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'])
print(json.dumps({'quality_canaries':checks}),file=sys.stderr,flush=True)
if not all(checks.values()):raise SystemExit(3)
sys.stdout.buffer.write((subject/'artifact.txt').read_bytes())
'''


def make_quality_subject(trusted_run, git_root, extracted):
    """Build a real, separate Git capsule, never a fake delivered baseline SHA."""
    trusted_run = canonical_directory(trusted_run)
    subject_root = trusted_run/'subject'; subject_root.mkdir(mode=0o700)
    git_root = Path(git_root); git_root.mkdir(mode=0o700)  # exclusive fresh host-only directory
    files = {'artifact.txt':extracted['delivery_bytes'], 'check.py':QUALITY_CHECKER.encode(),
             'delivery-binding.json':canonical(extracted['binding'])}
    for name,data in files.items():
        (git_root/name).write_bytes(data); (git_root/name).chmod(0o600)
        (subject_root/name).write_bytes(data); (subject_root/name).chmod(0o400)
    env = dict(HOME=str(git_root),TMPDIR=str(git_root),PATH='/usr/bin:/bin',
               GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_TERMINAL_PROMPT='0',
               GIT_AUTHOR_NAME='Synthetic Delivery Capsule',GIT_AUTHOR_EMAIL='fixture@example.invalid',
               GIT_COMMITTER_NAME='Synthetic Delivery Capsule',GIT_COMMITTER_EMAIL='fixture@example.invalid')
    commands = []
    def git(*args):
        argv = ['/usr/bin/git','-c','core.hooksPath=/dev/null','-c','core.fsmonitor=false',
                '-c','core.untrackedCache=false','-c','commit.gpgsign=false','-c','init.templateDir=',*args]
        result = subprocess.run(argv,cwd=git_root,env=env,capture_output=True,timeout=15)
        commands.append(dict(argv=argv,exit_code=result.returncode,stdout=result.stdout.decode(errors='replace'),
                             stderr=result.stderr.decode(errors='replace')))
        write_json(trusted_run/'git-commands.json',commands)
        if result.returncode:raise ValueError('fixed capsule Git command failed')
        return result.stdout
    git('init','-q');git('add','--','artifact.txt','check.py','delivery-binding.json')
    git('commit','-qm','Synthetic document verification capsule; not a Worker code commit')
    commit=git('rev-parse','HEAD').decode().strip();tree=git('rev-parse','HEAD^{tree}').decode().strip()
    if not re.fullmatch(r'[0-9a-f]{40}',commit) or not re.fullmatch(r'[0-9a-f]{40}',tree):
        raise ValueError('unexpected Git object identity')
    raw_commit=git('cat-file','commit',commit)
    (trusted_run/'capsule.commit').write_bytes(raw_commit)
    manifest={name:dict(sha256=sha(data),mode='100644') for name,data in files.items()}
    return dict(subject=dict(commit=commit,tree=tree,manifest_sha256=sha(canonical(manifest))),
                manifest=manifest,commit_object=raw_commit.decode(),entrypoint='check.py')


def make_quality_plan(trusted_run, scratch_root, capsule, extracted, python_version):
    """The expected result is an independent fixed oracle, never captured bytes."""
    return dict(format='quality-plan/1',run_id='first-delivery',wp_id='WP-B',
        wp_revision=extracted['binding']['wp_revision'],kind='document',trusted_root=str(trusted_run),
        scratch_root=str(scratch_root),subject_root=str(Path(trusted_run)/'subject'),
        entrypoint=capsule['entrypoint'],subject=capsule['subject'],commit_object=capsule['commit_object'],
        manifest=capsule['manifest'],collector_sha256=COLLECTOR_SHA256,
        environment=dict(platform='darwin',python=PYTHON,python_version=python_version,sandbox='macos-seatbelt'),
        tests=[dict(id='document-bytes',required=True,input='',expected_exit=0,
                    expected_stdout_sha256=sha(FIRST_DELIVERY_ORACLE),timeout_seconds=5,skip_reason=None)])


WRAPPER = r'''import json,os,runpy,socket,sys
from pathlib import Path
config=json.loads(Path(sys.argv[1]).read_text())
c=Path(config['candidate']);t=Path(config['trusted']);source=t/'source'
checks={}
def denied(name, action):
    try: action()
    except PermissionError: checks[name]=True
    else: checks[name]=False
# Empty C root must remain anchored. Do this before creating home/tmp/work files.
denied('candidate_root_unlink',lambda:os.rmdir(c))
denied('trusted_write',lambda:(t/'marker').write_text('forged'))
denied('source_write',lambda:(source/'scripts/v4_worker_demo.py').write_text('forged'))
denied('trusted_hardlink_alias',lambda:os.link(t/'marker',c/'alias'))
denied('outside_read',lambda:Path(config['forbidden']).read_bytes())
denied('outside_write',lambda:Path(config['forbidden']).write_text('forged'))
s=socket.socket()
try: denied('network_connect',lambda:s.connect(('127.0.0.1',9)))
finally:s.close()
checks['credential_environment_absent']=not any(k in os.environ for k in
 ['GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'])
print(json.dumps({'sandbox_canaries':checks}),flush=True)
if not all(checks.values()):raise SystemExit(3)
(c/'home').mkdir();(c/'tmp').mkdir()
os.environ.update(HOME=str(c/'home'),TMPDIR=str(c/'tmp'),V4_OUTER_SEATBELT='1')
# -I -S suppresses user site, .pth, current directory imports and Python env paths.
sys.path[:0]=[str(source),str(t/'dependencies')]
sys.argv=[str(source/'scripts/v4_worker_demo.py'),'--root',str(c/'project')]
runpy.run_path(sys.argv[0],run_name='__main__')
'''


GATE_WRAPPER = r'''import json,os,runpy,socket,sys
from pathlib import Path
config=json.loads(Path(sys.argv[1]).read_bytes())
t=Path(config['trusted']);v=Path(config['scratch']);quality=t/'quality'
checks={}
def denied(name,action):
    try:action()
    except PermissionError:checks[name]=True
    else:checks[name]=False
denied('gate_root_unlink',lambda:os.rmdir(v))
denied('quality_receipt_write',lambda:(quality/'evidence.json').write_text('forged'))
denied('quality_receipt_hardlink',lambda:os.link(quality/'evidence.json',v/'alias'))
denied('outside_read',lambda:Path(config['forbidden']).read_bytes())
denied('outside_write',lambda:Path(config['forbidden']).write_text('forged'))
s=socket.socket()
try:denied('network_connect',lambda:s.connect(('127.0.0.1',9)))
finally:s.close()
checks['credential_environment_absent']=not any(k in os.environ for k in
 ['GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY','ANTHROPIC_API_KEY','SSH_AUTH_SOCK','CODEX_HOME'])
print(json.dumps({'gate_canaries':checks}),file=sys.stderr,flush=True)
if not all(checks.values()):raise SystemExit(3)
sys.path[:0]=[str(t/'source'),str(t/'dependencies')]
sys.argv=[str(t/'source/scripts/v4_quality.py'),'verify','--trust',str(quality/'trust.json'),
          '--trust-sha256',config['trust_sha256'],'--run-id','first-delivery']
runpy.run_path(sys.argv[0],run_name='__main__')
'''


def execute_logged(argv, cwd, environment, trusted_run, label, timeout):
    """Only internal fixed argv; record before spawn, preserve unknown outcomes."""
    record = dict(argv=argv,started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  outcome='not_started',pid=None,exit_code=None)
    write_json(trusted_run/(label+'.launch.json'),record)
    with (trusted_run/(label+'.stdout.log')).open('xb') as stdout, (trusted_run/(label+'.stderr.log')).open('xb') as stderr:
        process = subprocess.Popen(argv,cwd=cwd,env=environment,stdin=subprocess.DEVNULL,
                                   stdout=stdout,stderr=stderr,start_new_session=True,close_fds=True)
        record.update(pid=process.pid,outcome='unknown')
        write_json(trusted_run/(label+'.launch.json'),record)
        try:
            record['exit_code'] = process.wait(timeout=timeout)
            record['outcome'] = 'observed_exit'
        except BaseException as error:
            record.update(error_type=type(error).__name__,reason='owned group terminated; descendant termination not proven')
            if process.poll() is None:
                try:os.killpg(process.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:os.killpg(process.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    process.wait(timeout=5)
            record['exit_code'] = process.returncode
        finally:
            record['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            write_json(trusted_run/(label+'.result.json'),record)
    record['stdout_sha256'] = sha(regular(trusted_run/(label+'.stdout.log')))
    record['stderr_sha256'] = sha(regular(trusted_run/(label+'.stderr.log')))
    write_json(trusted_run/(label+'.result.json'),record)
    return record


def run_first_delivery_gate(fixture_root, frozen_manifest):
    """Finite opt-in document verification; no task-state write or native Agent."""
    root = canonical_directory(fixture_root); trusted = canonical_directory(root/'T')
    quality = trusted/'quality'; quality.mkdir(mode=0o700)  # never reuse intent/results
    result = dict(format='first-delivery-quality/1',passed=False,status='not_run',
                  evidence_level='synthetic_fixture',artifact_kind='document',provider_live=False,
                  engineering_accepted=False,run_id='first-delivery',authority_unchanged=None)
    try:
        if not all(sha(regular(trusted/name)) == item['sha256'] for name,item in frozen_manifest.items()):
            raise ValueError('frozen source/dependency inputs changed')
        collector = regular(trusted/'source/framework/quality/collector.py')
        if sha(collector) != COLLECTOR_SHA256:
            raise ValueError('collector is not the independently reviewed fixed program')
        extracted = extract_first_delivery(root/'C/project')
        result.update(authority_sha256=extracted['authority_sha256'],delivery_binding=extracted['binding'])
        write_json(quality/'result.json',result)
        capsule = make_quality_subject(quality,root/'G',extracted)
        scratch = root/'Q'; scratch.mkdir(mode=0o700)
        (quality/'collector.py').write_bytes(collector); (quality/'collector.py').chmod(0o400)
        environment = dict(HOME=str(quality),TMPDIR=str(scratch),PATH='/usr/bin:/bin',LC_ALL='C',LANG='C')
        version = execute_logged([PYTHON,'-I','-B','-S','--version'],quality,environment,quality,'python-version',5)
        version_text = regular(quality/'python-version.stdout.log',1024).decode().strip()
        if version['outcome'] != 'observed_exit' or version['exit_code'] != 0 or not re.fullmatch(r'Python [0-9]+\.[0-9]+\.[0-9]+',version_text):
            raise ValueError('system Python version not established')
        plan = make_quality_plan(quality,scratch,capsule,extracted,version_text.removeprefix('Python '))
        plan_bytes = canonical(plan); (quality/'plan.json').write_bytes(plan_bytes)
        trust = dict(format='quality-trust/1',runs={'first-delivery':dict(root=str(quality),
            plan_sha256=sha(plan_bytes),collector_sha256=COLLECTOR_SHA256,wp_id='WP-B',
            wp_revision=plan['wp_revision'],subject=plan['subject'])})
        trust_bytes = canonical(trust); (quality/'trust.json').write_bytes(trust_bytes)
        pinned_files = ['collector.py','plan.json','trust.json'] + ['subject/'+name for name in capsule['manifest']]
        pins = {name:sha(regular(quality/name)) for name in pinned_files}
        result.update(subject=capsule['subject'],subject_scope='verification capsule, not Worker code commit',
                      trust_sha256=sha(trust_bytes),plan_sha256=sha(plan_bytes),pinned_inputs=pins,status='collecting')
        write_json(quality/'result.json',result)
        collection = execute_logged([PYTHON,'-I','-B','-S',str(quality/'collector.py'),'--plan',str(quality/'plan.json'),
            '--plan-sha256',sha(plan_bytes)],quality,environment,quality,'collector',30)
        result['collection'] = collection
        if collection['outcome'] != 'observed_exit' or collection['exit_code'] != 0:
            raise ValueError('collection not known complete; no Gate or automatic retry')
        # A complete collection may contain failed checks. Only the Gate decides.
        verify_scratch = root/'V'; verify_scratch.mkdir(mode=0o700)
        (trusted/'gate-wrapper.py').write_text(GATE_WRAPPER)
        gate_config = dict(trusted=str(trusted),scratch=str(verify_scratch),
                           forbidden=str(root/'outside/marker'),trust_sha256=sha(trust_bytes))
        write_json(trusted/'gate-config.json',gate_config)
        (trusted/'gate-sandbox.sb').write_text(policy(trusted,verify_scratch))
        gate_controls = {name:sha(regular(trusted/name)) for name in ['gate-wrapper.py','gate-config.json','gate-sandbox.sb']}
        gate_argv = [SANDBOX,'-f',str(trusted/'gate-sandbox.sb'),PYTHON,'-I','-B','-S',
                     str(trusted/'gate-wrapper.py'),str(trusted/'gate-config.json')]
        gate_env = dict(HOME=str(verify_scratch),TMPDIR=str(verify_scratch),PATH='/usr/bin:/bin',LC_ALL='C',LANG='C')
        gate_run = execute_logged(gate_argv,trusted,gate_env,quality,'gate',30)
        result['gate_process'] = gate_run
        if gate_run['outcome'] != 'observed_exit' or gate_run['exit_code'] not in (0,1,2):
            raise ValueError('Gate execution unknown or boundary canary failed')
        gate = strict_json(regular(quality/'gate.stdout.log',1024*1024))
        if (gate.get('format') != 'quality-gate/1' or gate.get('status') not in ('passed','failed','unverifiable')
                or {'passed':0,'failed':1,'unverifiable':2}[gate['status']] != gate_run['exit_code']
                or gate.get('trust_sha256') != sha(trust_bytes)
                or gate.get('wp_id') != 'WP-B' or gate.get('wp_revision') != plan['wp_revision']
                or gate.get('subject') != capsule['subject'] or gate.get('plan_sha256') != sha(plan_bytes)):
            raise ValueError('Gate output/run binding mismatch')
        if any(sha(regular(quality/name)) != value for name,value in pins.items()):
            raise ValueError('quality protected inputs changed')
        if any(sha(regular(trusted/name)) != value for name,value in gate_controls.items()):
            raise ValueError('Gate protected controls changed')
        if not all(sha(regular(trusted/name)) == item['sha256'] for name,item in frozen_manifest.items()):
            raise ValueError('frozen inputs changed during quality run')
        current = extract_first_delivery(root/'C/project')
        result['authority_unchanged'] = current == extracted
        if not result['authority_unchanged']:raise ValueError('authority or delivery changed during quality run')
        result.update(status=gate['status'],gate=gate,passed=gate['status']=='passed',inputs_unchanged=True)
    except BaseException as error:
        result.update(status='error',passed=False,error_type=type(error).__name__,error=str(error))
    write_json(quality/'result.json',result)
    return result


def policy(trusted, candidate):
    # C's parent is not writable; explicit unlink denial additionally pins C itself.
    q = lambda p: json.dumps(str(p))
    reads = ['/System', '/usr', '/Library/Developer', '/Library/Apple',
             '/private/var/db/dyld', '/bin', '/sbin', '/private/preboot/Cryptexes', trusted, candidate]
    return '\n'.join([
        '(version 1)', '(deny default)', '(allow process*)',
        '(deny process-info* (target others))', '(allow file-read-metadata)',
        '(allow mach-lookup (global-name "com.apple.system.logger"))',
        '(deny mach-lookup (global-name "com.apple.securityd") (global-name "com.apple.security.agent"))',
        '(allow file-read* ' + ' '.join('(subpath '+q(p)+')' for p in reads) +
        ' (literal "/dev/null") (literal "/dev/urandom") (literal "/"))',
        '(allow file-map-executable)',
        '(allow file-write* (subpath '+q(candidate)+') (literal "/dev/null"))',
        '(deny file-write-unlink (literal '+q(candidate)+'))',
        '(allow signal (target children))', ''])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, help='approved read-only source tree; no network operations')
    parser.add_argument('--dependencies', required=True, help='existing system-Python-compatible site-packages; never installs packages')
    parser.add_argument('--verify-first-delivery', action='store_true',
                        help='also collect actual document-artifact evidence; never mark the code WP accepted')
    args = parser.parse_args()
    if sys.platform != 'darwin' or not sys.flags.isolated or not sys.flags.no_site:
        raise ValueError('run on macOS with python3 -I -S; helper bytes require independent review first')
    source = canonical_directory(args.source); dependencies = canonical_directory(args.dependencies)
    root = Path(tempfile.mkdtemp(prefix='v4-worker-demo-', dir='/private/tmp'))
    trusted = root/'T'; candidate = root/'C'; forbidden = root/'outside'
    for p in (trusted, candidate, forbidden): p.mkdir(mode=0o700)
    print('Evidence directory: ' + str(root), flush=True)
    manifest = {}; total = 0
    def freeze(original, target):
        nonlocal total
        data = regular(original); total += len(data)
        if total > 256 * 1024 * 1024 or len(manifest) >= 10000:
            raise ValueError('frozen input set exceeds bounded fixture size')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream: stream.write(data)
        target.chmod(0o400)
        manifest[str(target.relative_to(trusted))] = {'original':str(original),'sha256':sha(data),'bytes':len(data)}
    summary = {'format':'worker-demo-launch/1','evidence_level':'synthetic_fixture',
               'provider_live':False,'engineering_accepted':False,'passed':False,
               'verify_first_delivery':args.verify_first_delivery,
               'launcher_sha256':sha(regular(Path(__file__).absolute())), 'fixture':str(root)}
    proc = None
    try:
        for relative in ('framework', 'schemas'):
            for original in files_under(source/relative, {'.py'} if relative=='framework' else {'.json'}):
                freeze(original, trusted/'source'/original.relative_to(source))
        for relative in ('examples/protocol/in-progress.json','scripts/v4_worker_demo.py'):
            freeze(source/relative, trusted/'source'/relative)
        if args.verify_first_delivery:
            freeze(source/'scripts/v4_quality.py', trusted/'source/scripts/v4_quality.py')
        # Freeze just the explicit installed jsonschema dependency closure. .pth is
        # never copied/executed; optional format extras are intentionally unavailable.
        for name in DEPENDENCIES:
            original = dependencies/name
            if original.is_dir():
                for file in files_under(original): freeze(file,trusted/'dependencies'/file.relative_to(dependencies))
            else: freeze(original,trusted/'dependencies'/name)
        for directory in sorted(dependencies.glob('*.dist-info')):
            normalized=directory.name.lower().replace('-','_')
            if any(normalized.startswith(name+'_') for name in
                   ('jsonschema','jsonschema_specifications','referencing','rpds_py','attrs','typing_extensions')):
                for file in files_under(directory): freeze(file,trusted/'dependencies'/file.relative_to(dependencies))
        (trusted/'marker').write_text('protected marker\n');(forbidden/'marker').write_text('synthetic outside marker\n')
        (trusted/'wrapper.py').write_text(WRAPPER)
        write_json(trusted/'config.json',dict(candidate=str(candidate),trusted=str(trusted),forbidden=str(forbidden/'marker')))
        (trusted/'sandbox.sb').write_text(policy(trusted,candidate))
        write_json(trusted/'inputs.json',manifest)
        control_files = ['marker','wrapper.py','config.json','sandbox.sb','inputs.json']
        before = {name:sha(regular(trusted/name)) for name in control_files}
        argv = [SANDBOX,'-f',str(trusted/'sandbox.sb'),PYTHON,'-I','-B','-S',str(trusted/'wrapper.py'),str(trusted/'config.json')]
        env = {'HOME':str(candidate/'home'),'TMPDIR':str(candidate/'tmp'),
               'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LC_ALL':'C','LANG':'C'}
        summary.update(argv=argv,environment=env,started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       frozen_inputs=manifest,control_hashes=before)
        write_json(trusted/'launch.json',summary)
        with (trusted/'stdout.log').open('xb') as stdout, (trusted/'stderr.log').open('xb') as stderr:
            proc=subprocess.Popen(argv,cwd=trusted,env=env,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,start_new_session=True)
            summary['pid']=proc.pid
            try:
                summary['exit_code']=proc.wait(timeout=180)
                summary['outcome']='observed_exit'
            except subprocess.TimeoutExpired:
                # Only this owned Popen group. Descendant sessions may remain;
                # never read candidate PID files or pretend all writers stopped.
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
                summary.update(exit_code=proc.returncode,outcome='unknown',reason='deadline; descendant stop not proven')
        after={name:sha(regular(trusted/name)) for name in control_files}
        unchanged=all(sha(regular(trusted/name))==item['sha256'] for name,item in manifest.items()) and before==after
        summary.update(inputs_unchanged=unchanged,stdout_sha256=sha(regular(trusted/'stdout.log')),
                       stderr_sha256=sha(regular(trusted/'stderr.log')),
                       finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        # Exit proves only this fixed demonstration exited normally, not tests or
        # delivery acceptance. Raw stdout contains canaries and the demo summary.
        summary['passed']=summary['outcome']=='observed_exit' and summary['exit_code']==0 and unchanged
        if args.verify_first_delivery and summary['passed']:
            summary['demo_passed'] = True
            summary['passed'] = False
            summary['quality'] = run_first_delivery_gate(root,manifest)
            summary['passed'] = summary['quality']['passed']
    except BaseException as error:
        summary.update(outcome='error',passed=False,error_type=type(error).__name__,error=str(error))
        if proc is not None and proc.poll() is None:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
            summary['descendant_stop']='unknown'
    summary['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write_json(trusted/'result.json',summary)
    print(json.dumps({'passed':summary['passed'],'outcome':summary.get('outcome'),'evidence':str(trusted/'result.json')}))
    return 0 if summary['passed'] else 1


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError) as error:
        print(str(error),file=sys.stderr);sys.exit(2)
