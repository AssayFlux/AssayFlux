"""Local-first structured diagnostics with bounded, permission-restricted storage."""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path

from .model import Diagnostic

DEFAULT_REPORT_DIR = Path(os.environ.get("ASSAYFLUX_REPORT_DIR", Path.home() / ".assayflux" / "reports"))
MAX_REPORT_BYTES = 10 * 1024 * 1024
MAX_REPORTS = 20_000


def _private_dir(path: Path) -> Path:
    path = path.expanduser()
    if path.is_symlink():
        raise OSError("Diagnostic directory must not be a symbolic link")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode):
        raise OSError("Diagnostic path is not a directory")
    try: path.chmod(0o700)
    except OSError: pass
    return path


def _set_private_mode(fd: int, path: Path) -> None:
    """Set restrictive permissions on POSIX and remain compatible with Windows."""
    fchmod = getattr(os, "fchmod", None)
    if fchmod is not None:
        fchmod(fd, 0o600)
    else:
        if path.is_symlink():
            raise OSError("Diagnostic report path must not be a symbolic link")
        os.chmod(path, 0o600)


def _regular_file_size(path: Path) -> int:
    try: info = path.lstat()
    except FileNotFoundError: return 0
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise OSError("Diagnostic report target must be a regular non-symlink file")
    return info.st_size


def write_report(diagnostic: Diagnostic, report_dir: Path | None = None) -> Path:
    """Append a minimized JSONL diagnostic without following a report-file symlink."""
    root = _private_dir(Path(report_dir) if report_dir is not None else DEFAULT_REPORT_DIR)
    target = root / "diagnostics.jsonl"
    rotated = root / "diagnostics.previous.jsonl"
    if _regular_file_size(target) >= MAX_REPORT_BYTES:
        _regular_file_size(rotated)
        try: rotated.unlink()
        except FileNotFoundError: pass
        os.replace(target, rotated)
        try:
            fd_rot = os.open(rotated, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            try: _set_private_mode(fd_rot, rotated)
            finally: os.close(fd_rot)
        except OSError: pass
    record = json.dumps(diagnostic.to_dict(), ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(target, flags, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode): raise OSError("Diagnostic report target is not a regular file")
        _set_private_mode(fd, target)
        view = memoryview(record)
        while view:
            written = os.write(fd, view)
            if written <= 0: raise OSError("Could not finish writing diagnostic report")
            view = view[written:]
    finally: os.close(fd)
    return target


def read_reports(report_dir: Path | None = None) -> list[dict]:
    root = Path(report_dir) if report_dir is not None else DEFAULT_REPORT_DIR
    rows: list[dict] = []
    if root.is_symlink() or not root.is_dir(): return rows
    for path in (root / "diagnostics.previous.jsonl", root / "diagnostics.jsonl"):
        try:
            fd=os.open(path,os.O_RDONLY | getattr(os,"O_NOFOLLOW",0))
            try:
                info=os.fstat(fd)
                if not stat.S_ISREG(info.st_mode): continue
                size=info.st_size
                if not size: continue
                if size>MAX_REPORT_BYTES: os.lseek(fd,size-MAX_REPORT_BYTES,os.SEEK_SET)
                chunks=[]; remaining=MAX_REPORT_BYTES+1
                while remaining>0:
                    chunk=os.read(fd,min(65536,remaining))
                    if not chunk: break
                    chunks.append(chunk); remaining-=len(chunk)
                raw=b"".join(chunks)
            finally: os.close(fd)
            text = raw.decode("utf-8", errors="replace")
            if size > MAX_REPORT_BYTES: text = text.split("\n", 1)[-1]
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            if len(rows) >= MAX_REPORTS: return rows
            try: rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"code":"AF-REPORT-CORRUPT", "line":line_no, "message":"Malformed report entry"})
    return rows
