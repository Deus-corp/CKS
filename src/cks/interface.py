"""
CKS Interface — Public API.

This module exposes the canonical public API required by the
CKS‑B001‑PY specification.  All functions delegate to a shared
ReferenceEngine instance and are observationally pure.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union

from .core import KnowledgeObject, KnowledgeStructure
from .diagnostics import DiagnosticCollection
from .engine import ReferenceEngine
from .result import ValidationResult
from .serialization import SerializationError

__all__ = [
    "validate",
    "parse",
    "serialize",
    "construct",
    "diagnose",
    "inspect",
    "compare",
    "extract",
    "project",
    "evolve",
    "ReferenceEngine",
    "SerializationError",
]

# Shared engine instance – stateless, thread‑safe.
_engine = ReferenceEngine()


# ---------------------------------------------------------------------------
# Construction & Serialization
# ---------------------------------------------------------------------------

def construct(objects: List[KnowledgeObject]) -> KnowledgeStructure:
    """Construct a KnowledgeStructure from a list of KnowledgeObjects."""
    return _engine.construct(objects)


def parse(source: Union[str, dict]) -> KnowledgeStructure:
    """Parse a serialized representation into a KnowledgeStructure."""
    return _engine.parse(source)


def serialize(structure: KnowledgeStructure) -> str:
    """Serialize a KnowledgeStructure to its canonical JSON representation."""
    return _engine.serialize(structure)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(structure: KnowledgeStructure) -> ValidationResult:
    """Validate a Canonical Knowledge Structure."""
    return _engine.validate(structure)


def diagnose(structure: KnowledgeStructure) -> DiagnosticCollection:
    """Return diagnostics for a structure without a full ValidationResult."""
    return _engine.diagnose(structure)


# ---------------------------------------------------------------------------
# Inspection & Comparison
# ---------------------------------------------------------------------------

def inspect(structure: KnowledgeStructure) -> Dict[str, object]:
    """Return a canonical summary of the structure's observable properties."""
    return _engine.inspect(structure)


def compare(
    left: KnowledgeStructure,
    right: KnowledgeStructure,
) -> Dict[str, object]:
    """Compare two KnowledgeStructures for structural equivalence."""
    return _engine.compare(left, right)


def extract(
    structure: KnowledgeStructure,
    identity: str,
) -> Optional[KnowledgeObject]:
    """Extract a single KnowledgeObject by its canonical identity."""
    return _engine.extract(structure, identity)


def project(
    structure: KnowledgeStructure,
    identities: List[str],
) -> KnowledgeStructure:
    """Project a subset of KnowledgeObjects into a new KnowledgeStructure."""
    return _engine.project(structure, identities)


# ---------------------------------------------------------------------------
# Evolution
# ---------------------------------------------------------------------------

def evolve(
    structure: KnowledgeStructure,
    transformations: List,
) -> KnowledgeStructure:
    """Apply a sequence of admissible structural evolutions.

    .. note::
        Full evolution semantics are defined in CKS‑004 and will be
        implemented in a future release.
    """
    return _engine.evolve(structure, transformations)