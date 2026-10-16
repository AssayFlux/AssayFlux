"""Tests for the AssayFlux Scientific Systems code generators."""

from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

from assayflux.generator import (
    BaseGenerator,
    GeneratedFile,
    GenerationResult,
    HtmlGenerator,
    CssGenerator,
    JsGenerator,
    PythonGenerator,
    SqlGenerator,
    ProjectBuilder,
)


class TestGeneratorContracts(unittest.TestCase):
    """Verify the shared generator interface."""

    def setUp(self):
        self.spec = {
            "title": "AssayFlux Demo",
            "content": "Welcome to AssayFlux.",
            "theme": "light",
            "primary_color": "#24434A",
            "backend": "simple",
            "tables": [
                {
                    "name": "experiments",
                    "columns": [
                        {
                            "name": "id",
                            "type": "INTEGER",
                            "primary_key": True,
                        },
                        {
                            "name": "name",
                            "type": "TEXT",
                            "not_null": True,
                        },
                    ],
                }
            ],
        }

        self.generators = [
            HtmlGenerator(),
            CssGenerator(),
            JsGenerator(),
            PythonGenerator(),
            SqlGenerator(),
        ]

    def test_all_generators_inherit_base_class(self):
        for generator in self.generators:
            with self.subTest(generator=generator.name):
                self.assertIsInstance(generator, BaseGenerator)

    def test_generator_names_are_unique(self):
        names = [generator.name for generator in self.generators]

        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(
            set(names),
            {"html", "css", "javascript", "python", "sql"},
        )

    def test_all_generators_return_successful_results(self):
        for generator in self.generators:
            with self.subTest(generator=generator.name):
                result = generator.generate(self.spec)

                self.assertIsInstance(result, GenerationResult)
                self.assertTrue(
                    result.success,
                    msg=f"{generator.name}: {result.errors}",
                )
                self.assertTrue(result.files)

                for generated_file in result.files:
                    self.assertIsInstance(
                        generated_file,
                        GeneratedFile,
                    )
                    self.assertTrue(generated_file.path)
                    self.assertIsInstance(
                        generated_file.content,
                        str,
                    )
                    self.assertTrue(generated_file.language)

    def test_generated_paths_are_expected(self):
        expected_paths = {
            "html": "index.html",
            "css": "css/style.css",
            "javascript": "js/main.js",
            "python": "backend/app.py",
            "sql": "database/schema.sql",
        }

        for generator in self.generators:
            with self.subTest(generator=generator.name):
                result = generator.generate(self.spec)

                self.assertTrue(
                    result.success,
                    msg=str(result.errors),
                )
                self.assertIn(
                    expected_paths[generator.name],
                    {item.path for item in result.files},
                )

    def test_non_dictionary_specifications_are_rejected(self):
        for generator in self.generators:
            with self.subTest(generator=generator.name):
                result = generator.generate(None)

                self.assertFalse(result.success)
                self.assertTrue(result.errors)


class TestHtmlGenerator(unittest.TestCase):
    """Verify HTML generation, validation, and text escaping."""

    def setUp(self):
        self.generator = HtmlGenerator()

    def test_generates_default_page(self):
        result = self.generator.generate({})

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(len(result.files), 1)
        self.assertEqual(result.files[0].path, "index.html")

        html = result.files[0].content

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Welcome to AssayFlux", html)
        self.assertIn('lang="en"', html)
        self.assertIn("AssayFlux Scientific Systems", html)

    def test_uses_supplied_title_and_content(self):
        result = self.generator.generate(
            {
                "title": "Laboratory Portal",
                "content": "Experiment dashboard",
            }
        )

        self.assertTrue(result.success, msg=str(result.errors))

        html = result.files[0].content

        self.assertIn("Laboratory Portal", html)
        self.assertIn("Experiment dashboard", html)

    def test_escapes_html_in_titles_and_content(self):
        result = self.generator.generate(
            {
                "title": '<script>alert("title")</script>',
                "content": '<img src=x onerror="alert(1)">',
            }
        )

        self.assertTrue(result.success, msg=str(result.errors))

        html = result.files[0].content

        self.assertNotIn(
            '<script>alert("title")</script>',
            html,
        )
        self.assertNotIn(
            '<img src=x onerror="alert(1)">',
            html,
        )
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;img", html)

    def test_generates_multiple_pages(self):
        result = self.generator.generate(
            {
                "title": "Research Portal",
                "pages": [
                    {
                        "title": "Experiments",
                        "filename": "experiments.html",
                        "content": "Experiment records",
                    },
                    {
                        "title": "Reports",
                        "filename": "reports.html",
                        "content": "Research reports",
                    },
                ],
            }
        )

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(
            {item.path for item in result.files},
            {"experiments.html", "reports.html"},
        )

    def test_creates_filename_from_page_title(self):
        result = self.generator.generate(
            {
                "pages": [
                    {
                        "title": "Research Results 2026",
                        "content": "Results",
                    }
                ]
            }
        )

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(
            result.files[0].path,
            "research-results-2026.html",
        )

    def test_rejects_non_dictionary_specification(self):
        result = self.generator.generate([])

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_empty_application_title(self):
        result = self.generator.generate({"title": "   "})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_non_string_page_content(self):
        result = self.generator.generate({"content": 123})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_non_list_pages(self):
        result = self.generator.generate({"pages": "not a list"})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_non_dictionary_page(self):
        result = self.generator.generate({"pages": ["invalid"]})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_path_traversal(self):
        unsafe_filenames = [
            "../outside.html",
            "pages/../../outside.html",
            "/tmp/outside.html",
            r"pages\outside.html",
        ]

        for filename in unsafe_filenames:
            with self.subTest(filename=filename):
                result = self.generator.generate(
                    {
                        "pages": [
                            {
                                "title": "Unsafe Page",
                                "filename": filename,
                                "content": "Test",
                            }
                        ]
                    }
                )

                self.assertFalse(result.success)
                self.assertTrue(result.errors)

    def test_rejects_non_html_filename(self):
        result = self.generator.generate(
            {
                "pages": [
                    {
                        "title": "Reports",
                        "filename": "reports.txt",
                        "content": "Reports",
                    }
                ]
            }
        )

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_duplicate_filenames(self):
        result = self.generator.generate(
            {
                "pages": [
                    {
                        "title": "First",
                        "filename": "reports.html",
                        "content": "First page",
                    },
                    {
                        "title": "Second",
                        "filename": "reports.html",
                        "content": "Second page",
                    },
                ]
            }
        )

        self.assertFalse(result.success)
        self.assertTrue(result.errors)


class TestCssGenerator(unittest.TestCase):
    """Verify CSS themes, colors, and responsive styling."""

    def setUp(self):
        self.generator = CssGenerator()

    def test_generates_stylesheet(self):
        result = self.generator.generate({})

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(result.files[0].path, "css/style.css")

        css = result.files[0].content

        self.assertIn(":root", css)
        self.assertIn("body", css)
        self.assertIn("--primary: #24434A;", css)
        self.assertIn("--bg: #F6F4EF;", css)

    def test_uses_supplied_primary_color(self):
        result = self.generator.generate(
            {"primary_color": "#2563eb"}
        )

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertIn(
            "--primary: #2563eb;",
            result.files[0].content,
        )

    def test_supports_dark_theme(self):
        result = self.generator.generate({"theme": "dark"})

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertIn(
            "--bg: #0f172a;",
            result.files[0].content,
        )
        self.assertIn(
            "--surface: #1e293b;",
            result.files[0].content,
        )

    def test_accepts_short_hex_colors(self):
        for color in ("#123", "#1234", "#AABBCC", "#AABBCCDD"):
            with self.subTest(color=color):
                result = self.generator.generate(
                    {"primary_color": color}
                )

                self.assertTrue(
                    result.success,
                    msg=str(result.errors),
                )

    def test_rejects_invalid_colors(self):
        invalid_colors = [
            "red",
            "url(javascript:alert(1))",
            "#12",
            "#12345",
            "#1234567",
            "#123456789",
            "#12; color: red",
            "",
        ]

        for color in invalid_colors:
            with self.subTest(color=color):
                result = self.generator.generate(
                    {"primary_color": color}
                )

                self.assertFalse(result.success)
                self.assertTrue(result.errors)

    def test_rejects_unknown_theme(self):
        result = self.generator.generate({"theme": "neon"})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_non_string_theme(self):
        result = self.generator.generate({"theme": None})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_non_string_color(self):
        result = self.generator.generate({"primary_color": 123})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_includes_responsive_layout(self):
        result = self.generator.generate({})

        self.assertTrue(result.success, msg=str(result.errors))

        css = result.files[0].content

        self.assertIn("@media (max-width: 600px)", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn(":focus-visible", css)


class TestJavaScriptGenerator(unittest.TestCase):
    """Verify JavaScript generation and safe string encoding."""

    def setUp(self):
        self.generator = JsGenerator()

    def test_generates_javascript_file(self):
        result = self.generator.generate(
            {"title": "AssayFlux Laboratory"}
        )

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(result.files[0].path, "js/main.js")

        source = result.files[0].content

        self.assertIn("DOMContentLoaded", source)
        self.assertIn("AssayFlux Laboratory", source)
        self.assertIn('"use strict";', source)
        self.assertIn("const APP_NAME", source)

    def test_encodes_quotes_and_newlines_safely(self):
        title = 'Lab "Alpha"\\Beta\nSecond line'

        result = self.generator.generate({"title": title})

        self.assertTrue(result.success, msg=str(result.errors))

        source = result.files[0].content
        encoded_title = json.dumps(title, ensure_ascii=True)

        self.assertIn(
            f"const APP_NAME = {encoded_title};",
            source,
        )

    def test_rejects_empty_title(self):
        result = self.generator.generate({"title": "   "})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_non_string_title(self):
        result = self.generator.generate({"title": 123})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_non_dictionary_specification(self):
        result = self.generator.generate(None)

        self.assertFalse(result.success)
        self.assertTrue(result.errors)


class TestPythonGenerator(unittest.TestCase):
    """Verify generated Python source and validation."""

    def setUp(self):
        self.generator = PythonGenerator()

    def test_generates_valid_simple_backend(self):
        result = self.generator.generate(
            {
                "title": "AssayFlux Backend",
                "backend": "simple",
            }
        )

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(result.files[0].path, "backend/app.py")

        ast.parse(result.files[0].content)

    def test_generates_valid_flask_backend(self):
        result = self.generator.generate(
            {
                "title": "AssayFlux API",
                "backend": "flask",
            }
        )

        self.assertTrue(result.success, msg=str(result.errors))

        source = result.files[0].content

        self.assertIn("from flask import Flask, jsonify", source)
        self.assertIn("/api/health", source)

        ast.parse(source)

    def test_escapes_title_in_generated_python(self):
        title = 'Research "Alpha"\\Beta\nSecond line'

        result = self.generator.generate({"title": title})

        self.assertTrue(result.success, msg=str(result.errors))

        source = result.files[0].content

        ast.parse(source)
        self.assertIn(json.dumps(title, ensure_ascii=True), source)

    def test_rejects_empty_title(self):
        result = self.generator.generate({"title": "   "})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_non_string_title(self):
        result = self.generator.generate({"title": 123})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_unsupported_backend(self):
        result = self.generator.generate({"backend": "unknown"})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_non_string_backend(self):
        result = self.generator.generate({"backend": None})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)


class TestSqlGenerator(unittest.TestCase):
    """Verify SQL schema generation and validation."""

    def test_generates_table_schema(self):
        result = SqlGenerator().generate(
            {
                "tables": [
                    {
                        "name": "experiments",
                        "columns": [
                            {
                                "name": "id",
                                "type": "INTEGER",
                                "primary_key": True,
                            },
                            {
                                "name": "description",
                                "type": "TEXT",
                                "not_null": True,
                            },
                        ],
                    }
                ]
            }
        )

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(
            result.files[0].path,
            "database/schema.sql",
        )

        sql = result.files[0].content

        self.assertIn(
            'CREATE TABLE IF NOT EXISTS "experiments"',
            sql,
        )
        self.assertIn('"id" INTEGER PRIMARY KEY', sql)
        self.assertIn('"description" TEXT NOT NULL', sql)

    def test_escapes_single_quotes_in_string_defaults(self):
        rendered = SqlGenerator.sanitize_value(
            "researcher's notes"
        )

        self.assertEqual(rendered, "'researcher''s notes'")

    def test_renders_boolean_and_null_defaults(self):
        self.assertEqual(SqlGenerator.sanitize_value(True), "TRUE")
        self.assertEqual(SqlGenerator.sanitize_value(False), "FALSE")
        self.assertEqual(SqlGenerator.sanitize_value(None), "NULL")

    def test_rejects_invalid_table_identifier(self):
        with self.assertRaises(ValueError):
            SqlGenerator.escape_identifier("invalid table name")

    def test_rejects_unsupported_column_type(self):
        result = SqlGenerator().generate(
            {
                "tables": [
                    {
                        "name": "experiments",
                        "columns": [
                            {
                                "name": "id",
                                "type": "UNSAFE_TYPE",
                            }
                        ],
                    }
                ]
            }
        )

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_empty_column_list(self):
        result = SqlGenerator().generate(
            {
                "tables": [
                    {
                        "name": "experiments",
                        "columns": [],
                    }
                ]
            }
        )

        self.assertFalse(result.success)
        self.assertTrue(result.errors)


class TestProjectBuilder(unittest.TestCase):
    """Verify complete project generation and filesystem safety."""

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)

        self.output_directory = Path(self.temporary_directory.name)
        self.builder = ProjectBuilder(self.output_directory)

        self.spec = {
            "title": "AssayFlux Research Portal",
            "content": "Welcome to the research portal.",
            "theme": "light",
            "primary_color": "#24434A",
            "backend": "simple",
            "tables": [
                {
                    "name": "experiments",
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "title", "type": "TEXT"},
                    ],
                }
            ],
        }

    def test_builds_complete_website(self):
        result = self.builder.build_website(self.spec)

        self.assertTrue(result.success, msg=str(result.errors))

        website = self.output_directory / "website"

        expected_files = [
            "index.html",
            "css/style.css",
            "js/main.js",
            "backend/app.py",
            "database/schema.sql",
            "README.md",
        ]

        for relative_path in expected_files:
            with self.subTest(path=relative_path):
                self.assertTrue(
                    (website / relative_path).is_file(),
                    msg=f"Missing generated file: {relative_path}",
                )

    def test_generated_python_backend_parses(self):
        result = self.builder.build_website(self.spec)

        self.assertTrue(result.success, msg=str(result.errors))

        backend = (
            self.output_directory
            / "website"
            / "backend"
            / "app.py"
        )

        ast.parse(backend.read_text(encoding="utf-8"))

    def test_generated_javascript_preserves_title(self):
        result = self.builder.build_website(self.spec)

        self.assertTrue(result.success, msg=str(result.errors))

        javascript = (
            self.output_directory
            / "website"
            / "js"
            / "main.js"
        ).read_text(encoding="utf-8")

        self.assertIn("AssayFlux Research Portal", javascript)

    def test_rejects_non_dictionary_specification(self):
        result = self.builder.build_website([])

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_empty_project_title(self):
        result = self.builder.build_website({"title": "   "})

        self.assertFalse(result.success)
        self.assertTrue(result.errors)

    def test_rejects_directory_traversal(self):
        project_root = self.output_directory / "safe-project"

        with self.assertRaises(ValueError):
            ProjectBuilder._write_files(
                project_root,
                [
                    GeneratedFile(
                        path="../outside.txt",
                        content="This must not be written.",
                        language="text",
                    )
                ],
            )

    def test_rejects_duplicate_output_paths(self):
        project_root = self.output_directory / "duplicate-project"

        with self.assertRaises(ValueError):
            ProjectBuilder._write_files(
                project_root,
                [
                    GeneratedFile(
                        path="index.html",
                        content="First file",
                        language="html",
                    ),
                    GeneratedFile(
                        path="index.html",
                        content="Second file",
                        language="html",
                    ),
                ],
            )


if __name__ == "__main__":
    unittest.main()