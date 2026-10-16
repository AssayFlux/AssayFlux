class RuntimeError(Exception):
    """Custom exception for runtime execution failures."""
    pass


class Environment:
    """Runtime memory environment for variable storage and lookup."""
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name: str, value):
        self.values[name] = value

    def get(self, name: str):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable '{name}'.")

    def assign(self, name: str, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RuntimeError(f"Cannot assign to undefined variable '{name}'.")


class Interpreter:
    """Executes AssayFlux Abstract Syntax Tree structures."""
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env

    def interpret(self, ast_nodes):
        results = []
        for node in ast_nodes:
            results.append(self.visit(node))
        return results

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visit_{type(node).__name__} method implemented in Interpreter.")
