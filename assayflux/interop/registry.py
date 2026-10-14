"""
Language adapter registry for AssayFlux.

The registry provides a central location for registering and
retrieving language adapters without coupling the interpreter
to individual language implementations.
"""

from threading import RLock

from assayflux.interop.base import LanguageAdapter


class AdapterRegistry:
    """Manage language adapters by their canonical identifiers."""

    def __init__(self) -> None:
        self._adapters: dict[str, LanguageAdapter] = {}
        self._lock = RLock()

    @staticmethod
    def _normalize_language(language: str) -> str:
        """Normalize and validate a language identifier."""
        if not isinstance(language, str):
            raise ValueError("Language identifier must be a string.")

        normalized = language.strip().lower()

        if not normalized:
            raise ValueError("Language identifier must not be empty.")

        return normalized

    def register(
        self,
        adapter: LanguageAdapter,
        *,
        replace: bool = False,
    ) -> None:
        """
        Register a language adapter.

        Duplicate registrations are rejected unless replace=True.
        """
        if not isinstance(adapter, LanguageAdapter):
            raise TypeError(
                "Adapter must be an instance of LanguageAdapter."
            )

        if not isinstance(replace, bool):
            raise ValueError("replace must be a boolean.")

        language = self._normalize_language(adapter.language)

        with self._lock:
            if language in self._adapters and not replace:
                raise ValueError(
                    f"An adapter for '{language}' is already registered."
                )

            self._adapters[language] = adapter

    def get(self, language: str) -> LanguageAdapter:
        """Return the adapter registered for a language."""
        normalized = self._normalize_language(language)

        with self._lock:
            adapter = self._adapters.get(normalized)

        if adapter is None:
            raise KeyError(
                f"No adapter registered for language '{normalized}'."
            )

        return adapter

    def is_registered(self, language: str) -> bool:
        """Return whether a language has a registered adapter."""
        normalized = self._normalize_language(language)

        with self._lock:
            return normalized in self._adapters

    def available_languages(self) -> tuple[str, ...]:
        """
        Return the sorted identifiers of registered adapters
        whose required runtimes are currently available.
        """
        with self._lock:
            adapters = tuple(self._adapters.items())

        available = []

        for language, adapter in adapters:
            try:
                if adapter.is_available():
                    available.append(language)
            except Exception:
                # An adapter that cannot verify availability should
                # not be advertised as currently available.
                continue

        return tuple(sorted(available))

    def registered_languages(self) -> tuple[str, ...]:
        """Return every registered language identifier."""
        with self._lock:
            return tuple(sorted(self._adapters))