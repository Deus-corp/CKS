"""
CKS Result — Canonical Validation Result.

This module implements the immutable ValidationResult type defined in
CKS‑005 (Section 7) and CKS‑006 (Section 7).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .diagnostics import DiagnosticCollection


@dataclass(frozen=True)
class ValidationResult:
    """Canonical outcome of a validation execution.

    Attributes
    ----------
    is_valid : bool
        ``True`` if every applicable constraint is satisfied.
    diagnostics : DiagnosticCollection
        All diagnostics produced during validation.
    evaluated_constraints : list of str
        Identifiers of the constraints that were evaluated.
    metadata : dict
        Implementation‑independent metadata (pipeline, version, …).
    """

    is_valid: bool
    diagnostics: DiagnosticCollection = field(
        default_factory=lambda: DiagnosticCollection()
    )
    evaluated_constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)