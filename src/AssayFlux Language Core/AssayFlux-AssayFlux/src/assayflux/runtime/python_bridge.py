"""Restricted convenience bridge for trusted Python libraries; explicitly NOT a sandbox."""
from __future__ import annotations

import importlib
from typing import Any

from assayflux.diagnostics.model import PythonBridgeError, SecurityError, SourceLocation
from assayflux.security.capabilities import CapabilityManager
from assayflux.security.checkpoints import SecurityPolicy

_MAX_DEPTH = 16
_MAX_ITEMS = 100_000
_HARD_DENIED_MODULE_ROOTS = frozenset({
    "os", "subprocess", "sys", "builtins", "importlib", "ctypes", "cffi",
    "socket", "ssl", "urllib", "http", "requests", "httpx", "aiohttp",
    "ftplib", "smtplib", "multiprocessing", "threading", "concurrent",
    "signal", "resource", "pathlib", "shutil", "tempfile", "pickle",
    "marshal", "shelve", "sqlite3", "pty", "pdb",
})
_HARD_DENIED_CALLS = {
    "numpy": frozenset({"load", "save", "savez", "savez_compressed", "fromfile", "tofile", "memmap"}),
    "pandas": frozenset({"read_csv", "read_excel", "read_pickle", "read_parquet", "read_feather", "read_hdf", "read_sql", "to_pickle"}),
    "torch": frozenset({"load", "save", "hub"}),
    "joblib": frozenset({"load", "dump"}),
}

def is_python_module_hard_denied(module_name: str) -> bool:
    return bool(module_name) and module_name.split(".",1)[0] in _HARD_DENIED_MODULE_ROOTS

_DEFAULT_CALLS = {
    "math": {"sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "log", "log10", "log2", "exp", "ceil", "floor", "fabs", "isfinite", "isinf", "isnan", "degrees", "radians"},
    "statistics": {"mean", "median", "median_low", "median_high", "fmean", "pstdev", "pvariance", "stdev", "variance", "harmonic_mean", "geometric_mean"},
    "json": {"dumps", "loads"},
}

def _validate_value(value: Any, *, depth: int = 0, count: list[int] | None = None) -> Any:
    if count is None: count = [0]
    count[0] += 1
    if count[0] > _MAX_ITEMS or depth > _MAX_DEPTH:
        raise PythonBridgeError("Python bridge value exceeds structural limits")
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, int) and not isinstance(value, bool) and value.bit_length() > 4096:
            raise PythonBridgeError("Integer exceeds bridge numeric limit")
        if isinstance(value, float) and not __import__("math").isfinite(value):
            raise PythonBridgeError("Non-finite floats are not supported by the bridge")
        if isinstance(value, str) and len(value) > 1_000_000: raise PythonBridgeError("String exceeds bridge size limit")
        return value
    # NumPy arrays cross the boundary only as bounded primitive lists; arbitrary
    # objects and native handles are never passed through implicitly.
    value_type=type(value)
    if value_type.__module__ == "numpy" and value_type.__name__ != "ndarray" and hasattr(value,"item") and hasattr(value,"dtype"):
        try: value=value.item(); value_type=type(value)
        except Exception as exc: raise PythonBridgeError("Could not safely convert NumPy scalar",details=type(exc).__name__) from exc
    if value_type.__module__ == "numpy" and value_type.__name__ == "ndarray":
        try:
            if int(value.size)>_MAX_ITEMS or int(value.ndim)>8: raise PythonBridgeError("NumPy array exceeds bridge shape or item limits")
            value=value.tolist()
        except PythonBridgeError: raise
        except Exception as exc: raise PythonBridgeError("Could not safely convert NumPy array",details=type(exc).__name__) from exc
    if isinstance(value, (list, tuple)):
        return [_validate_value(x, depth=depth+1, count=count) for x in value]
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value): raise PythonBridgeError("Bridge dictionary keys must be strings")
        return {k: _validate_value(v, depth=depth+1, count=count) for k, v in value.items()}
    raise PythonBridgeError(f"Unsupported Python bridge value type: {type(value).__name__}",
                            suggestion="Convert values to strings, numbers, booleans, null, lists, or string-keyed dictionaries.")

class PythonBridge:
    def __init__(self, policy: SecurityPolicy | None = None, *, allowed_calls: dict[str, set[str]] | None = None):
        self.policy = policy or SecurityPolicy()
        self.capabilities = CapabilityManager(self.policy.capabilities)
        self.allowed_calls = {name: set(calls) for name, calls in _DEFAULT_CALLS.items()}
        # Extensions are trusted-host configuration, never supplied by source code.
        for module_name, calls in (allowed_calls or {}).items():
            if module_name not in self.policy.allowed_python_modules:
                raise SecurityError(f"Cannot configure calls for unapproved module '{module_name}'")
            self.allowed_calls[module_name] = set(calls)
        for spec in self.policy.allowed_python_calls:
            if not isinstance(spec,str) or "." not in spec:
                raise SecurityError("Python callable grants must use 'module.function' notation")
            module_name,function_name=spec.rsplit(".",1)
            if module_name not in self.policy.allowed_python_modules or not module_name.isidentifier() and not all(x.isidentifier() for x in module_name.split(".")) or not function_name.isidentifier() or function_name.startswith("_"):
                raise SecurityError(f"Invalid or unapproved Python callable grant '{spec}'")
            self.allowed_calls.setdefault(module_name,set()).add(function_name)
    def call(self, module_name: str, function_name: str, *args, **kwargs):
        if not isinstance(module_name,str) or not isinstance(function_name,str): raise SecurityError("Python bridge module and callable names must be strings")
        if is_python_module_hard_denied(module_name): raise SecurityError(f"Python module '{module_name}' is blocked by the hard security policy")
        if function_name in {"open", "exec", "eval", "compile", "__import__", "system", "popen", "Popen", "spawn", "fork", "unlink", "remove", "chmod", "chown"}:
            raise SecurityError(f"Python callable '{module_name}.{function_name}' is blocked by the hard security policy")
        root=module_name.split(".",1)[0]
        if function_name in _HARD_DENIED_CALLS.get(root, frozenset()):
            raise SecurityError(f"Python callable '{module_name}.{function_name}' is blocked by the hard security policy")
        self.capabilities.require("python.call", operation=f"call {module_name}.{function_name}")
        self.capabilities.require(f"python.module:{module_name}", operation=f"import Python module {module_name}")
        if module_name not in self.policy.allowed_python_modules:
            raise SecurityError(f"Python module '{module_name}' is not permitted", location=SourceLocation(),
                                suggestion="Use an approved module or configure the trusted host application explicitly.")
        if not all(part.isidentifier() for part in module_name.split(".")) or not function_name.isidentifier() or function_name.startswith("_"):
            raise SecurityError("Invalid Python bridge symbol")
        if function_name not in self.allowed_calls.get(module_name, set()):
            raise SecurityError(f"Python callable '{module_name}.{function_name}' is not permitted", location=SourceLocation(),
                                suggestion="Only explicitly approved callables may cross the language boundary.")
        try: module = importlib.import_module(module_name)
        except Exception as exc: raise PythonBridgeError(f"Could not import Python module '{module_name}'", details=type(exc).__name__) from exc
        function = getattr(module, function_name, None)
        if not callable(function): raise PythonBridgeError(f"'{module_name}.{function_name}' is not an exposed callable")
        safe_args = [_validate_value(x) for x in args]
        safe_kwargs = {k: _validate_value(v) for k, v in kwargs.items() if isinstance(k, str) and not k.startswith("_")}
        if len(safe_kwargs) != len(kwargs): raise PythonBridgeError("Invalid keyword argument name")
        try: result = function(*safe_args, **safe_kwargs)
        except Exception as exc: raise PythonBridgeError(f"Python call '{module_name}.{function_name}' failed", details=type(exc).__name__) from exc
        return _validate_value(result)
