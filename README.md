<div align="center">

<br>

<img src="assayflux-logo.png" alt="AssayFlux — Programming Language and Interpreter" width="400">

<br>
<br>

# AssayFlux

### A Custom Programming Language and Interpreter

**Language Design · Interpreter · Scientific Computing · Interoperability**

A programming language built around readable syntax, strict indentation, explicit block termination, and a modular execution architecture.

<br>

[Language Reference](#language-reference) ·
[Getting Started](#getting-started) ·
[Examples](#examples) ·
[Architecture](#architecture) ·
[Documentation](#documentation)

<br>

---

</div>

<p align="justify">

AssayFlux is an experimental programming-language project that provides its own source syntax, lexer, parser, abstract syntax tree, interpreter, and command-line execution interface. Programs are written in files with the `.af` extension and executed by the AssayFlux runtime.

The language combines familiar programming concepts with its own syntax and formatting rules. It supports variable assignment, constants, expressions, conditional execution, repetition, functions, input, output, and integration with selected Python functionality.

The project is being developed incrementally. Its implementation, language specification, automated tests, and examples form the foundation for future improvements to the language and its development tools.

</p>

<div align="center">

### The AssayFlux Philosophy

**Readable code. Consistent structure. Explicit control.**

</div>

---

## Project Overview

<p align="justify">

AssayFlux is designed to make program structure clear and predictable. Rather than relying exclusively on indentation to determine where a block ends, the language combines indentation with the explicit `end` keyword. This makes the boundaries of conditionals, loops, and function definitions visible in the source code.

The language uses `show` to display values, `otherwise` to introduce additional conditional branches, and the `f.` prefix to declare functions. These conventions distinguish AssayFlux from languages whose syntax it may resemble.

</p>

| Property | Details |
|:---|:---|
| Project | AssayFlux |
| Full project name | AssayFlux Scientific Systems |
| Language type | Custom interpreted programming language |
| Source extension | `.af` |
| Implementation language | Python |
| Minimum Python version | Python 3.10 |
| Current package version | `0.2.0` |
| Core dependencies | None declared |
| Development tools | pytest and build |
| Command-line executable | `assayflux` |
| Primary entry point | `assayflux.cli:main` |
| License | See the repository's license file |

---

## What Makes AssayFlux Different?

### A Dedicated Language

AssayFlux programs use a custom source format and a dedicated parser and interpreter. They are not ordinary Python programs renamed with an `.af` extension.

### Explicit Block Structure

Conditional statements, loops, and function definitions use indentation to organize their bodies and `end` to terminate the block.

### A Distinct Output Statement

The language uses `show` to display an expression.

```text
show "Hello, AssayFlux!"
show 10 + 20
```

### Conditional Branches with `otherwise`

Additional conditional branches use `otherwise`, rather than `elif`.

```text
score = 85

if score >= 90
    show "Excellent!"
otherwise score >= 70
    show "Good work!"
else
    show "Keep practicing!"
end
```

### Custom Function Declarations

Functions are declared using the `f.` prefix and called using their ordinary names.

```text
f.add(a, b)
    return a + b
end

result = add(10, 20)
show result
```

### A Modular Foundation

The project separates lexical analysis, parsing, syntax-tree representation, execution, interoperability, testing, and documentation. This separation provides a foundation for extending the language without placing every responsibility in a single component.

---

# Language Reference

<p align="justify">

This reference describes the syntax and behavior established by the AssayFlux implementation and its accompanying examples. The distinction between implemented behavior and future development is important: a proposed feature or external-language adapter should not be considered fully supported simply because it appears in a design document or repository directory.

</p>

## Source Files and Program Structure

AssayFlux source files use the `.af` extension.

A simple program can declare application metadata, define a constant, and display its value.

```text
app "Hello AssayFlux"

constant GREETING = "Hello, AssayFlux!"

show GREETING
```

The program contains three statements.

- `app` declares the application name.
- `constant` creates a named value that cannot be reassigned.
- `show` evaluates an expression and displays the resulting value.

The `app` declaration provides application metadata. It is not a replacement for the interpreter or a standalone application-building system.

## Syntax Fundamentals

AssayFlux uses keywords, identifiers, literals, operators, punctuation, and indentation to describe a program.

| Element | Syntax | Purpose |
|:---|:---|:---|
| Application declaration | `app "My Program"` | Declares application metadata |
| Variable assignment | `name = "AssayFlux"` | Creates or updates a variable |
| Constant declaration | `constant LIMIT = 100` | Declares a constant |
| Output statement | `show expression` | Displays an evaluated expression |
| Conditional | `if condition` | Begins a conditional statement |
| Additional condition | `otherwise condition` | Introduces another conditional branch |
| Alternative branch | `else` | Provides the final alternative |
| Repetition | `repeat condition` | Repeats a block while its condition is true |
| Function declaration | `f.calculate(a, b)` | Declares a function |
| Return statement | `return expression` | Returns a value from a function |
| Loop termination | `stop` | Exits the active repetition loop |
| Iteration control | `skip` | Skips the remainder of the current iteration |
| Import statement | `import math` | Imports a Python module |
| Block terminator | `end` | Closes a block |
| Comment | `# explanation` | Documents source code without executing it |

These constructs must follow the grammar accepted by the current parser.

---

## Indentation and Formatting

<p align="justify">

Indentation is part of the AssayFlux language syntax. The lexer tracks indentation levels and emits indentation and dedentation tokens. The parser uses these tokens to validate the structure of each block.

Every indentation level consists of exactly four spaces. Tabs are prohibited, and an indentation increase must be exactly one level at a time. A block must also end with the appropriate `end` statement.

</p>

### The Four-Space Rule

Correct:

```text
if temperature > 25
    show "Temperature is high"
end
```

Incorrect:

```text
if temperature > 25
  show "Temperature is high"
end
```

The second example uses only two spaces for the body. It violates the four-space indentation rule.

### Nested Indentation

Each nested block adds another four spaces.

```text
if enabled
    repeat count < 3
        show count
        count = count + 1
    end
end
```

The indentation levels are:

| Statement | Indentation |
|:---|---|
| Outer `if` | No indentation |
| `repeat` inside `if` | Four spaces |
| Statements inside `repeat` | Eight spaces |
| `end` closing `repeat` | Four spaces |
| `end` closing `if` | No indentation |

### Block Alignment

The keywords `otherwise`, `else`, and the matching `end` must align with their corresponding block-opening statement.

```text
if score >= 90
    show "Excellent"
otherwise score >= 70
    show "Good"
else
    show "Keep practicing"
end
```

### Formatting Rules

- Use four spaces for each indentation level.
- Never use tabs for indentation.
- Increase indentation by one level at a time.
- Keep statements inside a block indented.
- Align conditional branches with their matching `if`.
- Close each block with `end`.
- Do not place a block terminator inside the indented body it closes.
- Do not use empty blocks; the current parser rejects them.
- Keep each statement on its own line.
- Use blank lines to separate logical sections of a program.
- Use comments to explain intent and important decisions.

Correct formatting is required for valid programs. Indentation is not merely a visual styling preference.

---

## Comments

Comments begin with `#`. The lexer ignores comment text outside string literals.

```text
# Define the sample information.
sample_name = "Sample A"
concentration = 25

# Display the stored values.
show sample_name
show concentration
```

Comments are useful for explaining why a calculation is performed, documenting assumptions, and helping other developers understand a program.

A comment does not create a block and does not replace a required `end`.

---

## Variables

<p align="justify">

Variables store values that can be used by later statements. AssayFlux supports ordinary assignment through the `=` operator. A variable can be assigned an initial value and subsequently updated.

</p>

```text
sample_name = "Control Sample"
measurement = 12
temperature = 25.5
active = true

show sample_name
show measurement
show temperature
show active

measurement = measurement + 3

show measurement
```

In this example, `measurement` initially contains `12`. The arithmetic expression adds `3`, and the variable is updated to `15`.

### Variable Assignment Rules

- Use an identifier as the variable name.
- Separate the name and expression with `=`.
- Evaluate the expression on the right-hand side.
- Use the variable name in later expressions.
- Reassign a variable when its value needs to change.
- Do not attempt to reassign a constant.

The runtime reports an error when an expression references an undefined variable.

---

## Constants

<p align="justify">

A constant is a named value that cannot be reassigned after initialization. Constants are declared using the `constant` keyword.

Constants are useful for values that should remain fixed throughout a program, such as a conversion factor, a threshold, or a configuration value.

</p>

```text
constant APPLICATION_NAME = "AssayFlux"
constant MAX_ATTEMPTS = 5
constant CONVERSION_FACTOR = 1.25

show APPLICATION_NAME
show MAX_ATTEMPTS
show CONVERSION_FACTOR
```

### Constant Rules

- Declare a constant using `constant`.
- Provide a valid identifier.
- Assign an initial expression using `=`.
- Read the constant by referring to its name.
- Do not reassign a constant after declaration.
- Do not redeclare a name that already exists in the same environment.

The interpreter enforces constant protection and reports an error if a constant is reassigned.

---

## Values and Data Types

<p align="justify">

The core language supports numeric literals, strings, Boolean values, identifiers, and expressions. Values may also come from supported Python functionality or function calls.

The following examples illustrate the core value categories without assuming support for unimplemented collection literals or an extensive static type system.

</p>

| Value category | Example | Description |
|:---|:---|:---|
| Integer | `25` | A whole numeric value |
| Decimal | `3.14` | A numeric value with a fractional part |
| String | `"Sample A"` | Text enclosed in quotation marks |
| Boolean true | `true` | A logical true value |
| Boolean false | `false` | A logical false value |
| Identifier | `measurement` | A reference to a named value |
| Arithmetic expression | `10 + 5` | An expression that computes a result |
| Function call | `add(10, 20)` | An expression that invokes a function |
| Module member | `math.sqrt(25)` | An expression that accesses a member of an imported module |

### Numeric Values

```text
constant SAMPLE_COUNT = 25
constant ABSORBANCE = 0.85
constant THRESHOLD = 1.20

show SAMPLE_COUNT
show ABSORBANCE
show THRESHOLD
```

### String Values

Strings can use single or double quotation marks.

```text
constant FIRST_MESSAGE = "Hello, AssayFlux"
constant SECOND_MESSAGE = 'Scientific computing'

show FIRST_MESSAGE
show SECOND_MESSAGE
```

A string literal cannot contain an unescaped newline. The lexer recognizes the following escape sequences:

| Escape | Meaning |
|:---|:---|
| `\n` | Newline |
| `\t` | Tab character inside a string |
| `\r` | Carriage return |
| `\\` | Backslash |
| `\'` | Single quotation mark |
| `\"` | Double quotation mark |

Example:

```text
show "AssayFlux\nScientific Systems"
show "Column A\tColumn B"
```

### Boolean Values

```text
constant IS_VALID = true
constant IS_EMPTY = false

show IS_VALID
show IS_EMPTY
```

Boolean values are useful in conditions and logical expressions.

Native list and dictionary literals should not be assumed to be supported by the current core language.

---

## Output with `show`

<p align="justify">

The `show` statement evaluates an expression and displays its value. It is the language's output statement and should be used in examples instead of `print`.

</p>

```text
show "Welcome to AssayFlux"
show 25
show 10 + 20
show true
```

### Displaying Calculated Results

```text
sample_a = 12
sample_b = 8

total = sample_a + sample_b

show "Sample A:"
show sample_a

show "Sample B:"
show sample_b

show "Combined result:"
show total
```

The values are calculated by the interpreter and displayed through `show`.

### Displaying Function Results

```text
f.add(a, b)
    return a + b
end

result = add(15, 25)

show "Calculated result:"
show result
```

The function call produces a value, which is then displayed.

---

## Operators and Expressions

<p align="justify">

Expressions combine values, identifiers, operators, and function calls. The parser implements operator precedence so that expressions can be evaluated according to the language's grammar.

The following operators are recognized by the current lexer and parser.

</p>

### Arithmetic Operators

| Operator | Example | Purpose |
|:---|:---|:---|
| `+` | `10 + 5` | Addition |
| `-` | `10 - 5` | Subtraction |
| `*` | `10 * 5` | Multiplication |
| `/` | `10 / 5` | Division |
| `%` | `10 % 3` | Remainder |

Example:

```text
constant FIRST_VALUE = 20
constant SECOND_VALUE = 6

show FIRST_VALUE + SECOND_VALUE
show FIRST_VALUE - SECOND_VALUE
show FIRST_VALUE * SECOND_VALUE
show FIRST_VALUE / SECOND_VALUE
show FIRST_VALUE % SECOND_VALUE
```

Division by zero produces a runtime error.

### Comparison Operators

| Operator | Example | Purpose |
|:---|:---|:---|
| `==` | `score == 100` | Equality |
| `!=` | `score != 100` | Inequality |
| `<` | `score < 100` | Less than |
| `>` | `score > 100` | Greater than |
| `<=` | `score <= 100` | Less than or equal |
| `>=` | `score >= 100` | Greater than or equal |

Example:

```text
score = 85

if score >= 90
    show "Excellent"
otherwise score >= 70
    show "Good"
else
    show "Needs improvement"
end
```

### Logical Operators

| Operator | Example | Purpose |
|:---|:---|:---|
| `and` | `ready and valid` | Logical conjunction |
| `or` | `ready or override` | Logical disjunction |
| `not` | `not enabled` | Logical negation |

Example:

```text
sample_valid = true
instrument_ready = true

if sample_valid and instrument_ready
    show "Ready to proceed"
else
    show "Check the sample or instrument"
end
```

The interpreter evaluates the logical expression as part of the condition.

### Operator Precedence

The parser evaluates expressions according to the following precedence, from higher to lower.

| Precedence | Expression category | Operators |
|:---|:---|:---|
| Highest | Primary expressions and grouping | Literals, identifiers, calls, parentheses |
| High | Unary expressions | Unary `+`, unary `-` |
| High | Multiplicative expressions | `*`, `/`, `%` |
| Medium | Additive expressions | `+`, `-` |
| Medium | Comparisons | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| Low | Logical negation | `not` |
| Lower | Logical conjunction | `and` |
| Lowest | Logical disjunction | `or` |

Use parentheses to make complicated expressions easier to read.

```text
result = (10 + 5) * 2

show result
```

Parentheses make the intended order of evaluation explicit.

---

## Conditional Statements

<p align="justify">

Conditional statements select which block of instructions should execute based on the value of a condition. AssayFlux uses `if`, `otherwise`, `else`, and `end`.

The `otherwise` keyword introduces another condition. Multiple `otherwise` branches may appear before an optional final `else` branch.

</p>

### Basic Conditional

```text
temperature = 30

if temperature > 25
    show "The temperature is high"
else
    show "The temperature is within the lower range"
end
```

The first branch executes when its condition is true. Otherwise, the alternative branch executes.

### Multiple Conditional Branches

```text
score = 85

if score >= 90
    show "Excellent performance"
otherwise score >= 75
    show "Good performance"
otherwise score >= 50
    show "Satisfactory performance"
else
    show "Further improvement is needed"
end
```

The interpreter checks the initial condition and then the `otherwise` conditions in order. The first matching branch executes. If none matches and an `else` branch exists, the alternative branch executes.

### Nested Conditions

```text
sample_valid = true
instrument_ready = true

if sample_valid
    if instrument_ready
        show "The measurement can proceed"
    else
        show "The instrument is not ready"
    end
else
    show "The sample must be checked"
end
```

Each nested conditional has its own indentation level and its own closing `end`.

### Conditional Formatting Rules

- Begin the conditional with `if`.
- Put the condition on the same line as `if`.
- Place the body on the following indented lines.
- Use `otherwise` for additional conditions.
- Use `else` for the final alternative.
- Align branch keywords with the matching `if`.
- Close the complete conditional with `end`.

The keyword `elif` is not part of AssayFlux conditional syntax.

---

## Loops and Repetition

<p align="justify">

AssayFlux uses `repeat` to execute a block repeatedly. The parser supports condition-controlled repetition, explicit counted repetition, unlimited repetition, and a bare `repeat` form that also represents an unlimited loop.

Each loop has an indented body and must end with `end`.

</p>

### Condition-Controlled Loop

A condition-controlled loop repeats while its condition evaluates to true.

```text
count = 0

repeat count < 5
    show count
    count = count + 1
end
```

The loop displays the current value and increments it until the condition becomes false.

### Counted Loop

The explicit counted form uses `repeat count` followed by a count expression.

```text
repeat count 5
    show "This instruction is repeated"
end
```

The count must evaluate to a valid non-negative integer. A count of zero results in zero iterations.

A numeric literal can also be used directly as the repetition count.

```text
repeat 3
    show "AssayFlux"
end
```

This form repeats the body three times.

### Unlimited Loop

The explicit unlimited form uses `repeat forever`.

```text
repeat forever
    show "Waiting for a stop condition"
    stop
end
```

The `stop` statement exits the active loop. A loop without a terminating condition or an effective exit may run indefinitely, subject to runtime limits.

A bare `repeat` also represents unlimited repetition:

```text
repeat
    show "Running"
    stop
end
```

### Stopping a Loop

The `stop` statement terminates the nearest active repetition loop.

```text
count = 0

repeat forever
    count = count + 1
    show count

    if count >= 3
        stop
    end
end
```

The program exits the loop when the counter reaches the specified threshold.

### Skipping an Iteration

The `skip` statement skips the remaining instructions in the current iteration and proceeds to the next iteration.

```text
count = 0

repeat count < 5
    count = count + 1

    if count == 3
        skip
    end

    show count
end
```

When `count` reaches `3`, the `show` statement is skipped for that iteration.

### Loop Reference

| Form | Example | Behavior |
|:---|:---|:---|
| Condition-controlled | `repeat count < 5` | Repeats while the condition is true |
| Explicit counted | `repeat count 5` | Repeats the specified number of times |
| Numeric counted | `repeat 5` | Repeats a numeric literal count |
| Explicit unlimited | `repeat forever` | Repeats until stopped or interrupted |
| Bare repetition | `repeat` | Creates an unlimited loop |
| Stop | `stop` | Exits the active loop |
| Skip | `skip` | Skips the current iteration |

The interpreter enforces a maximum loop-iteration limit. Programs should nevertheless use clear exit conditions and avoid unnecessary unlimited loops.

---

## Functions

<p align="justify">

Functions group instructions into reusable units. AssayFlux function declarations use the `f.` prefix, while function calls use the function name without that prefix.

Parameters are placed inside parentheses and separated by commas. A function body is indented, and `end` closes the definition. The `return` statement can return a calculated value.

</p>

### Defining a Function

```text
f.add(a, b)
    return a + b
end
```

The declaration defines a function named `add` with two parameters, `a` and `b`.

### Calling a Function

```text
f.add(a, b)
    return a + b
end

result = add(10, 20)

show result
```

The call is written as `add(10, 20)`, not `f.add(10, 20)`.

### Multiple Functions

```text
f.add(a, b)
    return a + b
end

f.multiply(a, b)
    return a * b
end

sum = add(10, 20)
product = multiply(5, 6)

show "Addition result:"
show sum

show "Multiplication result:"
show product
```

This example follows the structure of the repository's `examples/functions.af` file.

### Functions Without an Explicit Return

A function can execute instructions without an explicit `return`.

```text
f.display_message()
    show "The function has executed"
end

display_message()
```

A function without an explicit return does not provide a calculated return value.

### Function Rules

- Start a function declaration with `f.`.
- Use a valid function name.
- Put parameters inside parentheses.
- Separate parameters with commas.
- Indent the function body by four spaces.
- Use `return` to return a value.
- Close the function definition with `end`.
- Call the function without the `f.` prefix.
- Supply the expected number of arguments.

The interpreter validates function argument counts and enforces a maximum function-call depth.

---

## Input

<p align="justify">

AssayFlux provides an `input()` function through the interpreter environment. It reads input using the host Python process's standard input mechanism.

The input example in the repository demonstrates a prompt followed by an input operation and a response.

</p>

```text
show "What is your name?"
name = input()

show "Hello,"
show name
```

The program displays the prompt, waits for input, and then displays the supplied value.

### Example Interaction

```text
What is your name?
Alex
Hello,
Alex
```

The exact terminal interaction depends on the environment in which the interpreter is running.

Input is useful for interactive programs, but programs that require validated or numeric input should explicitly handle the type and format of the received value.

---

## Importing Python Modules

<p align="justify">

The interpreter provides a Python module-import mechanism. An AssayFlux program can import a Python module and access its members using dotted names.

Python interoperability allows a program to reuse functionality available in the host Python environment. It does not mean that every Python library is automatically available, and it does not make the interpreter a security sandbox.

</p>

### Importing a Module

```text
import math

result = math.sqrt(25)

show result
```

The expected result is:

```text
5.0
```

### Importing with an Alias

```text
import numpy as np

result = np.sqrt(25)

show result
```

This example requires NumPy to be installed in the Python environment and the relevant import and member-access operations to be supported.

The project does not declare NumPy as a core dependency.

### Importing a Module Member

```text
import math

radius = 5
area_factor = math.pi * radius * radius

show area_factor
```

This illustrates the use of a Python module member in an AssayFlux expression.

### Python Integration Considerations

- The requested Python module must be available in the host environment.
- Import aliases must follow the supported syntax.
- Module member access must follow the parser's expression rules.
- External functions may impose their own argument and type requirements.
- Import and execution errors can occur at runtime.
- Imported Python code executes with the permissions of the AssayFlux process.

Only integrations that have been implemented and tested should be described as fully supported.

---

## Program Lifecycle and `destroy()`

<p align="justify">

The interpreter provides a `destroy()` operation that terminates the current AssayFlux execution and clears state owned by that interpreter instance.

This is an interpreter lifecycle operation. It is not a command for deleting files, erasing a device, destroying the repository, or modifying the operating system.

</p>

Example:

```text
show "The program is starting"

destroy()

show "This statement will not execute"
```

The `destroy()` call terminates the current program execution. Statements after it do not execute.

A destroyed interpreter instance cannot be reused to run another program. A new interpreter instance must be created for a new execution.

---

## Application Metadata

The `app` declaration identifies the application associated with a source program.

```text
app "Sample Calculator"

constant VERSION = "0.2.0"

show "Application:"
show "Sample Calculator"

show "Version:"
show VERSION
```

The application name is metadata recognized by the parser. It does not, by itself, create a graphical application, package an Android app, or provide a graphical user interface.

---

# Complete Examples

<p align="justify">

The examples in this section demonstrate how individual language features work together. They are designed to be readable for people who are learning AssayFlux and to illustrate the actual syntax used by the repository's example programs.

</p>

## A Simple Greeting

```text
app "Greeting Program"

constant GREETING = "Hello, AssayFlux!"

show GREETING
```

This program declares its application name, defines a constant, and displays the constant's value.

## Variables and Calculations

```text
app "Simple Calculator"

first_number = 15
second_number = 5

sum = first_number + second_number
difference = first_number - second_number
product = first_number * second_number
quotient = first_number / second_number

show "First number:"
show first_number

show "Second number:"
show second_number

show "Sum:"
show sum

show "Difference:"
show difference

show "Product:"
show product

show "Quotient:"
show quotient
```

The program stores two values, calculates four results, and displays them.

## Classifying a Score

```text
app "Score Classifier"

score = 85

if score >= 90
    show "Excellent"
otherwise score >= 75
    show "Good"
otherwise score >= 50
    show "Satisfactory"
else
    show "Needs improvement"
end
```

The program checks the score against several thresholds. The first matching branch determines the message.

## Repeating a Calculation

```text
app "Counter"

count = 0

repeat count < 5
    show count
    count = count + 1
end

show "Counting complete"
```

The counter begins at zero and increases by one on every iteration until it reaches five.
## Reusable Calculations

```text
app "Calculation Functions"

f.add(a, b)
    return a + b
end

f.subtract(a, b)
    return a - b
end

f.multiply(a, b)
    return a * b
end

addition_result = add(12, 8)
subtraction_result = subtract(12, 8)
multiplication_result = multiply(12, 8)

show "Addition:"
show addition_result

show "Subtraction:"
show subtraction_result

show "Multiplication:"
show multiplication_result
```

This program defines three functions and calls each function with two arguments.

## Interactive Greeting

```text
app "Interactive Greeting"

show "Enter your name:"
name = input()

show "Welcome to AssayFlux,"
show name
```

This program demonstrates the relationship between output, input, and variables.

## A More Complete Example

```text
app "Sample Evaluation"

constant ACCEPTANCE_LIMIT = 50

sample_name = "Control Sample"
measurement = 72

show "Sample evaluation"
show sample_name

show "Measured value:"
show measurement

if measurement >= ACCEPTANCE_LIMIT
    show "The measurement meets the defined threshold"
otherwise measurement < ACCEPTANCE_LIMIT
    show "The measurement is below the defined threshold"
end

show "Evaluation complete"
```

This example combines application metadata, a constant, variables, output, comparisons, and conditional execution.

The threshold is illustrative. Real scientific or clinical applications must use validated methods, appropriate units, documented acceptance criteria, and verified calculations.

---

# Command-Line Usage

<p align="justify">

AssayFlux provides a command-line interface for running source files. The package defines the `assayflux` console command, which accepts a path to an AssayFlux source file.

</p>

## Requirements

- Python 3.10 or later.
- Access to the AssayFlux repository.
- A terminal or command-line environment.
- `pip` for installing the package.

The core package declares no required third-party runtime dependencies.

## Install the Development Version

Clone the repository and move into its directory.

```bash
git clone https://github.com/AssayFlux/AssayFlux.git
cd AssayFlux
```

Install the project in editable mode with development tools.

```bash
python -m pip install -e ".[dev]"
```

This installs the package and its optional development dependencies, including pytest and build.

## Run an Example

Run the greeting program.

```bash
assayflux examples/hello.af
```

Run the variable example.

```bash
assayflux examples/variables.af
```

Run the conditional example.

```bash
assayflux examples/conditions.af
```

Run the loop example.

```bash
assayflux examples/loops.af
```

Run the function example.

```bash
assayflux examples/functions.af
```

Run the input example.

```bash
assayflux examples/input.af
```

The input example waits for interactive input.
## Run Without Installing the Console Command

From the repository directory, use the module entry point when available.

```bash
python -m assayflux examples/hello.af
```

The package also exposes the CLI through `assayflux.cli:main`.

## Error Handling

The command-line interface reports file-reading and execution errors and returns a non-zero exit status when execution fails.

For example, attempting to run a file that does not exist produces an error instead of executing a nonexistent program.

---

# Development and Testing

<p align="justify">

Automated testing is essential for keeping the lexer, parser, interpreter, examples, and language specification consistent. AssayFlux includes tests for language behavior and command-line execution.

Contributors should run the test suite after changing language syntax, interpreter behavior, error handling, or interoperability.

</p>

## Install Development Dependencies

```bash
python -m pip install -e ".[dev]"
```

## Run the Test Suite

```bash
python -m pytest
```

The project also documents a standard-library unittest invocation for the relevant tests.

```bash
python -m unittest discover -s tests -v
```

Use the test runner appropriate to the tests being executed.

## What the Tests Cover

The existing core tests cover areas including:

- Parsing basic language statements.
- Output through `show`.
- Arithmetic expressions.
- Boolean values.
- Conditional execution.
- Condition-controlled repetition.
- Counted repetition.
- Unlimited repetition.
- Loop termination using `stop`.
- Iteration control using `skip`.
- Constant declarations and protection.
- Undefined variable errors.
- Function declarations and return values.
- Function argument-count validation.
- Python module imports.
- Division-by-zero errors.
- Interpreter lifecycle behavior.
- Command-line file execution and missing-file errors.

The repository also includes tests for language execution and interoperability. Tests that depend on optional external runtimes may be skipped when those runtimes are unavailable.

The presence of a test file does not guarantee that every possible edge case or external runtime has been verified.

---

# Architecture

<p align="justify">

AssayFlux separates source processing from program execution. The lexer recognizes the language's tokens and indentation structure. The parser validates syntax and constructs an abstract syntax tree. The interpreter evaluates that structure, manages execution state, and invokes supported language operations.

Interoperability components provide a separate mechanism for integrating external runtimes and tools.

</p>

## Execution Pipeline

```text
              AssayFlux Source
                  main.af
                    |
                    v
              Source Reader
                    |
                    v
                  Lexer
                    |
                    v
                  Tokens
                    |
                    v
                  Parser
                    |
                    v
       Abstract Syntax Tree (AST)
                    |
                    v
               Interpreter
                    |
          +---------+---------+
          |         |         |
          v         v         v
      Variables  Functions  Control Flow
          |         |         |
          +---------+---------+
                    |
                    v
           Runtime Operations
                    |
          +---------+---------+
          |                   |
          v                   v
      Program Output    Interoperability
```

This diagram illustrates the high-level execution architecture. It does not imply that every planned external runtime or integration is fully supported.

## Lexer

The lexer converts source text into tokens.

Its responsibilities include:

- Recognizing keywords and identifiers.
- Recognizing numeric and string literals.
- Recognizing operators and punctuation.
- Skipping comments.
- Tracking line and column locations.
- Enforcing indentation rules.
- Rejecting invalid characters and malformed strings.
- Emitting indentation and dedentation tokens.

Primary implementation:

`assayflux/lexer.py`

## Parser

The parser transforms tokens into a structured representation of the program.

Its responsibilities include:

- Parsing declarations and assignments.
- Parsing expressions and function calls.
- Parsing conditional branches.
- Parsing repetition constructs.
- Parsing function definitions.
- Parsing import statements.
- Validating block indentation.
- Enforcing explicit block termination.
- Reporting syntax errors.

Primary implementation:

`assayflux/parser.py`

## Abstract Syntax Tree

The abstract syntax tree represents the logical structure of a program independently of its original formatting.

AST nodes represent statements and expressions such as assignments, constants, binary operations, conditionals, loops, function calls, imports, and return statements.

Primary implementation:

`assayflux/ast_nodes.py`

## Interpreter

The interpreter executes the parsed program.

Its responsibilities include:

- Managing variable and constant environments.
- Evaluating expressions.
- Executing statements.
- Resolving names and functions.
- Managing function calls and return values.
- Controlling loop execution.
- Invoking input and output operations.
- Handling runtime errors.
- Managing interpreter lifecycle state.
- Integrating with supported interoperability components.

Primary implementation:

`assayflux/interpreter.py`

## Command-Line Interface

The CLI reads a source file, creates an interpreter, executes the source, and reports failures.

Primary implementation:

`assayflux/cli.py`

The module entry point is:

`assayflux/__main__.py`

## Interoperability

The project includes an interoperability subsystem intended to provide a modular foundation for external-language integration.

The exact availability and maturity of each integration must be evaluated separately. An adapter file, registry entry, installed runtime, successful test, and officially supported integration are different things.

---
# Repository Structure

The repository separates language implementation, interoperability, examples, tests, and documentation.

```text
AssayFlux/
|
|-- assayflux/
|   |-- __init__.py
|   |-- __main__.py
|   |-- cli.py
|   |-- lexer.py
|   |-- parser.py
|   |-- ast_nodes.py
|   |-- interpreter.py
|   |
|   |-- interop/
|       |-- __init__.py
|       |-- base.py
|       |-- registry.py
|       |-- loader.py
|       |-- runtime.py
|       |
|       |-- adapters/
|           |-- python_adapter.py
|
|-- examples/
|   |-- hello.af
|   |-- variables.af
|   |-- conditions.af
|   |-- loops.af
|   |-- functions.af
|   |-- input.af
|
|-- tests/
|   |-- test_core.py
|   |-- test_cli.py
|   |-- test_language_execution.py
|
|-- DOCS/
|   |-- GRAMMAR.md
|   |-- LANGUAGE_SPECIFICATION.md
|   |-- DICTIONARY.md
|   |-- EXAMPLES.md
|   |-- ARCHITECTURE.md
|   |-- ROADMAP.md
|   |-- INTEROPERABILITY_AND_WEB.md
|   |-- RELEASE_AND_GITHUB.md
|
|-- pyproject.toml
|-- CONTRIBUTING.md
|-- SECURITY.md
|-- README.md
```

This is a guide to the main project components, not an exhaustive inventory of every repository file. Check the current repository tree for the latest file list.

---

# Documentation

The repository includes additional documentation for language syntax, implementation architecture, development, and future integrations.

| Document | Purpose |
|:---|:---|
| [`DOCS/GRAMMAR.md`](DOCS/GRAMMAR.md) | Describes the formal language grammar |
| [`DOCS/LANGUAGE_SPECIFICATION.md`](DOCS/LANGUAGE_SPECIFICATION.md) | Explains language design and intended behavior |
| [`DOCS/DICTIONARY.md`](DOCS/DICTIONARY.md) | Language terminology and reference material |
| [`DOCS/EXAMPLES.md`](DOCS/EXAMPLES.md) | Additional language examples |
| [`DOCS/ARCHITECTURE.md`](DOCS/ARCHITECTURE.md) | Describes implementation architecture |
| [`DOCS/ROADMAP.md`](DOCS/ROADMAP.md) | Outlines development goals |
| [`DOCS/INTEROPERABILITY_AND_WEB.md`](DOCS/INTEROPERABILITY_AND_WEB.md) | Discusses external runtimes and web technologies |
| [`DOCS/RELEASE_AND_GITHUB.md`](DOCS/RELEASE_AND_GITHUB.md) | Release and GitHub workflow guidance |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution guidance |
| [`SECURITY.md`](SECURITY.md) | Security policy and execution warnings |

The repository uses the uppercase directory name `DOCS`. Keep documentation links consistent with the actual repository paths.

The README is an introduction and practical reference. The specification and grammar documents provide additional technical detail.

---

# Interoperability and Future Development

<p align="justify">

AssayFlux is designed with modular interoperability in mind. Python is the initial integration target, while the architecture provides a foundation for investigating other language runtimes and tools.

Future integrations may involve compiled languages, scripting languages, databases, and web technologies. Each integration requires its own implementation, runtime requirements, interface, error handling, and tests.

The existence of an adapter or an item on the roadmap does not establish production readiness.

</p>
## Integration Status

Each external integration should be evaluated independently.

| Status | Meaning |
|:---|:---|
| Planned | The integration is a design or development goal |
| Adapter present | Integration code exists in the repository |
| Runtime available | The required external runtime is available in the environment |
| Tested | Automated tests verify the documented behavior |
| Supported | The integration is maintained, documented, and verified within a defined compatibility scope |

## Python

Python is the initial interoperability target. Imported modules execute within the permissions of the host process.

## Compiled and Scripting Languages

Future integrations may investigate languages such as C, C++, Java, JavaScript, Rust, and others. Support must be established through implementation and testing.

## Web Technologies

HTML and CSS are web-asset formats, not general-purpose execution targets equivalent to the AssayFlux interpreter. They should be managed as assets and rendered through a browser, WebView, or web server where appropriate.

JavaScript execution requires an appropriate JavaScript runtime or browser environment.

## Scientific Computing

The long-term direction includes reusing established scientific and numerical libraries rather than recreating every scientific operation inside the language.

Scientific applications must still validate their calculations, data handling, units, error conditions, and external dependencies.

---

# Security

<p align="justify">

AssayFlux is an early-stage interpreter intended for trusted programs and development environments. It must not be treated as a security sandbox.

Python imports can execute code with the permissions of the AssayFlux process. External-language adapters may launch programs that can access files, networks, and other system resources. Process timeouts alone do not restrict filesystem access, network access, memory use, or privileges.

</p>

### Safe Development Practices

- Run only source files that you trust.
- Do not execute unknown `.af` programs in a privileged environment.
- Avoid running untrusted code on a production server.
- Use a separate, restricted operating-system account for risky experiments.
- Use a properly configured container or OS sandbox when executing untrusted code.
- Restrict filesystem and network access where required.
- Apply CPU, memory, and process limits.
- Keep dependencies and external runtimes under control.

The core interpreter does not itself provide these isolation guarantees.

For security-related concerns, consult [`SECURITY.md`](SECURITY.md).

---

# Current Development Status

<p align="justify">

AssayFlux is under active development as a custom programming language and interpreter. Its core implementation includes lexical analysis, parsing, an abstract syntax tree, an interpreter, a command-line interface, examples, and automated tests.

The language and its supporting documentation continue to evolve. New syntax and interoperability features should be introduced alongside tests and corresponding documentation updates.

</p>

### Existing Foundation

- Custom `.af` source-file format.
- Dedicated lexer and parser.
- Abstract syntax tree representation.
- Variable assignment and constant declarations.
- Output through `show`.
- Conditional execution using `if`, `otherwise`, and `else`.
- Repetition using supported `repeat` forms.
- Loop control through `stop` and `skip`.
- Function declarations using `f.`.
- Return statements and function calls.
- Input through `input()`.
- Python module-import functionality.
- Interpreter lifecycle management through `destroy()`.
- Command-line program execution.
- Automated tests and example programs.
- Language specification, grammar, and architecture documentation.

### Areas Requiring Continued Verification

- Complete consistency between the grammar, parser, interpreter, examples, and documentation.
- Additional edge-case testing.
- Error reporting and diagnostics.
- Interoperability coverage across external runtimes.
- Runtime availability and compatibility requirements.
- Development tooling and future IDE integration.
- Release packaging and compatibility policies.

The project should claim support for a feature only to the extent that the implementation and tests establish that support.

---

# Contributing

<p align="justify">

Contributions can help improve the language implementation, test coverage, documentation, examples, interoperability, and developer experience.

Changes to language syntax should be coordinated with the grammar and language specification so that the documentation and implementation remain consistent.

</p>

### Development Workflow

Clone the repository and install the development dependencies.

```bash
git clone https://github.com/AssayFlux/AssayFlux.git
cd AssayFlux
python -m pip install -e ".[dev]"
```

Run the tests before submitting changes.

```bash
python -m pytest
```

### Contribution Principles

- Preserve established syntax unless a change is intentional.
- Add tests for new language behavior.
- Test invalid syntax and runtime error cases.
- Follow the four-space indentation rule in examples.
- Use `show` for AssayFlux output.
- Use `otherwise` for additional conditional branches.
- Use `f.` for function declarations.
- Keep documentation consistent with implementation.
- Do not describe placeholder integrations as tested features.
- Avoid introducing unnecessary core dependencies.
- Document compatibility changes clearly.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the repository's contribution guidance.

---
# Project Direction

<p align="justify">

The long-term objective is to develop AssayFlux into a more complete and reliable programming environment. This includes strengthening the core language, expanding automated verification, improving interoperability, refining developer tooling, and maintaining clear documentation.

The immediate priority is correctness and consistency: source code, grammar, interpreter behavior, examples, and tests should agree. New capabilities can then be introduced incrementally with a clear distinction between implemented functionality and future plans.

</p>

<div align="center">

---

### AssayFlux

**A language built with clarity, structure, and extensibility in mind.**

[View the Repository](https://github.com/AssayFlux/AssayFlux)

<br>

</div>