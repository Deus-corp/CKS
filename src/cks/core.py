"""
CKS Core — Canonical Knowledge Objects.

This module implements the fundamental immutable types defined in
CKS‑001 (Core Specification), Sections 1–2 and 8–9.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Canonical Identity
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ObjectIdentity:
    """Canonical identity of a Knowledge Object (CKS‑001, Section 2.2)."""

    id: str          # globally unique canonical identifier
    type: str        # canonical object type (Definition, Theorem, …)
    name: str        # canonical human‑readable designation


# ---------------------------------------------------------------------------
# Knowledge Object
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class KnowledgeObject:
    """Fundamental semantic unit of CKS (CKS‑001, Sections 1–2).

    Attributes
    ----------
    identity : ObjectIdentity
        Immutable canonical identity.
    structure : dict
        Canonical semantic structure (content, relations, metadata).
    """

    identity: ObjectIdentity
    structure: Dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Canonical Relation
# ---------------------------------------------------------------------------

class CanonicalRelation(KnowledgeObject):
    """Specialised Knowledge Object that represents a structural relationship
    between two or more Knowledge Objects (CKS‑001, Section 8).

    Parameters
    ----------
    identity : ObjectIdentity
        Canonical identity of the relation.
    participants : list of str
        Canonical identifiers of the participating Knowledge Objects.
    relation_type : str
        Semantic type of the relationship.
    structure : dict, optional
        Additional canonical semantic structure.
    """

    def __init__(
        self,
        identity: ObjectIdentity,
        *,
        participants: Iterable[str],
        relation_type: str,
        structure: Optional[Dict] = None,
    ) -> None:
        # Because KnowledgeObject is frozen we must bypass the dataclass
        # machinery to set the attributes.
        object.__setattr__(self, "identity", identity)
        struct = dict(structure or {})
        struct.setdefault("participants", list(participants))
        struct.setdefault("relation_type", relation_type)
        object.__setattr__(self, "structure", struct)

    @property
    def participants(self) -> List[str]:
        """Return the canonical identities of the participating objects."""
        return self.structure.get("participants", [])

    @property
    def relation_type(self) -> str:
        """Return the semantic type of this relation."""
        return self.structure.get("relation_type", "")


# ---------------------------------------------------------------------------
# Knowledge Structure
# ---------------------------------------------------------------------------

class KnowledgeStructure:
    """Immutable collection of Knowledge Objects (CKS‑001, Section 9).

    Parameters
    ----------
    objects : iterable of KnowledgeObject
        The Knowledge Objects that form this structure.  Every object must
        have a unique canonical identity.

    Raises
    ------
    ValueError
        If duplicate identities are detected.
    """

    def __init__(self, objects: Iterable[KnowledgeObject]) -> None:
        seen: Dict[str, str] = {}
        objs: List[KnowledgeObject] = []
        for obj in objects:
            oid = obj.identity.id
            if oid in seen:
                raise ValueError(
                    f"Duplicate canonical identity '{oid}' "
                    f"(first seen as {seen[oid]!r})"
                )
            seen[oid] = obj.identity.name
            objs.append(obj)
        # Store the objects in an immutable tuple – observational purity.
        self._objects: Tuple[KnowledgeObject, ...] = tuple(objs)

    # -- read-only accessors ------------------------------------------------

    @property
    def objects(self) -> Tuple[KnowledgeObject, ...]:
        """Return all Knowledge Objects in this structure."""
        return self._objects

    def relations(self) -> List[CanonicalRelation]:
        """Return every CanonicalRelation contained in this structure."""
        return [o for o in self._objects if isinstance(o, CanonicalRelation)]

    def get(self, identity: str) -> Optional[KnowledgeObject]:
        """Return the Knowledge Object with the given canonical identity,
        or ``None`` if no such object exists.
        """
        for obj in self._objects:
            if obj.identity.id == identity:
                return obj
        return None

    def __repr__(self) -> str:
        return (
            f"<KnowledgeStructure "
            f"objects={len(self._objects)} "
            f"relations={len(self.relations())}>"
        )