"""
CKS Core — Canonical Knowledge Objects.

This module implements the fundamental immutable semantic types defined
by CKS-001 (Core Specification).

Implemented concepts:

- ObjectIdentity
- KnowledgeObject
- CanonicalRelation
- KnowledgeStructure
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Iterator, Mapping


def _freeze(value: Any) -> Any:
    """
    Recursively freeze a canonical value.

    Rules
    -----
    Mapping -> MappingProxyType
    list -> tuple
    tuple -> tuple
    set -> frozenset

    Primitive immutable values are returned unchanged.
    """

    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                key: _freeze(item)
                for key, item in value.items()
            }
        )

    if isinstance(value, list):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(value, tuple):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(value, set):
        return frozenset(
            _freeze(item)
            for item in value
        )

    return value

# ============================================================================
# Internal Helpers
# ============================================================================


def _freeze_mapping(
    mapping: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Recursively freeze a semantic mapping.

    Every nested mapping and collection becomes immutable.
    """

    return MappingProxyType(
        {
            key: _freeze(value)
            for key, value in mapping.items()
        }
    )

# ============================================================================
# Canonical Identity
# ============================================================================


@dataclass(frozen=True, slots=True)
class ObjectIdentity:
    """
    Immutable canonical identity of a Knowledge Object.

    Defined in CKS-001, Section 2.2.
    """

    id: str
    type: str
    name: str


# ============================================================================
# Knowledge Object
# ============================================================================


@dataclass(frozen=True, slots=True)
class KnowledgeObject:
    """
    Fundamental semantic unit of the Canonical Knowledge Structure.

    A Knowledge Object consists of an immutable canonical identity and
    an immutable semantic structure.

    Defined in CKS-001, Sections 1–2.
    """

    identity: ObjectIdentity
    structure: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Freeze the semantic structure.

        KnowledgeObjects are deeply immutable with respect to their
        top-level semantic mapping.
        """

        object.__setattr__(
            self,
            "structure",
            _freeze_mapping(self.structure),
        )


# ============================================================================
# Canonical Relation
# ============================================================================


class CanonicalRelation(KnowledgeObject):
    """
    Canonical semantic relation between Knowledge Objects.

    Defined in CKS-001, Section 8.
    """

    def __init__(
        self,
        identity: ObjectIdentity,
        *,
        participants: Iterable[str],
        relation_type: str,
        structure: Mapping[str, Any] | None = None,
    ) -> None:
        struct = dict(structure or {})

        struct.setdefault("participants", tuple(participants))
        struct.setdefault("relation_type", relation_type)

        object.__setattr__(
            self,
            "identity",
            identity,
        )

        object.__setattr__(
            self,
            "structure",
            _freeze_mapping(struct),
        )

    @property
    def participants(self) -> tuple[str, ...]:
        """
        Return the participating canonical identities.

        A defensive copy is returned to preserve the immutability of the
        underlying CanonicalRelation.
        """
        return tuple(self.structure["participants"])

    @property
    def relation_type(self) -> str:
        """Semantic relation type."""
        return str(self.structure["relation_type"])


# ============================================================================
# Knowledge Structure
# ============================================================================


class KnowledgeStructure:
    """
    Immutable collection of Knowledge Objects.

    Defined in CKS-001, Section 9.
    """

    __slots__ = (
        "_objects",
        "_index",
        "_relations",
    )

    def __init__(self, objects: Iterable[KnowledgeObject]) -> None:
        object_list: list[KnowledgeObject] = []
        index: dict[str, KnowledgeObject] = {}
        relations: list[CanonicalRelation] = []

        for obj in objects:
            oid = obj.identity.id

            if oid in index:
                raise ValueError(
                    f"Duplicate canonical identity '{oid}'."
                )

            index[oid] = obj
            object_list.append(obj)

            if isinstance(obj, CanonicalRelation):
                relations.append(obj)

        self._objects = tuple(object_list)
        self._index = index
        self._relations = tuple(relations)

    # ------------------------------------------------------------------
    # Basic collection protocol
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self) -> Iterator[KnowledgeObject]:
        return iter(self._objects)

    def __contains__(self, identity: str) -> bool:
        return identity in self._index

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def objects(self) -> tuple[KnowledgeObject, ...]:
        """
        Return every Knowledge Object.

        The returned tuple is immutable.
        """
        return self._objects

    def relations(self) -> tuple[CanonicalRelation, ...]:
        """
        Return every Canonical Relation.
        """
        return self._relations

    def get(self, identity: str) -> KnowledgeObject | None:
        """
        Return the object with the given canonical identity.

        Returns
        -------
        KnowledgeObject | None
        """
        return self._index.get(identity)
    
    def _canonical_signature(
        self,
    ) -> tuple[
        tuple[
            str,
            str,
            str,
            tuple[tuple[str, object], ...],
        ],
        ...,
    ]:
        """
        Return the canonical semantic signature of the structure.

        Object order is ignored.

        The signature completely describes the semantic content of the
        KnowledgeStructure.
        """

        signature = []

        for obj in self._objects:

            structure = tuple(
                sorted(obj.structure.items())
            )

            signature.append(
                (
                    obj.identity.id,
                    obj.identity.type,
                    obj.identity.name,
                    structure,
                )
            )

        return tuple(sorted(signature))
    
    def structurally_equivalent(
        self,
        other: object,
    ) -> bool:
        """
        Determine whether two KnowledgeStructures are semantically
        equivalent.

        Two structures are structurally equivalent when every canonical
        object, identity and semantic structure is identical,
        independently of ordering.
        """

        if not isinstance(
            other,
            KnowledgeStructure,
        ):
            return False

        return (
            self._canonical_signature()
            == other._canonical_signature()
        )
    
    def identity_equivalent(
        self,
        other: object,
    ) -> bool:
        """
        Compare only canonical identities.

        This is weaker than structural equivalence.
        """

        if not isinstance(
            other,
            KnowledgeStructure,
        ):
            return False

        return (
            frozenset(self._index)
            == frozenset(other._index)
        )
    
    def __eq__(self, other: object) -> bool:
        """
        Structural equality.

        Equality is defined in terms of structural equivalence.
        """

        return self.structurally_equivalent(other)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"KnowledgeStructure("
            f"objects={len(self._objects)}, "
            f"relations={len(self._relations)})"
        )