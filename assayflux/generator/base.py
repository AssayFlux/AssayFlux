"""
Base classes for AssayFlux code generators.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class GeneratedFile:
    """Represents a single generated file."""
    path: str                    # relative path inside the project
    content: str
    language: str = ""


@dataclass
class GenerationResult:
    """Result of a generation process."""
    success: bool
    files: List[GeneratedFile] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    message: str = ""


class BaseGenerator(ABC):
    """Abstract base class for all generators."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the generator (html, css, python, etc.)."""
        ...

    @abstractmethod
    def generate(self, spec: Dict[str, Any]) -> GenerationResult:
        """Generate code from a specification dictionary."""
        ...