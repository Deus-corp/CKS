"""
Canonical Knowledge Structure (CKS).

Reference implementation of the Canonical Knowledge Structure (CKS)
specifications.

The package exposes the canonical public API defined by CKS-007 together
with the immutable canonical data model.

Typical usage:

    import cks

    structure = cks.parse(source)
    result = cks.validate(structure)

Advanced users may instantiate their own ReferenceEngine or build
custom validation pipelines using the lower-level modules.

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

VERSION = tuple(
    int(part)
    for part in __version__.split(".")
)

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
    "VERSION",
]