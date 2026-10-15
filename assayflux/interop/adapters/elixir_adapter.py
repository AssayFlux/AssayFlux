"""
Elixir language adapter for AssayFlux.

Executes Elixir source code through the Elixir runtime.

Requirement:
- Elixir installed and available through the 'elixir' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class ElixirAdapter(LanguageAdapter):
    """Execute Elixir source code."""

    @property
    def language(self) -> str:
        return "elixir"

    def is_available(self) -> bool:
        """Check whether the Elixir runtime is available."""
        return shutil.which("elixir") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Execute trusted Elixir source code."""
        if not isinstance(source, str):
            raise ValueError("Elixir source must be a string.")

        if not source.strip():
            raise ValueError("Elixir source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        elixir = shutil.which("elixir")

        if elixir is None:
            raise RuntimeError(
                "Elixir is unavailable. Install Elixir and "
                "ensure the 'elixir' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_elixir_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "program.exs"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [elixir, str(source_path)],
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
                        "Elixir execution exceeded the "
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
                f"Could not execute the Elixir program: {exc}"
            ) from exc