"""Execute a small smoke-test program through every language adapter."""

import os
import unittest

from assayflux.interop.loader import get_adapter, get_default_registry


MARKER = "ASSAYFLUX_SMOKE_OK"

REQUIRE_ALL_RUNTIMES = (
    os.environ.get("ASSAYFLUX_REQUIRE_ALL_RUNTIMES", "")
    .strip()
    .lower()
    in {"1", "true", "yes", "on"}
)


SMOKE_PROGRAMS = {
    "python": 'print("ASSAYFLUX_SMOKE_OK")',

    "javascript": 'console.log("ASSAYFLUX_SMOKE_OK");',

    "c": (
        '#include <stdio.h>\n'
        'int main(void) { puts("ASSAYFLUX_SMOKE_OK"); return 0; }'
    ),

    "cpp": (
        '#include <iostream>\n'
        'int main() { '
        'std::cout << "ASSAYFLUX_SMOKE_OK" << std::endl; '
        'return 0; }'
    ),

    "java": (
        'public class Main { '
        'public static void main(String[] args) { '
        'System.out.println("ASSAYFLUX_SMOKE_OK"); '
        '} }'
    ),

    "rust": 'fn main() { println!("ASSAYFLUX_SMOKE_OK"); }',

    "typescript": 'console.log("ASSAYFLUX_SMOKE_OK");',

    "go": (
        'package main\n'
        'import "fmt"\n'
        'func main() { fmt.Println("ASSAYFLUX_SMOKE_OK") }'
    ),

    "kotlin": 'fun main() { println("ASSAYFLUX_SMOKE_OK") }',

    "csharp": (
        'using System;\n'
        'public class Program { '
        'public static void Main() { '
        'Console.WriteLine("ASSAYFLUX_SMOKE_OK"); '
        '} }'
    ),

    "php": '<?php echo "ASSAYFLUX_SMOKE_OK";',

    "ruby": 'puts "ASSAYFLUX_SMOKE_OK"',

    "lua": 'print("ASSAYFLUX_SMOKE_OK")',

    "perl": 'print "ASSAYFLUX_SMOKE_OK";',

    "fortran": (
        'program main\n'
        '  print *, "ASSAYFLUX_SMOKE_OK"\n'
        'end program main'
    ),

    "swift": 'print("ASSAYFLUX_SMOKE_OK")',

    "dart": 'void main() { print("ASSAYFLUX_SMOKE_OK"); }',

    "r": 'cat("ASSAYFLUX_SMOKE_OK")',

    "julia": 'println("ASSAYFLUX_SMOKE_OK")',

    "crystal": 'puts "ASSAYFLUX_SMOKE_OK"',

    "scala": (
        'object Main { '
        'def main(args: Array[String]): Unit = '
        'println("ASSAYFLUX_SMOKE_OK") }'
    ),

    "elixir": 'IO.puts("ASSAYFLUX_SMOKE_OK")',

    "erlang": (
        '-module(assayflux_main).\n'
        '-export([main/0]).\n'
        'main() -> io:format("ASSAYFLUX_SMOKE_OK~n").'
    ),

    "haskell": 'main = putStrLn "ASSAYFLUX_SMOKE_OK"',

    "ocaml": 'print_endline "ASSAYFLUX_SMOKE_OK"',

    "fsharp": 'printfn "ASSAYFLUX_SMOKE_OK"',

    "zig": (
        'const std = @import("std");\n'
        'pub fn main() void { '
        'std.debug.print("ASSAYFLUX_SMOKE_OK\\n", .{}); }'
    ),

    "nim": 'echo "ASSAYFLUX_SMOKE_OK"',

    "d": (
        'import std.stdio;\n'
        'void main() { writeln("ASSAYFLUX_SMOKE_OK"); }'
    ),

    "cobol": (
        'identification division.\n'
        'program-id. assayflux-smoke.\n'
        'procedure division.\n'
        '    display "ASSAYFLUX_SMOKE_OK".\n'
        '    stop run.'
    ),
}


class TestAdapterExecutionSmoke(unittest.TestCase):
    """Check that language adapters actually execute source code."""

    def test_all_registered_languages_have_smoke_programs(self):
        registry = get_default_registry()

        self.assertEqual(
            set(SMOKE_PROGRAMS),
            set(registry.registered_languages()),
            "Every registered adapter must have a smoke-test program.",
        )

    def test_language_adapters_execute_programs(self):
        registry = get_default_registry()

        unavailable = []
        failures = []

        for language in registry.registered_languages():
            with self.subTest(language=language):
                adapter = get_adapter(language)

                if not adapter.is_available():
                    unavailable.append(language)

                    if REQUIRE_ALL_RUNTIMES:
                        failures.append(
                            f"{language}: runtime/compiler unavailable"
                        )

                    continue

                try:
                    result = adapter.execute(
                        SMOKE_PROGRAMS[language],
                        timeout=120.0,
                    )

                except Exception as exc:
                    failures.append(
                        f"{language}: {type(exc).__name__}: {exc}"
                    )
                    continue

                output = result.stdout + "\n" + result.stderr

                if not result.success:
                    failures.append(
                        f"{language}: execution failed with exit code "
                        f"{result.returncode}; "
                        f"stdout={result.stdout!r}; "
                        f"stderr={result.stderr!r}"
                    )

                elif MARKER not in output:
                    failures.append(
                        f"{language}: expected output marker missing; "
                        f"stdout={result.stdout!r}; "
                        f"stderr={result.stderr!r}"
                    )

        if unavailable and not REQUIRE_ALL_RUNTIMES:
            print(
                "\nAdapters skipped because runtimes are unavailable: "
                + ", ".join(unavailable)
            )

        self.assertFalse(
            failures,
            "Adapter execution failures:\n- " + "\n- ".join(failures),
        )


if __name__ == "__main__":
    unittest.main()