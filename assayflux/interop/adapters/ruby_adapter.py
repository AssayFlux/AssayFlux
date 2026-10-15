"""
Ruby language adapter for AssayFlux.

Executes Ruby source code through the Ruby interpreter.

Requirement:
- Ruby installed and available through the 'ruby' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class RubyAdapter(LanguageAdapter):
    """Execute Ruby source code."""

    @property
    def language(self) -> str:
        return "ruby"

    def is_available(self) -> bool:
        """Check whether the Ruby interpreter is available."""
        return shutil.which("ruby") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Execute trusted Ruby source code."""
        if not isinstance(source, str):
            raise ValueError("Ruby source must be a string.")

        if not source.strip():
            raise ValueError("Ruby source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        ruby = shutil.which("ruby")

        if ruby is None:
            raise RuntimeError(
                "Ruby is unavailable. Install Ruby and ensure "
                "the 'ruby' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_ruby_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "program.rb"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [ruby, str(source_path)],
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
                        "Ruby execution exceeded the "
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
                f"Could not execute the Ruby program: {exc}"
            ) from exc