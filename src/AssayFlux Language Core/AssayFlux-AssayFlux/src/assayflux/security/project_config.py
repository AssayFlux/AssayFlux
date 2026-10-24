"""Load trusted project-level Python interoperability grants."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from assayflux.diagnostics.model import SecurityError
from assayflux.runtime.python_bridge import is_python_module_hard_denied
from assayflux.security.checkpoints import SecurityPolicy

_MODULE_NAME = re.compile(r"[A-Za-z_]\\w*(?:\\.[A-Za-z_]\\w*)*\\Z")
_CALL_NAME = re.compile(r"([A-Za-z_]\\w*(?:\\.[A-Za-z_]\\w*)*)\\.([A-Za-z_]\\w*)\\Z")


def _string_list(value: Any, key: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise SecurityError(f"assayflux.toml: '{key}' must be an array of strings")
    return value


def load_security_policy(project_root: str | Path) -> SecurityPolicy:
    """Load explicit Python module/call grants from assayflux.toml.

    This file is trusted host configuration, not source code. Its Python grants
    are intentionally exact-call allowlists; installed packages are not
    automatically exposed to .af programs.
    """
    config_path = Path(project_root).expanduser().resolve() / "assayflux.toml"
    if not config_path.exists():
        return SecurityPolicy()
    if not config_path.is_file():
        raise SecurityError("assayflux.toml must be a regular file")

    try:
        with config_path.open("rb") as stream:
            config = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SecurityError(
            "Could not read trusted project configuration",
            details=type(exc).__name__,
            suggestion="Check the syntax and permissions of assayflux.toml.",
        ) from exc

    python_config = config.get("python", {})
    if not isinstance(python_config, dict):
        raise SecurityError("assayflux.toml: [python] must be a table")
    unknown_keys = set(python_config) - {"modules", "calls"}
    if unknown_keys:
        raise SecurityError(
            "Unknown key in [python] configuration",
            details=", ".join(sorted(unknown_keys)),
        )

    base = SecurityPolicy()
    extra_modules = _string_list(python_config.get("modules", []), "python.modules")
    extra_calls = _string_list(python_config.get("calls", []), "python.calls")
    modules = list(base.allowed_python_modules)

    for module_name in extra_modules:
        if not _MODULE_NAME.fullmatch(module_name) or is_python_module_hard_denied(module_name):
            raise SecurityError(f"Invalid or blocked Python module grant: '{module_name}'")
        if module_name not in modules:
            modules.append(module_name)

    calls = list(base.allowed_python_calls)
    for spec in extra_calls:
        match = _CALL_NAME.fullmatch(spec)
        if not match:
            raise SecurityError(f"Invalid Python callable grant: '{spec}'")
        module_name, function_name = match.groups()
        if module_name not in modules:
            raise SecurityError(
                f"Python callable '{spec}' refers to a module not listed in [python].modules",
                suggestion=f"Add '{module_name}' to python.modules in assayflux.toml.",
            )
        if is_python_module_hard_denied(module_name) or function_name.startswith("_"):
            raise SecurityError(f"Invalid or blocked Python callable grant: '{spec}'")
        if spec not in calls:
            calls.append(spec)

    # A configured Python table opts this project into the Python bridge. Module
    # access and callable access are separately explicit capabilities.
    grants = set(base.capabilities)
    if extra_modules or extra_calls:
        grants.add("python.call")
        grants.update(f"python.module:{module_name}" for module_name in modules)

    return SecurityPolicy(
        max_source_bytes=base.max_source_bytes,
        max_value_bytes=base.max_value_bytes,
        max_line_chars=base.max_line_chars,
        max_steps=base.max_steps,
        max_loop_iterations=base.max_loop_iterations,
        max_output_chars=base.max_output_chars,
        max_numeric_bits=base.max_numeric_bits,
        allowed_python_modules=tuple(modules),
        allowed_python_calls=tuple(calls),
        capabilities=tuple(sorted(grants)),
        allow_file_imports=base.allow_file_imports,
        allow_network=base.allow_network,
    )
