"""
AssayFlux Scientific Systems
============================

AssayFlux is an experimental programming language project designed
for scientific computing and future multi-language integration.

The package will eventually provide:
- A lexer for tokenizing AssayFlux source code.
- A parser for validating language syntax.
- An interpreter for executing AssayFlux programs.
- A standard library for scientific computing.
- Interfaces for integrating other programming languages.

Project version: 0.2.0
"""

__title__ = "AssayFlux Scientific Systems"
__version__ = "0.2.0"
__author__ = "AssayFlux Contributors"
__description__ = (
    "A programming language for scientific computing "
    "and multi-language integration."
)

__all__ = [
    "__title__",
    "__version__",
    "__author__",
    "__description__",
"""Command-line launcher for AssayFlux."""

import argparse
import sys
from pathlib import Path

from assayflux.interpreter import Interpreter


def main():
    parser = argparse.ArgumentParser(
        prog="assayflux",
        description="Run an AssayFlux Scientific Systems program.",
    )

    parser.add_argument(
        "file",
        help="Path to the AssayFlux source file.",
    )

    args = parser.parse_args()
    source_path = Path(args.file)

    if not source_path.is_file():
        print(
            f"AssayFlux error: File not found: {source_path}",
            file=sys.stderr,
        )
        return 1

    try:
        source = source_path.read_text(encoding="utf-8")
        interpreter = Interpreter()
        interpreter.run(source)
    except (OSError, UnicodeError) as error:
        print(
            f"AssayFlux file error: {error}",
            file=sys.stderr,
        )
        return 1
    except Exception as error:
        print(
            f"AssayFlux execution error: {error}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())