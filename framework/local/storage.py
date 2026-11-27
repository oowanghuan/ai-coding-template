"""Trusted single-host controller primitives. Not a distributed or hostile-user lock."""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid

from framework.core.protocol import load_json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def fingerprint(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or relative.startswith('/') or '\\' in relative:
        raise ValueError('unsafe path')
    if any(p in ('', '.', '..') for p in relative.rstrip('/').split('/')):
        raise ValueError('unsafe path')
    path = root
    for part in relative.rstrip('/').split('/'):
        path = path / part
        if path.is_symlink():
            raise ValueError('symlink refused: ' + relative)
    return path


def root_path(value):
    path = Path(value).absolute()
    if not path.is_dir() or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('root must be an existing directory without symlink ancestors')
    return path


def atomic_json(path, value):
    if path.is_symlink() or (path.exists() and path.stat().st_nlink != 1):
        raise ValueError('linked authority file refused')
    temporary = path.parent / ('.write-' + uuid.uuid4().hex)
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(canonical(value) + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextlib.contextmanager
def authority_lock(root, create=False):
    directory = safe_path(root, '.ai-org')
    if create:
        directory.mkdir(mode=0o700, exist_ok=True)
    if not directory.is_dir():
        raise ValueError('project authority not initialized')
    path = safe_path(root, '.ai-org/lock')
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        if os.fstat(fd).st_nlink != 1 or not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('invalid lock file')
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)  # Never unlink the lock inode.


def check_install_journal(root):
    path = safe_path(root, '.ai-org/install-journal.json')
    if path.exists() and load_json(path)['state'] not in ('committed', 'rolled_back'):
        raise ValueError('installation outcome unknown; reconcile before authority writes')
