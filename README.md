<div align="center">

<br>

<img src="assayflux-logo.png" alt="AssayFlux Logo" width="260">

<br><br>

# AssayFlux

### Programming Language and Interpreter

**Language Design · Custom Syntax · Interpreter · Runtime · Testing**

A programming-language project dedicated to designing, implementing, and documenting the AssayFlux language.

<br>

---

## Language Reference

**A detailed guide to AssayFlux syntax, instructions, expressions, program structure, and examples.**

---

</div>

<p align="justify">

AssayFlux is a programming-language project built around its own source-file format, `.af`, and a dedicated interpreter. This document serves as a central reference for the language: its syntax, programming constructs, expressions, declarations, execution concepts, and example programs.

The purpose of this reference is to make the language easier to understand, develop, test, and extend. Each section explains the purpose of a construct and illustrates its usage wherever the syntax is sufficiently established.

</p>

<div align="center">

## Table of Contents

</div>

| Section | Description |
|:---|:---|
| 1. Language Overview | Introduction to AssayFlux and its source files |
| 2. Syntax Fundamentals | Instructions, identifiers, numbers, strings, and symbols |
| 3. Variables and Constants | Storing values and declaring constants |
| 4. Data Types and Values | Strings, numbers, booleans, and identifiers |
| 5. Operators and Expressions | Arithmetic and expression evaluation |
| 6. Function Calls | Calling functions and evaluating arguments |
| 7. Conditions | Conditional execution and branching |
| 8. Loops | Repetition and loop control |
| 9. Functions | Defining functions and returning values |
| 10. Program Control | Stopping, skipping, and controlling execution |
| 11. Runtime Management | The proposed `destroy()` operation |
| 12. Example Programs | Existing `.af` example categories |
| 13. Interpreter Architecture | Lexer, parser, syntax tree, and runtime |
| 14. Testing | Verification and regression testing |
| 15. Syntax Status | Distinguishing established syntax from features requiring verification |

---

<div align="center">

# 1. Language Overview

</div>

<p align="justify">

AssayFlux uses `.af` as its source-file extension. Programs written in the language are intended to be processed by the AssayFlux interpreter.

The language's design includes declarations, values, expressions, function calls, and programming constructs that can be developed and verified through individual source files and automated tests.

The exact behavior of each construct is determined by the interpreter implementation. A syntax example should therefore be considered authoritative only when it agrees with the actual parser and runtime.

</p>

<div align="center">

### Language Fundamentals

</div>

| Property | Details |
|:---|:---|
| Language name | AssayFlux |
| Source-file extension | `.af` |
| Language category | Custom programming language |
| Execution component | AssayFlux interpreter |
| Primary purpose | Writing and interpreting AssayFlux programs |
| Example programs | `hello.af`, `variables.af`, `conditions.af`, `loops.af`, `functions.af`, `input.af` |
| Implementation components | Parser, abstract syntax tree, interpreter, and tests |
| Documentation objective | Describe supported syntax and runtime behavior accurately |

---

<div align="center">

# 2. Syntax Fundamentals

</div>

<p align="justify">

Programming-language syntax defines how instructions, expressions, declarations, and values are represented in source code. The interpreter must recognize this syntax before it can determine what a program means or how it should execute.

The following table documents the fundamental elements recorded in the AssayFlux design and implementation notes. Where a specific spelling or grammar rule has not been verified, the entry identifies that limitation rather than inventing a definitive language rule.

</p>

| Syntax element | Purpose | Example | Explanation |
|:---|:---|:---|:---|
| Source file | Contains a program | `hello.af` | AssayFlux examples use the `.af` extension. |
| Identifier | Refers to a named value | `total` | Identifiers can appear in expressions when defined and supported by the runtime. |
| Constant declaration | Declares a constant | `constant LIMIT = 100` | The recorded declaration syntax uses `constant`, a name, `=`, and an expression. |
| Assignment symbol | Separates a declaration name from its value | `=` | Used in the recorded constant-declaration syntax. |
| Numeric literal | Represents a number | `42` | Numeric literals are among the recorded supported expression values. |
| String literal | Represents text | `"AssayFlux"` | Double-quoted strings appear in the previously discussed language design. |
| Boolean value | Represents a logical value | `true` | Boolean values are recorded among supported expression values; exact capitalization should follow the implementation. |
| Arithmetic expression | Combines numeric values and operators | `5 + 3` | Arithmetic expressions are recorded as supported. |
| Function call | Invokes a function | `calculate()` | Function calls are recorded as supported expression forms. |
| Instruction keyword | Introduces a language construct | `constant` | Keywords must match the spelling recognized by the parser. |
| Block terminator | Closes a block | `end` | Discussed for block-based control-flow and function syntax; confirm support for each construct. |
| Comment marker | Introduces a comment | `# comment` | Discussed during language design; verify that the current lexer recognizes it. |

<div align="center">

### Important Syntax Rule

</div>

<p align="justify">

Examples in this reference use readable spacing and consistent indentation. These formatting choices improve readability, but the actual requirements for whitespace, line breaks, capitalization, and statement termination must be determined by the lexer and parser.

</p>

---

<div align="center">

# 3. Variables and Constants

</div>

<p align="justify">

Variables and constants represent named values. A constant declaration is part of the previously recorded AssayFlux interpreter implementation. The precise syntax for mutable variable assignment must be confirmed independently rather than inferred from the existence of constant declarations.

</p>

| Construct | Syntax or example | Purpose | Status |
|:---|:---|:---|:---|
| Constant declaration | `constant LIMIT = 100` | Declares a named constant with a value. | Recorded in the interpreter implementation notes. |
| Numeric constant | `constant COUNT = 10` | Associates a constant name with a numeric expression. | Uses the recorded declaration form. |
| String constant | `constant TITLE = "AssayFlux"` | Associates a constant name with a string expression. | Verify string-literal handling against the current parser. |
| Boolean constant | `constant ENABLED = true` | Associates a constant name with a boolean expression. | Verify the accepted boolean spelling against the implementation. |
| Arithmetic constant | `constant TOTAL = 5 + 3` | Uses an arithmetic expression as the declared value. | Arithmetic expressions are recorded as supported. |
| Identifier reference | `LIMIT` | Refers to a named value in an expression. | Depends on the name being available in the evaluation environment. |
| Mutable assignment | `total = 10` | Illustrates a conventional assignment form. | Do not treat this as confirmed AssayFlux syntax until verified. |
| Constant reassignment | `LIMIT = 200` | Illustrates an attempted reassignment. | Expected behavior must be established from the interpreter's constant-handling rules. |

<div align="center">

### Constant Declaration Example

</div>

```text
constant LIMIT = 100
constant COUNT = 10
constant TITLE = "AssayFlux"
```

<p align="justify">

The example illustrates the recorded declaration form. Whether all three declarations execute successfully depends on the current implementation's handling of numeric and string values, declaration scope, and duplicate names.

</p>

---

<div align="center">

# 4. Data Types and Values

</div>

<p align="justify">

Values are the building blocks of expressions. The recorded interpreter notes identify strings, numbers, booleans, identifiers, arithmetic expressions, and function calls among the expression forms.

This table describes those categories without assuming unsupported collection types or additional type-system features.

</p>

| Value category | Example | General meaning | Documentation note |
|:---|:---|:---|:---|
| Integer-like number | `25` | Represents a whole numeric value. | Numeric literal support is recorded. |
| Decimal number | `3.14` | Represents a fractional numeric value. | Confirm decimal parsing and numeric precision in the implementation. |
| String | `"Hello"` | Represents textual data. | String expression support is recorded. |
| Boolean | `true` | Represents a logical value. | Confirm the exact accepted boolean tokens. |
| Identifier | `LIMIT` | Refers to a named value. | Requires a valid binding in the interpreter environment. |
| Arithmetic expression | `10 + 5` | Computes a numeric result. | Arithmetic support is recorded. |
| Function-call expression | `calculate()` | Evaluates a function call. | Function-call expressions are recorded. |
| List literal | `[1, 2, 3]` | Conventional notation for a list. | Native list literals were previously noted as unsupported. |
| Dictionary literal | `{"name": "value"}` | Conventional notation for a mapping. | Native dictionary literals were previously noted as unsupported. |
| Null-like value | `null` | Often represents an absent value. | Do not assume this token exists in AssayFlux. |

<div align="center">

### Example: Values in Declarations

</div>

```text
constant COUNT = 25
constant RATE = 3.14
constant MESSAGE = "Hello, AssayFlux"
```

<p align="justify">

These examples demonstrate the intended appearance of numeric and string declarations. The implementation should be consulted to establish accepted numeric formats, escape sequences, string delimiters, and evaluation behavior.

</p>

---

<div align="center">

# 5. Operators and Expressions

</div>

<p align="justify">

An expression combines values, identifiers, operators, and possibly function calls to produce a result. Arithmetic expression support is recorded in the interpreter notes. The complete operator inventory, precedence rules, associativity, and comparison semantics must be taken from the actual parser and evaluator.

</p>

| Operator or expression | Example | Conventional purpose | Verification required |
|:---|:---|:---|:---|
| Addition `+` | `5 + 3` | Adds numeric values. | Confirm the parser and evaluator support this operator. |
| Subtraction `-` | `10 - 4` | Subtracts one value from another. | Confirm operator support and precedence. |
| Multiplication `*` | `6 * 7` | Multiplies numeric values. | Confirm operator support and precedence. |
| Division `/` | `12 / 3` | Divides one value by another. | Confirm division semantics and zero-division handling. |
| Parentheses `()` | `(2 + 3) * 4` | Conventionally groups expressions. | Confirm grouping syntax in the parser. |
| Equality `==` | `x == 10` | Conventionally compares values. | Exact comparison syntax is unverified. |
| Inequality `!=` | `x != 10` | Conventionally tests whether values differ. | Exact comparison syntax is unverified. |
| Less-than `<` | `x < 10` | Conventionally compares ordering. | Exact comparison syntax is unverified. |
| Greater-than `>` | `x > 10` | Conventionally compares ordering. | Exact comparison syntax is unverified. |
| Logical AND | `a and b` | Conventionally combines conditions. | Keyword and evaluation behavior are unverified. |
| Logical OR | `a or b` | Conventionally combines conditions. | Keyword and evaluation behavior are unverified. |
| Logical NOT | `not a` | Conventionally negates a condition. | Keyword and evaluation behavior are unverified. |
| Function-call expression | `calculate()` | Evaluates a function invocation. | Function-call support is recorded; exact argument grammar needs verification. |

<div align="center">

### Arithmetic Example

</div>

```text
constant RESULT = 5 + 3
```

<p align="justify">

This example uses the recorded constant-declaration form and arithmetic expression support. It should be retained as an executable example only if the current interpreter accepts the expression exactly as written.

</p>

---

<div align="center">

# 6. Function Calls

</div>

<p align="justify">

A function call requests the execution or evaluation of a named function. Function calls are recorded among the interpreter's supported expression forms. The precise rules for function definitions, arguments, return values, and scope should be documented separately from the general call syntax.

</p>

| Construct | Example | Purpose | Status |
|:---|:---|:---|:---|
| Zero-argument call | `calculate()` | Calls a function without explicit arguments. | Function-call expressions are recorded. |
| Call with one argument | `calculate(5)` | Illustrates passing one argument. | Verify argument parsing and function parameter support. |
| Call with multiple arguments | `calculate(5, 3)` | Illustrates passing multiple arguments. | Verify separator and argument-count rules. |
| Nested call | `calculate(other())` | Illustrates a call inside another expression. | Verify nested-call parsing and evaluation. |
| Call in a declaration | `constant RESULT = calculate()` | Illustrates using a call as a declared expression. | Verify compatibility between calls and declarations. |
| Unknown function | `missing_function()` | Illustrates an unresolved function name. | Document the actual runtime error behavior. |

<div align="center">

### Function-Call Example

</div>

```text
constant RESULT = calculate()
```

<p align="justify">

The example illustrates the relationship between a constant declaration and a function-call expression. It does not establish that a function named `calculate` is built into AssayFlux.

</p>

---

<div align="center">

# 7. Conditional Execution

</div>

<p align="justify">

Conditional statements allow a program to choose between execution paths based on a condition. The previously discussed AssayFlux design used `if`, `elif`, `else`, and `end` for block-based conditional syntax.

Their presence in design discussions does not, by itself, establish that every form is implemented in the current interpreter.

</p>

| Keyword or construct | Illustrative syntax | Intended purpose | Status |
|:---|:---|:---|:---|
| `if` | `if condition` | Begins a conditional branch. | Previously discussed; verify parser support. |
| `elif` | `elif other_condition` | Introduces another conditional branch. | Previously discussed; verify parser support. |
| `else` | `else` | Introduces a fallback branch. | Previously discussed; verify parser support. |
| `end` | `end` | Closes a conditional block. | Previously discussed for block termination. |
| Condition expression | `x > 10` | Supplies a value to test. | Comparison syntax must be verified. |
| Nested condition | `if condition` inside another block | Illustrates nested branching. | Verify nesting and block matching. |
| Missing terminator | Conditional block without `end` | Illustrates malformed block structure. | Document the parser's actual error response. |

<div align="center">

### Illustrative Conditional Structure

</div>

```text
if condition
    # conditional body
else
    # alternative body
end
```

<p align="justify">

This is a structural illustration of the previously discussed design, not a guaranteed executable program. The comment marker, condition grammar, indentation rules, and exact block syntax must all be confirmed against the current implementation.

</p>

---

<div align="center">

# 8. Loops and Repetition

</div>

<p align="justify">

Loops allow a program to repeat instructions. Earlier AssayFlux design discussions included `repeat`, `times`, `while`, `stop`, `skip`, and `end`. The interpreter's actual grammar determines which loop forms are available and how their conditions, counts, and control-flow statements behave.

</p>

| Keyword or construct | Illustrative syntax | Intended purpose | Status |
|:---|:---|:---|:---|
| `repeat` | `repeat ...` | Introduces a repetition construct. | Previously discussed; verify exact grammar. |
| `times` | `repeat 5 times` | Illustrates count-based repetition. | Previously discussed; verify parser support. |
| `while` | `while condition` | Illustrates condition-controlled repetition. | Previously discussed; verify parser support. |
| `stop` | `stop` | Intended to terminate a loop. | Previously discussed; verify execution semantics. |
| `skip` | `skip` | Intended to skip the current iteration. | Previously discussed; verify execution semantics. |
| `end` | `end` | Closes a loop block. | Previously discussed for block termination. |
| Loop condition | `while condition` | Determines whether a loop continues. | Depends on the supported condition grammar. |
| Loop count | `repeat 5 times` | Specifies an illustrative repetition count. | Exact numeric and boundary rules are unverified. |
| Nested loops | One loop inside another | Illustrates nested repetition. | Verify nesting and control-flow handling. |
| Infinite-loop prevention | A loop with no terminating condition | Highlights a potential execution hazard. | Document runtime safeguards only if implemented. |

<div align="center">

### Illustrative Count-Based Loop

</div>

```text
repeat 5 times
    # repeated instructions
end
```

<div align="center">

### Illustrative Condition-Based Loop

</div>

```text
while condition
    # repeated instructions
end
```

<p align="justify">

These examples document the earlier proposed design. Before presenting them as official executable syntax, verify the parser's exact requirements for the repetition count, condition expression, body, and closing keyword.

</p>

---

<div align="center">

# 9. Functions and Return Values

</div>

<p align="justify">

Functions provide a way to group instructions under a name and potentially return a result. Earlier design discussions used `func`, `return`, and `end` for function-related syntax. Their complete behavior—including parameter declarations, local scope, recursion, and return-value rules—must be verified in the interpreter.

</p>

| Keyword or construct | Illustrative syntax | Intended purpose | Status |
|:---|:---|:---|:---|
| `func` | `func calculate` | Introduces a function definition. | Previously discussed; exact grammar unverified. |
| Function name | `calculate` | Identifies the function. | Naming rules must match the parser. |
| Parameters | `func calculate(a, b)` | Illustrates a function accepting parameters. | Verify parameter syntax and support. |
| Function body | Instructions between declaration and terminator | Contains the function's operations. | Depends on the implemented block grammar. |
| `return` | `return result` | Illustrates returning a value. | Previously discussed; verify runtime behavior. |
| `end` | `end` | Closes a function block. | Previously discussed for block termination. |
| Function call | `calculate()` | Invokes a function. | Function-call expressions are recorded. |
| Recursive call | A function calling itself | Illustrates recursion. | Verify recursion support and runtime limits. |
| Missing function | Calling an undefined function | Illustrates a resolution failure. | Actual error behavior must be documented. |

<div align="center">

### Illustrative Function Structure

</div>

```text
func calculate
    return 10
end
```

<p align="justify">

This example reflects the previously discussed block-based design. It should not be described as a confirmed executable example until the current parser and interpreter have been checked.

</p>

---

<div align="center">

# 10. Program Control

</div>
