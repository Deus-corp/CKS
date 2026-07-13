"""
CKS Interface — Canonical Public API.

This module provides the canonical entry points defined by the
Canonical Knowledge Interface (CKS-007).

Applications should normally import functions from this module rather
than interacting directly with internal implementation modules.

Every exported function is:

    • deterministic
    • observationally pure
    • implementation-independent
"""

from __future__ import annotations

from typing import Any
from typing import Iterable
from typing import Mapping

from .core import KnowledgeObject
from .core import KnowledgeStructure

from .diagnostics import DiagnosticCollection
from .engine import ReferenceEngine
from .result import ValidationResult
from .serialization import SerializationError

__all__ = [
    # Construction
    "construct",
    "parse",
    "serialize",

    # Validation
    "validate",
    "diagnose",

    # Inspection
    "inspect",
    "compare",
    "extract",
    "project",

    # Evolution
    "evolve",

    # Public classes
    "ReferenceEngine",
    "SerializationError",
]

# Canonical shared ReferenceEngine.
#
# The ReferenceEngine is stateless and observationally pure, therefore a
# single process-wide instance is sufficient.
_ENGINE = ReferenceEngine()

# =============================================================================
# Canonical Public API
# =============================================================================

# ---------------------------------------------------------------------------
# Construction & Serialization
# ---------------------------------------------------------------------------

def construct(
    objects: Iterable[KnowledgeObject],
) -> KnowledgeStructure:
    """
    Construct a canonical KnowledgeStructure.

    This is the canonical entry point for building structures from
    Knowledge Objects.
    """
    return _ENGINE.construct(objects)


def parse(
    source: str | dict,
) -> KnowledgeStructure:
    """
    Parse canonical JSON into a KnowledgeStructure.

    The accepted serialization format is defined by CKS-003.
    """
    return _ENGINE.parse(source)


def serialize(
    structure: KnowledgeStructure,
) -> str:
    """
    Serialize a KnowledgeStructure to canonical JSON.

    The resulting representation is suitable for canonical round-trip
    serialization.
    """
    return _ENGINE.serialize(structure)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(
    structure: KnowledgeStructure,
) -> ValidationResult:
    """
    Execute the complete canonical validation pipeline.

    This function corresponds to the Validator defined in CKS-005.
    """
    return _ENGINE.validate(structure)


def diagnose(
    structure: KnowledgeStructure,
) -> DiagnosticCollection:
    """
    Return only diagnostics produced during validation.

    Unlike validate(), this function omits the ValidationResult wrapper.
    """
    return _ENGINE.diagnose(structure)


# ---------------------------------------------------------------------------
# Inspection & Comparison
# ---------------------------------------------------------------------------

def inspect(
    structure: KnowledgeStructure,
) -> Mapping[str, object]:
    """
    Return a canonical summary of the structure's observable properties.
    """
    return _ENGINE.inspect(structure)


def compare(
    left: KnowledgeStructure,
    right: KnowledgeStructure,
) -> Mapping[str, object]:
    """
    Compare two KnowledgeStructures.

    Comparison is based on canonical structural equivalence.
    """
    return _ENGINE.compare(left, right)


def extract(
    structure: KnowledgeStructure,
    identity: str,
) -> KnowledgeObject | None:
    """
    Extract a single KnowledgeObject by its canonical identity.
    """
    return _ENGINE.extract(structure, identity)


def project(
    structure: KnowledgeStructure,
    identities: Iterable[str],
) -> KnowledgeStructure:
    """
    Project a subset of a KnowledgeStructure.

    Missing identities are ignored.
    """
    return _ENGINE.project(structure, identities)


# ---------------------------------------------------------------------------
# Evolution
# ---------------------------------------------------------------------------

def evolve(
    structure: KnowledgeStructure,
    transformations: Iterable[Any],
) -> KnowledgeStructure:
    """
    Apply a sequence of admissible structural evolutions.

    .. note::
        Full evolution semantics are defined in CKS‑004 and will be
        implemented in a future release.
    """
    return _ENGINE.evolve(structure, transformations)