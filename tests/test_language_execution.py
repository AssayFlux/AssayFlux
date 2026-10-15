"""Smoke tests for the AssayFlux language execution adapters."""

import pytest

from assayflux.interop.loader import get_default_registry
from assayflux.interop.runtime import execute_code


SMOKE_TESTS = {
    "python": 'print("ASSAYFLUX_SMOKE_OK")',
    "javascript": 'console.log("ASSAYFLUX_SMOKE_OK");',
    "typescript": 'console.log("ASSAYFLUX_SMOKE_OK");',
    "c": '#include <stdio.h>\nint main(void) { puts("ASSAYFLUX_SMOKE_OK"); return 0; }',
    "cpp": '#include <iostream>\nint main() { std::cout << "ASSAYFLUX_SMOKE_OK" << std::endl; return 0; }',
    "java": 'public class Main { public static void main(String[] args) { System.out.println("ASSAYFLUX_SMOKE_OK"); } }',
    "rust": 'fn main() { println!("ASSAYFLUX_SMOKE_OK"); }',
    "go": 'package main\nimport "fmt"\nfunc main() { fmt.Println("ASSAYFLUX_SMOKE_OK") }',
    "kotlin": 'fun main() { println("ASSAYFLUX_SMOKE_OK") }',
    "csharp": 'using System; class Program { static void Main() { Console.WriteLine("ASSAYFLUX_SMOKE_OK"); } }',
    "php": '<?php echo "ASSAYFLUX_SMOKE_OK\\n";',
    "ruby": 'puts "ASSAYFLUX_SMOKE_OK"',
    "lua": 'print("ASSAYFLUX_SMOKE_OK")',
    "perl": 'print "ASSAYFLUX_SMOKE_OK\\n";',
    "fortran": 'program main\nprint *, "ASSAYFLUX_SMOKE_OK"\nend program main',
    "swift": 'print("ASSAYFLUX_SMOKE_OK")',
    "dart": 'void main() { print("ASSAYFLUX_SMOKE_OK"); }',
    "r": 'cat("ASSAYFLUX_SMOKE_OK\\n")',
    "julia": 'println("ASSAYFLUX_SMOKE_OK")',
    "crystal": 'puts "ASSAYFLUX_SMOKE_OK"',
    "scala": 'object Main { def main(args: Array[String]): Unit = println("ASSAYFLUX_SMOKE_OK") }',
    "elixir": 'IO.puts("ASSAYFLUX_SMOKE_OK")',
    "erlang": '-module(main).\n-export([start/0]).\nstart() -> io:format("ASSAYFLUX_SMOKE_OK~n"), halt().',
    "haskell": 'main = putStrLn "ASSAYFLUX_SMOKE_OK"',
    "ocaml": 'print_endline "ASSAYFLUX_SMOKE_OK";;',
    "fsharp": 'printfn "ASSAYFLUX_SMOKE_OK"',
    "zig": 'const std = @import("std");\npub fn main() void { std.debug.print("ASSAYFLUX_SMOKE_OK\\n", .{}); }',
    "nim": 'echo "ASSAYFLUX_SMOKE_OK"',
    "d": 'import std.stdio; void main() { writeln("ASSAYFLUX_SMOKE_OK"); }',
    "cobol": '       IDENTIFICATION DIVISION.\n       PROGRAM-ID. MAINPROG.\n       PROCEDURE DIVISION.\n           DISPLAY "ASSAYFLUX_SMOKE_OK".\n           STOP RUN.\n',
}


@pytest.mark.parametrize("language", sorted(SMOKE_TESTS))
def test_language_executes_smoke_program(language):
    """Run a minimal program when its external runtime is available."""

    registry = get_default_registry()

    if not registry.is_registered(language):
        pytest.fail(f"{language}: adapter is not registered")

    adapter = registry.get(language)

    if not adapter.is_available():
        pytest.skip(f"{language}: required runtime is not installed")

    result = execute_code(
        language,
        SMOKE_TESTS[language],
        timeout=30,
    )

    assert result.returncode == 0, (
        f"{language} execution failed.\n"
        f"Exit code: {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    combined_output = result.stdout + result.stderr

    assert "ASSAYFLUX_SMOKE_OK" in combined_output, (
        f"{language} ran but did not produce the expected output.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )