# AssayFlux

**One language. Clear rules. Controlled execution.**

AssayFlux is an experimental programming language with canonical `.af` source files, a grammar-driven lexer/parser, source-located AST, semantic checks, and a budgeted interpreter.

## Quick start

Requires Python 3.11 or newer.

```bash
python -m pip install -e ".[dev]"
assayflux check examples/hello.af
assayflux run examples/hello.af
```

## Language example

```af
project "Hello AssayFlux"

name = "AssayFlux"
answer = 6 * 7

f.greet(person):
    show "Hello, " + person
end

greet(name)
show answer

3 times:
    show "Build. Test. Improve."
end
```

## Canonical choices

- Files use `.af`.
- Project declaration: `project "Name"`.
- Assignment: `NAME = expression`.
- Functions: `f.name(parameters): ... end`.
- Null and booleans: `null`, `true`, `false`.
- Counted repetition: `N times:`.
- Compound statements use indentation and a matching `end`.

Read [GRAMMAR.md](GRAMMAR.md) for syntax and [SECURITY.md](SECURITY.md) for runtime boundaries.

## Core architecture

- `src/assayflux/language/grammar.lark` — canonical grammar and token rules.
- `src/assayflux/language/parser.py` — lexer/parser integration and AST construction.
- `src/assayflux/language/ast_nodes.py` — source-located AST.
- `src/assayflux/language/ast_validator.py` — structural AST validation.
- `src/assayflux/language/semantic.py` — name resolution and conservative type checks.
- `src/assayflux/runtime/interpreter.py` — budgeted interpreter.
- `src/assayflux/diagnostics/` — structured compiler/runtime errors.
- `src/assayflux/security/` — source validation and runtime policy.
- `src/assayflux/cli.py` and `src/assayflux/api.py` — command-line and public APIs.

The lexer is provided by Lark's contextual lexer from the canonical grammar; token definitions should not be duplicated in a second, divergent lexer.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests
```

The repository intentionally focuses on the language core. Separate services can be reconnected later through explicit, tested language APIs. No photo-editing functionality is part of the core.

AssayFlux is experimental software, not an OS-enforced sandbox. Do not run untrusted programs with sensitive privileges.
