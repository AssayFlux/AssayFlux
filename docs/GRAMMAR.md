# AssayFlux Grammar
# AssayFlux Scientific Systems — Version 0.1.0
# Status: Proposed authoritative grammar
# Source extension: .af

(* ============================================================
   1. CORE LANGUAGE RULES
   ============================================================ *)

(* AssayFlux combines Python-inspired syntax with custom keywords.

   Strict formatting rules:
   - Every statement inside a block must be indented.
   - Indentation must use spaces, not tabs.
   - Four spaces represent one indentation level.
   - Nested blocks require additional indentation.
   - Every block must also be closed by the keyword "end".
   - "end" must align with the statement that opened the block.
   - "else" and "otherwise" must align with their matching "if".
   - Blank lines do not affect indentation.
   - Comments do not create blocks.
*)

program =
    { newline | comment },
    [ app_declaration, newline ],
    { statement | newline | comment } ;

app_declaration =
    "app", string_literal ;

(* ============================================================
   2. LEXICAL RULES
   ============================================================ *)

identifier =
    identifier_start, { identifier_continue } ;

identifier_start =
    letter | "_" ;

identifier_continue =
    letter | digit | "_" ;

letter =
    "A"…"Z" | "a"…"z" ;

digit =
    "0"…"9" ;

integer_literal =
    digit, { digit } ;

float_literal =
    digit, { digit }, ".", digit, { digit } ;

boolean_literal =
    "true" | "false" ;

string_literal =
      single_quoted_string
    | double_quoted_string ;

single_quoted_string =
    "'", { single_string_character }, "'" ;

double_quoted_string =
    '"', { double_string_character }, '"' ;

(* Supported escape sequences:
   \\  backslash
   \'  single quote
   \"  double quote
   \n  newline
   \t  tab
   \r  carriage return
*)

comment =
    "#", { any_character_except_newline } ;

newline =
    line_ending ;

(* The lexer must emit indentation information.
   Tabs are rejected in indentation.
   Each indentation level is four spaces.
   Indentation changes must be consistent.
*)

(* ============================================================
   3. RESERVED KEYWORDS
   ============================================================ *)

(* Reserved words:
   app, const, return, end, if, otherwise, else, repeat,
   stop, skip, show, true, false, and, or, not, import, as.
*)

(* The prefix "f." is reserved for function declarations.
   The operator "nt=" is invalid.
   The operator "!=" means not equal.
*)

(* ============================================================
   4. STATEMENTS
   ============================================================ *)

statement =
      assignment
    | constant_declaration
    | show_statement
    | if_statement
    | repeat_statement
    | function_declaration
    | return_statement
    | stop_statement
    | skip_statement
    | import_statement
    | expression_statement ;

assignment =
    identifier, "=", expression ;

constant_declaration =
    "const", identifier, "=", expression ;

show_statement =
    "show", expression ;

return_statement =
    "return", [ expression ] ;

stop_statement =
    "stop" ;

skip_statement =
    "skip" ;

expression_statement =
    expression ;

(* ============================================================
   5. STRICT BLOCK FORMATTING
   ============================================================ *)

(* Each block-opening statement establishes a required
   indentation level for its body.

   The block body must be indented exactly one level deeper
   than its opening statement.

   Nested blocks increase indentation by another level.

   The closing "end" must align with its opening statement.

   Empty blocks are permitted only if explicitly supported
   by the implementation. Otherwise, they are syntax errors.
*)

statement_block =
    indented_statement, { indented_statement } ;

indented_statement =
    indentation, statement, newline ;

(* "indentation" is a lexical property and must be validated
   by the lexer/parser. It is not ordinary expression syntax.
*)

(* ============================================================
   6. CONDITIONAL STATEMENTS
   ============================================================ *)

if_statement =
    "if", expression, newline,
    statement_block,
    { otherwise_clause },
    [ else_clause ],
    indentation, "end" ;

otherwise_clause =
    indentation, "otherwise", expression, newline,
    statement_block ;

else_clause =
    indentation, "else", newline,
    statement_block ;

(* Rules:
   - "otherwise" introduces another condition.
   - Multiple "otherwise" clauses are permitted.
   - "else" is optional and must appear last.
   - "otherwise" and "else" align with their matching "if".
   - "end" aligns with the opening "if".
*)

(* ============================================================
   7. LOOPS
   ============================================================ *)

repeat_statement =
    "repeat", [ expression ], newline,
    statement_block,
    indentation, "end" ;

(* A conditional repeat loop runs while its condition is true.
   A repeat statement without a condition runs indefinitely.
*)

(* "stop" exits the innermost active loop.
   "skip" begins the next iteration of the innermost loop.
   Both are invalid outside a loop.
*)

(* ============================================================
   8. FUNCTIONS
   ============================================================ *)

function_declaration =
    "f.", identifier,
    "(", [ parameter_list ], ")",
    newline,
    statement_block,
    indentation, "end" ;

parameter_list =
    identifier, { ",", identifier } ;

function_call =
    identifier, "(", [ argument_list ], ")" ;

argument_list =
    expression, { ",", expression } ;

(* Function declarations require "f.".
   Function calls do not use "f.".
   "return" is valid only inside a function.
*)

(* ============================================================
   9. IMPORTS
   ============================================================ *)

import_statement =
    "import", module_path, [ "as", identifier ] ;

module_path =
    identifier, { ".", identifier } ;

module_member_access =
    identifier, { ".", identifier } ;

(* Intended Python integration example:
   import math
   result = math.sqrt(25)
   show result

   Runtime integration must be implemented and tested separately.
*)

(* ============================================================
   10. EXPRESSIONS
   ============================================================ *)

expression =
    logical_or_expression ;

logical_or_expression =
    logical_and_expression,
    { "or", logical_and_expression } ;

logical_and_expression =
    logical_not_expression,
    { "and", logical_not_expression } ;

logical_not_expression =
      "not", logical_not_expression
    | comparison_expression ;

comparison_expression =
    additive_expression,
    [ comparison_operator, additive_expression ] ;

comparison_operator =
      "=="
    | "!="
    | "<"
    | ">"
    | "<="
    | ">=" ;

additive_expression =
    multiplicative_expression,
    { ("+" | "-"), multiplicative_expression } ;

multiplicative_expression =
    unary_expression,
    { ("*" | "/" | "%"), unary_expression } ;

unary_expression =
      ("+" | "-"), unary_expression
    | primary_expression ;

primary_expression =
      literal
    | identifier
    | function_call
    | module_member_access
    | "(", expression, ")" ;

literal =
      integer_literal
    | float_literal
    | string_literal
    | boolean_literal ;

(* Precedence, highest to lowest:
   1. Parentheses and primary expressions
   2. Unary + and -
   3. *, /, %
   4. +, -
   5. Comparisons
   6. not
   7. and
   8. or
*)

(* ============================================================
   11. EXAMPLE PROGRAM
   ============================================================ *)

(* Valid AssayFlux example:

   app "Example"

   const LIMIT = 5
   count = 0

   f.add(a, b)
       return a + b
   end

   repeat count < LIMIT
       if count != 3
           show add(count, 10)
       otherwise count == 3
           show "Skipping three"
       else
           show "Other value"
       end

       count = count + 1
   end
*)

(* ============================================================
   12. ERROR RULES
   ============================================================ *)

(* Syntax errors must be reported for:
   - Missing "end".
   - Unmatched "end".
   - Incorrect indentation.
   - Tabs used for indentation.
   - Inconsistent indentation levels.
   - "else" or "otherwise" at the wrong indentation.
   - Invalid operators.
   - Invalid identifiers.
   - Unexpected end of file inside a block.

   Errors should include a filename, line, column, and message
   whenever that information is available.
*)

(* ============================================================
   13. IMPLEMENTATION CONFORMANCE
   ============================================================ *)

(* This file defines the intended syntax.
   It does not itself implement the lexer, parser, or interpreter.

   The implementation must be updated to enforce these rules.
   Automated tests must cover valid and invalid formatting.

   The language must not claim strict indentation support
   until the implementation and tests verify it.
*)