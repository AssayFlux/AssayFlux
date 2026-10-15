"""
Lua language adapter for AssayFlux.

Executes Lua source code through the Lua interpreter.

Requirement:
- Lua installed and available through the 'lua' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class LuaAdapter(LanguageAdapter):
    """Execute Lua source code."""

    @property
    def language(self) -> str:
        return "lua"

    def is_available(self) -> bool:
        """Check whether the Lua interpreter is available."""
        return shutil.which("lua") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Execute trusted Lua source code."""
        if not isinstance(source, str):
            raise ValueError("Lua source must be a string.")

        if not source.strip():
            raise ValueError("Lua source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        lua = shutil.which("lua")

        if lua is None:
            raise RuntimeError(
                "Lua is unavailable. Install Lua and ensure "
                "the 'lua' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_lua_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "program.lua"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [lua, str(source_path)],
                        cwd=workdir,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )

                except subprocess.TimeoutExpired as exc:
                    stdout = exc.stdout or ""
                    stderr = exc.stderr or ""

                    if isinstance(stdout, bytes):
                        stdout = stdout.decode(
                            "utf-8",
                            errors="replace",
                        )

                    if isinstance(stderr, bytes):
                        stderr = stderr.decode(
                            "utf-8",
                            errors="replace",
                        )

                    message = (
                        "Lua execution exceeded the "
                        f"{timeout}-second timeout."
                    )
                    stderr = f"{stderr.rstrip()}\n{message}\n"

                    return ExecutionResult(
                        language=self.language,
                        stdout=stdout,
                        stderr=stderr,
                        returncode=124,
                    )

                return ExecutionResult(
                    language=self.language,
                    stdout=execution.stdout,
                    stderr=execution.stderr,
                    returncode=execution.returncode,
                )

        except OSError as exc:
            raise RuntimeError(
                f"Could not execute the Lua program: {exc}"
            ) from exc