from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from assayflux.diagnostics.model import RuntimeErrorAF, SecurityError
from assayflux.integrations.cli_anything import discover_harnesses, run_harness


def test_discover_harnesses_finds_cli_anything_entry_point(tmp_path: Path):
    executable = tmp_path / "cli-anything-demo"
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(executable.stat().st_mode | 0o111)

    assert discover_harnesses(str(tmp_path)) == [
        discover_harnesses.__globals__["Harness"]("cli-anything-demo", str(executable.resolve()))
    ]


def test_run_requires_explicit_external_tool_opt_in():
    with pytest.raises(SecurityError, match="explicit opt-in"):
        run_harness("cli-anything-demo", [], allow_external_tools=False)


def test_run_rejects_unknown_harness_even_with_opt_in():
    with patch("assayflux.integrations.cli_anything.discover_harnesses", return_value=[]):
        with pytest.raises(RuntimeErrorAF, match="not installed"):
            run_harness("cli-anything-demo", [], allow_external_tools=True)


def test_run_passes_arguments_without_a_shell(tmp_path: Path):
    executable = tmp_path / "cli-anything-demo"
    executable.write_text("#!/usr/bin/env python3\nimport sys\nprint(repr(sys.argv[1:]))\n", encoding="utf-8")
    executable.chmod(executable.stat().st_mode | 0o111)
    harness = discover_harnesses(str(tmp_path))[0]

    with (
        patch("assayflux.integrations.cli_anything.discover_harnesses", return_value=[harness]),
        patch("assayflux.integrations.cli_anything.subprocess.run") as run,
    ):
        run.return_value = subprocess.CompletedProcess(
            args=[harness.executable, "project", "show; echo unsafe"],
            returncode=0,
            stdout="ok\n",
            stderr="",
        )
        result = run_harness(
            harness.name,
            ["project", "show; echo unsafe"],
            allow_external_tools=True,
        )

    assert result.stdout == "ok\n"
    args, kwargs = run.call_args
    assert args[0] == [harness.executable, "project", "show; echo unsafe"]
    assert kwargs["shell"] is False
    assert kwargs["timeout"] == 60


def test_run_rejects_invalid_timeout():
    with pytest.raises(SecurityError, match="timeout"):
        run_harness("cli-anything-demo", [], allow_external_tools=True, timeout=301)
