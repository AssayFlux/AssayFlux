# AssayFlux Language Examples

**Project:** AssayFlux Scientific Systems  
**Language:** AssayFlux  
**Version:** 0.1.0  
**Status:** Examples for the proposed language specification

---

## 1. Hello World

```assayflux
show "Hello, World!"
```

Expected output:

```text
Hello, World!
```

## 2. Variables

```assayflux
name = "AssayFlux"
version = 0.1

show name
show version
```

## 3. Numbers and Calculations

```assayflux
a = 10
b = 5

sum = a + b
difference = a - b
product = a * b
quotient = a / b
remainder = a % b

show sum
show difference
show product
show quotient
show remainder
```

## 4. Boolean Values

```assayflux
is_ready = true
has_error = false

show is_ready
show has_error
```

## 5. Constants

```assayflux
const PI = 3.14159
const MAX_ITERATIONS = 1000

show PI
show MAX_ITERATIONS
```

Constants cannot be reassigned after initialization.

## 6. Conditional Statements

```assayflux
temperature = 30

if temperature > 35
    show "It is very hot"
otherwise temperature > 20
    show "The temperature is moderate"
else
    show "It is cold"
end
```

Rules:

- `if` introduces the first condition.
- `otherwise` introduces an additional condition.
- `else` provides an optional final alternative.
- `end` closes the conditional statement.
- `otherwise`, `else`, and `end` must align with the opening `if`.
- Statements inside each branch must be indented by four spaces.

## 7. Comparison Operators

```assayflux
a = 10
b = 20

show a == b
show a != b
show a > b
show a < b
show a >= b
show a <= b
```

The `!=` operator means not equal.

The former `nt=` operator is not valid AssayFlux syntax.

## 8. Logical Operators

### Logical AND

```assayflux
age = 25
has_permission = true

if age >= 18 and has_permission
    show "Access granted"
else
    show "Access denied"
end
```

### Logical OR

```assayflux
is_scientist = false
is_student = true

if is_scientist or is_student
    show "Scientific tools available"
else
    show "General tools available"
end
```

### Logical NOT

```assayflux
is_ready = false

if not is_ready
    show "Not ready"
end
```

## 9. Repetition

A conditional `repeat` loop continues while its condition is true.

```assayflux
count = 0

repeat count < 5
    show "Hello from AssayFlux"
    count = count + 1
end
```

The loop executes five times.

The loop's `end` must align with `repeat`.

## 10. Stop a Loop

The `stop` statement exits the innermost active loop.

```assayflux
repeat true
    show "Loop running"
    stop
end
```

Expected output:

```text
Loop running
```

## 11. Skip an Iteration

The `skip` statement skips the remainder of the current iteration.

```assayflux
count = 0

repeat count < 5
    count = count + 1

    if count == 3
        skip
    end

    show count
end
```

Expected output:

```text
1
2
4
5
```

## 12. Functions

Function declarations use the `f.` prefix.

```assayflux
f.add(a, b)
    return a + b
end

result = add(10, 20)

show result
```

Expected output:

```text
30
```

Function declarations use `f.name(...)`.

Function calls use `name(...)`.

The function's `end` must align with its declaration.

## 13. Functions Without an Explicit Return

```assayflux
f.greet(name)
    show "Hello"
    show name
end

greet("AssayFlux")
```

A function without an explicit return value does not return a computed result.

## 14. Scientific Calculations

```assayflux
mass = 10
acceleration = 9.8

force = mass * acceleration

show "Force calculation"
show force
```

Expected output:

```text
Force calculation
98.0
```

## 15. Python Library Integration

AssayFlux is designed to reuse existing Python libraries rather than recreate their functionality.

For example, the intended syntax for using Python's `math` library is:

```assayflux
import math

result = math.sqrt(25)

show result
```

Expected output:

```text
5.0
```

**Implementation status:** This example describes the intended behavior. It must not be considered a verified working program until the interpreter supports module imports, member access, and external function calls.

## 16. Nested Blocks

AssayFlux uses strict indentation and explicit `end` statements together.

```assayflux
count = 0

repeat count < 5
    if count != 3
        show count
    else
        show "Skipping three"
    end

    count = count + 1
end
```

Rules:

1. Use four spaces per indentation level.
2. Do not use tabs for indentation.
3. Indent statements inside a block.
4. Indent nested blocks further.
5. Align `else` and `otherwise` with their matching `if`.
6. Align `end` with the statement that opened the block.
7. Reject inconsistent indentation.

Indentation and `end` are both required.

## 17. Error Reporting Goals

AssayFlux should provide understandable diagnostics for invalid programs.

For example:

```text
AssayFlux Syntax Error

File: example.af
Line: 5
Problem: Missing 'end'.
Suggestion: Add 'end' to close the current block.
```

This is an example of the intended diagnostic format, not a claim about the current interpreter's output.

## 18. Multi-Language Integration Goals

AssayFlux is intended to support integrations with:

- Python
- JavaScript
- C
- C++
- Java
- Rust

Python is the initial integration target.

Each integration must have defined rules for execution, values, errors, dependencies, and runtime requirements.

These are project goals until implemented and tested.

## 19. Implementation Status

These examples describe the intended AssayFlux syntax.

They do not guarantee that every example currently executes successfully.

The lexer, parser, abstract syntax tree, interpreter, and tests must be updated to match the authoritative grammar.

Each feature should be tracked separately as:

1. Specified.
2. Parsed.
3. Implemented.
4. Tested.

## 20. Compatibility Policy

The authoritative grammar is maintained in `GRAMMAR.md`.

The language specification is maintained in `LANGUAGE_SPECIFICATION.md`.

If an example conflicts with either authoritative document, the conflict must be resolved rather than silently changing the language.

Breaking syntax changes must be documented and versioned.