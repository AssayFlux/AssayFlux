"""
HTML Generator for AssayFlux.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .base import BaseGenerator, GeneratedFile, GenerationResult


class HtmlGenerator(BaseGenerator):

    @property
    def name(self) -> str:
        return "html"

    def generate(self, spec: Dict[str, Any]) -> GenerationResult:
        try:
            title = spec.get("title", "AssayFlux App")
            pages = spec.get("pages", [])
            files: List[GeneratedFile] = []

            if not pages:
                # Single page fallback
                content = self._render_page(title, spec.get("content", "Welcome to AssayFlux"))
                files.append(GeneratedFile(
                    path="index.html",
                    content=content,
                    language="html"
                ))
            else:
                for page in pages:
                    page_title = page.get("title", "Page")
                    page_content = page.get("content", "")
                    filename = page.get("filename", self._slugify(page_title) + ".html")
                    content = self._render_page(page_title, page_content, title)
                    files.append(GeneratedFile(
                        path=filename,
                        content=content,
                        language="html"
                    ))

            return GenerationResult(success=True, files=files, message="HTML generated successfully")
        except Exception as e:
            return GenerationResult(success=False, errors=[str(e)])

    def _render_page(self, page_title: str, content: str, site_title: str = "AssayFlux") -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} | {site_title}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>{site_title}</h1>
        <nav>
            <a href="index.html">Home</a>
        </nav>
    </header>

    <main>
        <h2>{page_title}</h2>
        <div class="content">
            {content}
        </div>
    </main>

    <footer>
        <p>Built with AssayFlux</p>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>
"""

    def _slugify(self, text: str) -> str:
        return text.lower().replace(" ", "-").replace("_", "-")