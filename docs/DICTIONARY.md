# AssayFlux Scientific Systems — Language Dictionary

**Language:** AssayFlux Scientific Systems  
**Short name:** AssayFlux  
**Source file extension:** `.af`  
**Current project version:** 0.1.0  
**Document type:** Language Dictionary and Reference  
**Status:** Initial draft

---

## 1. About This Dictionary

The AssayFlux Language Dictionary explains the vocabulary, syntax,
operators, data types, statements, and programming concepts of AssayFlux.

Its purpose is to help beginners, programmers, educators, and developers
understand how to read and write AssayFlux programs.

This document will evolve alongside the language.

### Documentation Status

Each feature must eventually be classified as one of the following:

- **Implemented:** Available in the current interpreter and tested.
- **Specified:** Its intended behavior has been documented.
- **Planned:** Intended for a future implementation.
- **Experimental:** Available but not yet considered stable.

A documented example does not automatically mean that the current
interpreter can execute it.

---

## 2. Basic Language Information

### 2.1 Language Name

The full name is AssayFlux Scientific Systems.

The short name is AssayFlux.

### 2.2 Source File Extension

AssayFlux source files use the `.af` extension.

Example filename:

`hello.af`

### 2.3 Comments

Comments explain code and are ignored during execution.

The initial comment syntax uses `#`.

Example:

```text
# This is an AssayFlux comment
show `Hello`
```

**Status:** Implemented in the initial lexer; execution behavior should
be verified with tests.

### 2.4 Statements

A statement is an instruction in an AssayFlux program.

Examples include displaying a value, assigning a variable, declaring
a function, and evaluating a conditional.

Example:

```text
show `Hello, World!`
```

### 2.5 Blocks

A block is a group of statements belonging to a construct such as a
function, conditional, or repetition statement.

The language uses `end` to close several block constructs.

Example:

```text
if true
    show `Condition passed`
end
```

Indentation is intended to improve readability but is not mandatory.

---

## 3. Variables and Values

### 3.1 Variable

A variable is a named storage location whose value can be assigned
and, where permitted, changed.

Example:

```text
count = 10
show count
```

**Status:** Specified; assignment and execution require automated tests.

### 3.2 Assignment Operator

The `=` operator assigns a value to a variable.

Example:

```text
score = 85
```

The expression on the right is evaluated and its value is assigned
to the variable on the left.

### 3.3 Reassignment

Reassignment changes the value of an existing variable.

Example:

```text
count = 10
count = count + 1
show count
```

Expected result: `11`, provided the relevant interpreter behavior
is implemented correctly.

### 3.4 Integer

An integer is a whole-number value.

Examples:

```text
age = 18
count = 100
temperature = -5
```

**Status:** Integer literals are recognized by the initial lexer.

### 3.5 Decimal Number

A decimal number represents a value with a fractional part.

Example:

```text
temperature = 25.5
```

**Status:** Decimal literals are recognized by the initial lexer.

### 3.6 String

A string is a sequence of characters.

AssayFlux uses backticks to delimit strings.

Example:

```text
name = `AssayFlux`
show name
```

**Status:** Backtick-delimited strings are recognized by the initial lexer.

### 3.7 Boolean

A Boolean represents a truth value.

AssayFlux uses:

- `true`
- `false`

Example:

```text
enabled = true
show enabled
```

**Status:** Boolean literals are recognized by the initial lexer.
Runtime behavior requires verification.

### 3.8 Constants

A constant is intended to represent a value that cannot be reassigned
after declaration.

The initial language design uses the `const` keyword.

Intended example:

```text
const PI = 3.14159
show PI
```

**Status:** Syntax is being developed. Constant enforcement must be
verified before this feature is considered complete.

---

## 4. Output

### 4.1 `show`

**Purpose:** Display a value.

Syntax:

`show expression`

Example:

```text
show `Hello, World!`
show 123
```

Variables and expressions may also be displayed.

Example:

```text
result = 10 + 20
show result
```

**Status:** Implemented in the initial interpreter; output behavior
should be covered by automated tests.

---

## 5. Operators

### 5.1 Arithmetic Operators

| Operator | Intended meaning | Example |
|---|---|---|
| `+` | Addition | `2 + 3` |
| `-` | Subtraction | `8 - 3` |
| `*` | Multiplication | `4 * 5` |
| `/` | Division | `10 / 2` |
| `%` | Remainder | `10 % 3` |

Arithmetic behavior, including division results and division by zero,
must be specified and tested.

### 5.2 Comparison Operators

| Operator | Intended meaning | Example |
|---|---|---|
| `==` | Equal to | `a == b` |
| `nt=` | Not equal to | `a nt= b` |
| `>` | Greater than | `a > b` |
| `<` | Less than | `a < b` |
| `>=` | Greater than or equal to | `a >= b` |
| `<=` | Less than or equal to | `a <= b` |

The initial lexer recognizes these operator spellings.

Their behavior should be verified by interpreter tests.

### 5.3 Logical Operators

| Keyword | Intended meaning |
|---|---|
| `and` | Logical conjunction |
| `or` | Logical disjunction |
| `not` | Logical negation |

Examples of intended expressions:

```text
age >= 18 and enabled == true
```

```text
age < 18 or enabled == false
```

**Status:** The initial lexer and parser recognize logical operators.
Their exact evaluation rules require testing and formal specification.

---

## 6. Conditional Statements

### 6.1 `if`

**Purpose:** Execute a block when a condition is true.

Syntax:

```text
if condition
    statements
end
```

Example:

```text
if score >= 90
    show `Excellent`
end
```

### 6.2 `otherwise`

**Purpose:** Check another condition when the preceding condition
or branch has not been selected.

Example:

```text
if score >= 90
    show `Excellent`
otherwise score >= 70
    show `Good`
end
```

### 6.3 `else`

**Purpose:** Provide a fallback branch when no preceding condition
matches.

Example:

```text
if score >= 90
    show `Excellent`
otherwise score >= 70
    show `Good`
else
    show `Keep practicing`
end
```

**Status:** The initial parser includes support for `if`, `otherwise`,
`else`, and `end`. These examples must be verified through execution tests.

---

## 7. Repetition and Loop Control

### 7.1 `repeat`

**Purpose:** Repeat a block of statements.

Example:

```text
repeat 3
    show `Hello`
end
```

The intended behavior is to execute the block three times.

The exact rules for repetition counts and invalid values must be
defined and tested.

### 7.2 `stop`

**Purpose:** Exit the current repetition block early.

Intended example:

```text
repeat 10
    stop
end
```

### 7.3 `skip`

**Purpose:** Skip the remainder of the current iteration and proceed
to the next iteration.

Intended example:

```text
repeat 5
    skip
end
```

**Status:** The initial parser and interpreter contain loop-control
support. Exact behavior requires tests.

---

## 8. Functions

### 8.1 Function Definition

AssayFlux uses the `f.` prefix when declaring a function.

General form:

```text
f.function_name(parameters)
    statements
end
```

Example:

```text
f.add(a, b)
    result = a + b
    return result
end
```

The function name in this example is `add`.

### 8.2 Parameters

Parameters are names that receive values supplied when a function
is called.

In the example:

```text
f.add(a, b)
```

`a` and `b` are parameters.

### 8.3 Function Call

A function call executes a previously defined function.

Example:

```text
result = add(10, 20)
show result
```

The intended result is `30`.

### 8.4 `return`

**Purpose:** Return a value from a function.

Example:

```text
f.square(number)
    return number * number
end
```

Calling `square(5)` is intended to return `25`.

**Status:** Function definitions, calls, and return statements have
initial implementations. Scope rules, recursion, argument validation,
and return behavior require testing.

---

## 9. Input

### 9.1 `input()`

**Purpose:** Receive information from the user.

Intended example:

```text
show `What is your name?`
name = input()
show name
```

The exact return type, input handling, and behavior when input is
unavailable must be specified.

**Status:** Planned. Do not assume that `input()` works in the current
interpreter until it has been implemented and tested.

---

## 10. Modules and Imports

### 10.1 `import`

**Purpose:** Import functionality from another module or supported
external language.

Intended example:

```text
import mathematics
```

The actual import syntax, module search paths, security rules, and
loading behavior remain to be defined.

### 10.2 `as`

**Purpose:** Introduce an alias for an imported module or symbol.

Intended example:

```text
import mathematics as math
```

**Status:** Import-related syntax exists in the initial lexer and parser.
A complete module system is planned and must be implemented.

---

## 11. Errors and Diagnostics

AssayFlux should provide useful error messages instead of unexplained
tracebacks whenever possible.

The long-term diagnostic system should identify:

- The category of error.
- The source filename.
- The line and column.
- The relevant source location.
- A concise explanation.
- A possible correction when one can be suggested.

Examples of error categories include:

- Invalid character.
- Unterminated string.
- Unexpected token.
- Undefined variable.
- Incorrect function argument count.
- Division by zero.
- Invalid operation.
- Missing block terminator.

**Status:** Error reporting is under development.

---

## 12. Multi-Language Integration

AssayFlux is intended to provide a consistent programming interface
to selected existing languages.

Potential integrations include:

| Language | Possible integration approach | Status |
|---|---|---|
| Python | Interpreter and Python API interoperability | Planned |
| C | Native library interfaces | Planned |
| C++ | Native library interfaces | Planned |
| Java | JVM interoperability | Planned |
| JavaScript | JavaScript runtime interoperability | Planned |
| Rust | Native library interfaces | Planned |

Each integration must define:

- How functions are called.
- How arguments and return values are converted.
- How errors cross language boundaries.
- How memory and resources are managed.
- How dependencies are installed.
- How untrusted code is handled.

Listing a language here does not mean that integration is already available.

---

## 13. Naming and Syntax Conventions

The initial language design uses:

- `.af` for source files.
- Backticks for string literals.
- `#` for comments.
- `show` for output.
- `=` for assignment.
- `f.` for function declarations.
- `return` for returning a value.
- `end` for closing supported blocks.
- `if`, `otherwise`, and `else` for conditional branches.
- `repeat` for repetition.
- `stop` and `skip` for loop control.
- `and`, `or`, and `not` for logical operations.
- `nt=` for inequality.

These conventions must be maintained consistently or changed through an
explicit language-specification update.

---

## 14. Compatibility and Stability

Before a feature is considered stable, it should have:

1. A documented definition.
2. A clearly defined syntax.
3. A defined runtime behavior.
4. Automated tests.
5. Examples that execute successfully.
6. Documented error cases where applicable.

Changes to established syntax or behavior should be recorded in the
project's version history and release notes.

---

## 15. How to Learn AssayFlux

Beginners should learn in this order:

1. Comments and basic statements.
2. Variables and values.
3. Strings, integers, decimals, and Booleans.
4. Output with `show`.
5. Arithmetic and comparison operators.
6. Conditional statements.
7. Repetition and loop control.
8. Functions and return values.
9. Input and modules when implemented.
10. Multi-language integration when available.

Start with the example programs in the repository's `examples` directory.

---

## 16. Contributing to This Dictionary

When a new language feature is introduced:

1. Define its purpose.
2. Document its syntax.
3. Explain its behavior.
4. Provide an example.
5. Describe relevant errors and edge cases.
6. Add tests for the implementation.
7. Update this dictionary and the formal language specification.

The dictionary should describe the actual language, not merely proposed
features.

---

## 17. Document History

### Version 0.1.0

- Established the initial AssayFlux dictionary.
- Documented the initial syntax conventions.
- Identified implemented, specified, and planned features.
- Established a foundation for future language reference documentation.