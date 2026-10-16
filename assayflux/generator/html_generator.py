"""
HTML generator for AssayFlux Scientific Systems.
"""

from __future__ import annotations

import re
from html import escape
from pathlib import PurePosixPath
from typing import Any

from .base import BaseGenerator, GeneratedFile, GenerationResult


class HtmlGenerator(BaseGenerator):
    """Generate safe HTML pages for an AssayFlux project."""

    @property
    def name(self) -> str:
        return "html"

    def generate(
        self,
        spec: dict[str, Any],
    ) -> GenerationResult:
        """Generate one or more HTML pages from a specification."""

        try:
            if not isinstance(spec, dict):
                raise TypeError(
                    "The HTML generator specification "
                    "must be a dictionary."
                )

            site_title = spec.get("title", "AssayFlux App")

            self._validate_text(
                site_title,
                "The application title",
                allow_empty=False,
            )

            pages = spec.get("pages", [])

            if not isinstance(pages, list):
                raise TypeError(
                    "The pages setting must be a list."
                )

            files: list[GeneratedFile] = []
            used_paths: set[str] = set()

            if not pages:
                page_content = spec.get(
                    "content",
                    "Welcome to AssayFlux",
                )

                self._validate_text(
                    page_content,
                    "The page content",
                )

                files.append(
                    GeneratedFile(
                        path="index.html",
                        content=self._render_page(
                            page_title=site_title,
                            content=page_content,
                            site_title=site_title,
                        ),
                        language="html",
                    )
                )

            else:
                for index, page in enumerate(pages):
                    if not isinstance(page, dict):
                        raise TypeError(
                            f"Page {index + 1} must be a dictionary."
                        )

                    page_title = page.get("title", "Page")
                    page_content = page.get("content", "")

                    self._validate_text(
                        page_title,
                        f"Page {index + 1} title",
                        allow_empty=False,
                    )
                    self._validate_text(
                        page_content,
                        f"Page {index + 1} content",
                    )

                    default_filename = (
                        self._slugify(page_title) + ".html"
                    )
                    filename = page.get(
                        "filename",
                        default_filename,
                    )

                    self._validate_filename(filename)

                    normalized_path = str(
                        PurePosixPath(filename)
                    )

                    if normalized_path in used_paths:
                        raise ValueError(
                            "Duplicate HTML output filename: "
                            f"{normalized_path!r}."
                        )

                    used_paths.add(normalized_path)

                    files.append(
                        GeneratedFile(
                            path=normalized_path,
                            content=self._render_page(
                                page_title=page_title,
                                content=page_content,
                                site_title=site_title,
                            ),
                            language="html",
                        )
                    )

            return GenerationResult(
                success=True,
                files=files,
                message="HTML generated successfully.",
            )

        except (TypeError, ValueError) as exc:
            return GenerationResult(
                success=False,
                errors=[str(exc)],
                message="HTML generation failed.",
            )

    @staticmethod
    def _validate_text(
        value: Any,
        label: str,
        allow_empty: bool = True,
    ) -> None:
        """Validate text fields used in generated HTML."""

        if not isinstance(value, str):
            raise TypeError(f"{label} must be a string.")

        if not allow_empty and not value.strip():
            raise ValueError(f"{label} must not be empty.")

    @staticmethod
    def _validate_filename(filename: Any) -> None:
        """Reject unsafe or unsuitable HTML output filenames."""

        if not isinstance(filename, str):
            raise TypeError(
                "The HTML page filename must be a string."
            )

        if not filename or filename != filename.strip():
            raise ValueError(
                "The HTML page filename must not be empty "
                "or contain surrounding whitespace."
            )

        if "\\" in filename:
            raise ValueError(
                "The HTML page filename must use forward slashes."
            )

        path = PurePosixPath(filename)

        if (
            path.is_absolute()
            or filename.startswith("/")
            or any(part in {"", ".", ".."} for part in filename.split("/"))
        ):
            raise ValueError(
                f"Unsafe HTML page filename: {filename!r}."
            )

        if path.suffix.lower() != ".html":
            raise ValueError(
                "HTML page filenames must end with '.html'."
            )

    @staticmethod
    def _render_page(
        page_title: str,
        content: str,
        site_title: str = "AssayFlux",
    ) -> str:
        """Render an HTML page while escaping all supplied text."""

        safe_page_title = escape(page_title, quote=True)
        safe_site_title = escape(site_title, quote=True)
        safe_content = escape(content, quote=True)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="AssayFlux Scientific Systems">
    <title>{safe_page_title} | {safe_site_title}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>{safe_site_title}</h1>
        <nav aria-label="Main navigation">
            <a href="index.html">Home</a>
        </nav>
    </header>

    <main>
        <h2>{safe_page_title}</h2>
        <div class="content">{safe_content}</div>
    </main>

    <footer>
        <p>Built with AssayFlux Scientific Systems</p>
    </footer>

    <script src="js/main.js" defer></script>
</body>
</html>
"""

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert a page title into a predictable filename slug."""

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            text.lower(),
        ).strip("-")

        return slug or "page"