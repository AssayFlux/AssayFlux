"""
Go language adapter for AssayFlux.

Compiles and executes Go source code using the Go toolchain.

Requirements:
- Go compiler and toolchain available through the `go` command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class GoAdapter(LanguageAdapter):
    """Compile and execute Go source code."""

    @property
    def language(self) -> str:
        return "go"

    def is_available(self) -> bool:
        """Check whether the Go toolchain is available."""
        return shutil.which("go") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Go source code."""
        if not isinstance(source, str):
            raise ValueError("Go source must be a string.")

        if not source.strip():
            raise ValueError("Go source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        go = shutil.which("go")

        if go is None:
            raise RuntimeError(
                "Go is unavailable. Install the Go toolchain and "
                "ensure the 'go' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_go_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "main.go"
                executable_path = workdir / "assayflux_program"

                source_path.write_text(source, encoding="utf-8")

                try:
                    compilation = subprocess.run(
                        [
                            go,
                            "build",
                            "-o",
                            str(executable_path),
                            str(source_path),
                        ],
                        cwd=workdir,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                        env=None,
                    )
                except subprocess.TimeoutExpired:
                    return ExecutionResult(
                        language=self.language,
                        stdout="",
                        stderr=(
                            "Go compilation exceeded the "
                            f"{timeout}-second timeout.\n"
                        ),
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
                        [str(executable_path)],
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
                        "Go execution exceeded the "
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
                f"Could not compile or execute the Go program: {exc}"
            ) from exc