"""
Nim language adapter for AssayFlux.

Compiles and executes Nim source code using the Nim compiler.

Requirement:
- Nim installed and available through the 'nim' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class NimAdapter(LanguageAdapter):
    """Compile and execute Nim source code."""

    @property
    def language(self) -> str:
        return "nim"

    def is_available(self) -> bool:
        """Check whether the Nim compiler is available."""
        return shutil.which("nim") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Nim source code."""
        if not isinstance(source, str):
            raise ValueError("Nim source must be a string.")

        if not source.strip():
            raise ValueError("Nim source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        nim = shutil.which("nim")

        if nim is None:
            raise RuntimeError(
                "Nim is unavailable. Install Nim and ensure "
                "the 'nim' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_nim_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "main.nim"
                executable = workdir / "assayflux_program"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    compilation = subprocess.run(
                        [
                            nim,
                            "c",
                            "--hints:off",
                            "--warnings:off",
                            "--out:" + str(executable),
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
                        "Nim compilation exceeded the "
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
                        [str(executable)],
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
                        "Nim execution exceeded the "
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
                f"Could not compile or execute the Nim "
                f"program: {exc}"
            ) from exc