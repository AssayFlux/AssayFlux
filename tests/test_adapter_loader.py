"""Tests for the AssayFlux default adapter loader."""

import unittest

from assayflux.interop.base import LanguageAdapter
from assayflux.interop.loader import (
    available_languages,
    get_adapter,
    get_default_registry,
)


EXPECTED_LANGUAGES = (
    "c",
    "cobol",
    "cpp",
    "crystal",
    "csharp",
    "d",
    "dart",
    "elixir",
    "erlang",
    "fortran",
    "fsharp",
    "go",
    "haskell",
    "java",
    "javascript",
    "julia",
    "kotlin",
    "lua",
    "nim",
    "ocaml",
    "perl",
    "php",
    "python",
    "r",
    "ruby",
    "rust",
    "scala",
    "swift",
    "typescript",
    "zig",
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

    def test_all_30_languages_are_registered(self):
        registry = get_default_registry()

        registered = registry.registered_languages()

        self.assertEqual(len(registered), 30)
        self.assertEqual(registered, EXPECTED_LANGUAGES)

    def test_every_registered_adapter_implements_contract(self):
        for language in EXPECTED_LANGUAGES:
            with self.subTest(language=language):
                adapter = get_adapter(language)

                self.assertIsInstance(adapter, LanguageAdapter)
                self.assertEqual(adapter.language, language)

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

    def test_available_languages_returns_sorted_tuple(self):
        languages = available_languages()

        self.assertIsInstance(languages, tuple)
        self.assertEqual(languages, tuple(sorted(languages)))

    def test_available_languages_are_registered(self):
        registry = get_default_registry()

        for language in available_languages():
            with self.subTest(language=language):
                self.assertTrue(registry.is_registered(language))

    def test_python_availability_matches_runtime(self):
        adapter = get_adapter("python")
        languages = available_languages()

        if adapter.is_available():
            self.assertIn("python", languages)
        else:
            self.assertNotIn("python", languages)

    def test_javascript_adapter_is_registered(self):
        adapter = get_adapter("javascript")

        self.assertIsInstance(adapter, LanguageAdapter)
        self.assertEqual(adapter.language, "javascript")

    def test_unregistered_language_raises_key_error(self):
        with self.assertRaises(KeyError):
            get_adapter("unknown_assayflux_language")


if __name__ == "__main__":
    unittest.main()