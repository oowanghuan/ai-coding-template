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
import datetime
import hashlib
import json
import os
from pathlib import Path
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


def sha(data):
    return hashlib.sha256(data).hexdigest()


def regular(path):
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
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > LIMIT:
                raise ValueError('input must be bounded single-link regular file: ' + str(path))
            with os.fdopen(os.dup(leaf), 'rb') as stream:
                data = stream.read(LIMIT + 1)
            if len(data) > LIMIT:
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
    parser.add_argument('--source', required=True, help='approved source tree; no Git/network operations')
    parser.add_argument('--dependencies', required=True, help='existing system-Python-compatible site-packages; never installs packages')
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
               'launcher_sha256':sha(regular(Path(__file__).absolute())), 'fixture':str(root)}
    proc = None
    try:
        for relative in ('framework', 'schemas'):
            for original in files_under(source/relative, {'.py'} if relative=='framework' else {'.json'}):
                freeze(original, trusted/'source'/original.relative_to(source))
        for relative in ('examples/protocol/in-progress.json','scripts/v4_worker_demo.py'):
            freeze(source/relative, trusted/'source'/relative)
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
    except BaseException as error:
        summary.update(outcome='error',error_type=type(error).__name__,error=str(error))
        if proc is not None and proc.poll() is None:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
            summary['descendant_stop']='unknown'
    write_json(trusted/'result.json',summary)
    print(json.dumps({'passed':summary['passed'],'outcome':summary.get('outcome'),'evidence':str(trusted/'result.json')}))
    return 0 if summary['passed'] else 1


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError) as error:
        print(str(error),file=sys.stderr);sys.exit(2)
