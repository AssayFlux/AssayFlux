"""Master test suite for AssayFlux language interoperability."""

import unittest
from unittest.mock import patch

from assayflux.interop import (
    ExecutionResult,
    available_languages,
    dispatch,
    get_adapter,
)
from assayflux.interop.adapters.master_adapter import MasterAdapter


class MasterAdapterRegistrationTests(unittest.TestCase):
    """Test registration and discovery of language targets."""

    def test_all_declared_targets_are_registered(self):
        """Every declared language must have a registered adapter."""

        for language in MasterAdapter.registered_languages():
            with self.subTest(language=language):
                adapter = get_adapter(language)

                self.assertEqual(adapter.language, language)

    def test_registered_targets_are_unique(self):
        """The language registry must not contain duplicates."""

        languages = MasterAdapter.registered_languages()

        self.assertEqual(len(languages), len(set(languages)))

    def test_every_registered_target_has_an_execution_strategy(self):
        """Every declared target must be one of the supported targets."""

        expected = {
            "bash",
            "c",
            "cpp",
            "csharp",
            "cobol",
            "crystal",
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
            "sql",
            "swift",
            "typescript",
            "zig",
            "html",
            "css",
        }

        actual = set(MasterAdapter.registered_languages())

        self.assertEqual(actual, expected)

    def test_language_aliases_resolve_to_canonical_names(self):
        """Aliases must resolve to their expected canonical names."""

        aliases = {
            "py": "python",
            "PY": "python",
            "js": "javascript",
            "node": "javascript",
            "c++": "cpp",
            "cc": "cpp",
            "c#": "csharp",
            "cs": "csharp",
            "f#": "fsharp",
            "fs": "fsharp",
            "hs": "haskell",
            "rs": "rust",
            "rb": "ruby",
            "rscript": "r",
            "ts": "typescript",
            "sh": "bash",
            "shell": "bash",
            "sqlite": "sql",
            "sqlite3": "sql",
            "htm": "html",
        }

        for alias, expected in aliases.items():
            with self.subTest(alias=alias):
                adapter = get_adapter(alias)

                self.assertEqual(adapter.language, expected)

    def test_language_names_are_case_insensitive(self):
        """Language lookup must accept uppercase names."""

        self.assertEqual(get_adapter("PYTHON").language, "python")
        self.assertEqual(get_adapter("JavaScript").language, "javascript")
        self.assertEqual(get_adapter("SQL").language, "sql")

    def test_unknown_language_is_rejected(self):
        """Unknown language identifiers must raise KeyError."""

        with self.assertRaises(KeyError):
            get_adapter("language_that_does_not_exist")

    def test_empty_language_is_rejected(self):
        """An empty language identifier must not be accepted."""

        with self.assertRaises(KeyError):
            get_adapter("")


class MasterAdapterAvailabilityTests(unittest.TestCase):
    """Test runtime availability reporting."""

    def test_available_languages_returns_a_collection(self):
        """Availability discovery must return a predictable collection."""

        result = available_languages()

        self.assertIsInstance(result, tuple)
        self.assertEqual(result, tuple(sorted(set(result))))

    def test_available_languages_contains_only_registered_targets(self):
        """Availability reporting must not invent language names."""

        registered = set(MasterAdapter.registered_languages())
        available = set(available_languages())

        self.assertTrue(available.issubset(registered))

    def test_python_runtime_is_available(self):
        """The Python runtime running the test suite must be available."""

        adapter = get_adapter("python")

        self.assertTrue(adapter.is_available())

    def test_static_asset_targets_are_available(self):
        """HTML and CSS are handled without external runtimes."""

        self.assertTrue(get_adapter("html").is_available())
        self.assertTrue(get_adapter("css").is_available())


class MasterAdapterExecutionTests(unittest.TestCase):
    """Test actual execution and the shared result contract."""

    def test_python_executes_successfully(self):
        """Python source must execute and return standard output."""

        result = dispatch("python", "print(2 + 3)")

        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.language, "python")
        self.assertEqual(result.stdout, "5\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.returncode, 0)
        self.assertGreaterEqual(result.duration, 0.0)

    def test_python_accepts_unicode_output(self):
        """Unicode output must be preserved."""

        result = dispatch("python", "print('AssayFlux 科学')")

        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "AssayFlux 科学\n")

    def test_python_preserves_runtime_errors(self):
        """Python exceptions must be returned as failed results."""

        result = dispatch(
            "python",
            "raise ValueError('master test error')",
        )

        self.assertFalse(result.success)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)
        self.assertIn("master test error", result.stderr)

    def test_python_preserves_nonzero_exit_code(self):
        """A program's nonzero exit status must be preserved."""

        result = dispatch("python", "raise SystemExit(7)")

        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 7)

    def test_python_supports_multiple_statements(self):
        """Multiple source statements must execute in order."""

        source = """
value = 10
value += 5
print(value)
print(value * 2)
"""

        result = dispatch("python", source)

        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "15\n30\n")

    def test_python_alias_executes_successfully(self):
        """The py alias must execute Python source."""

        result = dispatch("py", "print('alias works')")

        self.assertTrue(result.success)
        self.assertEqual(result.language, "python")
        self.assertEqual(result.stdout, "alias works\n")

    def test_sql_executes_queries(self):
        """SQL statements must execute against an in-memory database."""

        source = """
CREATE TABLE samples (
    id INTEGER PRIMARY KEY,
    name TEXT
);
INSERT INTO samples (id, name) VALUES (1, 'Sample A');
INSERT INTO samples (id, name) VALUES (2, 'Sample B');
SELECT id, name FROM samples ORDER BY id;
"""

        result = dispatch("sql", source)

        self.assertTrue(result.success)
        self.assertEqual(result.language, "sql")
        self.assertEqual(
            result.stdout,
            "1\tSample A\n2\tSample B\n",
        )
        self.assertEqual(result.stderr, "")

    def test_sql_reports_invalid_statements(self):
        """Invalid SQL must return an error result."""

        result = dispatch("sql", "SELECT * FROM missing_table;")

        self.assertFalse(result.success)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SQLite error", result.stderr)

    def test_sql_alias_executes_successfully(self):
        """The sqlite alias must resolve to SQL execution."""

        result = dispatch("sqlite", "SELECT 6 * 7;")

        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "42\n")

    def test_html_is_handled_as_a_static_asset(self):
        """HTML handling must clearly identify its limited behavior."""

        result = dispatch(
            "html",
            "<!doctype html><html><body>Hello</body></html>",
        )

        self.assertTrue(result.success)
        self.assertIn("HTML static asset accepted", result.stdout)
        self.assertIn("browser rendering is not performed", result.stdout)

    def test_css_is_handled_as_a_static_asset(self):
        """CSS handling must clearly identify its limited behavior."""

        result = dispatch(
            "css",
            "body { font-family: sans-serif; }",
        )

        self.assertTrue(result.success)
        self.assertIn("CSS static asset accepted", result.stdout)
        self.assertIn("browser rendering is not performed", result.stdout)

    def test_empty_html_source_is_rejected(self):
        """Empty static assets must return a failed result."""

        result = dispatch("html", "   ")

        self.assertFalse(result.success)
        self.assertNotEqual(result.returncode, 0)

    def test_unavailable_runtime_returns_clear_error(self):
        """Missing language runtimes must not crash the dispatcher."""

        adapter = get_adapter("javascript")

        with patch.object(adapter, "is_available", return_value=False):
            result = adapter.execute("console.log('test')")

        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 127)
        self.assertIn("Runtime unavailable", result.stderr)

    def test_timeout_is_reported(self):
        """Long-running subprocesses must respect the timeout."""

        result = dispatch(
            "python",
            "while True:\n    pass",
            timeout=0.2,
        )

        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 124)
        self.assertIn("timed out", result.stderr.lower())


class MasterAdapterValidationTests(unittest.TestCase):
    """Test invalid arguments and execution safeguards."""

    def test_non_string_source_is_rejected(self):
        """Source must be a string."""

        with self.assertRaises(TypeError):
            dispatch("python", 123)

    def test_non_string_language_is_rejected(self):
        """Language identifiers must be strings."""

        with self.assertRaises(TypeError):
            dispatch(None, "print('test')")

    def test_zero_timeout_is_rejected(self):
        """A zero timeout must be rejected."""

        with self.assertRaises(ValueError):
            dispatch("python", "print('test')", timeout=0)

    def test_negative_timeout_is_rejected(self):
        """A negative timeout must be rejected."""

        with self.assertRaises(ValueError):
            dispatch("python", "print('test')", timeout=-1)

    def test_infinite_timeout_is_rejected(self):
        """An infinite timeout must be rejected."""

        with self.assertRaises(ValueError):
            dispatch("python", "print('test')", timeout=float("inf"))

    def test_boolean_timeout_is_rejected(self):
        """Boolean values must not be treated as numeric timeouts."""

        with self.assertRaises(TypeError):
            dispatch("python", "print('test')", timeout=True)


if __name__ == "__main__":
    unittest.main()