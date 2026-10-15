"""
AssayFlux Scientific Systems
Parser Implementation

Converts lexer tokens into an Abstract Syntax Tree (AST).

Version: 0.1.0
"""

from typing import List

from assayflux.ast_nodes import (
    Assignment,
    BinaryOperation,
    BooleanLiteral,
    ConstantDeclaration,
    ConditionalBranch,
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


class ParserError(Exception):
    """Raised when tokens do not follow AssayFlux grammar."""

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
    ):
        self.message = message
        self.line = line
        self.column = column

        super().__init__(
            f"AssayFlux Parser Error at line {line}, "
            f"column {column}: {message}"
        )


class Parser:
    """Parses AssayFlux tokens into an AST."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

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
        """Check the current token's value."""

        return self.current().value == value

    def match_value(self, value: str) -> bool:
        """Consume a token if its value matches."""

        if self.check_value(value):
            self.advance()
            return True

        return False

    def expect_value(self, value: str) -> Token:
        """Require a token with a specific value."""

        if not self.check_value(value):
            token = self.current()

            raise ParserError(
                f"Expected {value!r}, found "
                f"{token.value!r}.",
                token.line,
                token.column,
            )

        return self.advance()

    def expect_type(
        self,
        token_type: str,
        description: str,
    ) -> Token:
        """Require a token of a particular type."""

        token = self.current()

        if token.type != token_type:
            raise ParserError(
                f"Expected {description}, found "
                f"{token.value!r}.",
                token.line,
                token.column,
            )

        return self.advance()

    def skip_newlines(self):
        """Skip newline separators."""

        while self.current().type == "NEWLINE":
            self.advance()

    def parse(self) -> Program:
        """Parse an entire AssayFlux program."""

        statements = []
        self.skip_newlines()

        while self.current().type != "EOF":
            if self.current().type in ("INDENT", "DEDENT"):
                token = self.current()

                raise ParserError(
                    "Unexpected indentation outside a block.",
                    token.line,
                    token.column,
                )

            if self.check_value("end"):
                token = self.current()

                raise ParserError(
                    "Unexpected 'end': no block is open.",
                    token.line,
                    token.column,
                )

            statements.append(self.parse_statement())
            self.finish_statement()
            self.skip_newlines()

        return Program(statements=statements)

    def finish_statement(self):
        """Require a statement to end at a line boundary."""

        token = self.current()

        if token.type in ("NEWLINE", "EOF", "DEDENT"):
            return

        raise ParserError(
            f"Unexpected token {token.value!r} "
            "after a statement.",
            token.line,
            token.column,
        )

    def parse_statement(self):
        """Parse one statement."""

        token = self.current()

        if token.type in ("EOF", "INDENT", "DEDENT"):
            raise ParserError(
                "Expected a statement.",
                token.line,
                token.column,
            )

        if token.type == "NEWLINE":
            self.advance()
            return self.parse_statement()

        if token.value == "show":
            return self.parse_show()

        if token.value == "if":
            return self.parse_if()

        if token.value == "repeat":
            return self.parse_repeat()

        if token.value == "stop":
            self.advance()
            return StopStatement(
                line=token.line,
                column=token.column,
            )

        if token.value == "skip":
            self.advance()
            return SkipStatement(
                line=token.line,
                column=token.column,
            )

        if token.value == "return":
            return self.parse_return()

        if token.value == "import":
            return self.parse_import()

        if token.value == "const":
            return self.parse_constant()

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

        raise ParserError(
            f"Unexpected token {token.value!r} at "
            "the beginning of a statement.",
            token.line,
            token.column,
        )

    def parse_show(self) -> ShowStatement:
        """Parse: show expression."""

        token = self.expect_value("show")
        value = self.parse_expression()

        return ShowStatement(
            line=token.line,
            column=token.column,
            value=value,
        )

    def parse_assignment(self) -> Assignment:
        """Parse: identifier = expression."""

        name_token = self.expect_type(
            "IDENTIFIER",
            "a variable name",
        )

        self.expect_value("=")
        value = self.parse_expression()

        return Assignment(
            line=name_token.line,
            column=name_token.column,
            name=name_token.value,
            value=value,
        )

    def parse_constant(self) -> ConstantDeclaration:
        """Parse: const identifier = expression."""

        token = self.expect_value("const")

        name_token = self.expect_type(
            "IDENTIFIER",
            "a constant name",
        )

        self.expect_value("=")
        value = self.parse_expression()

        return ConstantDeclaration(
            line=token.line,
            column=token.column,
            name=name_token.value,
            value=value,
        )

    def parse_return(self) -> ReturnStatement:
        """Parse a return statement."""

        token = self.expect_value("return")

        if self.current().type in (
            "NEWLINE",
            "EOF",
            "DEDENT",
        ):
            return ReturnStatement(
                line=token.line,
                column=token.column,
                value=None,
            )

        if self.check_value("end"):
            return ReturnStatement(
                line=token.line,
                column=token.column,
                value=None,
            )

        return ReturnStatement(
            line=token.line,
            column=token.column,
            value=self.parse_expression(),
        )

    def parse_function_definition(self) -> FunctionDefinition:
        """Parse: f.name(parameters) ... end."""

        start = self.expect_type(
            "IDENTIFIER",
            "the function prefix 'f'",
        )

        self.expect_value(".")
        name_token = self.expect_type(
            "IDENTIFIER",
            "a function name",
        )

        self.expect_value("(")

        parameters = []

        if not self.check_value(")"):
            while True:
                parameter = self.expect_type(
                    "IDENTIFIER",
                    "a parameter name",
                )
                parameters.append(parameter.value)

                if not self.match_value(","):
                    break

        self.expect_value(")")
        self.require_newline(
            "after a function declaration"
        )

        body = self.parse_block({"end"})
        self.expect_value("end")

        return FunctionDefinition(
            line=start.line,
            column=start.column,
            name=name_token.value,
            parameters=parameters,
            body=body,
        )

    def parse_if(self) -> IfStatement:
        """Parse if, otherwise, else, and end."""

        start = self.expect_value("if")
        condition = self.parse_expression()

        self.require_newline("after an if condition")

        body = self.parse_block(
            {"otherwise", "else", "end"}
        )

        otherwise_branches = []

        while self.match_value("otherwise"):
            branch_token = self.tokens[
                self.position - 1
            ]

            branch_condition = self.parse_expression()

            self.require_newline(
                "after an otherwise condition"
            )

            branch_body = self.parse_block(
                {"otherwise", "else", "end"}
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
            self.require_newline("after else")
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

    def parse_repeat(self) -> RepeatStatement:
        """Parse: repeat [condition] ... end."""

        start = self.expect_value("repeat")

        if self.current().type in (
            "NEWLINE",
            "EOF",
        ):
            count = None
        else:
            count = self.parse_expression()

        self.require_newline("after repeat")

        body = self.parse_block({"end"})
        self.expect_value("end")

        return RepeatStatement(
            line=start.line,
            column=start.column,
            count=count,
            body=body,
        )

    def parse_import(self) -> ImportStatement:
        """Parse: import module or import module as alias."""

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

    def parse_block(self, terminators: set):
        """Parse an indented block until a terminator."""

        statements = []
        self.skip_newlines()

        self.expect_type(
            "INDENT",
            "an indented block using four spaces",
        )

        self.skip_newlines()

        while self.current().type != "EOF":
            token = self.current()

            if token.type == "DEDENT":
                self.advance()
                break

            if token.value in terminators:
                raise ParserError(
                    "A block terminator must appear "
                    "after the block's indentation has closed.",
                    token.line,
                    token.column,
                )

            if token.type == "INDENT":
                raise ParserError(
                    "Unexpected nested indentation. "
                    "A nested block must start with "
                    "a valid block-opening statement.",
                    token.line,
                    token.column,
                )

            statements.append(self.parse_statement())
            self.finish_statement()
            self.skip_newlines()

        else:
            token = self.current()

            raise ParserError(
                "Unexpected end of file while parsing "
                "an indented block.",
                token.line,
                token.column,
            )

        if not statements:
            token = self.current()

            raise ParserError(
                "Empty blocks are not allowed.",
                token.line,
                token.column,
            )

        return statements

    def require_newline(self, context: str):
        """Require a newline after a block header."""

        if self.current().type == "NEWLINE":
            self.skip_newlines()
            return

        token = self.current()

        raise ParserError(
            f"Expected a newline {context}.",
            token.line,
            token.column,
        )

    # --------------------------------------------------------
    # Expressions
    # --------------------------------------------------------

    def parse_expression(self):
        """Parse an expression."""

        return self.parse_or()

    def parse_or(self):
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

    def parse_and(self):
        """Parse logical AND expressions."""

        expression = self.parse_comparison()

        while self.match_value("and"):
            operator = self.tokens[self.position - 1]
            right = self.parse_comparison()

            expression = BinaryOperation(
                line=operator.line,
                column=operator.column,
                left=expression,
                operator="and",
                right=right,
            )

        return expression

    def parse_comparison(self):
        """Parse comparison expressions."""

        expression = self.parse_additive()

        comparison_operators = {
            "==",
            "!=",
            ">",
            "<",
            ">=",
            "<=",
        }

        while (
            self.current().type == "OPERATOR"
            and self.current().value in comparison_operators
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

    def parse_additive(self):
        """Parse addition and subtraction."""

        expression = self.parse_multiplicative()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in ("+", "-")
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

    def parse_multiplicative(self):
        """Parse multiplication, division, and remainder."""

        expression = self.parse_unary()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in ("*", "/", "%")
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

    def parse_unary(self):
        """Parse unary operators."""

        if (
            self.current().value in ("-", "+", "not")
            and self.current().type in (
                "OPERATOR",
                "KEYWORD",
            )
        ):
            operator = self.advance()
            operand = self.parse_unary()

            return UnaryOperation(
                line=operator.line,
                column=operator.column,
                operator=operator.value,
                operand=operand,
            )

        return self.parse_primary()

    def parse_primary(self):
        """Parse literals, identifiers, calls, and parentheses."""

        token = self.current()

        if token.type == "NUMBER":
            self.advance()

            if "." in token.value:
                value = float(token.value)
            else:
                value = int(token.value)

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

            expression = Identifier(
                line=token.line,
                column=token.column,
                name=token.value,
            )

            while True:
                if self.match_value("("):
                    arguments = []

                    if not self.check_value(")"):
                        while True:
                            arguments.append(
                                self.parse_expression()
                            )

                            if not self.match_value(","):
                                break

                    self.expect_value(")")

                    if not isinstance(expression, Identifier):
                        raise ParserError(
                            "Only named functions are "
                            "supported in this initial parser.",
                            token.line,
                            token.column,
                        )

                    expression = FunctionCall(
                        line=token.line,
                        column=token.column,
                        name=expression.name,
                        arguments=arguments,
                    )

                    continue

                if self.match_value("."):
                    member = self.expect_type(
                        "IDENTIFIER",
                        "a member name",
                    )

                    expression = MemberAccess(
                        line=token.line,
                        column=token.column,
                        object=expression,
                        member=member.value,
                    )

                    continue

                break

            return expression

        if self.match_value("("):
            expression = self.parse_expression()
            self.expect_value(")")
            return expression

        raise ParserError(
            f"Expected an expression, found "
            f"{token.value!r}.",
            token.line,
            token.column,
        )


def parse(source: str) -> Program:
    """Tokenize and parse AssayFlux source code."""

    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


__all__ = [
    "Parser",
    "ParserError",
    "parse",
    "LexerError",
]


if __name__ == "__main__":
    example = (
        "x = 10\n"
        "y = 20\n"
        "result = x + y\n"
        "show result\n"
    )

    try:
        program = parse(example)
        print(program)

    except (LexerError, ParserError) as error:
        print(error)