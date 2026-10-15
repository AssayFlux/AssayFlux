"""
Swift language adapter for AssayFlux.

Compiles and executes Swift source code using the Swift compiler.

Requirement:
- Swift installed and available through the 'swiftc' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class SwiftAdapter(LanguageAdapter):
    """Compile and execute Swift source code."""

    @property
    def language(self) -> str:
        return "swift"

    def is_available(self) -> bool:
        """Check whether the Swift compiler is available."""
        return shutil.which("swiftc") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Swift source code."""
        if not isinstance(source, str):
            raise ValueError("Swift source must be a string.")

        if not source.strip():
            raise ValueError("Swift source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        compiler = shutil.which("swiftc")

        if compiler is None:
            raise RuntimeError(
                "Swift is unavailable. Install the Swift toolchain "
                "and ensure 'swiftc' is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_swift_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "main.swift"
                executable = workdir / "program"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    compilation = subprocess.run(
                        [
                            compiler,
                            str(source_path),
                            "-o",
                            str(executable),
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

                    stderr = (
                        f"{stderr.rstrip()}\n"
                        "Swift compilation exceeded the "
                        f"{timeout}-second timeout.\n"
                    )

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

                    stderr = (
                        f"{stderr.rstrip()}\n"
                        "Swift execution exceeded the "
                        f"{timeout}-second timeout.\n"
                    )

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
                f"Could not compile or execute the Swift "
                f"program: {exc}"
            ) from exc