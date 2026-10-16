"""Tests for the AssayFlux code generation system."""

from __future__ import annotations

import ast
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
    """Verify the common interface used by all generators."""

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

    def test_all_generators_return_generation_results(self):
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
                    self.assertIsInstance(generated_file, GeneratedFile)
                    self.assertTrue(generated_file.path)
                    self.assertIsInstance(generated_file.content, str)
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

                self.assertTrue(result.success, msg=str(result.errors))
                self.assertIn(
                    expected_paths[generator.name],
                    {file.path for file in result.files},
                )


class TestHtmlGenerator(unittest.TestCase):
    """Verify HTML generation."""

    def test_generates_default_page(self):
        result = HtmlGenerator().generate({})

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(len(result.files), 1)
        self.assertEqual(result.files[0].path, "index.html")
        self.assertIn("<!DOCTYPE html>", result.files[0].content)
        self.assertIn("Welcome to AssayFlux", result.files[0].content)

    def test_uses_supplied_title_and_content(self):
        result = HtmlGenerator().generate(
            {
                "title": "Laboratory Portal",
                "content": "Experiment dashboard",
            }
        )

        self.assertTrue(result.success, msg=str(result.errors))
        content = result.files[0].content

        self.assertIn("Laboratory Portal", content)
        self.assertIn("Experiment dashboard", content)

    def test_generates_multiple_pages(self):
        result = HtmlGenerator().generate(
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
        paths = {file.path for file in result.files}

        self.assertEqual(
            paths,
            {"experiments.html", "reports.html"},
        )


class TestCssGenerator(unittest.TestCase):
    """Verify CSS generation."""

    def test_generates_stylesheet(self):
        result = CssGenerator().generate({})

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(result.files[0].path, "css/style.css")
        self.assertIn(":root", result.files[0].content)
        self.assertIn("body", result.files[0].content)

    def test_uses_supplied_primary_color(self):
        result = CssGenerator().generate(
            {"primary_color": "#24434A"}
        )

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertIn("--primary: #24434A;", result.files[0].content)

    def test_supports_dark_theme(self):
        result = CssGenerator().generate({"theme": "dark"})

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertIn("--bg: #0f172a;", result.files[0].content)


class TestJavaScriptGenerator(unittest.TestCase):
    """Verify JavaScript generation."""

    def test_generates_javascript_file(self):
        result = JsGenerator().generate(
            {"title": "AssayFlux Laboratory"}
        )

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(result.files[0].path, "js/main.js")
        self.assertIn("DOMContentLoaded", result.files[0].content)
        self.assertIn("AssayFlux Laboratory", result.files[0].content)


class TestPythonGenerator(unittest.TestCase):
    """Verify generated Python source code."""

    def test_generates_valid_simple_backend(self):
        result = PythonGenerator().generate(
            {"title": "AssayFlux Backend", "backend": "simple"}
        )

        self.assertTrue(result.success, msg=str(result.errors))
        self.assertEqual(result.files[0].path, "backend/app.py")

        # Parse the generated source without executing it.
        ast.parse(result.files[0].content)

    def test_generates_valid_flask_backend_source(self):
        result = PythonGenerator().generate(
            {"title": "AssayFlux API", "backend": "flask"}
        )

        self.assertTrue(result.success, msg=str(result.errors))
        source = result.files[0].content

        self.assertIn("from flask import Flask, jsonify", source)
        self.assertIn("/api/health", source)
        ast.parse(source)


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
        rendered = SqlGenerator.sanitize_value("researcher's notes")

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