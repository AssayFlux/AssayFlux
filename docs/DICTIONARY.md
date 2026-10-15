# AssayFlux Scientific Systems — Language Dictionary

**Language:** AssayFlux Scientific Systems  
**Short name:** AssayFlux  
**Version:** 0.1.0  
**File extension:** `.af`  
**Document status:** Language reference for early development

---

## 1. Purpose

This dictionary defines the terminology, keywords, operators, syntax conventions, and core concepts of AssayFlux.

AssayFlux is a custom programming language designed for scientific computing, general-purpose programming, and interoperability with existing programming languages and libraries.

Its initial implementation is based on Python, with the long-term goal of integrating selected capabilities from Python, C, C++, Java, JavaScript, and Rust.

**Important:** A documented feature is not necessarily implemented. Actual support must be verified against the interpreter and automated tests.

---

## 2. Basic Language Terms

| Term | Meaning |
|---|---|
| AssayFlux | Short name of the programming language. |
| AssayFlux Scientific Systems | Full language name. |
| `.af` | File extension for AssayFlux source files. |
| Source code | Instructions written in AssayFlux. |
| Lexer | Converts source text into tokens. |
| Token | A meaningful unit recognized by the lexer. |
| Parser | Processes tokens according to the language grammar. |
| Abstract Syntax Tree (AST) | Structured representation of a program. |
| Interpreter | Executes a parsed AssayFlux program. |
| Runtime | The environment in which a program executes. |
| Expression | Code that produces a value. |
| Statement | An instruction that performs an action. |
| Identifier | A name used for a variable, constant, function, or module. |
| Literal | A value written directly in source code. |
| Scope | The region in which a name can be accessed. |
| Module | A reusable unit of code or library. |
| Interoperability | Communication between AssayFlux and another language or runtime. |
| Adapter | A component that connects AssayFlux to an external runtime or implementation. |

---

## 3. Variables

A variable is a named storage location whose value can be assigned or changed.

### Syntax

```assayflux
name = expression
```

### Example

```assayflux
name = "AssayFlux"
version = 0.1
count = 10

show name
show version
show count
```

### Rules

- Identifiers must follow the language's identifier rules.
- Assignment uses `=`.
- A variable can hold a value supported by the runtime.
- Reassignment behavior must follow the language specification.
- An undefined variable should produce a clear error when accessed.

---

## 4. Constants

A constant is a name intended to hold a value that cannot be reassigned after its definition.

### Syntax

```assayflux
const NAME = expression
```

### Example

```assayflux
const PI = 3.14159
const LANGUAGE = "AssayFlux"

show PI
show LANGUAGE
```

### Rules

- The `const` keyword introduces a constant.
- A constant requires an initial value.
- Reassignment should produce an error.
- Constant enforcement must be implemented by the interpreter; uppercase names alone do not make values constant.

---

## 5. Data Types

AssayFlux is intended to support common programming and scientific data types.

| Type | Description | Example |
|---|---|---|
| Integer | Whole number | `42` |
| Floating-point number | Number with a fractional component | `3.14` |
| String | Text enclosed in quotes | `"Hello"` |
| Boolean | Logical true or false value | `true` |
| Null-like value | Represents the absence of a value, if supported | Implementation-defined |
| List | Ordered collection of values, if supported | Implementation-defined |
| Tuple | Fixed ordered collection, if supported | Implementation-defined |
| Dictionary | Key-value collection, if supported | Implementation-defined |
| Function | Callable block of code | `add` |
| Module | Imported library or module | `math` |

This table describes intended or possible language concepts. It does not guarantee that every type is currently supported.

---

## 6. Strings

Strings represent text.

### Supported Quote Styles

AssayFlux syntax uses single or double quotes.

```assayflux
first = "Hello, World!"
second = 'Scientific Computing'

show first
show second
```

### Rules

- Strings use matching single or double quotation marks.
- Backticks are not string delimiters.
- Escape-sequence support must be defined by the language specification and implemented by the lexer.
- Unterminated strings should produce a clear syntax error.

---

## 7. Comments

Comments explain code and are not executed as program instructions.

### Syntax

```assayflux
# This is a comment
```

### Example

```assayflux
# Calculate a total
price = 100
quantity = 3

total = price * quantity
show total
```

The `#` character begins a comment outside a string.

The current language specification defines single-line comments. Multiline comments are not assumed to be supported.

---

## 8. Output

The `show` keyword displays the result of an expression.

### Syntax

```assayflux
show expression
```

### Example

```assayflux
show "Welcome to AssayFlux"

number = 25
show number
show number * 2
```

### Rules

- `show` is the language's output statement.
- The expression following `show` is evaluated before its result is displayed.
- Output formatting depends on the runtime.
- Input and output behavior must be tested in the actual interpreter.

---

## 9. Operators

### 9.1 Arithmetic Operators

| Operator | Meaning | Example |
|---|---|---|
| `+` | Addition | `10 + 5` |
| `-` | Subtraction | `10 - 5` |
| `*` | Multiplication | `10 * 5` |
| `/` | Division | `10 / 5` |
| `%` | Remainder | `10 % 3` |
| `**` | Exponentiation, if supported | `2 ** 3` |

### 9.2 Comparison Operators

| Operator | Meaning | Example |
|---|---|---|
| `==` | Equal to | `a == b` |
| `!=` | Not equal to | `a != b` |
| `>` | Greater than | `a > b` |
| `<` | Less than | `a < b` |
| `>=` | Greater than or equal to | `a >= b` |
| `<=` | Less than or equal to | `a <= b` |

**Important:** The not-equal operator is `!=`. The form `nt=` is invalid.

### 9.3 Assignment Operator

| Operator | Meaning | Example |
|---|---|---|
| `=` | Assign a value | `count = 10` |

Assignment and equality comparison are different operations.

### 9.4 Logical Operators

| Operator | Meaning | Example |
|---|---|---|
| `and` | Logical conjunction | `age > 17 and active == true` |
| `or` | Logical disjunction | `a == 0 or b == 0` |
| `not` | Logical negation | `not active` |

Logical operators combine or invert conditions.

Their precedence and evaluation behavior must follow the formal language specification.

---

## 10. Boolean Values

Boolean values represent logical truth.

```assayflux
active = true
completed = false

show active
show completed
```

### Boolean Literals

- `true`
- `false`

The language uses lowercase Boolean literals.

Their runtime representation must be consistent across native operations and interoperability adapters.

---

## 11. Conditional Statements

Conditional statements execute code according to a condition.

### Keywords

| Keyword | Purpose |
|---|---|
| `if` | Begins a conditional branch. |
| `otherwise` | Introduces an additional condition. |
| `else` | Introduces the fallback branch. |
| `end` | Closes the conditional block. |

### Example

```assayflux
temperature = 30

if temperature > 35
    show "Very hot"
otherwise temperature > 20
    show "Moderate temperature"
else
    show "Cold"
end
```

### Rules

- A conditional begins with `if`.
- Additional conditions use `otherwise`.
- The optional fallback branch uses `else`.
- The conditional ends with `end`.
- Indentation is mandatory.
- `otherwise` and `else` must align with their matching `if`.
- Each block must use four spaces per indentation level.
- Tabs are prohibited for indentation.

---

## 12. Loops and Repetition

The `repeat` keyword introduces a repetition block.

### Example: Condition-Based Loop

```assayflux
count = 0

repeat count < 5
    show count
    count = count + 1
end
```

### Loop Keywords

| Keyword | Purpose |
|---|---|
| `repeat` | Begins a loop. |
| `stop` | Exits the nearest enclosing loop. |
| `skip` | Skips the current iteration of the nearest enclosing loop. |
| `end` | Closes the loop block. |

### Example: Stop

```assayflux
count = 0

repeat true
    if count == 3
        stop
    end

    show count
    count = count + 1
end
```

### Example: Skip

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

### Rules

- Every loop block must end with `end`.
- Loop bodies require four-space indentation.
- `stop` exits the nearest enclosing loop.
- `skip` advances to the next iteration of the nearest enclosing loop.
- The interpreter must prevent infinite execution where appropriate, without changing valid program semantics unexpectedly.

---

## 13. Functions

Functions package reusable instructions.

AssayFlux uses the `f.` prefix for function declarations.

### Declaration Syntax

```assayflux
f.function_name(parameters)
    # Function body
end
```

### Calling Syntax

```assayflux
function_name(arguments)
```

### Example

```assayflux
f.add(a, b)
    return a + b
end

result = add(10, 20)
show result
```

### Keywords and Concepts

| Term | Purpose |
|---|---|
| `f.` | Prefix used in function declarations. |
| `return` | Returns a value from a function. |
| Parameter | A name receiving a value during a function call. |
| Argument | A value supplied when calling a function. |
| Function call | Executes a function. |

### Rules

- Function declarations use `f.name(parameters)`.
- Function calls use `name(arguments)`, without the `f.` prefix.
- Function bodies require four-space indentation.
- Each function declaration must end with `end`.
- `return` exits the current function and provides its return value, subject to the implemented semantics.
- Invalid argument counts and undefined functions should produce clear errors.

---

## 14. Indentation and Block Formatting

AssayFlux requires strict indentation.

### Mandatory Rules

1. Use exactly four spaces for each indentation level.
2. Do not use tabs for indentation.
3. Indent statements inside a block by one level.
4. Increase indentation for nested blocks.
5. Align `otherwise` and `else` with their matching `if`.
6. Align `end` with the keyword that opened its block.
7. Every block must have its required matching `end`.
8. Incorrect indentation must be reported as an error.

### Correct Example

```assayflux
if true
    show "Outer block"

    if true
        show "Inner block"
    end
end
```

### Incorrect Example

```assayflux
if true
  show "Incorrect indentation"
end
```

The second example uses two spaces instead of four and should be rejected under the strict indentation rules.

Indentation and explicit block endings are both required. One does not replace the other.

---

## 15. Imports and Modules

Imports are intended to allow AssayFlux programs to reuse existing libraries.

### Intended Syntax

```assayflux
import math
```

An alias may be expressed as:

```assayflux
import numpy as np
```

Module members may be accessed through member notation:

```assayflux
import math

result = math.sqrt(25)
show result
```

### Intended Capabilities

- Import supported modules.
- Assign module aliases.
- Access supported functions and attributes.
- Exchange compatible values with external libraries.
- Report import and runtime errors clearly.

### Important Limitations

Import syntax is part of the language design, but full import execution must be implemented and tested.

Python module interoperability does not automatically provide support for C, C++, Java, JavaScript, or Rust.

---

## 16. Scientific Computing

AssayFlux is designed to support scientific and numerical workloads by reusing existing libraries.

### Intended Areas

- Mathematics
- Statistics
- Numerical computation
- Data analysis
- Scientific visualization
- Engineering calculations
- Simulation
- Scientific file processing

### Example: Basic Calculation

```assayflux
radius = 5
area = 3.14159 * radius * radius

show area
```

### Intended Python Ecosystem Integration

Potential integrations include:

- NumPy for numerical arrays.
- SciPy for scientific algorithms.
- SymPy for symbolic mathematics.
- pandas for tabular data.
- Matplotlib for plotting.

These are examples of potential library integrations, not a guarantee that the current interpreter can import or execute them.

---

## 17. Multi-Language Interoperability

Interoperability allows AssayFlux to communicate with other programming languages and runtimes.

### Planned Integration Targets

| Language | Potential integration approach |
|---|---|
| Python | Python runtime, modules, and adapter interface |
| C | Native libraries and foreign-function interfaces |
| C++ | Native libraries and compatible interoperability layers |
| Java | JVM-based integration |
| JavaScript | Embedded or external JavaScript runtime |
| Rust | Native libraries and compatible extension interfaces |

### Design Requirements

Every integration should define:

- How functions are called.
- How arguments are converted.
- How return values are converted.
- How errors are reported.
- How dependencies are managed.
- How resources are released.
- Which platforms are supported.
- What security boundaries apply.

External code must not be assumed safe merely because it is called through an adapter.

A subprocess-based adapter is not automatically a security sandbox.

---

## 18. Errors and Diagnostics

AssayFlux should provide understandable errors during lexing, parsing, and execution.

### Error Categories

| Category | Meaning |
|---|---|
| Lexical error | Invalid or malformed token. |
| Syntax error | Source code violates the grammar. |
| Indentation error | Block indentation violates formatting rules. |
| Name error | An undefined name is accessed. |
| Type error | An operation receives an incompatible value. |
| Runtime error | An error occurs during execution. |
| Import error | A module cannot be imported. |
| Interoperability error | An external adapter or runtime operation fails. |

### Diagnostic Goals

Errors should identify the problem and, where possible, provide:

- The source file.
- The line number.
- The relevant location.
- The cause of the error.
- A useful suggestion for correcting it.

The exact error categories and messages depend on implementation progress.

---

## 19. Reserved Keywords

The following words have special meaning in the intended language syntax.

| Keyword | Meaning |
|---|---|
| `const` | Declares a constant. |
| `show` | Displays a value. |
| `if` | Begins a conditional. |
| `otherwise` | Adds another conditional branch. |
| `else` | Begins the fallback branch. |
| `repeat` | Begins a loop. |
| `stop` | Exits the nearest enclosing loop. |
| `skip` | Skips the current loop iteration. |
| `return` | Returns from a function. |
| `end` | Closes a block. |
| `true` | Boolean true value. |
| `false` | Boolean false value. |
| `and` | Logical conjunction. |
| `or` | Logical disjunction. |
| `not` | Logical negation. |
| `import` | Imports a module. |
| `as` | Specifies an import alias. |

Keyword reservation, case sensitivity, and name restrictions must be enforced consistently by the lexer and parser.

---

## 20. Naming Conventions

The following are recommended conventions, not necessarily mandatory syntax rules.

| Element | Recommended style | Example |
|---|---|---|
| Variables | `snake_case` | `sample_count` |
| Constants | Uppercase with underscores | `MAX_VALUE` |
| Functions | `snake_case` | `calculate_area` |
| Modules | Short descriptive names | `math` |
| Boolean variables | Descriptive logical names | `is_valid` |

The language specification, not a naming convention, determines which identifiers are valid.

---

## 21. Source File and Project Conventions

| Item | Convention |
|---|---|
| Language source file | `.af` |
| Package name | `assayflux` |
| Interoperability package | `assayflux.interop` |
| Test directory | `tests/` |
| Example directory | `examples/` |
| Documentation directory | `docs/` |

These conventions describe the current project organization and may evolve as the implementation grows.

---

## 22. Implementation Status

AssayFlux is in early development.

The dictionary describes the intended language and does not, by itself, establish that every feature works.

Before marking a feature as implemented:

1. Implement the behavior in the appropriate language component.
2. Add automated tests.
3. Run the test suite.
4. Confirm that the tests pass.
5. Update `docs/SPECIFICATION_STATUS.md`.
6. Update examples and other documentation when necessary.

Planned syntax must be clearly distinguished from tested functionality.

---

## 23. Related Documentation

Refer to these files in the repository for more detailed information:

- `README.md` — project overview.
- `docs/LANGUAGE_SPECIFICATION.md` — language design and normative rules.
- `docs/GRAMMAR.md` — grammar and syntax.
- `docs/EXAMPLES.md` — example programs.
- `docs/ARCHITECTURE.md` — implementation architecture.
- `docs/ROADMAP.md` — development plan.
- `docs/SPECIFICATION_STATUS.md` — feature status and implementation notes.

When documents disagree, resolve the conflict explicitly and update the affected documentation. Do not silently treat an unimplemented feature as working.

---

## 24. Core Principles

AssayFlux development follows these principles:

1. **Consistency:** Syntax and runtime behavior should be predictable.
2. **Strict formatting:** Four-space indentation and explicit `end` statements are mandatory.
3. **Scientific usefulness:** Reuse established scientific libraries where appropriate.
4. **Interoperability:** External integrations must have clear interfaces and conversion rules.
5. **Transparency:** Documented plans must be distinguished from implemented features.
6. **Testability:** Features should have automated tests.
7. **Maintainability:** Keep the lexer, parser, AST, interpreter, and adapters modular.
8. **Portability:** Platform limitations must be documented and tested.
9. **Security:** External execution and imported code must be treated carefully.
10. **Compatibility:** Changes to syntax and semantics must be documented.

---

**End of AssayFlux Language Dictionary**