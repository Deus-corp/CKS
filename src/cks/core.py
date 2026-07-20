"""
CKS Core — Canonical Knowledge Objects.
"""

from __future__ import annotations

import hashlib
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


# ============================================================================
# Canonical (Merkle-style) Hashing
# ============================================================================
#
# _canonical_hash(value) is a deterministic digest of a frozen CKS
# value, used to give KnowledgeObject/CanonicalRelation a leaf hash and
# KnowledgeStructure a root hash for O(1) structural-equivalence
# comparison (see KnowledgeStructure.structurally_equivalent below).
#
# Every recursive call returns a FIXED-SIZE 32-byte SHA-256 digest.
# This is what makes the encoding provably unambiguous without needing
# a length prefix between every concatenated piece: once a child value
# has been reduced to a fixed-width digest, concatenating any number
# of such digests can never be mis-parsed as a different grouping of
# digests, the way concatenating variable-length strings can (e.g.
# str(tuple(...)) is NOT a safe hash preimage -- Python's repr rules
# for 1-tuples vs 2-tuples happen to block the simplest such collision,
# but that is an accident of CPython's repr, not a guaranteed property
# of the encoding). Only true leaves (str/int/float/bool/None/...) and
# the element *count* of a container are length-prefixed, since those
# are the only variable-width pieces left once children are digests.
#
# This hash is used for equivalence checks and diffing, not as a
# cryptographic commitment exposed outside the process -- a negligible
# collision probability under SHA-256 is an accepted trade-off for
# O(1) comparison, consistent with how e.g. git or Merkle-based
# storage systems treat content hashes.

_HASH_TAG_MAP = b"map"
_HASH_TAG_SEQ = b"seq"
_HASH_TAG_SET = b"set"
_HASH_TAG_LEAF = b"leaf"


def _uint32(n: int) -> bytes:
    return n.to_bytes(4, "big", signed=False)


def _canonical_hash(value: Any) -> bytes:
    """Return a 32-byte deterministic digest of a frozen CKS value."""
    if isinstance(value, Mapping):
        entries = sorted(
            (_canonical_hash(key), _canonical_hash(val))
            for key, val in value.items()
        )
        body = b"".join(k_digest + v_digest for k_digest, v_digest in entries)
        return hashlib.sha256(_HASH_TAG_MAP + _uint32(len(entries)) + body).digest()

    if isinstance(value, (list, tuple)):
        body = b"".join(_canonical_hash(item) for item in value)
        return hashlib.sha256(_HASH_TAG_SEQ + _uint32(len(value)) + body).digest()

    if isinstance(value, (set, frozenset)):
        digests = sorted(_canonical_hash(item) for item in value)
        body = b"".join(digests)
        return hashlib.sha256(_HASH_TAG_SET + _uint32(len(digests)) + body).digest()

    # Leaf value (str, int, float, bool, None, ...). Both the type
    # name and the value's repr are individually length-prefixed, so
    # e.g. the leaf (type="str", value="5") can never be confused with
    # (type="int", value="5") or with a differently-split byte stream.
    type_name = type(value).__name__.encode("ascii")
    value_bytes = repr(value).encode("utf-8")
    payload = (
        _uint32(len(type_name)) + type_name
        + _uint32(len(value_bytes)) + value_bytes
    )
    return hashlib.sha256(_HASH_TAG_LEAF + payload).digest()


def _compute_leaf_hash(identity: "ObjectIdentity", structure: Mapping[str, Any]) -> bytes:
    """Merkle leaf hash for one KnowledgeObject: its identity plus its
    (already-frozen) semantic structure."""
    identity_tuple = (identity.id, identity.type, identity.name)
    return _canonical_hash((identity_tuple, structure))


@dataclass(frozen=True, slots=True)
class ObjectIdentity:
    id: str
    type: str
    name: str


@dataclass(frozen=True, slots=True)
class KnowledgeObject:
    identity: ObjectIdentity
    structure: Mapping[str, Any] = field(default_factory=dict)

    #: Merkle leaf hash, computed once in __post_init__. Not part of
    #: the dataclass's generated __eq__/__repr__ (init=False,
    #: compare=False) since it is fully determined by identity+structure
    #: -- it is a cached derivation, not independent state.
    _hash: bytes = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        frozen_structure = _freeze_mapping(self.structure)
        object.__setattr__(self, "structure", frozen_structure)
        object.__setattr__(self, "_hash", _compute_leaf_hash(self.identity, frozen_structure))

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
        frozen_struct = _freeze_mapping(struct)
        object.__setattr__(self, "identity", identity)
        object.__setattr__(self, "structure", frozen_struct)
        object.__setattr__(self, "_hash", _compute_leaf_hash(identity, frozen_struct))

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
    __slots__ = ("_objects", "_index", "_relations", "_root_hash", "_identity_hash")

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

        # Merkle root: hash of the sorted set of leaf hashes. Sorting
        # makes the root independent of construction/insertion order,
        # matching the order-independence _canonical_signature already
        # guaranteed before this hash existed.
        sorted_leaf_hashes = sorted(obj._hash for obj in object_list)
        self._root_hash = hashlib.sha256(
            _HASH_TAG_SET + _uint32(len(sorted_leaf_hashes)) + b"".join(sorted_leaf_hashes)
        ).digest()

        # A second, narrower hash over identities only (ids present),
        # backing identity_equivalent -- unaffected by content changes.
        sorted_ids = sorted(self._index.keys())
        self._identity_hash = hashlib.sha256(
            _HASH_TAG_SET + _uint32(len(sorted_ids))
            + b"".join(_canonical_hash(i) for i in sorted_ids)
        ).digest()

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

    @property
    def root_hash(self) -> str:
        """Hex digest of the Merkle root, for external comparison/logging."""
        return self._root_hash.hex()

    def _canonical_signature(self) -> tuple:
        signature = []
        for obj in self._objects:
            structure = _normalize_structure(obj.structure)
            signature.append((obj.identity.id, obj.identity.type, obj.identity.name, structure))
        return tuple(sorted(signature))

    def structurally_equivalent(self, other: object) -> bool:
        """
        Whether `other` has the same content as this structure.

        Implemented as O(1) root-hash comparison rather than the
        O(N log N) signature comparison this used before: two
        structures with the same objects (any order) hash to the same
        SHA-256 root, and a hash collision between genuinely different
        structures is cryptographically negligible -- the same
        trade-off git and other Merkle-based systems make for content
        equality.
        """
        if not isinstance(other, KnowledgeStructure):
            return False
        return self._root_hash == other._root_hash

    def identity_equivalent(self, other: object) -> bool:
        if not isinstance(other, KnowledgeStructure):
            return False
        return self._identity_hash == other._identity_hash

    def __eq__(self, other: object) -> bool:
        return self.structurally_equivalent(other)

    def __hash__(self) -> int:
        # KnowledgeStructure was previously unhashable (an __eq__
        # without a matching __hash__ makes Python set __hash__ =
        # None). Now that equality is itself hash-based, exposing a
        # consistent __hash__ is both correct (equal objects already
        # share a root hash, so they trivially share this too) and
        # useful -- e.g. structures as dict keys or set members.
        return hash(self._root_hash)

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

    # ------------------------------------------------------------------
    # Structural Diff
    # ------------------------------------------------------------------

    def diff(self, target: "KnowledgeStructure") -> list[Any]:
        """
        Compute the ordered list of StructuralOperators that, applied
        via cks.evolution.compose(self, ops), reconstruct `target`.

        Cascade correctness: RemoveObject.apply() removes not just the
        target object but every CanonicalRelation that references it
        (see RemoveObject's own docstring/contract). A diff that only
        compares "which ids differ between source and target" would
        miss this: a relation whose own hash is UNCHANGED but which
        references an object being removed or replaced would be
        silently destroyed by that cascade and never scheduled to
        come back -- the resulting structure would then NOT actually
        equal `target`, defeating the purpose of a diff. This method
        explicitly finds every such relation and folds it into the
        remove/add sets, even though from a pure id-comparison
        standpoint it "didn't change".

        Operation order -- relations removed, then objects removed,
        then objects added, then relations added -- guarantees no
        relation ever transiently references a nonexistent object
        during application (preserving referential integrity, i.e.
        NoDanglingRelationConstraint, at every intermediate step).
        """
        # Imported lazily (not at module scope) to avoid a circular
        # import: cks.evolution imports KnowledgeStructure/
        # CanonicalRelation from this module, so importing
        # cks.evolution back at module scope here would make the two
        # modules unable to finish initializing each other.
        from cks.evolution import AddObject, AddRelation, RemoveObject, RemoveRelation

        source_ids = set(self._index.keys())
        target_ids = set(target._index.keys())
        common_ids = source_ids & target_ids

        added_ids = target_ids - source_ids
        removed_ids = source_ids - target_ids
        modified_ids = {
            oid for oid in common_ids
            if self._index[oid]._hash != target._index[oid]._hash
        }

        def is_relation(structure: "KnowledgeStructure", oid: str) -> bool:
            return isinstance(structure._index[oid], CanonicalRelation)

        # Direct (non-cascade) changes, split into objects vs relations.
        direct_remove_relations = {oid for oid in (removed_ids | modified_ids) if is_relation(self, oid)}
        direct_remove_objects = {oid for oid in (removed_ids | modified_ids) if not is_relation(self, oid)}
        direct_add_relations = {oid for oid in (added_ids | modified_ids) if is_relation(target, oid)}
        direct_add_objects = {oid for oid in (added_ids | modified_ids) if not is_relation(target, oid)}

        # Cascade: every relation in SOURCE that references an object
        # about to disappear (removed outright, or modified -- which
        # requires remove-then-add since there is no in-place modify
        # operator) will be cascade-deleted by RemoveObject.apply(),
        # regardless of whether it was otherwise scheduled for removal.
        cascade_relations = {
            rel.identity.id
            for rel in self._relations
            if any(pid in direct_remove_objects for pid in rel.participants)
        }
        cascade_only_relations = cascade_relations - direct_remove_relations

        all_remove_relations = direct_remove_relations | cascade_only_relations
        # A cascade-only relation must be re-added afterwards using
        # target's copy IF it still exists there; if it doesn't, the
        # cascade deletion was correct and nothing more is needed.
        all_add_relations = direct_add_relations | (cascade_only_relations & target_ids)

        operators: list[Any] = []
        for rid in all_remove_relations:
            operators.append(RemoveRelation(rid))
        for oid in direct_remove_objects:
            operators.append(RemoveObject(oid))
        for oid in direct_add_objects:
            operators.append(AddObject(target._index[oid]))
        for rid in all_add_relations:
            operators.append(AddRelation(target._index[rid]))

        return operators