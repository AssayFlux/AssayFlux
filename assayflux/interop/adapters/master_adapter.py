"""
AssayFlux Master Language Adapter
=================================

A shared execution engine for AssayFlux language integrations.

The same adapter class is configured for a particular language.
The loader can therefore register one instance per language while
keeping execution behavior consistent.

Supported programming-language targets:
    Python, JavaScript, Ruby, PHP, Lua, Perl, R, Julia, C, C++,
    C#, Rust, Go, Zig, D, Nim, Crystal, Java, Kotlin, Scala,
    F#, Haskell, OCaml, Elixir, Erlang, COBOL, Fortran, Dart,
    Swift, TypeScript, and Bash.

Additional targets:
    SQL using Python's SQLite engine.
    HTML and CSS as static assets.

Important:
    This adapter is not a security sandbox. Running source code
    can access the host environment with the permissions of the
    AssayFlux process. Do not execute untrusted code on a system
    containing sensitive data.
"""

from __future__ import annotations

import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class MasterAdapter(LanguageAdapter):
    """
    Shared adapter configured for one target language.

    Example:
        adapter = MasterAdapter("python")
        result = adapter.execute("print(2 + 3)")

    The adapter does not install compilers or runtimes. It checks
    the host environment and uses tools already installed there.
    """

    SUPPORTED_LANGUAGES = (
        "bash",
        "c",
        "cpp",
        "csharp",
        "cobol",
        "crystal",
        "d",
        "dart",
        "elixir",
        "erlang",
        "fortran",
        "fsharp",
        "go",
        "haskell",
        "java",
        "javascript",
        "julia",
        "kotlin",
        "lua",
        "nim",
        "ocaml",
        "perl",
        "php",
        "python",
        "r",
        "ruby",
        "rust",
        "scala",
        "sql",
        "swift",
        "typescript",
        "zig",
        "html",
        "css",
    )

    ALIASES = {
        "js": "javascript",
        "node": "javascript",
        "c++": "cpp",
        "cc": "cpp",
        "c#": "csharp",
        "cs": "csharp",
        "f#": "fsharp",
        "fs": "fsharp",
        "hs": "haskell",
        "rs": "rust",
        "rb": "ruby",
        "py": "python",
        "rscript": "r",
        "ts": "typescript",
        "sh": "bash",
        "shell": "bash",
        "sqlite": "sql",
        "sqlite3": "sql",
        "htm": "html",
    }

    def __init__(self, language: str) -> None:
        if not isinstance(language, str):
            raise TypeError("Language must be a string.")

        normalized = language.strip().lower()

        if not normalized:
            raise ValueError("Language must not be empty.")

        normalized = self.ALIASES.get(normalized, normalized)

        if normalized not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{language}'. "
                f"Supported targets: "
                f"{', '.join(self.SUPPORTED_LANGUAGES)}"
            )

        self._language = normalized

    @property
    def language(self) -> str:
        """Return this adapter's canonical language identifier."""
        return self._language

    @classmethod
    def normalize_language(cls, language: str) -> str:
        """Normalize a language name or alias."""
        if not isinstance(language, str):
            raise ValueError("Language identifier must be a string.")

        normalized = language.strip().lower()

        if not normalized:
            raise ValueError("Language identifier must not be empty.")

        return cls.ALIASES.get(normalized, normalized)

    @classmethod
    def registered_languages(cls) -> tuple[str, ...]:
        """Return all language targets supported by this adapter."""
        return cls.SUPPORTED_LANGUAGES

    def _has_any(self, *commands: str) -> bool:
        """Return True if any named executable exists."""
        return any(shutil.which(command) for command in commands)

    def is_available(self) -> bool:
        """
        Check whether this language's required tools are available.

        Availability does not guarantee that every program will
        compile or execute successfully.
        """
        language = self._language

        checks: dict[str, Callable[[], bool]] = {
            "python": lambda: bool(sys.executable),
            "javascript": lambda: self._has_any("node"),
            "ruby": lambda: self._has_any("ruby"),
            "php": lambda: self._has_any("php"),
            "lua": lambda: self._has_any("lua"),
            "perl": lambda: self._has_any("perl"),
            "r": lambda: self._has_any("Rscript"),
            "julia": lambda: self._has_any("julia"),
            "c": lambda: self._has_any("gcc", "clang"),
            "cpp": lambda: self._has_any("g++", "clang++"),
            "csharp": lambda: self._has_any("dotnet", "csc", "mcs"),
            "rust": lambda: self._has_any("rustc"),
            "go": lambda: self._has_any("go"),
            "zig": lambda: self._has_any("zig"),
            "d": lambda: self._has_any("dmd", "gdc", "ldc2"),
            "nim": lambda: self._has_any("nim"),
            "crystal": lambda: self._has_any("crystal"),
            "java": lambda: (
                self._has_any("javac") and self._has_any("java")
            ),
            "kotlin": lambda: self._has_any("kotlinc"),
            "scala": lambda: self._has_any("scala", "scala-cli"),
            "fsharp": lambda: self._has_any("dotnet", "fsi", "fsharpi"),
            "haskell": lambda: self._has_any("runghc", "runhaskell"),
            "ocaml": lambda: self._has_any("ocaml"),
            "elixir": lambda: self._has_any("elixir"),
            "erlang": lambda: self._has_any("escript"),
            "cobol": lambda: self._has_any("cobc"),
            "fortran": lambda: self._has_any("gfortran", "flang"),
            "dart": lambda: self._has_any("dart"),
            "swift": lambda: self._has_any("swift"),
            "typescript": lambda: self._has_any(
                "tsx", "ts-node", "tsc"
            ),
            "bash": lambda: self._has_any("bash"),
            "sql": self._sqlite_available,
            "html": lambda: True,
            "css": lambda: True,
        }

        try:
            return checks[language]()
        except (KeyError, OSError):
            return False

    @staticmethod
    def _sqlite_available() -> bool:
        """Check whether Python's SQLite engine is usable."""
        try:
            import sqlite3

            connection = sqlite3.connect(":memory:")
            connection.close()
            return True
        except Exception:
            return False

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """
        Execute source code for this adapter's configured language.

        A fresh temporary directory is used for generated source files
        and compiled artifacts. This is temporary-file management,
        not operating-system-level isolation.
        """
        started = time.perf_counter()

        if not isinstance(source, str):
            raise TypeError("Source code must be a string.")

        if isinstance(timeout, bool) or not isinstance(
            timeout, (int, float)
        ):
            raise TypeError("Timeout must be a number.")

        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Timeout must be a finite positive number.")

        timeout = float(timeout)

        if not self.is_available():
            return self._result(
                stdout="",
                stderr=(
                    f"Runtime unavailable for '{self._language}'. "
                    "Install the required runtime or compiler, then retry."
                ),
                returncode=127,
                started=started,
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_"
            ) as directory:
                workdir = Path(directory)

                return self._execute_in_directory(
                    source=source,
                    workdir=workdir,
                    deadline=started + timeout,
                    started=started,
                )

        except subprocess.TimeoutExpired:
            return self._result(
                stdout="",
                stderr=(
                    f"Execution timed out after {timeout:g} seconds."
                ),
                returncode=124,
                started=started,
            )
        except (OSError, RuntimeError) as exc:
            return self._result(
                stdout="",
                stderr=f"Execution error: {exc}",
                returncode=1,
                started=started,
            )

    def _result(
        self,
        *,
        stdout: str,
        stderr: str,
        returncode: int,
        started: float,
    ) -> ExecutionResult:
        """Build a result using the shared result contract."""
        return ExecutionResult(
            language=self._language,
            stdout=stdout,
            stderr=stderr,
            returncode=returncode,
            duration=max(0.0, time.perf_counter() - started),
        )

    def _remaining(self, deadline: float) -> float:
        """Return remaining execution time or raise a timeout."""
        remaining = deadline - time.perf_counter()

        if remaining <= 0:
            raise subprocess.TimeoutExpired(
                cmd=self._language,
                timeout=0,
            )

        return remaining

    def _run(
        self,
        command: list[str],
        *,
        cwd: Path,
        deadline: float,
    ) -> subprocess.CompletedProcess[str]:
        """
        Run a command without a shell and within the shared deadline.

        Commands are passed as argument lists, not shell command
        strings, to avoid shell interpretation of arguments.
        """
        return subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=self._remaining(deadline),
            check=False,
        )

    def _write(
        self,
        workdir: Path,
        filename: str,
        source: str,
    ) -> Path:
        """Write UTF-8 source into the temporary work directory."""
        path = workdir / filename
        path.write_text(source, encoding="utf-8")
        return path

    def _from_process(
        self,
        process: subprocess.CompletedProcess[str],
        started: float,
    ) -> ExecutionResult:
        """Convert a process result into the common result format."""
        return ExecutionResult(
            language=self._language,
            stdout=process.stdout or "",
            stderr=process.stderr or "",
            returncode=process.returncode,
            duration=max(0.0, time.perf_counter() - started),
        )

    def _compile_then_run(
        self,
        compile_command: list[str],
        run_command: list[str],
        *,
        workdir: Path,
        deadline: float,
        started: float,
    ) -> ExecutionResult:
        """Compile source, then run the resulting program."""
        compilation = self._run(
            compile_command,
            cwd=workdir,
            deadline=deadline,
        )

        if compilation.returncode != 0:
            return self._from_process(compilation, started)

        execution = self._run(
            run_command,
            cwd=workdir,
            deadline=deadline,
        )

        combined_stderr = (
            (compilation.stderr or "") + (execution.stderr or "")
        )

        return ExecutionResult(
            language=self._language,
            stdout=execution.stdout or "",
            stderr=combined_stderr,
            returncode=execution.returncode,
            duration=max(0.0, time.perf_counter() - started),
        )

    def _execute_in_directory(
        self,
        *,
        source: str,
        workdir: Path,
        deadline: float,
        started: float,
    ) -> ExecutionResult:
        """Select and execute the runner for the configured language."""
        language = self._language

        if language == "python":
            path = self._write(workdir, "main.py", source)
            return self._from_process(
                self._run(
                    [sys.executable, str(path)],
                    cwd=workdir,
                    deadline=deadline,
                ),
                started,
            )

        if language == "javascript":
            path = self._write(workdir, "main.js", source)
            return self._from_process(
                self._run(
                    ["node", str(path)],
                    cwd=workdir,
                    deadline=deadline,
                ),
                started,
            )

        if language == "ruby":
            path = self._write(workdir, "main.rb", source)
            return self._from_process(
                self._run(["ruby", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "php":
            path = self._write(workdir, "main.php", source)
            return self._from_process(
                self._run(["php", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "lua":
            path = self._write(workdir, "main.lua", source)
            return self._from_process(
                self._run(["lua", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "perl":
            path = self._write(workdir, "main.pl", source)
            return self._from_process(
                self._run(["perl", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "r":
            path = self._write(workdir, "main.R", source)
            return self._from_process(
                self._run(["Rscript", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "julia":
            path = self._write(workdir, "main.jl", source)
            return self._from_process(
                self._run(["julia", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "bash":
            path = self._write(workdir, "main.sh", source)
            return self._from_process(
                self._run(["bash", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "c":
            path = self._write(workdir, "main.c", source)
            executable = workdir / "main"
            compiler = shutil.which("gcc") or shutil.which("clang")

            return self._compile_then_run(
                [str(compiler), str(path), "-o", str(executable)],
                [str(executable)],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "cpp":
            path = self._write(workdir, "main.cpp", source)
            executable = workdir / "main"
            compiler = shutil.which("g++") or shutil.which("clang++")

            return self._compile_then_run(
                [
                    str(compiler),
                    "-std=c++17",
                    str(path),
                    "-o",
                    str(executable),
                ],
                [str(executable)],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "rust":
            path = self._write(workdir, "main.rs", source)
            executable = workdir / "main"

            return self._compile_then_run(
                ["rustc", str(path), "-o", str(executable)],
                [str(executable)],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "go":
            path = self._write(workdir, "main.go", source)
            return self._from_process(
                self._run(
                    ["go", "run", str(path)],
                    cwd=workdir,
                    deadline=deadline,
                ),
                started,
            )

        if language == "zig":
            path = self._write(workdir, "main.zig", source)
            return self._from_process(
                self._run(
                    ["zig", "run", str(path)],
                    cwd=workdir,
                    deadline=deadline,
                ),
                started,
            )

        if language == "java":
            if "class Main" not in source:
                source = (
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    f"{source}\n"
                    "    }\n"
                    "}\n"
                )

            path = self._write(workdir, "Main.java", source)

            return self._compile_then_run(
                ["javac", str(path)],
                ["java", "-cp", str(workdir), "Main"],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "kotlin":
            path = self._write(workdir, "Main.kt", source)
            jar = workdir / "main.jar"

            return self._compile_then_run(
                ["kotlinc", str(path), "-include-runtime", "-d", str(jar)],
                ["java", "-jar", str(jar)],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "typescript":
            path = self._write(workdir, "main.ts", source)

            if shutil.which("tsx"):
                command = ["tsx", str(path)]
            elif shutil.which("ts-node"):
                command = ["ts-node", str(path)]
            else:
                output_dir = workdir / "compiled"
                compile_result = self._run(
                    [
                        "tsc",
                        "--target",
                        "ES2020",
                        "--module",
                        "commonjs",
                        "--outDir",
                        str(output_dir),
                        str(path),
                    ],
                    cwd=workdir,
                    deadline=deadline,
                )

                if compile_result.returncode != 0:
                    return self._from_process(compile_result, started)

                return self._from_process(
                    self._run(
                        ["node", str(output_dir / "main.js")],
                        cwd=workdir,
                        deadline=deadline,
                    ),
                    started,
                )

            return self._from_process(
                self._run(command, cwd=workdir, deadline=deadline),
                started,
            )

        if language == "swift":
            path = self._write(workdir, "main.swift", source)
            return self._from_process(
                self._run(["swift", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "dart":
            path = self._write(workdir, "main.dart", source)
            return self._from_process(
                self._run(["dart", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "haskell":
            path = self._write(workdir, "Main.hs", source)
            runner = shutil.which("runghc") or shutil.which("runhaskell")

            return self._from_process(
                self._run([str(runner), str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "ocaml":
            path = self._write(workdir, "main.ml", source)
            return self._from_process(
                self._run(["ocaml", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "elixir":
            path = self._write(workdir, "main.exs", source)
            return self._from_process(
                self._run(["elixir", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "erlang":
            path = self._write(workdir, "main.escript", source)
            return self._from_process(
                self._run(["escript", str(path)], cwd=workdir, deadline=deadline),
                started,
            )

        if language == "fortran":
            path = self._write(workdir, "main.f90", source)
            executable = workdir / "main"
            compiler = shutil.which("gfortran") or shutil.which("flang")

            return self._compile_then_run(
                [str(compiler), str(path), "-o", str(executable)],
                [str(executable)],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "cobol":
            path = self._write(workdir, "main.cob", source)
            executable = workdir / "main"

            return self._compile_then_run(
                ["cobc", "-x", "-o", str(executable), str(path)],
                [str(executable)],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "nim":
            path = self._write(workdir, "main.nim", source)
            executable = workdir / "main"

            return self._compile_then_run(
                [
                    "nim",
                    "c",
                    "--hints:off",
                    "--out:" + str(executable),
                    str(path),
                ],
                [str(executable)],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "crystal":
            path = self._write(workdir, "main.cr", source)
            executable = workdir / "main"

            return self._compile_then_run(
                ["crystal", "build", str(path), "-o", str(executable)],
                [str(executable)],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "d":
            path = self._write(workdir, "main.d", source)
            executable = workdir / "main"

            if shutil.which("dmd"):
                compile_command = ["dmd", "-of=" + str(executable), str(path)]
            elif shutil.which("ldc2"):
                compile_command = ["ldc2", "-of=" + str(executable), str(path)]
            else:
                compile_command = ["gdc", str(path), "-o", str(executable)]

            return self._compile_then_run(
                compile_command,
                [str(executable)],
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "scala":
            path = self._write(workdir, "main.scala", source)

            if shutil.which("scala-cli"):
                command = ["scala-cli", "run", str(path)]
            else:
                command = ["scala", str(path)]

            return self._from_process(
                self._run(command, cwd=workdir, deadline=deadline),
                started,
            )

        if language == "fsharp":
            path = self._write(workdir, "main.fsx", source)

            if shutil.which("dotnet"):
                command = ["dotnet", "fsi", str(path)]
            elif shutil.which("fsi"):
                command = ["fsi", str(path)]
            else:
                command = ["fsharpi", str(path)]

            return self._from_process(
                self._run(command, cwd=workdir, deadline=deadline),
                started,
            )

        if language == "csharp":
            path = self._write(workdir, "Program.cs", source)

            if shutil.which("dotnet"):
                project = workdir / "AssayFluxTemp.csproj"
                project.write_text(
                    "<Project Sdk=\"Microsoft.NET.Sdk\">"
                    "<PropertyGroup>"
                    "<OutputType>Exe</OutputType>"
                    "<TargetFramework>net8.0</TargetFramework>"
                    "<ImplicitUsings>enable</ImplicitUsings>"
                    "<Nullable>enable</Nullable>"
                    "</PropertyGroup></Project>",
                    encoding="utf-8",
                )

                return self._from_process(
                    self._run(
                        ["dotnet", "run", "--project", str(project), "--no-launch-profile"],
                        cwd=workdir,
                        deadline=deadline,
                    ),
                    started,
                )

            compiler = shutil.which("csc") or shutil.which("mcs")
            executable = workdir / "main.exe"

            if Path(compiler).name == "mcs":
                compile_command = [str(compiler), "-out:" + str(executable), str(path)]
            else:
                compile_command = [str(compiler), "/out:" + str(executable), str(path)]

            runner = shutil.which("mono")

            if runner:
                run_command = [str(runner), str(executable)]
            else:
                run_command = [str(executable)]

            return self._compile_then_run(
                compile_command,
                run_command,
                workdir=workdir,
                deadline=deadline,
                started=started,
            )

        if language == "sql":
            return self._execute_sql(source, started)

        if language in ("html", "css"):
            return self._handle_static_asset(source, started)

        raise RuntimeError(
            f"No execution strategy is implemented for '{language}'."
        )

    def _execute_sql(
        self,
        source: str,
        started: float,
    ) -> ExecutionResult:
        """
        Execute SQL in an in-memory SQLite database.

        Each request starts with an empty database. Multiple SQL
        statements can create tables, insert rows, and query them.
        Query results are formatted as tab-separated output.
        """
        import sqlite3

        connection = sqlite3.connect(":memory:")
        output: list[str] = []

        try:
            statement = ""

            for line in source.splitlines():
                statement += line + "\n"

                if not sqlite3.complete_statement(statement):
                    continue

                sql = statement.strip()
                statement = ""

                if not sql:
                    continue

                cursor = connection.execute(sql)

                if cursor.description:
                    for row in cursor.fetchall():
                        output.append("\t".join(str(value) for value in row))

            if statement.strip():
                raise sqlite3.OperationalError(
                    "Incomplete SQL statement at end of input."
                )

            return self._result(
                stdout="".join(line + "\n" for line in output),
                stderr="",
                returncode=0,
                started=started,
            )

        except sqlite3.Error as exc:
            return self._result(
                stdout="".join(line + "\n" for line in output),
                stderr=f"SQLite error: {exc}",
                returncode=1,
                started=started,
            )
        finally:
            connection.close()

    def _handle_static_asset(
        self,
        source: str,
        started: float,
    ) -> ExecutionResult:
        """
        Accept HTML or CSS source as a static asset.

        This does not launch a browser or claim to perform full
        standards-compliant HTML/CSS validation.
        """
        if not source.strip():
            return self._result(
                stdout="",
                stderr=f"{self._language.upper()} source is empty.",
                returncode=1,
                started=started,
            )

        description = (
            "HTML static asset accepted; browser rendering is not performed."
            if self._language == "html"
            else "CSS static asset accepted; browser rendering is not performed."
        )

        return self._result(
            stdout=description + "\n",
            stderr="",
            returncode=0,
            started=started,
        )