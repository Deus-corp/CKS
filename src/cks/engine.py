"""
CKS Engine — Reference Engine Orchestrator.

This module implements the ReferenceEngine class defined in CKS‑006
(Section 4).  It orchestrates the complete validation pipeline and
exposes every canonical operation required by the Canonical Knowledge
Interface (CKS‑007).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .core import KnowledgeStructure
from .diagnostics import Diagnostic, DiagnosticCollection
from .result import ValidationResult
from .serialization import parse as _parse, serialize as _serialize
from .validator import validate as _validate


class ReferenceEngine:
    """Canonical Reference Engine (CKS‑006).

    This class is stateless with respect to canonical semantics.
    Every method is observationally pure and deterministic.
    """

    # ------------------------------------------------------------------
    # Construction & Serialization
    # ------------------------------------------------------------------

    def construct(self, objects: List[Any]) -> KnowledgeStructure:
        """Construct a KnowledgeStructure from a list of KnowledgeObjects."""
        return KnowledgeStructure(objects)

    def parse(self, source: str | dict) -> KnowledgeStructure:
        """Parse a serialized representation into a KnowledgeStructure."""
        return _parse(source)

    def serialize(self, structure: KnowledgeStructure) -> str:
        """Serialize a KnowledgeStructure to its canonical JSON representation."""
        return _serialize(structure)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, structure: KnowledgeStructure) -> ValidationResult:
        """Execute the complete canonical validation pipeline."""
        return _validate(structure)

    def diagnose(self, structure: KnowledgeStructure) -> DiagnosticCollection:
        """Return diagnostics without a full ValidationResult wrapper."""
        result = _validate(structure)
        return result.diagnostics

    # ------------------------------------------------------------------
    # Inspection & Comparison
    # ------------------------------------------------------------------

    def inspect(self, structure: KnowledgeStructure) -> Dict[str, object]:
        """Return a canonical summary of the structure's observable properties."""
        return {
            "object_count": len(structure.objects),
            "relation_count": len(structure.relations()),
            "unique_types": sorted({
                obj.identity.type for obj in structure.objects
            }),
        }

    def compare(
        self,
        left: KnowledgeStructure,
        right: KnowledgeStructure,
    ) -> Dict[str, object]:
        """Compare two KnowledgeStructures for structural equivalence."""
        left_ids = sorted(obj.identity.id for obj in left.objects)
        right_ids = sorted(obj.identity.id for obj in right.objects)
        return {
            "identical_ids": left_ids == right_ids,
            "left_count": len(left_ids),
            "right_count": len(right_ids),
        }

    def extract(
        self,
        structure: KnowledgeStructure,
        identity: str,
    ) -> Optional[Any]:
        """Extract a single KnowledgeObject by its canonical identity."""
        return structure.get(identity)

    def project(
        self,
        structure: KnowledgeStructure,
        identities: List[str],
    ) -> KnowledgeStructure:
        """Project a subset of KnowledgeObjects into a new KnowledgeStructure."""
        selected = []
        for oid in identities:
            obj = structure.get(oid)
            if obj is not None:
                selected.append(obj)
        return KnowledgeStructure(selected)

    # ------------------------------------------------------------------
    # Evolution
    # ------------------------------------------------------------------

    def evolve(
        self,
        structure: KnowledgeStructure,
        transformations: List[Any],
    ) -> KnowledgeStructure:
        """Apply a sequence of admissible structural evolutions.

        .. note::
            Currently a placeholder.  Full evolution semantics are
            defined in CKS‑004 and will be implemented in a future
            release.
        """
        # For now, return the structure unchanged.
        _ = transformations  # unused
        return structure