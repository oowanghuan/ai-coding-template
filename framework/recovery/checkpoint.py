"""Bounded filesystem checkpoints. No Git, task-state writes, or execution authority.

The scheduler calls this at explicit events and quiesces writers for a coherent
snapshot. Two complete reads detect observed changes; this is not an atomic
filesystem snapshot or a live watcher. Pins must be retained outside candidate
write authority. Every operation is limited to its explicit directory arguments.
"""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import uuid

MAX_FILE = 16 * 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024
MAX_FILES = 4096
MAX_DIRS = 1024
MAX_MANIFEST = 4 * 1024 * 1024
SEARCH = 0x40000000 if sys.platform == 'darwin' else getattr(os, 'O_PATH', os.O_RDONLY)
ID = re.compile(r'^[A-Za-z][A-Za-z0-9._:-]{0,127}$')
SHA40 = re.compile(r'^[0-9a-f]{40}$')
SHA64 = re.compile(r'^[0-9a-f]{64}$')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(raw): return hashlib.sha256(raw).hexdigest()


def relative(value):
    if not isinstance(value, str) or not value or '\\' in value or '\0' in value:
        raise ValueError('invalid relative path')
    if any(part in ('', '.', '..') for part in value.split('/')):
        raise ValueError('traversal or absolute path refused')
    return value


def absolute(value):
    value = os.fspath(value)
    if not isinstance(value, str) or not value.startswith('/') or '..' in value.split('/') or '\0' in value:
        raise ValueError('explicit absolute non-traversing path required')
    return Path(value)


def open_directory(value):
    path = absolute(value)
    fd = os.open('/', SEARCH | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for number, part in enumerate(path.parts[1:]):
            mode = os.O_RDONLY if number == len(path.parts)-2 else SEARCH
            child = os.open(part, mode | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = child
        # Root-only input is intentionally not a useful workspace.
        if path == Path('/'): raise ValueError('filesystem root is not a work directory')
        return fd
    except BaseException:
        os.close(fd); raise


def signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def read_regular(parent, name, limit=MAX_FILE):
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > limit:
            raise ValueError('bounded single-link regular file required')
        chunks = []; count = 0
        while True:
            raw = os.read(fd, min(65536, limit + 1 - count))
            if not raw: break
            chunks.append(raw); count += len(raw)
            if count > limit: raise ValueError('file size limit exceeded')
        after = os.fstat(fd)
        if signature(before) != signature(after) or count != before.st_size:
            raise ValueError('file changed while reading')
        return b''.join(chunks), before
    finally: os.close(fd)


def write_file(parent, name, raw, executable=False):
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o700 if executable else 0o600, dir_fd=parent)
    try:
        view = memoryview(raw)
        while view:
            written = os.write(fd, view)
            if written <= 0: raise OSError('short write')
            view = view[written:]
        os.fsync(fd)
    finally: os.close(fd)


def scan(root, target=None, exclude_git=False):
    files = {}; directories = []; observations = {}; total = [0]
    def walk(source_fd, target_fd, prefix=''):
        before = os.fstat(source_fd); observations[prefix] = signature(before)
        for name in sorted(os.listdir(source_fd)):
            relative(name); path = prefix + name
            info = os.stat(name, dir_fd=source_fd, follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode): raise ValueError('symlink refused: ' + path)
            if not prefix and name == '.git' and exclude_git:
                if not stat.S_ISDIR(info.st_mode) and not (stat.S_ISREG(info.st_mode) and info.st_nlink == 1):
                    raise ValueError('unsafe excluded Git metadata')
                continue
            if stat.S_ISDIR(info.st_mode):
                directories.append(path)
                if len(directories) > MAX_DIRS: raise ValueError('directory limit exceeded')
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=source_fd)
                out = None
                try:
                    if signature(os.fstat(child)) != signature(info): raise ValueError('directory replaced while reading')
                    if target_fd is not None:
                        os.mkdir(name, 0o700, dir_fd=target_fd)
                        out = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=target_fd)
                    walk(child, out, path + '/')
                    if out is not None: os.fsync(out)
                finally:
                    os.close(child)
                    if out is not None: os.close(out)
            elif stat.S_ISREG(info.st_mode):
                raw, opened = read_regular(source_fd, name)
                if signature(info) != signature(opened): raise ValueError('file replaced while reading')
                total[0] += len(raw)
                if total[0] > MAX_TOTAL or len(files) >= MAX_FILES: raise ValueError('checkpoint size limit exceeded')
                executable = bool(opened.st_mode & stat.S_IXUSR)
                files[path] = {'sha256':digest(raw), 'size':len(raw), 'mode':'100755' if executable else '100644'}
                observations[path] = signature(opened)
                if target_fd is not None: write_file(target_fd, name, raw, executable)
            else: raise ValueError('special file refused: ' + path)
        if signature(before) != signature(os.fstat(source_fd)): raise ValueError('directory changed while reading')
    walk(root, target)
    return files, sorted(directories), observations


def publish(parent_fd, stage, destination):
    """Kernel-enforced atomic no-replace directory publication; no unsafe fallback."""
    library = ctypes.CDLL(None, use_errno=True)
    if sys.platform == 'darwin':
        fn = library.renameatx_np; flags = 0x00000004  # RENAME_EXCL, sys/stdio.h
    elif sys.platform.startswith('linux') and hasattr(library, 'renameat2'):
        fn = library.renameat2; flags = 1  # RENAME_NOREPLACE
    else: raise ValueError('atomic no-replace publication unavailable')
    fn.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    fn.restype = ctypes.c_int
    if fn(parent_fd, os.fsencode(stage), parent_fd, os.fsencode(destination), flags) != 0:
        error = ctypes.get_errno(); raise OSError(error, os.strerror(error), destination)
    os.fsync(parent_fd)


def context_valid(context):
    required = {'wp_ref','assignment_ref','authority_epoch','fencing_token','baseline_sha',
                'last_valid_commit','completed','remaining','unknown_operations'}
    if not isinstance(context, dict) or not required <= set(context): raise ValueError('checkpoint context missing binding')
    for key in ('wp_ref','assignment_ref'):
        if not isinstance(context[key], str) or not ID.fullmatch(context[key]): raise ValueError('invalid context identifier')
    for key in ('authority_epoch','fencing_token'):
        if type(context[key]) is not int or context[key] < 1: raise ValueError('invalid execution fence')
    for key in ('baseline_sha','last_valid_commit'):
        if not isinstance(context[key], str) or not SHA40.fullmatch(context[key]): raise ValueError('invalid commit binding')
    for key in ('completed','remaining'):
        values = context[key]
        if not isinstance(values, list) or any(not isinstance(v,str) or not v.strip() for v in values): raise ValueError('invalid work narrative')
    unknown = context['unknown_operations']
    if not isinstance(unknown, list): raise ValueError('unknown operations must be a list')
    ids = set()
    for value in unknown:
        if not isinstance(value,dict) or set(value) != {'id','intent','reconciliation'}: raise ValueError('invalid unknown operation')
        if any(not isinstance(value[k],str) or not value[k].strip() for k in value): raise ValueError('empty unknown operation')
        if not ID.fullmatch(value['id']) or value['id'] in ids: raise ValueError('duplicate/invalid operation ID')
        ids.add(value['id'])
    if len(canonical(context)) > MAX_MANIFEST // 2: raise ValueError('context too large')


def baseline_valid(baseline):
    if not isinstance(baseline,dict) or len(baseline)>MAX_FILES: raise ValueError('invalid baseline manifest')
    for path, entry in baseline.items():
        relative(path)
        if path == '.git' or path.startswith('.git/'): raise ValueError('Git metadata is not tracked content')
        if not isinstance(entry,dict) or set(entry) != {'sha256','mode'}: raise ValueError('invalid baseline entry')
        if not isinstance(entry['sha256'],str) or not SHA64.fullmatch(entry['sha256']) or entry['mode'] not in ('100644','100755'):
            raise ValueError('invalid baseline entry')


def distinct(source, destination):
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('source and destination must be disjoint')


def make_stage(destination):
    destination = absolute(destination)
    parent = open_directory(destination.parent)
    try:
        try: os.stat(destination.name,dir_fd=parent,follow_symlinks=False)
        except FileNotFoundError: pass
        else: raise FileExistsError('destination exists; nothing overwritten')
        name = '.checkpoint-staging-' + uuid.uuid4().hex
        os.mkdir(name, 0o700, dir_fd=parent)
        fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        return parent, name, fd
    except BaseException:
        os.close(parent); raise


def create_snapshot(workspace, destination, context, baseline_manifest, exclude_git=True):
    """Snapshot explicit content; baseline manifest is supplied by trusted scheduler.

    On failure, original content and any uniquely named incomplete staging tree
    remain preserved. An incomplete staging tree is never a published checkpoint.
    """
    workspace = absolute(workspace); destination = absolute(destination); distinct(workspace,destination)
    context_valid(context); baseline_valid(baseline_manifest)
    context = strict_json(canonical(context)); baseline_manifest = strict_json(canonical(baseline_manifest))
    if type(exclude_git) is not bool: raise ValueError('exclude_git must be boolean')
    source = open_directory(workspace)
    parent = stage_fd = data = None
    try:
        parent, stage, stage_fd = make_stage(destination)
        os.mkdir('data',0o700,dir_fd=stage_fd)
        data = os.open('data',os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,dir_fd=stage_fd)
        first = scan(source,data,exclude_git); second = scan(source,exclude_git=exclude_git)
        if first != second: raise ValueError('workspace changed across checkpoint reads')
        files, directories, _ = first
        staged_files, staged_directories, _ = scan(data)
        if staged_files != files or staged_directories != directories: raise ValueError('staging content changed before publication')
        for path, entry in files.items():
            baseline = baseline_manifest.get(path)
            entry.update(tracked=baseline is not None, dirty=baseline is None or any(entry[k]!=baseline[k] for k in ('sha256','mode')))
        manifest = {'format':'recovery-checkpoint/1','context':context,'baseline_manifest':baseline_manifest,
                    'files':files,'directories':directories,'deleted_tracked':sorted(set(baseline_manifest)-set(files)),
                    'excluded_git_metadata':exclude_git}
        raw = canonical(manifest) + b'\n'
        if len(raw)>MAX_MANIFEST: raise ValueError('manifest too large')
        write_file(stage_fd,'manifest.json',raw);os.fsync(data);os.fsync(stage_fd)
        publish(parent,stage,destination.name)
        return {'path':str(destination),'manifest_sha256':digest(raw),'file_count':len(files),
                'tracked_count':sum(v['tracked'] for v in files.values()),
                'untracked_count':sum(not v['tracked'] for v in files.values()),
                'dirty_count':sum(v['dirty'] for v in files.values()),'deleted_tracked':manifest['deleted_tracked']}
    finally:
        for fd in (data,stage_fd,parent,source):
            if fd is not None: os.close(fd)


def strict_json(raw):
    def pairs(items):
        value = {}
        for key,item in items:
            if key in value: raise ValueError('duplicate JSON key')
            value[key] = item
        return value
    def invalid(_): raise ValueError('nonfinite JSON')
    return json.loads(raw.decode(),object_pairs_hook=pairs,parse_constant=invalid)


def inspect_open(root, expected_manifest_sha256):
    if not isinstance(expected_manifest_sha256,str) or not SHA64.fullmatch(expected_manifest_sha256): raise ValueError('checkpoint pin required')
    if set(os.listdir(root)) != {'manifest.json','data'}: raise ValueError('unexpected checkpoint contents')
    raw,_ = read_regular(root,'manifest.json',MAX_MANIFEST)
    if digest(raw)!=expected_manifest_sha256: raise ValueError('checkpoint manifest fingerprint mismatch')
    manifest = strict_json(raw)
    if not isinstance(manifest,dict) or set(manifest) != {'format','context','baseline_manifest','files','directories','deleted_tracked','excluded_git_metadata'} or manifest['format']!='recovery-checkpoint/1':
        raise ValueError('invalid checkpoint manifest')
    context_valid(manifest['context']);baseline_valid(manifest['baseline_manifest'])
    if type(manifest['excluded_git_metadata']) is not bool: raise ValueError('invalid exclusion field')
    data = os.open('data',os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,dir_fd=root)
    try: files,directories,_ = scan(data)
    finally: os.close(data)
    expected = {}
    if not isinstance(manifest['files'],dict): raise ValueError('invalid files')
    for path,entry in manifest['files'].items():
        relative(path)
        if not isinstance(entry,dict) or set(entry) != {'sha256','size','mode','tracked','dirty'}: raise ValueError('invalid file entry')
        if type(entry['size']) is not int or type(entry['tracked']) is not bool or type(entry['dirty']) is not bool: raise ValueError('invalid file field types')
        baseline = manifest['baseline_manifest'].get(path)
        if entry['tracked'] != (baseline is not None) or entry['dirty'] != (baseline is None or any(entry[k]!=baseline[k] for k in ('sha256','mode'))):
            raise ValueError('false tracked/dirty classification')
        expected[path] = {key:entry[key] for key in ('sha256','size','mode')}
    if files != expected or directories != manifest['directories'] or manifest['deleted_tracked']!=sorted(set(manifest['baseline_manifest'])-set(files)):
        raise ValueError('checkpoint content/manifest mismatch')
    return manifest


def load_snapshot(path, expected_manifest_sha256):
    root = open_directory(path)
    try: return inspect_open(root,expected_manifest_sha256)
    finally: os.close(root)


def restore_snapshot(path, expected_manifest_sha256, destination):
    """Restore bytes into a new absent directory; does not grant execution rights."""
    path = absolute(path); destination = absolute(destination);distinct(path,destination)
    root = open_directory(path);parent = stage_fd = source = None
    try:
        manifest = inspect_open(root,expected_manifest_sha256)
        parent,stage,stage_fd = make_stage(destination)
        source = os.open('data',os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,dir_fd=root)
        copied = scan(source,stage_fd)
        verified = inspect_open(root,expected_manifest_sha256)
        if verified != manifest or copied[:2] != scan(stage_fd)[:2]: raise ValueError('checkpoint changed during restore')
        # Explicitly compare copied bytes with the pinned manifest, not just another
        # copy of an attacker-mutated source between validation and copying.
        expected = {p:{k:e[k] for k in ('sha256','size','mode')} for p,e in manifest['files'].items()}
        if copied[0]!=expected or copied[1]!=manifest['directories']: raise ValueError('restored bytes differ from checkpoint')
        os.fsync(stage_fd);publish(parent,stage,destination.name)
        return {'path':str(destination),'manifest_sha256':expected_manifest_sha256,'file_count':len(expected),
                'context':manifest['context'],'execution_authorized':False}
    finally:
        for fd in (source,stage_fd,parent,root):
            if fd is not None: os.close(fd)
