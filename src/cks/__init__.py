"""
Canonical Knowledge Structure (CKS).

Reference implementation of the Canonical Knowledge Structure (CKS)
specifications.

The package exposes the canonical public API defined by CKS-007.

Typical usage:

    import cks

    structure = cks.parse(source)
    result = cks.validate(structure)

Only symbols defined here should normally be imported by user code.
"""

from __future__ import annotations

from .core import (
    CanonicalRelation,
    KnowledgeObject,
    KnowledgeStructure,
    ObjectIdentity,
)

from .diagnostics import (
    Diagnostic,
    DiagnosticCollection,
    DiagnosticSeverity,
)

from .engine import ReferenceEngine

from .result import ValidationResult

from .serialization import SerializationError

from .interface import (
    compare,
    construct,
    diagnose,
    evolve,
    extract,
    inspect,
    parse,
    project,
    serialize,
    validate,
)

__version__ = "0.1.0"

__all__ = [
    # Public API
    "construct",
    "parse",
    "serialize",
    "validate",
    "diagnose",
    "inspect",
    "compare",
    "extract",
    "project",
    "evolve",

    # Core model
    "ObjectIdentity",
    "KnowledgeObject",
    "CanonicalRelation",
    "KnowledgeStructure",

    # Diagnostics
    "DiagnosticSeverity",
    "Diagnostic",
    "DiagnosticCollection",

    # Validation
    "ValidationResult",

    # Engine
    "ReferenceEngine",

    # Exceptions
    "SerializationError",

    # Package metadata
    "__version__",
]