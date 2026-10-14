# AssayFlux Language Specification Status

**Language:** AssayFlux Scientific Systems  
**Short name:** AssayFlux  
**Source extension:** `.af`  
**Project version:** 0.1.0

## 1. Purpose

This document tracks the implementation status of AssayFlux language
features.

A feature must not be described as fully supported merely because its
syntax appears in an example or documentation file.

## 2. Status Definitions

- **Implemented:** Code for the feature exists.
- **Tested:** Automated tests verify the feature's behavior.
- **Planned:** The feature is intended but is not yet implemented.
- **Experimental:** The feature exists but its behavior may change.

## 3. Core Language

| Feature | Current status | Next action |
|---|---|---|
| Source extension `.af` | Defined | Preserve consistently |
| Comments using `#` | Implemented | Add execution tests |
| Integer literals | Implemented | Test numeric behavior |
| Decimal literals | Implemented | Test numeric behavior |
| Backtick strings | Implemented | Test escaping |
| Boolean literals | Implemented | Test conditions |
| Variables | Implemented | Test scope and reassignment |
| Constants | Initial implementation | Test reassignment errors |
| `show` | Implemented | Test output behavior |
| Arithmetic operators | Implemented | Test edge cases |
| Comparison operators | Implemented | Test all operators |
| Logical operators | Initial implementation | Test short-circuit behavior |
| `if` / `otherwise` / `else` | Implemented | Test branch selection |
| `repeat` | Implemented | Test loop boundaries |
| `stop` / `skip` | Implemented | Test loop control |
| Functions | Initial implementation | Test calls and scope |
| `return` | Initial implementation | Test returned values |
| `input()` | Planned | Implement runtime support |
| Module imports | Initial syntax | Design and implement module system |
| Useful diagnostics | Initial implementation | Improve errors and source locations |

## 4. Developer Tools

| Feature | Current status |
|---|---|
| Python package structure | Created |
| Command-line launcher | Created; needs execution tests |
| Automated unit tests | Initial suite passes |
| GitHub Actions | Configured |
| Multi-version Python testing | Planned |
| Static type checking | Planned |
| Test coverage reporting | Planned |
| Release automation | Planned |

## 5. Multi-Language Interoperability

The following integrations are goals, not currently guaranteed capabilities.

| Language | Status |
|---|---|
| Python | Planned |
| C | Planned |
| C++ | Planned |
| Java | Planned |
| JavaScript | Planned |
| Rust | Planned |

Each integration must have an implementation, documented calling
conventions, error handling, dependency requirements, and tests before
being advertised as supported.

## 6. Compatibility Policy

Before changing established language behavior:

1. Update the formal language specification.
2. Update the dictionary.
3. Add or update automated tests.
4. Implement the change.
5. Run the complete test suite.
6. Document incompatible changes in release notes.

## 7. Immediate Priorities

1. Expand automated tests.
2. Verify the interpreter's existing behavior.
3. Resolve differences between the grammar and implementation.
4. Define the language's formal syntax and semantics.
5. Implement missing core features.
6. Build the standard library and interoperability architecture.
7. Develop the Android IDE.

## 8. Release Principle

AssayFlux should only claim support for features that have been
implemented and verified.

A passing test suite confirms only the behavior covered by its tests.
It does not establish that every part of the language is complete.