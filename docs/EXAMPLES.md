# AssayFlux Language Examples

**Project:** AssayFlux Scientific Systems  
**Language:** AssayFlux  
**Version:** 0.1.0  
**Status:** Initial Draft

---

## 1. Hello World

```assayflux
show `Hello, World!`
```

Expected output:

```text
Hello, World!
```

---

## 2. Variables

```assayflux
name = `AssayFlux`
version = 0.1

show name
show version
```

---

## 3. Numbers and Calculations

```assayflux
a = 10
b = 5

sum = a + b
difference = a - b
product = a * b
quotient = a / b

show sum
show difference
show product
show quotient
```

---

## 4. Boolean Values

```assayflux
is_ready = true
has_error = false

show is_ready
show has_error
```

---

## 5. Conditional Statements

```assayflux
temperature = 30

if temperature > 35
    show `It is very hot`
otherwise temperature > 20
    show `The temperature is moderate`
else
    show `It is cold`
end
```

The `if` branch is checked first.

Each `otherwise` branch provides another condition.

The final `else` branch is the unconditional fallback.

Only the first matching branch should execute.

---

## 6. Comparison Operators

```assayflux
a = 10
b = 20

show a == b
show a nt= b
show a > b
show a < b
show a >= b
show a <= b
```

The `nt=` operator represents not equal.

---

## 7. Logical Operators

```assayflux
age = 25
has_permission = true

if age >= 18 and has_permission
    show `Access granted`
else
    show `Access denied`
end
```

```assayflux
is_scientist = false
is_student = true

if is_scientist or is_student
    show `Scientific tools available`
else
    show `General tools available`
end
```

---

## 8. Repetition

```assayflux
repeat 5
    show `Hello from AssayFlux`
end
```

This illustrates the planned repetition syntax.

The exact meaning of the number following `repeat` will be finalized in the language specification.

---

## 9. Stop a Loop

```assayflux
repeat
    show `Loop running`
    stop
end
```

The `stop` statement exits the nearest enclosing loop.

---

## 10. Skip an Iteration

```assayflux
repeat 5
    skip
    show `This statement is skipped`
end
```

The `skip` statement moves to the next iteration of the nearest enclosing loop.

This example illustrates the intended syntax. Execution details will be finalized with the loop specification.

---

## 11. Functions

```assayflux
f.add(a, b)
    return a + b
end

result = add(10, 20)

show result
```

Functions use the `f.` prefix in their declarations.

`return` provides a function's result.

`end` closes the function body.

The exact function declaration and call syntax will be finalized before interpreter implementation.

---

## 12. Functions Without a Return Value

```assayflux
f.greet(name)
    show `Hello`
    show name
end

greet(`AssayFlux`)
```

---

## 13. Scientific Calculations

```assayflux
mass = 10
acceleration = 9.8

force = mass * acceleration

show `Force calculation`
show force
```

This example demonstrates arithmetic that could be used in a scientific program.

---

## 14. Error Handling Goals

AssayFlux should eventually provide readable error messages.

For example, an invalid expression should produce an error containing:

- The error type.
- The source line number.
- A clear explanation.
- A suggested correction when possible.

Example of a planned diagnostic:

```text
AssayFlux Error
Line: 3
Problem: Invalid expression.
Suggestion: Check the expression and its operators.
```

This is an illustration of the intended diagnostic format, not current interpreter output.

---

## 15. Multi-Language Integration Goals

AssayFlux is intended to support integration with other programming languages.

Potential integration targets include:

- Python
- C
- C++
- Java
- JavaScript
- Rust

The implementation strategy, supported versions, runtime requirements, and interoperability rules will be documented separately.

These are project goals, not implemented features.

---

## 16. Current Implementation Status

At version `0.1.0`, these examples describe the intended language design.

They do not imply that an AssayFlux interpreter or compiler already exists.

Before implementation, the grammar and behavior of each feature must be finalized.

As the interpreter develops, examples should be tested and updated to match actual behavior.

---

## 17. Compatibility Policy

The language specification is the authoritative source for AssayFlux syntax and semantics.

If an example conflicts with the finalized specification, the specification takes precedence.

Breaking syntax changes must be documented in the project changelog.