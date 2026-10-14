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