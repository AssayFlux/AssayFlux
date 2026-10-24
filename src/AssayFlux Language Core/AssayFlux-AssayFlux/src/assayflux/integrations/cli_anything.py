"""Host-side adapter for installed CLI-Anything harnesses.

This adapter deliberately lives outside the .af interpreter. Harnesses are external
programs with their own side effects; they are never invoked implicitly by source code.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from assayflux.diagnostics.model import SecurityError, RuntimeErrorAF

_TOOL_NAME = re.compile(r"(?:cli-anything-[a-z0-9][a-z0-9-]*|cli-hub)\\Z")
_DEFAULT_TIMEOUT = 60
_MAX_TIMEOUT = 300


@dataclass(frozen=True, slots=True)
class Harness:
    """An installed harness executable discovered on PATH."""

    name: str
    executable: str


@dataclass(frozen=True, slots=True)
class HarnessResult:
    """Captured result of an explicitly requested external harness invocation."""

    tool: str
    returncode: int
    stdout: str
    stderr: str


def discover_harnesses(path_value: str | None = None) -> list[Harness]:
    """Discover CLI-Anything entry points on PATH without executing them."""
    search_path = os.environ.get("PATH", "") if path_value is None else path_value
    candidates: dict[str, str] = {}
    for directory in search_path.split(os.pathsep):
        if not directory:
            continue
        root = Path(directory).expanduser()
        try:
            entries = root.iterdir()
            for entry in entries:
                name = entry.name
                if not _TOOL_NAME.fullmatch(name) or name in candidates:
                    continue
                try:
                    if entry.is_file() and os.access(entry, os.X_OK):
                        candidates[name] = str(entry.resolve())
                except OSError:
                    continue
        except OSError:
            continue
    # shutil.which handles PATH/PATHEXT differences on platforms where entry
    # directory enumeration doesn't expose the executable's invocation name.
    for name in ("cli-hub",):
        executable = shutil.which(name, path=search_path)
        if executable and name not in candidates:
            candidates[name] = executable
    return [Harness(name, candidates[name]) for name in sorted(candidates)]


def run_harness(
    name: str,
    args: Sequence[str],
    *,
    allow_external_tools: bool = False,
    timeout: int = _DEFAULT_TIMEOUT,
    cwd: str | Path | None = None,
) -> HarnessResult:
    """Run a discovered harness with an argv list, never through a shell.

    Execution requires an explicit opt-in because a harness may edit files,
    launch desktop applications, or otherwise produce external side effects.
    """
    if not allow_external_tools:
        raise SecurityError(
            "External harness execution requires explicit opt-in",
            suggestion="Rerun with --allow-external-tools after reviewing the command.",
        )
    if not isinstance(name, str) or not _TOOL_NAME.fullmatch(name):
        raise SecurityError("Invalid CLI-Anything harness name")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= _MAX_TIMEOUT:
        raise SecurityError(f"Harness timeout must be between 1 and {_MAX_TIMEOUT} seconds")
    if any(not isinstance(arg, str) or "\x00" in arg for arg in args):
        raise SecurityError("Harness arguments must be strings without NUL characters")

    available = {harness.name: harness.executable for harness in discover_harnesses()}
    executable = available.get(name)
    if executable is None:
        raise RuntimeErrorAF(
            f"CLI-Anything harness '{name}' is not installed or not on PATH",
            suggestion="Install the desired harness in the active Python environment, then retry.",
        )

    working_directory = None
    if cwd is not None:
        try:
            working_directory = str(Path(cwd).expanduser().resolve(strict=True))
            if not Path(working_directory).is_dir():
                raise ValueError("not a directory")
        except (OSError, ValueError) as exc:
            raise RuntimeErrorAF("Harness working directory must be an existing directory") from exc

    try:
        completed = subprocess.run(
            [executable, *args],
            cwd=working_directory,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeErrorAF(
            f"CLI-Anything harness '{name}' exceeded its {timeout}-second timeout",
            suggestion="Use a shorter operation or explicitly choose a longer timeout (maximum 300 seconds).",
        ) from exc
    except OSError as exc:
        raise RuntimeErrorAF(
            f"Could not launch CLI-Anything harness '{name}'",
            details=type(exc).__name__,
        ) from exc

    return HarnessResult(name, completed.returncode, completed.stdout, completed.stderr)
