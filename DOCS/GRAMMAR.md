# AssayFlux Scientific Systems — Language Grammar

## Overview

AssayFlux Scientific Systems is a programming language designed to provide readable syntax, explicit block endings, scientific computing capabilities, and access to the Python ecosystem.

The language uses Python as its compatibility foundation. AssayFlux introduces a small set of custom keywords and constructs while retaining Python-like expressions, data structures, functions, classes, modules, exception handling, and standard-library access.

**Language name:** AssayFlux Scientific Systems  
**Short name:** AssayFlux  
**File extension:** `.af`  
**Current package version:** `0.2.0`  
**Compatibility foundation:** Python  
**Primary objective:** Make programming more readable while preserving access to Python libraries and enabling interoperability with other programming languages.

This document defines the intended language syntax and behavior. A feature described here is part of the language specification, but it should not be considered implemented until the lexer, parser or interpreter, runtime, and tests support it.

---

## Design Principles

AssayFlux follows these principles:

- Keep Python-like syntax wherever a custom replacement is not explicitly required.
- Use lowercase custom keywords.
- Use `show` instead of `print()` for displaying output.
- Use `otherwise` instead of `elif`.
- Use `constant` for declaring constants.
- Use `stop` instead of `break`.
- Use `skip` instead of `continue`.
- Use `true` and `false` instead of Python's `True` and `False`.
- Support explicit `end` terminators for compound blocks.
- Preserve Python's familiar expressions, operators, collections, and function-call conventions.
- Preserve compatibility with Python libraries wherever possible.
- Provide clear syntax errors with useful line and column information.
- Support interoperability with other languages through explicit adapters and runtimes.
- Avoid changing existing Python behavior unnecessarily.

---

# Lexical Structure

## Source Files

AssayFlux source files use the `.af` extension.

Example:

```text
hello.af
variables.af
conditions.af
loops.af
functions.af
```

A source file contains statements, expressions, declarations, comments, and optional blank lines.

## Character Encoding

Source files should use UTF-8 encoding.

## Case Sensitivity

AssayFlux identifiers are case-sensitive.

For example:

```text
sample = 10
Sample = 20

show sample
show Sample
```

These identifiers represent two different variables.

Keywords must be written using their specified lowercase forms.

For example:

```text
show "Hello"
```

The custom keyword is `show`, not `Show`.

## Whitespace

AssayFlux uses Python-style indentation to describe nested blocks.

Four spaces per indentation level are recommended.

Tabs and spaces should not be mixed within the same indentation structure.

Example:

```text
if temperature > 25:
    show "Temperature is high"
end
```

Indentation determines nesting. The `end` keyword explicitly terminates the block.

## Blank Lines

Blank lines may be used to separate logical sections of a program.

Example:

```text
constant LIMIT = 100


f.calculate(value):
    result = value * 2
    return result
end
```

## Comments

A hash symbol begins a single-line comment.

Example:

```text
# This is a comment
show "Hello, AssayFlux"
```

Comments continue to the end of the physical line.

Comments should not affect program execution.

## Identifiers

Identifiers name variables, functions, classes, modules, and other objects.

A typical identifier begins with a letter or underscore and may contain letters, digits, and underscores.

Examples:

```text
value = 10
sample_count = 25
_private_value = 5
result2 = 100
```

Python-compatible identifier rules should be retained where supported by the lexer.

Keywords cannot be used as ordinary identifiers unless explicitly escaped by a future language feature.

---

# Keywords

## Core AssayFlux Keywords

| AssayFlux keyword | Meaning | Python equivalent or relationship |
|---|---|---|
| `show` | Display output | `print()` |
| `otherwise` | Additional conditional branch | `elif` |
| `constant` | Declare a constant | No direct equivalent |
| `stop` | Exit the nearest loop | `break` |
| `skip` | Skip to the next loop iteration | `continue` |
| `true` | Boolean true | `True` |
| `false` | Boolean false | `False` |
| `end` | Explicitly terminate a compound block | No direct equivalent |
| `f.` | Introduce a function declaration | Related to `def` |
| `repeat` | Introduce a repetition construct | Depends on the specified repeat form |

The words `if`, `else`, `for`, `while`, `return`, `class`, `try`, `except`, `finally`, `raise`, `with`, `import`, `from`, `as`, `pass`, `and`, `or`, `not`, `in`, `is`, `lambda`, `yield`, `async`, and `await` retain their Python-like meanings where supported.

The keyword `otherwise` replaces `elif`. It does not replace `else`.

## Reserved Words and Future Keywords

Future versions may introduce additional keywords for scientific computing, parallel execution, language interoperability, and package management.

New keywords should be added without changing the meaning of existing valid programs unnecessarily.

---

# Literals

## Numeric Literals

AssayFlux supports Python-style numeric literals where supported by the implementation.

### Integers

```text
count = 10
negative = -5
large_number = 1000000
```

### Floating-Point Numbers

```text
temperature = 36.5
concentration = 0.025
ratio = 1.5e-3
```

### Complex Numbers

Python-compatible complex numbers may be used when supported by the runtime.

```text
signal = 2 + 3j
```

Numbers remain numeric values. They must not automatically be converted into strings.

## String Literals

Single-quoted and double-quoted strings are supported.

```text
first = "AssayFlux"
second = 'Scientific Systems'
```

Escape sequences should follow Python-compatible behavior.

```text
message = "First line\nSecond line"
```

Triple-quoted strings should follow Python-compatible behavior where implemented.

```text
description = """A scientific programming language
with Python interoperability."""
```

Backtick strings are not part of the guaranteed syntax in this specification. They should only be enabled if explicitly implemented and tested.

## Boolean Literals

AssayFlux uses lowercase boolean literals.

```text
active = true
finished = false
```

Boolean values should behave like Python booleans at the runtime boundary.

## None Value

Python-compatible `None` may be used to represent the absence of a value.

```text
result = None
```

The lowercase boolean literals `true` and `false` are distinct from `None`.

## Collection Literals

### Lists

```text
values = [10, 20, 30]
names = ["Alpha", "Beta", "Gamma"]
```

### Tuples

```text
coordinates = (10, 20)
```

### Dictionaries

```text
sample = {
    "id": "AF-001",
    "temperature": 25.5,
    "active": true
}
```

### Sets

```text
unique_values = {1, 2, 3}
```

Empty sets should use the Python-compatible `set()` expression because `{}` represents an empty dictionary.

---

# Operators

AssayFlux retains Python-style operators wherever possible.

## Arithmetic Operators

| Operator | Meaning |
|---|---|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `//` | Floor division |
| `%` | Modulo |
| `**` | Exponentiation |
| `@` | Matrix multiplication where supported |

Example:

```text
a = 10
b = 3

show a + b
show a - b
show a * b
show a / b
show a // b
show a % b
show a ** b
```

## Comparison Operators

| Operator | Meaning |
|---|---|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

Example:

```text
show 10 == 10
show 10 != 5
show 10 > 5
show 10 < 20
```

The not-equal operator is `!=`. The spelling `nt=` is not part of the language.

## Logical Operators

```text
and
or
not
```

Example:

```text
temperature = 25
pressure = 100

if temperature > 20 and pressure >= 100:
    show "Conditions satisfied"
end
```

Logical operators should follow Python-compatible short-circuit behavior.

## Membership Operators

```text
in
not in
```

Example:

```text
samples = ["A", "B", "C"]

if "A" in samples:
    show "Sample found"
end
```

## Identity Operators

```text
is
is not
```

Identity operators should retain Python-compatible semantics.

## Assignment Operators

AssayFlux retains Python-style assignment operators where supported.

```text
value = 10
value += 5
value -= 2
value *= 3
value /= 2
value //= 2
value %= 3
value **= 2
```

Assignment expressions such as `:=` may be supported if the parser implements Python-compatible behavior.

## Bitwise Operators

```text
&
|
^
~
<<
>>
```

These operators retain Python-compatible meanings for supported operand types.

---

# Expressions

## Basic Expressions

Expressions may include literals, identifiers, function calls, operators, collection displays, indexing, and attribute access.

```text
a = 10
b = 20

result = a + b * 2
show result
```

Operator precedence and associativity should follow Python-compatible rules.

## Parenthesized Expressions

```text
result = (10 + 5) * 2
show result
```

## Variable Assignment

```text
name = "AssayFlux"
count = 10
temperature = 25.5
active = true
```

Python-compatible multiple assignment may be supported.

```text
a, b = 10, 20
```

## Augmented Assignment

```text
count = 10
count += 1

show count
```

## Conditional Expressions

Python-compatible conditional expressions may be supported.

```text
result = "Pass" if score >= 50 else "Fail"
show result
```

The `otherwise` keyword is used for compound conditional statements, not as a replacement inside every Python expression.

---

# Output

## The `show` Statement

AssayFlux uses `show` to display values.

```text
show "Hello, AssayFlux"
show 10
show 10 + 20
```

Multiple values may be supported:

```text
name = "AssayFlux"
version = 0.2

show name, version
```

The intended behavior is similar to Python's `print()` function, but the exact handling of separators, formatting options, and output streams depends on the runtime implementation.

## Formatted Strings

Python-compatible formatted string literals may be supported.

```text
name = "AssayFlux"
version = 0.2

show f"Language: {name}"
show f"Version: {version}"
```

The `f` prefix in a formatted string is distinct from the `f.` function declaration syntax.

---

# Constants

## The `constant` Declaration

The `constant` keyword declares a name intended to remain unchanged after initialization.

```text
constant MAX_ATTEMPTS = 5
constant PI_VALUE = 3.141592653589793
constant LANGUAGE_NAME = "AssayFlux"
```

A constant must be initialized when declared.

The intended syntax is:

```text
constant IDENTIFIER = expression
```

Example:

```text
constant TAX_RATE = 0.18

price = 1000
tax = price * TAX_RATE

show tax
```

## Constant Reassignment

The interpreter should reject reassignment to a declared constant.

Example:

```text
constant MAXIMUM = 100

MAXIMUM = 200
```

Expected behavior:

```text
Error: Cannot reassign constant 'MAXIMUM'.
```

The exact error wording may differ, but the error should identify the constant and source location.

## Constant Scope

Constants should follow the scope rules of the environment in which they are declared.

Global constants should be available throughout the relevant module unless shadowing or scope rules specify otherwise.

Constant behavior must be enforced by the interpreter or runtime; the keyword alone does not make a value immutable.

---

# Conditional Statements

## The `if` Statement

```text
if condition:
    statements
end
```

Example:

```text
temperature = 25

if temperature > 20:
    show "Temperature is high"
end
```

The condition must evaluate to a value accepted by the language's truth-testing rules.

## The `otherwise` Branch

`otherwise` replaces Python's `elif`.

```text
if condition_one:
    statements
otherwise condition_two:
    statements
else:
    statements
end
```

Example:

```text
score = 75

if score >= 90:
    show "Excellent"
otherwise score >= 70:
    show "Good"
otherwise score >= 50:
    show "Pass"
else:
    show "Fail"
end
```

Conditions are evaluated from top to bottom. The first true condition determines the selected branch.

## The `else` Branch

`else` remains available as the final alternative branch.

```text
value = 5

if value > 10:
    show "Greater than ten"
else:
    show "Ten or less"
end
```

## Nested Conditions

```text
temperature = 25
pressure = 100

if temperature > 20:
    if pressure >= 100:
        show "Conditions satisfied"
    else:
        show "Pressure is too low"
    end
else:
    show "Temperature is too low"
end
```

Every compound block must have a matching `end` when explicit block termination is enabled.

---

# Loops

## The `while` Loop

The `while` loop repeats while its condition remains true.

```text
while condition:
    statements
end
```

Example:

```text
count = 1

while count <= 5:
    show count
    count += 1
end
```

## The `for` Loop

The `for` loop iterates over an iterable.

```text
for item in iterable:
    statements
end
```

Example:

```text
for value in [10, 20, 30]:
    show value
end
```

## Iterating Over a Range

Python-compatible `range()` behavior should be retained where supported.

```text
for number in range(5):
    show number
end
```

This produces the values zero through four.

A range with a starting point and step may be used:

```text
for number in range(2, 11, 2):
    show number
end
```

## The `stop` Statement

`stop` replaces Python's `break`.

It exits the nearest enclosing loop.

```text
for number in range(10):
    if number == 5:
        stop
    end

    show number
end
```

## The `skip` Statement

`skip` replaces Python's `continue`.

It skips the remaining statements in the current iteration and proceeds to the next iteration.

```text
for number in range(10):
    if number % 2 == 0:
        skip
    end

    show number
end
```

## The `repeat` Construct

The `repeat` keyword is intended to introduce a repetition construct.

Its exact grammar must be standardized by the implementation before it can be considered stable.

A possible counted-repeat form is:

```text
repeat 5:
    show "Repeated operation"
end
```

A possible condition-based form is:

```text
repeat while count < 5:
    show count
    count += 1
end
```

These forms are proposed syntax, not a claim that the current interpreter already supports them.

## The `5x.` Counted-Loop Form

A compact counted-loop form such as `5x.` has been considered for AssayFlux.

Example of the proposed style:

```text
5x.:
    show "Repeated operation"
end
```

The exact tokenization, count expression, and interaction with nested blocks must be formally defined before this syntax is implemented.

Until the lexer, grammar, interpreter, and tests agree on this form, the Python-compatible `for` loop and the standardized `repeat` form should be preferred.

## Nested Loops

```text
for row in range(3):
    for column in range(3):
        show row, column
    end
end
```

`stop` and `skip` should affect the nearest enclosing loop unless a future explicit label mechanism is introduced.

---

# Functions

## Function Declarations

AssayFlux uses `f.` to introduce a function declaration.

The intended declaration form is:

```text
f.function_name(parameters):
    statements
end
```

Example:

```text
f.greet(name):
    show f"Hello, {name}"
end

greet("AssayFlux")
```

The `f.` prefix belongs to the function declaration. Ordinary function calls use the function name without the prefix.

## Functions With Return Values

```text
f.add(a, b):
    return a + b
end

result = add(10, 20)
show result
```

`return` terminates the current function and optionally provides a result.

## Functions Without Explicit Return Values

```text
f.display_message():
    show "Welcome to AssayFlux"
end

display_message()
```

A function without an explicit return value should follow Python-compatible behavior where possible.

## Default Arguments

```text
f.greet(name, greeting="Hello"):
    show greeting, name
end

greet("Asha")
greet("Asha", "Welcome")
```

## Keyword Arguments

```text
f.describe_sample(name, temperature):
    show name
    show temperature
end

describe_sample(name="Sample A", temperature=25.5)
```

## Variable-Length Positional Arguments

Python-compatible `*args` syntax may be supported.

```text
f.total(*values):
    result = 0

    for value in values:
        result += value
    end

    return result
end

show total(1, 2, 3, 4)
```

## Variable-Length Keyword Arguments

Python-compatible `**kwargs` syntax may be supported.

```text
f.describe(**details):
    show details
end

describe(name="Sample A", status="Ready")
```

## Recursion

Functions may call themselves if the runtime supports ordinary recursive function calls.

```text
f.factorial(number):
    if number <= 1:
        return 1
    end

    return number * factorial(number - 1)
end

show factorial(5)
```

## Nested Functions

Nested function declarations may be supported using the same explicit block-ending rules.

```text
f.outer(value):
    f.inner(number):
        return number * 2
    end

    return inner(value)
end

show outer(10)
```

## Lambda Expressions

Python-compatible lambda expressions may be supported.

```text
square = lambda number: number * number
show square(5)
```

The `f.` declaration syntax does not automatically replace Python's lambda expression syntax.

---

# Scope and Namespaces

AssayFlux should preserve Python-compatible local and global name-resolution behavior wherever possible.

## Local Variables

```text
f.calculate():
    result = 10
    return result
end
```

The variable `result` belongs to the function's local scope unless explicitly declared otherwise.

## Global Variables

```text
application_name = "AssayFlux"

f.display_name():
    global application_name
    show application_name
end
```

Support for `global` and `nonlocal` should follow Python-compatible semantics.

## Name Shadowing

Local variables may shadow outer names according to the supported scope rules.

Constant enforcement must remain consistent with the language's declared constant semantics.

---

# Classes and Objects

Class syntax should remain Python-like except for the explicit `end` terminator.

## Class Declaration

```text
class Sample:
    def __init__(self, name, temperature):
        self.name = name
        self.temperature = temperature
    end

    def describe(self):
        show self.name
        show self.temperature
    end
end
```

This example uses Python-style method declarations. If AssayFlux later requires `f.` for methods as well, that change must be specified and tested consistently.

## Creating Objects

```text
sample = Sample("Sample A", 25.5)
sample.describe()
```

## Inheritance

Python-compatible inheritance may be supported.

```text
class Animal:
    def speak(self):
        show "Sound"
    end
end

class Dog(Animal):
    def speak(self):
        show "Bark"
    end
end

dog = Dog()
dog.speak()
```

## Properties and Special Methods

Python-compatible properties, descriptors, special methods, and method-resolution rules may be supported by the runtime.

Examples include:

```text
__str__
__repr__
__len__
__iter__
__next__
```

The presence of these names in the specification does not guarantee that every related feature has already been implemented.

---

# Imports and Modules

## Importing a Module

Python-compatible imports should be retained where supported.

```text
import math

show math.sqrt(25)
```

## Importing Specific Names

```text
from math import sqrt

show sqrt(25)
```

## Aliases

```text
import numpy as np

values = np.array([1, 2, 3])
show values
```

## Importing AssayFlux Modules

AssayFlux modules may use the `.af` extension.

Example project:

```text
project/
    main.af
    calculations.af
```

A future module system may allow:

```text
import calculations
```

The exact module search path, caching rules, package layout, and import resolution must be defined by the interpreter.

## Python Module Interoperability

The runtime should provide a way to import and use Python modules without requiring every Python library to be rewritten.

For example, once supported:

```text
import math

show math.sqrt(144)
```

Third-party libraries such as NumPy, SciPy, Matplotlib, pandas, and other Python packages should remain accessible through the Python runtime when their installation and platform requirements are satisfied.

---

# Exception Handling

Exception handling should retain Python-compatible structure with explicit block terminators.

## `try` and `except`

```text
try:
    result = 10 / 0
except ZeroDivisionError:
    show "Cannot divide by zero"
end
```

## Multiple Exception Types

```text
try:
    value = int("invalid")
except ValueError:
    show "Invalid numeric value"
except TypeError:
    show "Unexpected type"
end
```

## `else` and `finally`

```text
try:
    result = 10 / 2
except ZeroDivisionError:
    show "Division failed"
else:
    show result
finally:
    show "Operation finished"
end
```

## Raising Exceptions

```text
f.validate_temperature(value):
    if value < -273.15:
        raise ValueError("Temperature is below absolute zero")
    end

    return value
end
```

## Custom Exceptions

Python-compatible custom exception classes may be supported.

```text
class SampleError(Exception):
    pass
end
```

---

# Context Managers

Python-compatible `with` statements may be supported.

```text
with open("data.txt", "r") as file:
    content = file.read()
    show content
end
```

The runtime should preserve context-manager entry and exit behavior, including cleanup when exceptions occur.

---

# Comprehensions

Python-compatible comprehensions may be supported where implemented.

## List Comprehension

```text
squares = [number * number for number in range(5)]
show squares
```

## Conditional List Comprehension

```text
even_numbers = [
    number
    for number in range(10)
    if number % 2 == 0
]

show even_numbers
```

## Dictionary Comprehension

```text
squares = {
    number: number * number
    for number in range(5)
}

show squares
```

## Set Comprehension

```text
unique_squares = {
    number * number
    for number in range(5)
}

show unique_squares
```

## Generator Expressions

Python-compatible generator expressions may be supported.

```text
values = (number * 2 for number in range(5))
```

---

# Iterators and Generators

## Iteration

Objects implementing the Python iterator protocol should be iterable where supported.

```text
for value in [10, 20, 30]:
    show value
end
```

## Generators

Python-compatible generator functions may use `yield`.

```text
def generate_values():
    yield 10
    yield 20
    yield 30
end

for value in generate_values():
    show value
end
```

The exact declaration syntax must be consistent with the interpreter's function grammar. If `f.` is required for all function declarations, the generator declaration must use the same rule.

---

# Type Annotations

Python-compatible type annotations may be supported.

```text
def add(a: int, b: int) -> int:
    return a + b
end
```

Type annotations should not change Python-compatible runtime behavior unless AssayFlux introduces an explicit type-checking system.

If the language later adopts `f.` for all function declarations, the equivalent declaration should be standardized as:

```text
f.add(a: int, b: int) -> int:
    return a + b
end
```

The parser must choose and enforce one canonical form.

---

# Decorators

Python-compatible decorators may be supported.

```text
@staticmethod
def calculate():
    return 10
end
```

Decorator placement, evaluation order, and interaction with function declarations must follow the grammar actually implemented by the parser.

If `f.` is mandatory for function declarations, decorator support must be defined in combination with that syntax rather than assumed automatically.

---

# Asynchronous Programming

Python-compatible asynchronous constructs may be supported where the runtime permits them.

These include:

```text
async
await
async for
async with
```

Example of the intended structure:

```text
async def fetch_data():
    result = await some_async_operation()
    return result
end
```

The exact declaration form must match the chosen AssayFlux function grammar.

Asynchronous syntax requires runtime support and should not be considered available merely because the keywords are listed here.

---

# Pattern Matching

Python-compatible structural pattern matching may be supported.

```text
match value:
    case 1:
        show "One"
    case 2:
        show "Two"
    case _:
        show "Other"
end
```

The grammar must ensure that every `case` body and the enclosing `match` statement terminate correctly.

---

# File Operations

Python-compatible file operations should remain available through the standard library.

```text
with open("results.txt", "w") as file:
    file.write("AssayFlux results")
end
```

Supported modes should follow Python's file API.

The interpreter must not silently alter file paths or file permissions without an explicit runtime policy.

---

# Scientific Computing

AssayFlux is intended to support scientific and technical applications.

Scientific functionality should primarily be provided through Python interoperability rather than by reimplementing every numerical library.

Potentially accessible libraries include:

- NumPy
- SciPy
- Matplotlib
- pandas
- SymPy
- scikit-learn
- Pillow
- openpyxl

Availability depends on the user's Python environment, installed packages, operating system, processor architecture, and the compatibility of each dependency.

Example:

```text
import math

radius = 5
area = math.pi * radius ** 2

show area
```

When compatible libraries are installed, AssayFlux should provide access to their functions through its Python interoperability layer.

---

# Interoperability With Other Languages

## General Principle

AssayFlux aims to provide a unified entry point for interacting with multiple programming languages.

This does not mean that every program written in one language can automatically be translated into every other language without limitations.

Interoperability may be implemented through:

- Native language runtimes
- Foreign-function interfaces
- Subprocess execution
- Generated source code
- Compilers and build tools
- HTTP APIs
- Shared libraries
- Database drivers
- Explicit adapters

Each integration must document its requirements, supported operations, error handling, and limitations.

## Python

Python is the primary compatibility foundation.

The implementation should prioritize reliable Python interoperability.

## JavaScript

JavaScript interoperability may use a JavaScript runtime, a subprocess, generated code, or another explicitly supported bridge.

## HTML

HTML may be generated or written as an output artifact for web pages and interfaces.

HTML is a markup language, not a general-purpose programming language.

## CSS

CSS may be generated or written as an output artifact for styling web interfaces.

CSS is a style-sheet language, not a general-purpose programming language.

## SQL

SQL interoperability may use database drivers or supported database engines.

The implementation must document which SQL dialects are supported.

## C and C++

C and C++ interoperability may use compiled native extensions, shared libraries, subprocesses, or code generation.

A working C/C++ compiler and the required development tools may be necessary.

## Java

Java interoperability may use the JVM, Java compilation tools, subprocesses, or generated source code.

## Rust

Rust interoperability may use compiled libraries, foreign-function interfaces, subprocesses, or generated source code.

A compatible Rust toolchain may be required.

## Go

Go interoperability may use compiled programs, shared libraries where supported, subprocesses, or generated source code.

## R

R interoperability may use an installed R runtime, subprocess execution, or an explicit Python-to-R bridge.

## Julia

Julia interoperability may use an installed Julia runtime, subprocess execution, or an explicit bridge.

## Shell

Shell interoperability may execute approved commands through an operating-system process interface.

Example of a possible future API:

```text
result = shell.run("echo AssayFlux")
show result
```

The exact API is not standardized until implemented.

Shell execution must have clearly defined permissions and error handling. Programs must not assume that the same shell or command set is available on every operating system.

## PHP

PHP interoperability may use an installed PHP interpreter, subprocess execution, generated PHP source, or an explicit bridge.

The exact execution API and dependency requirements must be documented by the implementation.

## Ruby

Ruby interoperability may use an installed Ruby interpreter, subprocess execution, generated Ruby source, or an explicit bridge.

The exact execution API and dependency requirements must be documented by the implementation.

## Adapter Requirements

Every language adapter should document:

- Adapter name
- Target language
- Required runtime or compiler
- Supported operating systems
- Input and output formats
- Data conversion rules
- Error propagation
- Exit-code handling
- Security restrictions
- Supported interoperability operations
- Automated tests

An adapter must not report success merely because a target runtime is installed. It must verify that the requested operation actually ran successfully.

---

# Runtime Errors

AssayFlux should provide understandable errors for invalid syntax and failed execution.

Errors should include, where possible:

- Error category
- Source filename
- Line number
- Column number
- Relevant source text
- A concise explanation
- A suggestion when the likely correction is clear

Example:

```text
Error: Missing 'end' for the block opened on line 2.
File: main.af
Line: 5
```

Another example:

```text
Error: Cannot reassign constant 'MAXIMUM'.
File: main.af
Line: 8
```

The exact messages may vary, but diagnostics should be consistent and useful.

---

# Parser and Grammar Requirements

## Explicit Block Termination

Every compound statement that uses an AssayFlux block must have a matching `end`.

The parser should identify the block opened by each statement and report an error when the terminator is missing.

Example:

```text
if value > 10:
    show value
```

Expected diagnostic:

```text
Error: Missing 'end' for the 'if' block.
```

## Indentation Validation

Indentation must remain consistent with the nesting structure.

The parser should reject unexpected indentation, missing indentation, and inconsistent indentation.

## Nested Blocks

Nested blocks must be parsed using both indentation and the explicit `end` terminator.

Example:

```text
if active:
    for value in values:
        show value
    end
end
```

Each `end` closes the innermost currently open block.

## Error Recovery

Where possible, the parser should identify syntax errors without producing misleading follow-up errors.

The implementation may report multiple independent syntax errors in one run, provided error recovery remains reliable.

## Formal Grammar

A complete formal grammar must define:

- Tokens
- Identifiers
- Literal forms
- Expression precedence
- Assignment statements
- Simple statements
- Compound statements
- Conditional branches
- Loop bodies
- Function declarations
- Class declarations
- Exception-handling blocks
- Import statements
- Comprehensions
- Explicit block terminators
- Indentation rules
- Any special `repeat` syntax
- Any counted-loop syntax such as `5x.`

The formal grammar must match the lexer and parser implementation. Informal examples in this document are not a substitute for executable grammar productions.

---

# Python Compatibility Policy

## Preserve Python-Like Behavior

Features not explicitly changed by AssayFlux should remain Python-like wherever possible.

This includes:

- Arithmetic
- Comparison
- Logical expressions
- Collections
- Indexing and slicing
- Attribute access
- Function calls
- Iteration
- Exceptions
- Imports
- Classes
- Standard-library behavior
- Python package interoperability

## Explicit Syntax Differences

The following differences are intentional:

| Python | AssayFlux |
|---|---|
| `print(value)` | `show value` |
| `elif condition:` | `otherwise condition:` |
| `break` | `stop` |
| `continue` | `skip` |
| `True` | `true` |
| `False` | `false` |
| `def name(...):` | `f.name(...):` for the custom function declaration form |
| No explicit block terminator | `end` for supported compound blocks |
| No direct constant-declaration keyword | `constant NAME = value` |

These differences must be implemented consistently in the lexer, parser, interpreter, and tests.

## Avoid Unnecessary Syntax Changes

AssayFlux should not invent replacements for Python syntax without a clear reason.

For example, the following operators should remain unchanged:

```text
==
!=
+
-
*
/
**
and
or
not
```

The objective is to introduce a small, consistent set of custom features while retaining Python's established behavior elsewhere.

---

# Implementation and Conformance

## Specification Versus Implementation

This document describes intended language behavior.

A feature is considered implemented only when:

- The lexer recognizes its syntax.
- The parser accepts valid programs and rejects invalid ones.
- The interpreter or compiler executes the feature correctly.
- Error messages are appropriate.
- Automated tests verify the behavior.
- Existing functionality remains compatible.

A documented feature must not be advertised as working if it has not passed these checks.

## Required Core Tests

The project should test at least:

- Variable assignment
- Numeric expressions
- String literals
- Boolean literals
- `show`
- `constant` declarations
- Constant reassignment errors
- `if`, `otherwise`, and `else`
- Nested conditional blocks
- `for` loops
- `while` loops
- `stop`
- `skip`
- Function declarations using `f.`
- Function calls
- Return values
- Function parameters
- Explicit `end` handling
- Indentation validation
- Missing terminators
- Exception handling
- Module imports
- Python interoperability
- Language adapter behavior
- Invalid syntax diagnostics

## Regression Testing

New syntax must not break previously working features.

Every grammar change should run the existing automated test suite and any new tests associated with that change.

## Adapter Testing

Each language adapter should have tests that verify:

- Runtime or compiler detection
- Valid input execution
- Output capture
- Error capture
- Nonzero exit codes
- Missing-runtime behavior
- Invalid input behavior
- Data conversion
- Platform limitations

A successful GitHub Actions workflow indicates that the checks configured in that workflow passed. It does not automatically prove that every language feature or every adapter is fully implemented.

## Future Grammar Changes

Changes to the grammar should be documented and accompanied by tests.

Breaking syntax changes should be versioned and explained.

The project should maintain a clear distinction between:

- Implemented features
- Partially implemented features
- Planned features
- Unsupported features

---

# Final Language Goal

AssayFlux aims to provide a readable, Python-compatible programming language with selected custom syntax and a consistent path to multi-language interoperability.

The long-term goal is to let developers express workflows in AssayFlux and use other languages and their ecosystems through reliable, explicit integrations.

Achieving this goal requires a stable grammar, a well-tested interpreter, a clear runtime architecture, robust adapter interfaces, and automated conformance testing.

The priority is correctness and maintainability: a small set of dependable language features is more valuable than a large list of unimplemented promises.