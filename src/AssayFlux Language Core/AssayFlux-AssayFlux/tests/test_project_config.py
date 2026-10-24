from __future__ import annotations

from pathlib import Path

import pytest

from assayflux.diagnostics.model import SecurityError
from assayflux.security.project_config import load_security_policy


def test_default_policy_does_not_enable_python_capabilities(tmp_path: Path):
    policy = load_security_policy(tmp_path)

    assert policy.allowed_python_modules == ("math", "statistics", "json")
    assert "python.call" not in policy.capabilities


def test_project_config_grants_selected_python_libraries_and_calls(tmp_path: Path):
    (tmp_path / "assayflux.toml").write_text(
        '[python]\nmodules = ["numpy", "pandas"]\ncalls = ["numpy.mean", "numpy.std", "pandas.isna"]\n',
        encoding="utf-8",
    )

    policy = load_security_policy(tmp_path)

    assert "numpy" in policy.allowed_python_modules
    assert "pandas" in policy.allowed_python_modules
    assert set(policy.allowed_python_calls) == {"numpy.mean", "numpy.std", "pandas.isna"}
    assert "python.call" in policy.capabilities
    assert "python.module:numpy" in policy.capabilities
    assert "python.module:pandas" in policy.capabilities


def test_project_config_rejects_hard_denied_modules(tmp_path: Path):
    (tmp_path / "assayflux.toml").write_text(
        '[python]\nmodules = ["subprocess"]\n',
        encoding="utf-8",
    )

    with pytest.raises(SecurityError, match="blocked"):
        load_security_policy(tmp_path)


def test_project_config_requires_modules_for_callable_grants(tmp_path: Path):
    (tmp_path / "assayflux.toml").write_text(
        '[python]\ncalls = ["numpy.mean"]\n',
        encoding="utf-8",
    )

    with pytest.raises(SecurityError, match="not listed"):
        load_security_policy(tmp_path)


def test_project_config_rejects_unknown_python_keys(tmp_path: Path):
    (tmp_path / "assayflux.toml").write_text(
        '[python]\nallow_everything = true\n',
        encoding="utf-8",
    )

    with pytest.raises(SecurityError, match="Unknown key"):
        load_security_policy(tmp_path)
