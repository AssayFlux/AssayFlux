class SemanticError(Exception):
    """Custom exception for semantic analysis and scope violations."""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Semantic Error: {message} [Line: {line}, Col: {column}]")


class SymbolTable:
    """Manages hierarchical lexical scoping and symbol definitions."""
    def __init__(self, parent=None):
        self.symbols = set()
        self.parent = parent

    def define(self, name: str):
        self.symbols.add(name)

    def lookup(self, name: str) -> bool:
        if name in self.symbols:
            return True
        if self.parent:
            return self.parent.lookup(name)
        return False


class SemanticValidator:
    """AST visitor that validates scoping, variable declarations, and function references."""
    def __init__(self):
        self.current_scope = SymbolTable()

    def enter_scope(self):
        self.current_scope = SymbolTable(parent=self.current_scope)

    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent

    def visit(self, node):
        node_type = type(node).__name__
        visitor_method = getattr(self, f"visit_{node_type}", self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        if hasattr(node, "__dict__"):
            for child in node.__dict__.values():
                if isinstance(child, list):
                    for item in child:
                        if hasattr(item, "__dict__"):
                            self.visit(item)
                elif hasattr(child, "__dict__"):
                    self.visit(child)

    def visit_VarDeclNode(self, node):
        if node.name in self.current_scope.symbols:
            raise SemanticError(f"Variable '{node.name}' already declared in this scope.")
        self.current_scope.define(node.name)
        if node.value:
            self.visit(node.value)

    def visit_VarAccessNode(self, node):
        if not self.current_scope.lookup(node.name):
            raise SemanticError(f"Undeclared variable '{node.name}' referenced.")
