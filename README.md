<div align="center">

<br>

<img src="assayflux-logo.png" alt="AssayFlux" width="450">

<br><br>

#

### Programming Language & Interpreter

A dedicated programming-language project built around the development
of AssayFlux syntax, interpretation, and execution.

<br>

</div>

---

## Overview

AssayFlux is a programming-language project with its own `.af` source
files and an evolving interpreter implementation.

The repository includes example programs covering fundamental programming
concepts, including variables, conditions, loops, functions, and input.

The project focuses on developing a consistent language experience,
maintaining a testable implementation, and documenting supported behavior
as the interpreter evolves.

## Language Examples

The following source files demonstrate the principal example categories
currently associated with the project.

| Source file | Description |
|:--|:--|
| `hello.af` | Introductory program |
| `variables.af` | Variables and values |
| `conditions.af` | Conditional logic |
| `loops.af` | Loops and repetition |
| `functions.af` | Functions |
| `input.af` | Input handling |

The examples are intended to illustrate the language. Their precise
syntax and behavior are determined by the actual source files and the
interpreter implementation.

## Getting Started

### Explore the Source

Begin with the existing `.af` examples.

```text
hello.af
variables.af
conditions.af
loops.af
functions.af
input.af
```

Read the examples to understand the syntax currently supported by
AssayFlux.

### Running Programs

The execution command depends on the interpreter's actual entry point
and command-line interface.

Consult the repository's implementation and existing instructions
before running a program. No unverified execution command is specified
here.

## Interpreter Development

The interpreter is the central component responsible for processing
AssayFlux programs and producing their runtime behavior.

Development and verification can cover several areas:

- Source-code processing.
- Language syntax and expression handling.
- Variables and conditional execution.
- Loop and function behavior.
- Input and output.
- Runtime errors and diagnostics.
- Regression testing.

These areas describe the scope of interpreter development; they do not
imply that every capability is already implemented.

## Testing

Automated testing helps verify language behavior and detect regressions
when the interpreter changes.

The test suite should reflect the features supported by the current
implementation.

Testing priorities include:

- Valid and invalid source programs.
- Variable assignment and expressions.
- Conditional branches.
- Loop behavior and termination.
- Functions and input handling.
- Runtime error handling.
- Regression coverage for existing examples.

Use the testing framework and commands configured in the repository.

## Development Principles

AssayFlux development should prioritize:

**Consistency**

Keep syntax and runtime behavior predictable.

**Reliability**

Verify changes against examples and automated tests.

**Maintainability**

Keep the implementation understandable and straightforward to extend.

**Documentation**

Document supported behavior accurately and distinguish implemented
features from planned improvements.

## Project Status

AssayFlux is an evolving programming-language project.

The available language features, interpreter capabilities, installation
requirements, and execution methods should be established from the
current repository.

Documentation should reflect the implementation rather than promise
unverified functionality.

## Contributing

Contributions that improve the interpreter, examples, tests, and
documentation can help advance the project.

Before submitting changes:

1. Review the existing implementation.
2. Preserve existing behavior where possible.
3. Add tests for new or modified functionality.
4. Run the configured test suite.
5. Update documentation when behavior changes.

## Security

Do not commit passwords, access tokens, private credentials, or other
sensitive information.

Programs executed by an interpreter should be treated according to
the capabilities and security properties of the actual implementation.
Do not assume that arbitrary source code is safe to execute.

## License

Refer to the repository's license file, if present, for the applicable
licensing terms.

If no license has been established, clarify the licensing status before
claiming that unrestricted reuse or redistribution is permitted.

---
