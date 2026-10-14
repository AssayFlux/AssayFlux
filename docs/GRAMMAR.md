# AssayFlux Grammar

**Full Project Name:** AssayFlux Scientific Systems  
**Language:** AssayFlux  
**Version:** 0.1.0  
**Status:** Initial Draft

## 1. Introduction

AssayFlux is a general-purpose programming language designed for scientific computing and integration with other programming languages.

This document defines the initial grammar and syntax rules of AssayFlux using Extended Backus–Naur Form (EBNF).

## 2. Language Design Principles

- Readable and consistent syntax.
- Scientific computing capabilities.
- Multi-language interoperability.
- No mandatory indentation.
- Explicit block termination using `end`.
- Backtick-delimited strings.
- Clear error messages with line numbers and useful suggestions.
- Modular and extensible architecture.

## 3. Lexical Structure

### 3.1 Identifiers

Identifiers name variables, functions, and other language elements.

```ebnf
identifier = letter, { letter | digit | "_" } ;
letter = "A"…"Z" | "a"…"z" ;
digit = "0"…"9" ;
```

Examples:

```text
temperature
total_value
calculate_sum
```

Identifiers must begin with a letter.

### 3.2 Reserved Keywords

The initial reserved keywords are:

```text
app
let
const
return
end
if
otherwise
else
repeat
stop
skip
show
true
false
and
or
not
import
```

The `f.` prefix is reserved for function declarations.

The `nt=` operator means not equal.

Reserved keywords cannot be used as ordinary identifiers.

### 3.3 Numeric Literals

```ebnf
integer = digit, { digit } ;
float = digit, { digit }, ".", digit, { digit } ;
```

Examples:

```text
0
10
250
3.14
0.5
```

Scientific notation will be defined in a later revision.

### 3.4 String Literals

Strings use backticks as delimiters.

```ebnf
string_literal = "`", { string_character }, "`" ;
```

Examples:

```text
`Hello, AssayFlux!`
`Scientific Computing`
`Temperature is high`
```

Escape sequences will be defined in a later revision.

### 3.5 Boolean Literals

```ebnf
boolean_literal = "true" | "false" ;
```

Examples:

```text
true
false
```

### 3.6 Comments

Single-line comments begin with `//`.

Example:

```text
// This is an AssayFlux comment
let temperature = 25
```

Comments are ignored during program execution.

### 3.7 Whitespace and Indentation

Spaces, tabs, and newlines separate tokens where necessary.

Indentation is optional and does not determine block boundaries.

Blocks are terminated using the keyword `end`.

The parser must not require Python-style indentation.

## 4. Program Structure

An AssayFlux program consists of an optional application declaration followed by statements.

```ebnf
program = [ app_declaration ], { statement } ;
app_declaration = "app", string_literal ;
```

Example:

```text
app `Scientific Calculator`
```

## 5. Variables and Constants

### 5.1 Variable Declaration

The keyword `let` declares a variable.

```ebnf
variable_declaration = "let", identifier, "=", expression ;
```

Examples:

```text
let temperature = 25
let name = `AssayFlux`
let enabled = true
```

Variables are intended to support type inference.

### 5.2 Constant Declaration

The keyword `const` declares a constant.

```ebnf
constant_declaration = "const", identifier, "=", expression ;
```

Example:

```text
const PI = 3.14159
const MAX_ITERATIONS = 1000
```

Constants cannot be reassigned after initialization.

### 5.3 Assignment

```ebnf
assignment = identifier, "=", expression ;
```

Example:

```text
let temperature = 25
temperature = 30
```

Assignment to constants is prohibited.

## 6. Operators and Expressions

### 6.1 Arithmetic Operators

| Operator | Meaning |
|---|---|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Remainder |

Example:

```text
let sum = 10 + 5
let difference = 10 - 5
let product = 10 * 5
let quotient = 10 / 5
let remainder = 10 % 3
```

### 6.2 Comparison Operators

| Operator | Meaning |
|---|---|
| `==` | Equal |
| `nt=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

Example:

```text
let result = 10 nt= 5
show result
```

Expected output:

```text
true
```

### 6.3 Logical Operators

| Operator | Meaning |
|---|---|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

Examples:

```text
let first = true and false
let second = true or false
let third = not true
```

### 6.4 Expression Grammar

```ebnf
expression =
      literal
    | identifier
    | unary_expression
    | binary_expression
    | function_call
    | "(", expression, ")" ;

literal =
      integer
    | float
    | string_literal
    | boolean_literal ;

unary_expression =
      "-", expression
    | "not", expression ;

binary_expression =
    expression, binary_operator, expression ;

binary_operator =
      "+"
    | "-"
    | "*"
    | "/"
    | "%"
    | "=="
    | "nt="
    | "<"
    | ">"
    | "<="
    | ">="
    | "and"
    | "or" ;
```

Operator precedence and associativity must be defined explicitly before implementation.

## 7. Display Output

The keyword `show` displays a value.

```ebnf
show_statement = "show", expression ;
```

Examples:

```text
show `Hello, World!`
show 100
show temperature
```

The runtime should display the evaluated value.

## 8. Conditional Statements

AssayFlux uses `if`, `otherwise`, `else`, and `end` for conditional execution.

### 8.1 If Statement

```ebnf
if_statement =
    "if", expression, statement_block,
    { otherwise_clause },
    [ else_clause ],
    "end" ;
```

### 8.2 Otherwise Clause

```ebnf
otherwise_clause =
    "otherwise", expression, statement_block ;
```

The `otherwise` keyword introduces an additional condition.

### 8.3 Else Clause

```ebnf
else_clause =
    "else", statement_block ;
```

The `else` clause is the final alternative when no preceding condition is true.

### 8.4 Example

```text
let temperature = 25

if temperature > 30
    show `Hot`
otherwise temperature > 20
    show `Warm`
else
    show `Cold`
end
```

Expected output:

```text
Warm
```

Rules:

- `if` introduces the first condition.
- `otherwise` introduces another condition.
- Multiple `otherwise` clauses are permitted.
- `else` is optional and must be the final alternative.
- `end` terminates the conditional statement.
- Conditions must evaluate to Boolean values.
- Indentation is optional.

## 9. Repetition and Loops

The `repeat` keyword introduces a repetition block.

```ebnf
repeat_statement =
    "repeat", [ expression ], statement_block, "end" ;
```

Example:

```text
let count = 0

repeat count < 5
    show count
    count = count + 1
end
```

The intended behavior is to repeat while the condition evaluates to true.

The behavior of `repeat` without a condition will be specified separately.

### 9.1 Stop

The `stop` statement terminates the innermost active loop.

```ebnf
stop_statement = "stop" ;
```

Example:

```text
repeat true
    show `Running`
    stop
end
```

### 9.2 Skip

The `skip` statement skips the remaining statements in the current iteration.

```ebnf
skip_statement = "skip" ;
```

Example:

```text
let count = 0

repeat count < 5
    count = count + 1

    if count == 3
        skip
    end

    show count
end
```

`stop` and `skip` are valid only within an appropriate loop context.

## 10. Functions

### 10.1 Function Declaration

AssayFlux uses the `f.` prefix for function declarations.

```ebnf
function_declaration =
    "f.", identifier,
    "(",
    [ parameter_list ],
    ")",
    statement_block,
    "end" ;

parameter_list =
    identifier, { ",", identifier } ;
```

Example:

```text
f.add(a, b)
    return a + b
end
```

### 10.2 Function Return

The `return` keyword returns a value from a function.

```ebnf
return_statement = "return", [ expression ] ;
```

Example:

```text
f.square(number)
    return number * number
end
```

A function may return a value or return without an explicit value.

### 10.3 Function Calls

```ebnf
function_call =
    identifier,
    "(",
    [ argument_list ],
    ")" ;

argument_list =
    expression, { ",", expression } ;
```

Example:

```text
f.add(a, b)
    return a + b
end

let result = add(10, 20)
show result
```

Expected output:

```text
30
```

Function declarations and function calls have different syntax.

## 11. Modules and Imports

The `import` keyword introduces a module import.

```ebnf
import_statement = "import", identifier ;
```

Example:

```text
import math
```

The module system will eventually support reusable AssayFlux modules and external libraries.

Import paths, aliases, package resolution, and external-language bindings will be specified separately.

## 12. Statement Blocks

A statement block consists of zero or more statements.

```ebnf
statement_block = { statement } ;
```

Blocks are terminated by the `end` keyword associated with their enclosing construct.

Block-opening constructs include:

- `if`
- `otherwise`
- `else`
- `repeat`
- `f.` function declarations

Nested blocks must be parsed according to their enclosing constructs.

Indentation does not define block boundaries.

## 13. Complete Statement Categories

The initial statement categories are:

```ebnf
statement =
      variable_declaration
    | constant_declaration
    | assignment
    | show_statement
    | if_statement
    | repeat_statement
    | stop_statement
    | skip_statement
    | function_declaration
    | return_statement
    | import_statement
    | expression_statement ;
```

Expression statements permit standalone expressions where appropriate.

The implementation must reject invalid statements and illegal control-flow operations.

## 14. Multi-Language Integration

AssayFlux is designed to integrate with other programming languages.

Python is the initial integration target.

The planned architecture includes:

- Lexer.
- Parser.
- Abstract syntax tree.
- Semantic analyzer.
- Intermediate representation, if required.
- Execution engine.
- Foreign-function interface.
- Language-specific adapters.
- Standard library.

These are planned components, not implemented features.

External-language calling syntax will be defined in a separate interoperability specification.

## 15. Error Reporting

AssayFlux should provide clear and useful error messages.

Errors should include, where possible:

- Error category.
- File name.
- Line number.
- Column number.
- Explanation of the problem.
- Suggested correction.

Example:

Syntax Error: Missing 'end'.

File: example.af
Line: 8, Column: 1

Suggestion: Add 'end' to close the conditional block.

The implementation should distinguish lexical, syntax, semantic, runtime, and external integration errors.

## 16. Grammar Development Status

This document defines the initial syntax proposal for AssayFlux version 0.1.0.

The following areas require further formalization:

- String escape sequences.
- Numeric formats.
- Operator precedence and associativity.
- Type inference and type checking.
- Variable scope and reassignment.
- Conditional evaluation.
- Repetition behavior.
- Nested block parsing.
- Function calls and return behavior.
- Module resolution.
- External-language interoperability.
- Error recovery.

The grammar must be refined and tested before implementation.

## 17. Compatibility Policy

This specification is the authoritative reference for AssayFlux syntax.

Changes to keywords, operators, block structure, or function declaration syntax must be documented.

Breaking syntax changes should be recorded in the project changelog and versioned appropriately.