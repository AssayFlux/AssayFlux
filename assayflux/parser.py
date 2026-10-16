"""
AssayFlux Scientific Systems
Parser Implementation

Converts lexer tokens into an Abstract Syntax Tree (AST).

Canonical core syntax:
    show expression
    constant NAME = expression

    if condition:
        statements
    otherwise condition:
        statements
    else:
        statements
    end

    f.function_name(parameters):
        statements
    end

    repeat count:
        statements
    end

    repeat while condition:
        statements
    end

    repeat forever:
        statements
    end

    stop
    skip
    return expression

The parser preserves the existing AST node interfaces.
It does not execute programs.

Version: 1.0.0
"""

from __future__ import annotations

import ast as python_ast
from typing import List, Optional, Set

from assayflux.ast_nodes import (
    Assignment,
    AppDeclaration,
    BinaryOperation,
    BooleanLiteral,
    ConditionalBranch,
    ConstantDeclaration,
    Expression,
    ExpressionStatement,
    FunctionCall,
    FunctionDefinition,
    Identifier,
    IfStatement,
    ImportStatement,
    MemberAccess,
    NumberLiteral,
    Program,
    RepeatStatement,
    ReturnStatement,
    ShowStatement,
    SkipStatement,
    StopStatement,
    StringLiteral,
    UnaryOperation,
)
from assayflux.lexer import Lexer, LexerError, Token


PARSER_VERSION = "1.0.0"


__all__ = [
    "Parser",
    "ParserError",
    "parse",
    "LexerError",
    "PARSER_VERSION",
]


# ============================================================
# Parser Errors
# ============================================================


class ParserError(Exception):
    """
    Raised when tokens do not follow the AssayFlux grammar.

    Line and column numbers are one-based.
    """

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
        filename: str = "<string>",
    ):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename

        super().__init__(
            f"[{filename}:{line}:{column}] "
            f"AssayFlux Parser Error: {message}"
        )


# ============================================================
# Parser
# ============================================================


class Parser:
    """
    Parse AssayFlux tokens into AST nodes.

    The public constructor remains compatible with the existing
    Parser(tokens) API.
    """

    COMPARISON_OPERATORS = {
        "==",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
    }

    ADDITIVE_OPERATORS = {
        "+",
        "-",
    }

    MULTIPLICATIVE_OPERATORS = {
        "*",
        "/",
        "//",
        "%",
    }

    def __init__(self, tokens: List[Token]):
        if not isinstance(tokens, (list, tuple)):
            raise TypeError(
                "Parser expects a list or tuple of Token objects."
            )

        self.tokens = list(tokens)
        self.position = 0

        # Context tracking prevents control-flow statements from
        # appearing outside their valid enclosing constructs.
        self.function_depth = 0
        self.loop_depth = 0

        if not self.tokens:
            raise ValueError(
                "Parser received an empty token sequence."
            )

        for token in self.tokens:
            if not isinstance(token, Token):
                raise TypeError(
                    "Every parser input item must be a Token."
                )

        if self.tokens[-1].type != "EOF":
            last = self.tokens[-1]

            self.tokens.append(
                Token(
                    type="EOF",
                    value="EOF",
                    line=last.line,
                    column=last.column,
                    start=last.end,
                    end=last.end,
                    filename=last.filename,
                    lexeme="",
                )
            )

    # --------------------------------------------------------
    # Token navigation
    # --------------------------------------------------------

    def current(self) -> Token:
        """Return the current token."""
        return self.tokens[self.position]

    def peek(self, offset: int = 1) -> Token:
        """Look ahead without consuming a token."""
        index = min(
            self.position + offset,
            len(self.tokens) - 1,
        )

        return self.tokens[index]

    def advance(self) -> Token:
        """Consume and return the current token."""
        token = self.current()

        if token.type != "EOF":
            self.position += 1

        return token

    def check_value(self, value: str) -> bool:
        """Check the current token value."""
        return self.current().value == value

    def check_type(self, token_type: str) -> bool:
        """Check the current token type."""
        return self.current().type == token_type

    def match_value(self, value: str) -> bool:
        """Consume a token when its value matches."""
        if self.check_value(value):
            self.advance()
            return True

        return False

    def match_type(self, token_type: str) -> Optional[Token]:
        """Consume a token when its type matches."""
        if self.check_type(token_type):
            return self.advance()

        return None

    def _error(
        self,
        message: str,
        token: Optional[Token] = None,
    ) -> None:
        """Raise a location-aware parser error."""
        token = token or self.current()

        raise ParserError(
            message,
            token.line,
            token.column,
            getattr(token, "filename", "<string>"),
        )

    def expect_value(self, value: str) -> Token:
        """Require a particular token value."""
        token = self.current()

        if token.value != value:
            self._error(
                f"Expected {value!r}, found {token.value!r}.",
                token,
            )

        return self.advance()

    def expect_type(
        self,
        token_type: str,
        description: str,
    ) -> Token:
        """Require a particular token type."""
        token = self.current()

        if token.type != token_type:
            self._error(
                f"Expected {description}, "
                f"found {token.value!r}.",
                token,
            )

        return self.advance()

    def skip_newlines(self) -> None:
        """Consume consecutive newline tokens."""
        while self.check_type("NEWLINE"):
            self.advance()

    # --------------------------------------------------------
    # Program entry point
    # --------------------------------------------------------

    def parse(self) -> Program:
        """Parse a complete AssayFlux program."""
        statements = []

        self.skip_newlines()

        while not self.check_type("EOF"):
            token = self.current()

            if token.type in {"INDENT", "DEDENT"}:
                self._error(
                    "Unexpected indentation outside a compound block.",
                    token,
                )

            if token.value == "end":
                self._error(
                    "Unexpected 'end': no compound block is open.",
                    token,
                )

            if token.value in {"otherwise", "else"}:
                self._error(
                    f"Unexpected {token.value!r}: "
                    "it must belong to an open 'if' statement.",
                    token,
                )

            statement = self.parse_statement()
            statements.append(statement)

            self.finish_statement()
            self.skip_newlines()

        return Program(statements=statements)

    # --------------------------------------------------------
    # Statement boundaries
    # --------------------------------------------------------

    def finish_statement(self) -> None:
        """
        Ensure that a statement ends at a legal boundary.

        NEWLINE separates statements.
        DEDENT closes the current indentation scope.
        EOF ends the source file.
        """
        token = self.current()

        if token.type in {"NEWLINE", "DEDENT", "EOF"}:
            return

        self._error(
            f"Unexpected token {token.value!r} after a statement. "
            "Check the expression or remove trailing syntax.",
            token,
        )

    def require_newline(self, context: str) -> None:
        """Require a newline after a compound statement header."""
        token = self.current()

        if token.type != "NEWLINE":
            self._error(
                f"Expected a newline {context}; "
                f"found {token.value!r}.",
                token,
            )

        self.skip_newlines()

    # --------------------------------------------------------
    # Statement dispatch
    # --------------------------------------------------------

    def parse_statement(self):
        """Parse one supported statement."""
        token = self.current()

        if token.type in {"EOF", "INDENT", "DEDENT"}:
            self._error(
                "Expected a statement.",
                token,
            )

        if token.type == "NEWLINE":
            self.advance()
            return self.parse_statement()

        if token.value == "show":
            return self.parse_show()

        if token.value == "app":
            return self.parse_app()

        if token.value == "if":
            return self.parse_if()

        if token.value == "repeat":
            return self.parse_repeat()

        if token.value == "stop":
            return self.parse_stop()

        if token.value == "skip":
            return self.parse_skip()

        if token.value == "return":
            return self.parse_return()

        if token.value == "import":
            return self.parse_import()

        if token.value == "constant":
            return self.parse_constant()

        if token.value == "pass":
            self._error(
                "'pass' is not implemented in the current AST. "
                "Empty blocks are therefore not allowed.",
                token,
            )

        if token.value in {"for", "while"}:
            self._error(
                f"{token.value!r} statements are not implemented "
                "as standalone constructs in the current AST. "
                "Use the documented 'repeat' forms where applicable.",
                token,
            )

        if (
            token.type == "IDENTIFIER"
            and token.value == "f"
            and self.peek().value == "."
        ):
            return self.parse_function_definition()

        if (
            token.type == "IDENTIFIER"
            and self.peek().value == "="
        ):
            return self.parse_assignment()

        expression = self.parse_expression()

        return ExpressionStatement(
            line=token.line,
            column=token.column,
            expression=expression,
        )

    # --------------------------------------------------------
    # Simple statements
    # --------------------------------------------------------

    def parse_app(self) -> AppDeclaration:
        """Parse application metadata: app "Name"."""
        start = self.expect_value("app")

        name = self.expect_type(
            "STRING",
            "an application name string",
        )

        return AppDeclaration(
            line=start.line,
            column=start.column,
            name=name.value,
        )

    def parse_show(self) -> ShowStatement:
        """Parse: show expression."""
        start = self.expect_value("show")

        if self.current().type in {
            "NEWLINE",
            "DEDENT",
            "EOF",
        }:
            self._error(
                "'show' requires an expression.",
                start,
            )

        value = self.parse_expression()

        return ShowStatement(
            line=start.line,
            column=start.column,
            value=value,
        )

    def parse_assignment(self) -> Assignment:
        """Parse: identifier = expression."""
        name_token = self.expect_type(
            "IDENTIFIER",
            "a variable name",
        )

        self.expect_value("=")

        if self.check_value("="):
            self._error(
                "Expected an assignment operator '='; "
                "found an equality operator.",
            )

        value = self.parse_expression()

        return Assignment(
            line=name_token.line,
            column=name_token.column,
            name=name_token.value,
            value=value,
        )

    def parse_constant(self) -> ConstantDeclaration:
        """Parse: constant NAME = expression."""
        start = self.expect_value("constant")

        name_token = self.expect_type(
            "IDENTIFIER",
            "a constant name",
        )

        self.expect_value("=")

        if self.check_value("="):
            self._error(
                "A constant declaration requires a single '='.",
            )

        value = self.parse_expression()

        return ConstantDeclaration(
            line=start.line,
            column=start.column,
            name=name_token.value,
            value=value,
        )

    def parse_return(self) -> ReturnStatement:
        """Parse return, optionally followed by an expression."""
        start = self.expect_value("return")

        if self.function_depth == 0:
            self._error(
                "'return' can only appear inside a function.",
                start,
            )

        if self.current().type in {
            "NEWLINE",
            "DEDENT",
            "EOF",
        }:
            return ReturnStatement(
                line=start.line,
                column=start.column,
                value=None,
            )

        if self.current().value == "end":
            return ReturnStatement(
                line=start.line,
                column=start.column,
                value=None,
            )

        value = self.parse_expression()

        return ReturnStatement(
            line=start.line,
            column=start.column,
            value=value,
        )

    def parse_stop(self) -> StopStatement:
        """Parse stop inside a repeat loop."""
        start = self.expect_value("stop")

        if self.loop_depth == 0:
            self._error(
                "'stop' can only appear inside a repeat loop.",
                start,
            )

        return StopStatement(
            line=start.line,
            column=start.column,
        )

    def parse_skip(self) -> SkipStatement:
        """Parse skip inside a repeat loop."""
        start = self.expect_value("skip")

        if self.loop_depth == 0:
            self._error(
                "'skip' can only appear inside a repeat loop.",
                start,
            )

        return SkipStatement(
            line=start.line,
            column=start.column,
        )

    # --------------------------------------------------------
    # Imports
    # --------------------------------------------------------

    def parse_import(self) -> ImportStatement:
        """
        Parse:
            import math
            import package.module
            import math as mathematics
        """
        start = self.expect_value("import")

        module_token = self.expect_type(
            "IDENTIFIER",
            "a module name",
        )

        module_parts = [module_token.value]

        while self.match_value("."):
            part = self.expect_type(
                "IDENTIFIER",
                "a module name component",
            )

            module_parts.append(part.value)

        alias = None

        if self.match_value("as"):
            alias_token = self.expect_type(
                "IDENTIFIER",
                "an import alias",
            )

            alias = alias_token.value

        return ImportStatement(
            line=start.line,
            column=start.column,
            module_name=".".join(module_parts),
            alias=alias,
        )

    # --------------------------------------------------------
    # Function declarations
    # --------------------------------------------------------

    def parse_function_definition(self) -> FunctionDefinition:
        """
        Parse:

            f.add(a, b):
                return a + b
            end
        """
        start = self.expect_type(
            "IDENTIFIER",
            "the function prefix 'f'",
        )

        if start.value != "f":
            self._error(
                "A function declaration must start with 'f.'.",
                start,
            )

        self.expect_value(".")

        name_token = self.expect_type(
            "IDENTIFIER",
            "a function name",
        )

        self.expect_value("(")

        parameters = []
        seen_parameters = set()

        if not self.check_value(")"):
            while True:
                parameter = self.expect_type(
                    "IDENTIFIER",
                    "a parameter name",
                )

                if parameter.value in seen_parameters:
                    self._error(
                        f"Duplicate function parameter "
                        f"{parameter.value!r}.",
                        parameter,
                    )

                seen_parameters.add(parameter.value)
                parameters.append(parameter.value)

                if not self.match_value(","):
                    break

                # Permit a trailing comma in a parameter list.
                if self.check_value(")"):
                    break

        self.expect_value(")")
        self.expect_value(":")

        self.require_newline(
            "after a function declaration header",
        )

        previous_loop_depth = self.loop_depth
        self.loop_depth = 0
        self.function_depth += 1

        try:
            body = self.parse_block({"end"})
            self.expect_value("end")
        finally:
            self.function_depth -= 1
            self.loop_depth = previous_loop_depth

        return FunctionDefinition(
            line=start.line,
            column=start.column,
            name=name_token.value,
            parameters=parameters,
            body=body,
        )

    # --------------------------------------------------------
    # Conditional statements
    # --------------------------------------------------------

    def parse_if(self) -> IfStatement:
        """
        Parse if / otherwise / else / end.

        Example:

            if score >= 90:
                show "Excellent"
            otherwise score >= 70:
                show "Good"
            else:
                show "Keep practising"
            end
        """
        start = self.expect_value("if")

        condition = self.parse_expression()
        self.expect_value(":")

        self.require_newline(
            "after an if condition",
        )

        body = self.parse_block(
            {"otherwise", "else", "end"},
        )

        otherwise_branches = []

        while self.match_value("otherwise"):
            branch_token = self.tokens[self.position - 1]

            branch_condition = self.parse_expression()
            self.expect_value(":")

            self.require_newline(
                "after an otherwise condition",
            )

            branch_body = self.parse_block(
                {"otherwise", "else", "end"},
            )

            otherwise_branches.append(
                ConditionalBranch(
                    line=branch_token.line,
                    column=branch_token.column,
                    condition=branch_condition,
                    statements=branch_body,
                )
            )

        else_body = None

   
        if self.match_value("else"):
            self.expect_value(":")

            self.require_newline(
                "after an else header",
            )

            else_body = self.parse_block({"end"})

        self.expect_value("end")

        return IfStatement(
            line=start.line,
            column=start.column,
            condition=condition,
            body=body,
            otherwise_branches=otherwise_branches,
            else_body=else_body,
        )

    # --------------------------------------------------------
    # Repeat statements
    # --------------------------------------------------------

    def parse_repeat(self) -> RepeatStatement:
        """
        Parse documented repeat forms:

            repeat 5:
                show "Repeated"
            end

            repeat count 5:
                show "Repeated"
            end

            repeat while counter < 5:
                counter = counter + 1
            end

            repeat forever:
                stop
            end

        A legacy condition form is also recognized:

            repeat counter < 5:
                counter = counter + 1
            end
        """
        start = self.expect_value("repeat")

        mode = "condition"
        condition = None
        count = None

        if self.match_value("forever"):
            mode = "forever"

        elif self.match_value("while"):
            mode = "condition"
            condition = self.parse_expression()

        elif self.match_value("count"):
            mode = "count"
            count = self.parse_expression()
            self._validate_repeat_count(count, start)

        else:
            if self.current().value == ":":
                self._error(
                    "A repeat header requires a count, condition, "
                    "'while' condition, 'count' expression, "
                    "or 'forever'.",
                    start,
                )

            expression = self.parse_expression()

            if isinstance(expression, NumberLiteral):
                mode = "count"
                count = expression
                self._validate_repeat_count(count, start)
            else:
                mode = "condition"
                condition = expression

        self.expect_value(":")

        self.require_newline(
            "after a repeat header",
        )

        self.loop_depth += 1

        try:
            body = self.parse_block({"end"})
            self.expect_value("end")
        finally:
            self.loop_depth -= 1

        return RepeatStatement(
            line=start.line,
            column=start.column,
            condition=condition,
            body=body,
            mode=mode,
            count=count,
        )

    def _validate_repeat_count(
        self,
        expression: Expression,
        start: Token,
    ) -> None:
        """
        Validate literal repeat counts.

        Dynamic count expressions are accepted because their
        values are determined at runtime.
        """
        if not isinstance(expression, NumberLiteral):
            return

        value = expression.value

        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
        ):
            self._error(
                "A repeat count must be a non-negative integer.",
                start,
            )
    # --------------------------------------------------------
    # Indented blocks
    # --------------------------------------------------------

    def parse_block(self, terminators: Set[str]):
        """
        Parse a non-empty indented block.

        The lexer must emit:
            NEWLINE
            INDENT
            statements
            DEDENT

        The caller consumes the explicit 'end' token.
        """
        statements = []

        self.skip_newlines()

        self.expect_type(
            "INDENT",
            "an indented block",
        )

        self.skip_newlines()

        while not self.check_type("EOF"):
            token = self.current()

            if token.type == "DEDENT":
                self.advance()
                break

            if token.value in terminators:
                self._error(
                    "The block's indentation has not closed "
                    "before its terminator. Check the indentation "
                    "of this statement.",
                    token,
                )

            if token.value == "end":
                self._error(
                    "Unexpected 'end' while parsing this block.",
                    token,
                )

            if token.type == "INDENT":
                self._error(
                    "Unexpected indentation. Nested blocks must "
                    "begin with a valid compound statement.",
                    token,
                )

            if token.value in {"otherwise", "else"}:
                self._error(
                    f"Unexpected {token.value!r} in this block.",
                    token,
                )

            statement = self.parse_statement()
            statements.append(statement)

            self.finish_statement()
            self.skip_newlines()

        else:
            token = self.current()

            self._error(
                "Unexpected end of file inside an indented block. "
                "A matching 'end' may be missing.",
                token,
            )

        if not statements:
            token = self.current()

            self._error(
                "Empty blocks are not allowed. Add a valid "
                "statement to this block.",
                token,
            )

        return statements

    # --------------------------------------------------------
    # Expression grammar
    #
    # Lowest to highest precedence:
    #     or
    #     and
    #     comparisons
    #     addition / subtraction
    #     multiplication / division / remainder
    #     unary operators
    #     exponentiation
    #     function calls / member access
    #     literals / identifiers / parenthesized expressions
    # --------------------------------------------------------

    def parse_expression(self) -> Expression:
        """Parse a complete expression."""
        return self.parse_or()

    def parse_or(self) -> Expression:
        """Parse logical OR expressions."""
        expression = self.parse_and()

        while self.match_value("or"):
            operator = self.tokens[self.position - 1]
            right = self.parse_and()

            expression = BinaryOperation(
                line=operator.line,
                column=operator.column,
                left=expression,
                operator="or",
                right=right,
            )

        return expression

    def parse_and(self) -> Expression:
        """Parse logical AND expressions."""
        expression = self.parse_not()

        while self.match_value("and"):
            operator = self.tokens[self.position - 1]
            right = self.parse_not()

            expression = BinaryOperation(
                line=operator.line,
                column=operator.column,
                left=expression,
                operator="and",
                right=right,
            )

        return expression

    def parse_not(self) -> Expression:
        """Parse logical negation."""
        if self.check_value("not"):
            operator = self.advance()
            operand = self.parse_not()

            return UnaryOperation(
                line=operator.line,
                column=operator.column,
                operator="not",
                operand=operand,
            )

        return self.parse_comparison()

    def parse_comparison(self) -> Expression:
        """Parse comparison operators."""
        expression = self.parse_additive()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in self.COMPARISON_OPERATORS
        ):
            operator = self.advance()
            right = self.parse_additive()

            expression = BinaryOperation(
                line=operator.line,
                column=operator.column,
                left=expression,
                operator=operator.value,
                right=right,
            )

        return expression

    def parse_additive(self) -> Expression:
        """Parse addition and subtraction."""
        expression = self.parse_multiplicative()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in self.ADDITIVE_OPERATORS
        ):
            operator = self.advance()
            right = self.parse_multiplicative()

            expression = BinaryOperation(
                line=operator.line,
                column=operator.column,
                left=expression,
                operator=operator.value,
                right=right,
            )

        return expression

    def parse_multiplicative(self) -> Expression:
        """Parse multiplication, division, floor division, and modulo."""
        expression = self.parse_unary()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in self.MULTIPLICATIVE_OPERATORS
        ):
            operator = self.advance()
            right = self.parse_unary()

            expression = BinaryOperation(
                line=operator.line,
                column=operator.column,
                left=expression,
                operator=operator.value,
                right=right,
            )

        return expression

    def parse_unary(self) -> Expression:
        """
        Parse unary plus and minus.

        Exponentiation is parsed separately so that expressions
        such as -2 ** 2 follow conventional Python precedence.
        """
        if (
            self.current().type == "OPERATOR"
            and self.current().value in {"+", "-"}
        ):
            operator = self.advance()
            operand = self.parse_unary()

            return UnaryOperation(
                line=operator.line,
                column=operator.column,
                operator=operator.value,
                operand=operand,
            )

        return self.parse_power()

    def parse_power(self) -> Expression:
        """Parse right-associative exponentiation."""
        expression = self.parse_postfix()

        if self.match_value("**"):
            operator = self.tokens[self.position - 1]
            right = self.parse_unary()

            expression = BinaryOperation(
                line=operator.line,
                column=operator.column,
                left=expression,
                operator="**",
                right=right,
            )

        return expression
    # --------------------------------------------------------
    # Postfix operations
    # --------------------------------------------------------

    def parse_postfix(self) -> Expression:
        """
        Parse primary expressions followed by member access
        and function calls.

        Supported examples:
            value
            math.sqrt
            math.sqrt(49)
            add(2, 3)
            outer(inner(4))
        """
        expression = self.parse_primary()

        while True:
            if self.match_value("."):
                member = self.expect_type(
                    "IDENTIFIER",
                    "a member name",
                )

                expression = MemberAccess(
                    line=member.line,
                    column=member.column,
                    object=expression,
                    member=member.value,
                )

                continue

            if self.match_value("("):
                arguments = []

                if not self.check_value(")"):
                    while True:
                        arguments.append(
                            self.parse_expression()
                        )

                        if not self.match_value(","):
                            break

                        # Permit a trailing comma.
                        if self.check_value(")"):
                            break

                self.expect_value(")")

                function_name = self._function_name(expression)

                expression = FunctionCall(
                    line=expression.line,
                    column=expression.column,
                    name=function_name,
                    arguments=arguments,
                )

                continue

            break

        return expression

    def _function_name(self, expression: Expression) -> str:
        """
        Convert supported call targets to the existing FunctionCall
        AST representation.

        The current AST stores function names as dotted strings,
        not as arbitrary callable expressions.
        """
        if isinstance(expression, Identifier):
            return expression.name

        if isinstance(expression, MemberAccess):
            parts = []
            current = expression

            while isinstance(current, MemberAccess):
                parts.insert(0, current.member)
                current = current.object

            if isinstance(current, Identifier):
                parts.insert(0, current.name)
                return ".".join(parts)

        self._error(
            "Unsupported function call target. "
            "Calls must target a function name or dotted member path."
        )

    # --------------------------------------------------------
    # Primary expressions
    # --------------------------------------------------------

    def parse_primary(self) -> Expression:
        """Parse a literal, identifier, or parenthesized expression."""
        token = self.current()

        if token.type == "NUMBER":
            self.advance()

            try:
                value = python_ast.literal_eval(token.value)
            except (ValueError, SyntaxError, TypeError, MemoryError):
                self._error(
                    f"Invalid numeric literal {token.value!r}.",
                    token,
                )

            if type(value) not in {int, float, complex}:
                self._error(
                    f"Unsupported numeric literal {token.value!r}.",
                    token,
                )

            return NumberLiteral(
                line=token.line,
                column=token.column,
                value=value,
            )

        if token.type == "STRING":
            self.advance()

            return StringLiteral(
                line=token.line,
                column=token.column,
                value=token.value,
            )

        if token.value == "true":
            self.advance()

            return BooleanLiteral(
                line=token.line,
                column=token.column,
                value=True,
            )

        if token.value == "false":
            self.advance()

            return BooleanLiteral(
                line=token.line,
                column=token.column,
                value=False,
            )

        if token.type == "IDENTIFIER":
            self.advance()

            return Identifier(
                line=token.line,
                column=token.column,
                name=token.value,
            )

        if token.value == "(":
            self.advance()

            expression = self.parse_expression()

            self.expect_value(")")

            return expression

        if token.type == "FSTRING":
            self._error(
                "Formatted strings are not implemented by the "
                "current AST and parser.",
                token,
            )

        if token.type == "BYTES":
            self._error(
                "Bytes literals are not implemented by the "
                "current AST and parser.",
                token,
            )

        self._error(
            f"Expected an expression, found {token.value!r}.",
            token,
        )

# ============================================================
# Public API
# ============================================================


def parse(source: str) -> Program:
    """
    Tokenize and parse AssayFlux source code.

    Example:
        program = parse('show "Hello"')
    """
    if not isinstance(source, str):
        raise TypeError(
            "parse(source) expects source code as a string."
        )

    tokens = Lexer(source).tokenize()

    return Parser(tokens).parse()


# ============================================================
# Command-line smoke test
# ============================================================


if __name__ == "__main__":
    example = (
        "constant BASE = 10\n"
        "f.add(a, b):\n"
        "    return a + b\n"
        "end\n"
        "result = add(BASE, 20)\n"
        "if result > 25:\n"
        "    show result\n"
        "otherwise result == 25:\n"
        "    show \"Exactly 25\"\n"
        "else:\n"
        "    show \"Below 25\"\n"
        "end\n"
    )

    try:
        program = parse(example)
        print(program)

    except (LexerError, ParserError) as error:
        print(error)