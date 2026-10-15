"""Automated tests for the AssayFlux language adapter registry."""

import unittest

from assayflux.interop.base import ExecutionResult, LanguageAdapter
from assayflux.interop.registry import AdapterRegistry


class FakeAdapter(LanguageAdapter):
    """A lightweight adapter for registry testing."""

    def __init__(self, language="fake", available=True):
        self._language = language
        self._available = available

    @property
    def language(self):
        return self._language

    def is_available(self):
        return self._available

    def execute(self, source, *, timeout=10.0):
        return ExecutionResult(
            language=self.language,
            stdout=source,
            stderr="",
            returncode=0,
        )


class TestAdapterRegistry(unittest.TestCase):
    """Verify registration and discovery behavior."""

    def setUp(self):
        self.registry = AdapterRegistry()
        self.adapter = FakeAdapter()

    def test_register_and_retrieve_adapter(self):
        self.registry.register(self.adapter)

        self.assertIs(self.registry.get("fake"), self.adapter)

    def test_language_lookup_is_case_insensitive(self):
        self.registry.register(self.adapter)

        self.assertIs(self.registry.get("FAKE"), self.adapter)
        self.assertIs(self.registry.get(" Fake "), self.adapter)

    def test_duplicate_registration_is_rejected(self):
        self.registry.register(self.adapter)

        with self.assertRaises(ValueError):
            self.registry.register(FakeAdapter())

    def test_explicit_replacement(self):
        self.registry.register(self.adapter)

        replacement = FakeAdapter(available=False)
        self.registry.register(replacement, replace=True)

        self.assertIs(self.registry.get("fake"), replacement)

    def test_unknown_language_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.registry.get("unknown")

    def test_registration_status(self):
        self.assertFalse(self.registry.is_registered("fake"))

        self.registry.register(self.adapter)

        self.assertTrue(self.registry.is_registered("fake"))

    def test_registered_languages_are_sorted(self):
        self.registry.register(FakeAdapter("zeta"))
        self.registry.register(FakeAdapter("alpha"))

        self.assertEqual(
            self.registry.registered_languages(),
            ("alpha", "zeta"),
        )

    def test_available_languages(self):
        self.registry.register(FakeAdapter("available", available=True))
        self.registry.register(FakeAdapter("missing", available=False))

        self.assertEqual(
            self.registry.available_languages(),
            ("available",),
        )

    def test_invalid_adapter_is_rejected(self):
        with self.assertRaises(TypeError):
            self.registry.register(object())

    def test_empty_language_lookup_is_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.get("   ")

    def test_invalid_language_type_is_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.get(None)

    def test_invalid_replace_flag_is_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.register(self.adapter, replace="yes")


if __name__ == "__main__":
    unittest.main()