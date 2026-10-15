"""
Rust language adapter for AssayFlux.

Compiles and executes Rust source code using the Rust compiler.

Warning:
Compiled programs are not sandboxed. Only execute trusted source code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class RustAdapter(LanguageAdapter):
    """Compile and execute Rust source code."""

    @property
    def language(self) -> str:
        return "rust"

    def is_available(self) -> bool:
        """Check whether the Rust compiler is available."""
        return shutil.which("rustc") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Rust source code."""
        if not isinstance(source, str):
            raise ValueError("Rust source must be a string.")

        if not source.strip():
            raise ValueError("Rust source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("Timeout must be a finite positive number.")

        compiler = shutil.which("rustc")

        if compiler is None:
            raise RuntimeError(
                "Rust is unavailable. Install Rust and ensure "
                "'rustc' is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_rust_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "main.rs"
                executable_path = workdir / "main"

                source_path.write_text(source, encoding="utf-8")

                try:
                    compilation = subprocess.run(
                        [
                            compiler,
                            "--edition=2021",
                            str(source_path),
                            "-o",
                            str(executable_path),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                except subprocess.TimeoutExpired:
                    return ExecutionResult(
                        language=self.language,
                        stdout="",
                        stderr=(
                            "Rust compilation exceeded the "
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
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                except subprocess.TimeoutExpired as exc:
                    stdout = exc.stdout or ""
                    stderr = exc.stderr or ""

                    if isinstance(stdout, bytes):
                        stdout = stdout.decode("utf-8", errors="replace")

                    if isinstance(stderr, bytes):
                        stderr = stderr.decode("utf-8", errors="replace")

                    message = (
                        "Rust execution exceeded the "
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
                f"Could not compile or execute the Rust program: {exc}"
            ) from exc