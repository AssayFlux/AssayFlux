class InteropRuntimeRegistry:
    """Manages secure cross-language execution and runtime adapters with type checking."""
    def __init__(self):
        self._registry = {}

    def register(self, language: str, handler: callable):
        """Registers a foreign language handler with callable verification."""
        if not callable(handler):
            raise TypeError(f"Handler for '{language}' must be a callable function.")
        self._registry[language.lower()] = handler

    def execute(self, language: str, payload: dict):
        """Executes foreign code payload with strict type validation."""
        lang = language.lower()
        if lang not in self._registry:
            raise KeyError(f"Unsupported interoperability language target: '{language}'")
        
        if not isinstance(payload, dict):
            raise TypeError("Interop execution payload must be formatted as a dictionary.")
            
        handler = self._registry[lang]
        try:
            return handler(payload)
        except Exception as e:
            raise RuntimeError(f"Error executing interop for '{language}': {e}")
