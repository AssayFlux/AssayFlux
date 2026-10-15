"""Tests for the AssayFlux command-line interface."""

import unittest
from unittest.mock import patch

from assayflux.cli import main


class CLITests(unittest.TestCase):
    """Test command-line execution."""

    def test_missing_file_returns_error(self):
        with patch(
            "sys.argv",
            ["assayflux", "file_that_does_not_exist.af"],
        ):
            self.assertEqual(main(), 1)

    def test_existing_file_executes_successfully(self):
        with patch("sys.argv", ["assayflux", "example.af"]):
            with patch("pathlib.Path.is_file", return_value=True):
                with patch(
                    "pathlib.Path.read_text",
                    return_value='show "Hello, AssayFlux!"',
                ):
                    with patch("assayflux.cli.Interpreter") as mock_interpreter:
                        result = main()

        self.assertEqual(result, 0)
        mock_interpreter.return_value.run.assert_called_once_with(
            'show "Hello, AssayFlux!"'
        )


if __name__ == "__main__":
    unittest.main()