"""
Erlang language adapter for AssayFlux.

Compiles and executes Erlang source code using erlc and erl.

Requirements:
- Erlang installed.
- Both 'erlc' and 'erl' available through PATH.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class ErlangAdapter(LanguageAdapter):
    """Compile and execute Erlang source code."""

    @property
    def language(self) -> str:
        return "erlang"

    def is_available(self) -> bool:
        """Check whether the Erlang compiler and runtime exist."""
        return (
            shutil.which("erlc") is not None
            and shutil.which("erl") is not None
        )

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Erlang source code."""
        if not isinstance(source, str):
            raise ValueError("Erlang source must be a string.")

        if not source.strip():
            raise ValueError("Erlang source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        erlc = shutil.which("erlc")
        erl = shutil.which("erl")

        if erlc is None or erl is None:
            raise RuntimeError(
                "Erlang is unavailable. Install Erlang and ensure "
                "both 'erlc' and 'erl' are on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_erlang_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "assayflux_main.erl"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    compilation = subprocess.run(
                        [
                            erlc,
                            "-o",
                            str(workdir),
                            str(source_path),
                        ],
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
                        "Erlang compilation exceeded the "
                        f"{timeout}-second timeout."
                    )
                    stderr = f"{stderr.rstrip()}\n{message}\n"

                    return ExecutionResult(
                        language=self.language,
                        stdout=stdout,
                        stderr=stderr,
                        returncode=124,
                    )

                if compilation.returncode != 0:
                    return ExecutionResult(
                        language=self.language,
                        stdout=compilation.stdout,
                        stderr=compilation.stderr,
                        returncode=compilation.returncode,
                    )

                try:
                    execution = subprocess.run(
                        [
                            erl,
                            "-noshell",
                            "-pa",
                            str(workdir),
                            "-eval",
                            "assayflux_main:main(), halt().",
                        ],
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
                        "Erlang execution exceeded the "
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
                f"Could not compile or execute the Erlang "
                f"program: {exc}"
            ) from exc