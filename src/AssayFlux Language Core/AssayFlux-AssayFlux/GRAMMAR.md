# AssayFlux Language Grammar

The executable grammar is `src/assayflux/language/grammar.lark`. The parser, AST construction, semantic checks, interpreter, and tests must agree with that grammar.

## Canonical choices

- Source files use **`.af` only**.
- Assignments use `NAME = expression`.
- Project metadata starts with `project "Name"`; the old `app` declaration is not accepted.
- Functions use `f.name(parameters):` and end with `end`.
- Null is `null`; booleans are `true` and `false`.
- Counted repetition uses `N times:`, where `N` is a non-negative integer literal.
- Compound blocks use a colon, indentation, and a matching `end`.
- Output uses `show`; conditional branches use `otherwise`; loops use `stop` and `skip`.

## Minimal program

```af
project "Hello AssayFlux"

name = "AssayFlux"
answer = 6 * 7
show "Hello, " + name
show answer
```

A `project` declaration is optional metadata. It names the project; it does not execute code or enable external services.

## Values and assignment

```af
sample_count = 12
temperature = 36.5
active = true
finished = false
missing_value = null
message = f"Sample count: {sample_count}"

constant MAX_SAMPLES = 100
```

An ordinary assignment creates a variable or updates an existing non-constant variable. A `constant NAME = expression` declaration creates a constant that cannot be reassigned.

## Functions

```af
f.multiply(value, factor = 2):
    return value * factor
end

show multiply(6)
```

Use the `f.` prefix for function declarations, not Python's `def` syntax.

## Conditions

```af
if temperature > 37:
    show "High"
otherwise temperature < 10:
    show "Low"
else:
    show "Normal"
end
```

## Repetition

```af
3 times:
    show "Again"
end

repeat sample_count:
    show "Processing"
end

for value in [10, 20, 30]:
    show value
end

while sample_count > 0:
    sample_count -= 1
end
```

Use `N times:` for a fixed non-negative integer literal and `repeat expression:` when the count is evaluated at runtime.

## Imports and expressions

```af
import math
show math.sqrt(144)
```

The executable grammar is intentionally narrower than Python. A feature is supported only when grammar, AST construction, semantic checks, and runtime behavior agree.

## Syntax rules

- Use UTF-8 and four spaces per indentation level.
- Names are case-sensitive.
- Comments begin with `#`.
- Every supported compound statement must have exactly one matching `end`.
- Use lowercase `null`, `true`, and `false`.
- Unsupported syntax must fail clearly rather than being described as implemented.
