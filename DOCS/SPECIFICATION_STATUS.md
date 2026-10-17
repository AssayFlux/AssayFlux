# AssayFlux Specification Status

This document tracks the relationship between the AssayFlux
language specification, its implementation, and its automated tests.

The presence of a source file does not, by itself, establish that
a feature is complete or supported.

## Status definitions

- **Specified:** The intended behavior is documented.
- **Implemented:** An implementation exists in the source code.
- **Tested:** Automated tests verify the documented behavior.
- **Verified:** The feature has been checked against its intended
  behavior in a defined environment.
- **Planned:** The feature is intended but is not yet complete.

A feature should be described as supported only when its documented
behavior has been verified.

## Language core

| Component | Implementation location | Verification requirement |
|---|---|---|
| Lexical analysis | `assayflux/lexer.py` | Token and lexical-error tests |
| Parsing | `assayflux/parser.py` | Grammar and parser tests |
| Abstract syntax tree | `assayflux/ast_nodes.py` | AST construction tests |
| Interpretation | `assayflux/interpreter.py` | Runtime behavior tests |
| Semantic validation | `assayflux/validator.py` | AST compatibility and semantic tests |
| Command-line interface | `assayflux/cli.py` | CLI execution tests |
| Package entry point | `assayflux/__main__.py` | Invocation tests |

## Language features

| Feature | Verification requirement |
|---|---|
| Variables and assignments | Assignment, scope, and reassignment tests |
| Constants | Declaration and reassignment tests |
| Numeric literals | Integer, floating-point, and supported numeric-form tests |
| String literals | Valid strings, escapes, and unterminated strings |
| Boolean literals | `true` and `false` evaluation |
| Arithmetic operators | Precedence, evaluation, and error tests |
| Comparison operators | Comparison behavior tests |
| Logical operators | Truth behavior and short-circuit tests |
| `show` | Output tests |
| `if` / `otherwise` / `else` | Branch-selection tests |
| `repeat` | Condition, count, and forever-loop tests |
| `stop` and `skip` | Loop-control tests |
| `pass` | No-operation behavior |
| Functions | Definition, calls, arguments, return values, and scope |
| Imports | Module resolution, aliases, and import errors |
| Member access | Module and object attribute tests |
| Error locations | Filename, line, and column tests |

## Interoperability

| Component | Implementation location | Verification requirement |
|---|---|---|
| Adapter interface | `assayflux/interop/base.py` | Interface contract tests |
| Adapter registry | `assayflux/interop/registry.py` | Registration and lookup tests |
| Adapter loader | `assayflux/interop/loader.py` | Resolution and availability tests |
| Interoperability runtime | `assayflux/interop/runtime.py` | Dispatch and error tests |
| Master adapter | `assayflux/interop/adapters/master_adapter.py` | Language-specific integration tests |
| Universal adapter | `assayflux/interop/adapters/universal_adapter.py` | Compatibility tests |

For each external language, distinguish between:

1. Adapter registered.
2. Required runtime available.
3. Execution implemented.
4. Integration tests passing.
5. Feature documented as supported.

These states must not be treated as equivalent.

## Code generation

| Generator | Implementation location | Verification requirement |
|---|---|---|
| HTML | `assayflux/generator/html_generator.py` | Generated document tests |
| CSS | `assayflux/generator/css_generator.py` | Generated stylesheet tests |
| JavaScript | `assayflux/generator/js_generator.py` | Generated source tests |
| Python | `assayflux/generator/python_generator.py` | Generated source tests |
| SQL | `assayflux/generator/sql_generator.py` | Generated query tests |
| Project builder | `assayflux/generator/project_builder.py` | End-to-end project tests |

Code generation does not automatically imply that the generated language
can be executed directly by the AssayFlux interpreter.

## Automated tests

The primary test suite is:

```bash
python -m pytest -q