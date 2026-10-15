# AssayFlux Language Specification

**Full Name:** AssayFlux Scientific Systems  
**Short Name:** AssayFlux  
**Version:** 0.2.0  
**Source Extension:** `.af`  
**Status:** Language design specification

---

## 1. Introduction

AssayFlux is a general-purpose programming language designed for scientific computing, automation, and interoperability with other programming languages.

Its syntax is inspired by Python, with custom keywords and explicit block termination.

AssayFlux aims to combine familiar programming concepts with a clear, consistent language specification.

The formal grammar in `GRAMMAR.md` is the authoritative reference for syntax.

## 2. Language Design Principles

AssayFlux follows these principles:

1. Readable and consistent syntax.
2. Python-inspired expressions and assignments.
3. Strict indentation for readable code.
4. Explicit `end` keywords for block termination.
5. Reuse of existing Python libraries wherever practical.
6. A common architecture for future language integrations.
7. Clear errors and predictable behavior.
8. Compatibility between the specification, implementation, and tests.

## 3. Source Files

AssayFlux source files use the `.af` extension.

Example:

`main.af`

An AssayFlux program consists of statements, expressions, and optional declarations.

## 4. Variables and Constants

Variables use ordinary assignment syntax.

```text
temperature = 25
name = "AssayFlux"
enabled = true
```

Constants use the `constant` keyword.

```text
constant PI = 3.14159
constant MAX_ITERATIONS = 1000
```

Variables may be reassigned according to the language's scope rules.

Constants cannot be reassigned after initialization.

## 5. Data and Strings

The initial language design includes:

- Integer values.
- Floating-point values.
- String values.
- Boolean values.
- Function return values.
- Objects supplied by supported external libraries.

Strings use single or double quotes.

```text
first = "Hello"
second = 'AssayFlux'
```

The language will define supported escape sequences and value-conversion rules.

## 6. Operators

AssayFlux uses familiar arithmetic and comparison operators.

| Operator | Purpose |
|---|---|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Remainder |
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

The custom operator `nt=` is not valid AssayFlux syntax.

## 7. Output

The `show` keyword displays a value.

```text
show "Hello, AssayFlux!"
show 10 + 20
```

The runtime will define how supported values are represented in output.

## 8. Conditional Statements

AssayFlux uses `if`, `otherwise`, `else`, and `end`.

```text
temperature = 25

if temperature > 30
    show "Hot"
otherwise temperature > 20
    show "Warm"
else
    show "Cold"
end
```

Rules:

- `if` introduces the first condition.
- `otherwise` introduces an additional condition.
- `else` provides an optional final alternative.
- `end` closes the complete conditional statement.

Only the first matching branch executes.

## 9. Loops

AssayFlux uses `repeat` for repetition.

```text
count = 0

repeat count < 5
    show count
    count = count + 1
end
```

The loop repeats while its condition evaluates to true.

The language also defines:

- `stop` — exits the innermost active loop.
- `skip` — skips the remainder of the current iteration.

Both statements must appear inside a loop.

## 10. Functions

Function declarations use the `f.` prefix.

```text
f.add(a, b)
    return a + b
end

result = add(10, 20)
show result
```

Rules:

- `f.` introduces a function declaration.
- Parameters are declared inside parentheses.
- `return` returns a value.
- `end` closes the function.
- Function calls do not use the `f.` prefix.

The language specification must define argument validation, function scope, recursion, and return behavior.

## 11. Strict Formatting

AssayFlux requires strict indentation.

The formatting rules are:

1. Use four spaces per indentation level.
2. Do not use tabs for indentation.
3. Indent statements inside a block by one level.
4. Indent nested blocks by additional levels.
5. Align `else` and `otherwise` with their matching `if`.
6. Align `end` with the statement that opened its block.
7. Reject inconsistent indentation.
8. Do not use indentation alone to replace a required `end`.

Example:

```text
if enabled
    repeat count < 3
        show count
        count = count + 1
    end
end
```

Indentation and explicit block termination are both required.

The lexer and parser must enforce these rules before strict formatting can be considered implemented.

## 12. Python Library Integration

Python is the initial interoperability target.

AssayFlux is intended to reuse Python libraries rather than recreate their functionality.

The proposed import syntax follows Python-style imports.

```text
import math

result = math.sqrt(25)
show result
```

The intended output is:

```text
5.0
```

This example defines the intended behavior; it does not establish that Python module imports and member access are fully implemented.

The integration layer must define:

- Module resolution.
- Alias handling.
- Function invocation.
- Argument and return-value conversion.
- Error propagation.
- Dependency management.
- Runtime requirements.

Executing Python code can execute arbitrary code. A normal Python process must not be treated as a security sandbox.

## 13. Multi-Language Interoperability

AssayFlux is designed to support additional language integrations.

Potential targets include:

- Python.
- JavaScript.
- C.
- C++.
- Java.
- Rust.

Each integration must have a defined interface, supported data types, error handling, runtime requirements, and automated tests.

These are development goals until the corresponding implementations have been verified.

## 14. Errors and Diagnostics

AssayFlux should distinguish between:

- Lexical errors.
- Syntax errors.
- Semantic errors.
- Runtime errors.
- Import errors.
- External integration errors.

Where possible, diagnostics should include the source file, line, column, explanation, and suggested correction.

## 15. Implementation Requirements

The language implementation consists of:

1. Lexer.
2. Parser.
3. Abstract syntax tree.
4. Semantic validation.
5. Interpreter.
6. Python interoperability layer.
7. Error reporting.
8. Automated tests.

Each component must follow the authoritative grammar.

A documented feature must not be described as implemented merely because its syntax is specified.

## 16. Compatibility

The language specification defines the intended behavior of AssayFlux.

Changes to established syntax must be documented.

Breaking changes must be recorded in the changelog and handled through an explicit versioning policy.

The grammar, examples, implementation, and tests must remain consistent.

## 17. Development Status

AssayFlux is being developed incrementally.

The existence of a specification does not establish that all specified features work.

Implementation status must be tracked separately and updated as features are implemented and tested.

The project must not claim complete language support until the relevant behavior has been verified.