"""
TypeScript language adapter for AssayFlux.

Compiles TypeScript using the TypeScript compiler (tsc) and
executes the resulting JavaScript using Node.js.

Requirements:
- Node.js
- TypeScript compiler (tsc)

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class TypeScriptAdapter(LanguageAdapter):
    """Compile and execute TypeScript source code."""

    @property
    def language(self) -> str:
        return "typescript"

    def is_available(self) -> bool:
        """Check whether Node.js and the TypeScript compiler exist."""
        return (
            shutil.which("node") is not None
            and shutil.which("tsc") is not None
        )

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted TypeScript source code."""
        if not isinstance(source, str):
            raise ValueError("TypeScript source must be a string.")

        if not source.strip():
            raise ValueError("TypeScript source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        node = shutil.which("node")
        compiler = shutil.which("tsc")

        if node is None or compiler is None:
            raise RuntimeError(
                "TypeScript is unavailable. Install Node.js and the "
                "TypeScript compiler, and ensure 'node' and 'tsc' "
                "are on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_typescript_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "main.ts"
                output_dir = workdir / "output"
                output_dir.mkdir()

                source_path.write_text(source, encoding="utf-8")

                try:
                    compilation = subprocess.run(
                        [
                            compiler,
                            "--target",
                            "ES2020",
                            "--module",
                            "commonjs",
                            "--lib",
                            "ES2020,DOM",
                            "--skipLibCheck",
                            "--outDir",
                            str(output_dir),
                            str(source_path),
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
                            "TypeScript compilation exceeded the "
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

                javascript_path = output_dir / "main.js"

                try:
                    execution = subprocess.run(
                        [node, str(javascript_path)],
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
                        "TypeScript execution exceeded the "
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
                "Could not compile or execute the TypeScript program: "
                f"{exc}"
            ) from exc