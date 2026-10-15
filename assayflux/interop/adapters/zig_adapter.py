"""
Zig language adapter for AssayFlux.

Compiles and executes Zig source code using the Zig compiler.

Requirement:
- Zig installed and available through the 'zig' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class ZigAdapter(LanguageAdapter):
    """Compile and execute Zig source code."""

    @property
    def language(self) -> str:
        return "zig"

    def is_available(self) -> bool:
        """Check whether the Zig compiler is available."""
        return shutil.which("zig") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Zig source code."""
        if not isinstance(source, str):
            raise ValueError("Zig source must be a string.")

        if not source.strip():
            raise ValueError("Zig source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        zig = shutil.which("zig")

        if zig is None:
            raise RuntimeError(
                "Zig is unavailable. Install Zig and ensure "
                "the 'zig' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_zig_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "main.zig"
                executable = workdir / "assayflux_program"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    compilation = subprocess.run(
                        [
                            zig,
                            "build-exe",
                            str(source_path),
                            "-femit-bin="
                            + str(executable),
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
                        "Zig compilation exceeded the "
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
                        "Zig execution exceeded the "
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
                f"Could not compile or execute the Zig "
                f"program: {exc}"
            ) from exc