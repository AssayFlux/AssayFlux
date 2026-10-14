"""Tests for the AssayFlux default adapter loader."""

import unittest

from assayflux.interop.base import LanguageAdapter
from assayflux.interop.loader import (
    available_languages,
    get_adapter,
    get_default_registry,
)


class TestAdapterLoader(unittest.TestCase):
    """Verify default adapter registration and discovery."""

    def test_default_registry_is_initialized(self):
        registry = get_default_registry()

        self.assertIsNotNone(registry)

    def test_default_registry_is_cached(self):
        first = get_default_registry()
        second = get_default_registry()

        self.assertIs(first, second)

    def test_python_adapter_is_registered(self):
        registry = get_default_registry()

        self.assertTrue(registry.is_registered("python"))

    def test_get_python_adapter(self):
        adapter = get_adapter("python")

        self.assertIsInstance(adapter, LanguageAdapter)
        self.assertEqual(adapter.language, "python")

    def test_language_lookup_is_case_insensitive(self):
        adapter = get_adapter("PYTHON")

        self.assertEqual(adapter.language, "python")

    def test_available_languages_returns_tuple(self):
        languages = available_languages()

        self.assertIsInstance(languages, tuple)
        self.assertEqual(languages, tuple(sorted(languages)))

    def test_python_is_available_when_runtime_is_available(self):
        adapter = get_adapter("python")

        if adapter.is_available():
            self.assertIn("python", available_languages())
        else:
            self.assertNotIn("python", available_languages())

    def test_unregistered_language_raises_key_error(self):
        with self.assertRaises(KeyError):
            get_adapter("javascript")


if __name__ == "__main__":
    unittest.main()
