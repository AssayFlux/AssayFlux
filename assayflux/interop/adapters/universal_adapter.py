"""
Backward-compatible universal adapter for AssayFlux.

The implementation delegates language execution to MasterAdapter.

Existing code can continue to import UniversalAdapter, while new
code should prefer a language-specific MasterAdapter instance.
"""

from __future__ import annotations

import time
from typing import Any

from assayflux.interop.adapters.master_adapter import MasterAdapter
from assayflux.interop.base import ExecutionResult, LanguageAdapter


class UniversalAdapter(LanguageAdapter):
    """
    Compatibility facade for the master language adapter.

    Legacy usage:
        adapter = UniversalAdapter()
        result = adapter.execute(
            "print(2 + 3)",
            language="python",
        )

    Preferred usage:
        adapter = MasterAdapter("python")
        result = adapter.execute("print(2 + 3)")
    """

    def __init__(self) -> None:
        self._master_adapters = {
            language: MasterAdapter(language)
            for language in MasterAdapter.registered_languages()
        }

    @property
    def language(self) -> str:
        """Identify this object as the legacy universal facade."""
        return "universal"

    def is_available(self) -> bool:
        """Return whether at least one supported target is available."""
        return any(
            adapter.is_available()
            for adapter in self._master_adapters.values()
        )

    def available_languages(self) -> list[str]:
        """Return canonical targets whose required tools are available."""
        available = []

        for language, adapter in self._master_adapters.items():
            try:
                if adapter.is_available():
                    available.append(language)
            except Exception:
                # A broken toolchain check must not hide other languages.
                continue

        return sorted(available)

    def language_info(self) -> dict[str, str]:
        """Describe each currently available language target."""
        descriptions = {
            "bash": "Bash shell",
            "c": "C compiler",
            "cpp": "C++ compiler",
            "csharp": "C#/.NET or compatible compiler",
            "cobol": "COBOL compiler",
            "crystal": "Crystal compiler",
            "d": "D compiler",
            "dart": "Dart runtime",
            "elixir": "Elixir runtime",
            "erlang": "Erlang escript runtime",
            "fortran": "Fortran compiler",
            "fsharp": "F# runtime",
            "go": "Go toolchain",
            "haskell": "Haskell interpreter",
            "java": "Java compiler and runtime",
            "javascript": "JavaScript via Node.js",
            "julia": "Julia runtime",
            "kotlin": "Kotlin compiler and Java runtime",
            "lua": "Lua runtime",
            "nim": "Nim compiler",
            "ocaml": "OCaml interpreter",
            "perl": "Perl runtime",
            "php": "PHP runtime",
            "python": "Current Python interpreter",
            "r": "Rscript runtime",
            "ruby": "Ruby runtime",
            "rust": "Rust compiler",
            "scala": "Scala runtime",
            "sql": "SQLite database engine",
            "swift": "Swift runtime",
            "typescript": "TypeScript runner or compiler",
            "zig": "Zig compiler",
            "html": "HTML static asset handling",
            "css": "CSS static asset handling",
        }

        return {
            language: descriptions.get(language, language)
            for language in self.available_languages()
        }

    def execute(
        self,
        source: str,
        language: str | None = None,
        timeout: float = 15.0,
        **kwargs: Any,
    ) -> ExecutionResult:
        """
        Execute code using the requested target language.

        The optional language argument preserves the old interface.
        If omitted, the call returns a clear error rather than guessing
        which language the source code uses.
        """
        started = time.perf_counter()

        if kwargs:
            names = ", ".join(sorted(kwargs))
            return ExecutionResult(
                language="universal",
                stdout="",
                stderr=f"Unexpected keyword argument(s): {names}",
                returncode=2,
                duration=time.perf_counter() - started,
            )

        if not isinstance(source, str):
            raise TypeError("Source code must be a string.")

        if language is None or not isinstance(language, str) or not language.strip():
            return ExecutionResult(
                language="universal",
                stdout="",
                stderr=(
                    "A target language must be specified. "
                    f"Available targets: {', '.join(self.available_languages())}"
                ),
                returncode=2,
                duration=time.perf_counter() - started,
            )

        try:
            canonical = MasterAdapter.normalize_language(language)
        except ValueError as exc:
            return ExecutionResult(
                language="universal",
                stdout="",
                stderr=str(exc),
                returncode=2,
                duration=time.perf_counter() - started,
            )

        adapter = self._master_adapters.get(canonical)

        if adapter is None:
            return ExecutionResult(
                language=canonical,
                stdout="",
                stderr=f"Unsupported language: '{language}'.",
                returncode=2,
                duration=time.perf_counter() - started,
            )

        return adapter.execute(source, timeout=timeout)


__all__ = ["UniversalAdapter"]