"""
CKS Engine — Reference Engine Orchestrator.

This module implements the ReferenceEngine class defined in CKS-006
(Section 4). It orchestrates the complete validation pipeline and
exposes every canonical operation required by the Canonical Knowledge
Interface (CKS-007).
"""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .core import KnowledgeObject, KnowledgeStructure
from .diagnostics import DiagnosticCollection
from .result import ValidationResult
from .serialization import parse as _parse
from .serialization import serialize as _serialize
from .validator import validate as _validate


# =============================================================================
# Reference Engine
# =============================================================================


@dataclass(frozen=True, slots=True)
class ReferenceEngine:
    """
    Canonical Reference Engine.

    This class realises the Reference Engine defined by CKS-006.

    The engine is intentionally stateless.
    Multiple validation requests may safely reuse the same engine instance.

    Every operation is:

        • deterministic
        • observationally pure
        • implementation-independent
    """

    VERSION: str = "0.1.0"

    # ------------------------------------------------------------------
    # Construction & Serialization
    # ------------------------------------------------------------------

    def construct(
        self,
        objects: Iterable[KnowledgeObject],
    ) -> KnowledgeStructure:
        """
        Construct a canonical KnowledgeStructure.

        The resulting structure preserves canonical identity and
        observational purity.
        """

        return KnowledgeStructure(objects)

    def parse(
        self,
        source: str | dict,
    ) -> KnowledgeStructure:
        """
        Parse a serialized representation into a KnowledgeStructure.
        """

        return _parse(source)

    def serialize(
        self,
        structure: KnowledgeStructure,
    ) -> str:
        """
        Serialize a KnowledgeStructure to canonical JSON.
        """

        return _serialize(structure)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        structure: KnowledgeStructure,
    ) -> ValidationResult:
        """
        Execute the complete canonical validation pipeline.
        """

        return _validate(structure)

    def diagnose(
        self,
        structure: KnowledgeStructure,
    ) -> DiagnosticCollection:
        """
        Return only diagnostics produced during validation.
        """

        return self.validate(structure).diagnostics

    # ------------------------------------------------------------------
    # Inspection & Comparison
    # ------------------------------------------------------------------

    def inspect(
        self,
        structure: KnowledgeStructure,
    ) -> Mapping[str, object]:
        """
        Return an observable summary of a KnowledgeStructure.

        The summary is canonical and does not expose implementation
        details.
        """

        relation_types = sorted(
            {
                relation.relation_type
                for relation in structure.relations()
            }
        )

        return {
            "object_count": len(structure.objects),
            "relation_count": len(structure.relations()),
            "object_types": sorted(
                {
                    obj.identity.type
                    for obj in structure.objects
                }
            ),
            "relation_types": relation_types,
            "identities": tuple(
                obj.identity.id
                for obj in structure
            ),
        }

    def compare(
        self,
        left: KnowledgeStructure,
        right: KnowledgeStructure,
    ) -> Mapping[str, object]:
        """
        Compare two KnowledgeStructures.

        Comparison is based on canonical structural equivalence.
        """

        left_ids = sorted(obj.identity.id for obj in left.objects)
        right_ids = sorted(obj.identity.id for obj in right.objects)

        return {
            "equivalent": left_ids == right_ids,
            "left_objects": len(left.objects),
            "right_objects": len(right.objects),
            "left_relations": len(left.relations()),
            "right_relations": len(right.relations()),
        }

    def extract(
        self,
        structure: KnowledgeStructure,
        identity: str,
    ) -> KnowledgeObject | None:
        """
        Extract a single KnowledgeObject by canonical identity.
        """

        return structure.get(identity)
    
    def project(
        self,
        structure: KnowledgeStructure,
        identities: Iterable[str],
    ) -> KnowledgeStructure:
        """
        Project a subset of a KnowledgeStructure.

        Missing identities are ignored.
        """

        return KnowledgeStructure(
            obj
            for identity in identities
            if (obj := structure.get(identity)) is not None
        )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(version={self.VERSION!r})"
        )


__all__ = ["ReferenceEngine"]