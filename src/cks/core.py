"""
CKS Core — Canonical Knowledge Objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Iterator, Mapping


def _freeze(value: Any) -> Any:
    """Recursively freeze a canonical value."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _freeze_mapping(mapping: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType({key: _freeze(value) for key, value in mapping.items()})


@dataclass(frozen=True, slots=True)
class ObjectIdentity:
    id: str
    type: str
    name: str


@dataclass(frozen=True, slots=True)
class KnowledgeObject:
    identity: ObjectIdentity
    structure: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "structure", _freeze_mapping(self.structure))

    # ------------------------------------------------------------------
    # Copy semantics
    # ------------------------------------------------------------------
    # KnowledgeObject is immutable by contract, so copy/deepcopy can
    # safely return the same instance rather than attempting to clone
    # the internal MappingProxyType (which the stdlib copy module
    # cannot pickle-based deep-copy).
    def __copy__(self) -> "KnowledgeObject":
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> "KnowledgeObject":
        memo[id(self)] = self
        return self


class CanonicalRelation(KnowledgeObject):
    def __init__(
        self,
        identity: ObjectIdentity,
        *,
        participants: Iterable[str],
        relation_type: str,
        structure: Mapping[str, Any] | None = None,
    ) -> None:
        struct = dict(structure or {})
        frozen_participants = tuple(participants)
        for key, expected in (
            ("participants", frozen_participants),
            ("relation_type", relation_type),
        ):
            if key in struct:
                existing = struct[key]
                if key == "participants" and isinstance(existing, list):
                    existing = tuple(existing)
                if existing != expected:
                    raise ValueError(
                        f"Conflicting value for '{key}' in structure: "
                        f"expected {expected!r}, got {struct[key]!r}"
                    )
        struct["participants"] = frozen_participants
        struct["relation_type"] = relation_type
        object.__setattr__(self, "identity", identity)
        object.__setattr__(self, "structure", _freeze_mapping(struct))

    @property
    def participants(self) -> tuple[str, ...]:
        return tuple(self.structure["participants"])

    @property
    def relation_type(self) -> str:
        return str(self.structure["relation_type"])


def _normalize_structure(structure: Mapping[str, Any]) -> tuple[tuple[str, object], ...]:
    frozen = _freeze_mapping(structure)
    return tuple(sorted(frozen.items()))


class KnowledgeStructure:
    __slots__ = ("_objects", "_index", "_relations")

    def __init__(self, objects: Iterable[KnowledgeObject]) -> None:
        object_list: list[KnowledgeObject] = []
        index: dict[str, KnowledgeObject] = {}
        relations: list[CanonicalRelation] = []
        for obj in objects:
            oid = obj.identity.id
            if oid in index:
                raise ValueError(f"Duplicate canonical identity '{oid}'.")
            index[oid] = obj
            object_list.append(obj)
            if isinstance(obj, CanonicalRelation):
                relations.append(obj)
        self._objects = tuple(object_list)
        self._index = index
        self._relations = tuple(relations)

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self) -> Iterator[KnowledgeObject]:
        return iter(self._objects)

    def __contains__(self, identity: str) -> bool:
        return identity in self._index

    @property
    def objects(self) -> tuple[KnowledgeObject, ...]:
        return self._objects

    def relations(self) -> tuple[CanonicalRelation, ...]:
        return self._relations

    def get(self, identity: str) -> KnowledgeObject | None:
        return self._index.get(identity)

    def _canonical_signature(self) -> tuple:
        signature = []
        for obj in self._objects:
            structure = _normalize_structure(obj.structure)
            signature.append((obj.identity.id, obj.identity.type, obj.identity.name, structure))
        return tuple(sorted(signature))

    def structurally_equivalent(self, other: object) -> bool:
        if not isinstance(other, KnowledgeStructure):
            return False
        return self._canonical_signature() == other._canonical_signature()

    def identity_equivalent(self, other: object) -> bool:
        if not isinstance(other, KnowledgeStructure):
            return False
        return frozenset(self._index) == frozenset(other._index)

    def __eq__(self, other: object) -> bool:
        return self.structurally_equivalent(other)

    def __repr__(self) -> str:
        return f"KnowledgeStructure(objects={len(self._objects)}, relations={len(self._relations)})"

    # ------------------------------------------------------------------
    # Copy semantics
    # ------------------------------------------------------------------
    # KnowledgeStructure is immutable by contract. Returning self
    # avoids deep-copying internal MappingProxyType-bearing objects.
    def __copy__(self) -> "KnowledgeStructure":
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> "KnowledgeStructure":
        memo[id(self)] = self
        return self