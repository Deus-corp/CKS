"""
CKS Diagnostics — Canonical Diagnostic Model.

This module implements the canonical diagnostic types defined in
CKS‑006 (Section 8).  Diagnostics are observationally pure,
immutable, and implementation‑independent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple


class DiagnosticSeverity(Enum):
    """Canonical diagnostic severities."""

    INFORMATION = "information"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class Diagnostic:
    """A single canonical diagnostic (CKS‑006, Section 8)."""

    identity: str                     # canonical diagnostic identifier
    severity: DiagnosticSeverity
    message: str                      # human‑readable explanation
    location: Optional[str] = None    # canonical identity of the affected entity
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class DiagnosticCollection:
    """An ordered collection of Diagnostics.

    The collection is immutable and order‑independent for the purpose
    of canonical equivalence (CKS‑006, Section 8.8).
    """

    diagnostics: Tuple[Diagnostic, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        return len(self.diagnostics)

    def __iter__(self):
        return iter(self.diagnostics)

    def errors(self) -> Tuple[Diagnostic, ...]:
        """Return only diagnostics with severity ERROR."""
        return tuple(d for d in self.diagnostics if d.severity == DiagnosticSeverity.ERROR)

    def warnings(self) -> Tuple[Diagnostic, ...]:
        """Return only diagnostics with severity WARNING."""
        return tuple(d for d in self.diagnostics if d.severity == DiagnosticSeverity.WARNING)

    def info(self) -> Tuple[Diagnostic, ...]:
        """Return only diagnostics with severity INFORMATION."""
        return tuple(d for d in self.diagnostics if d.severity == DiagnosticSeverity.INFORMATION)