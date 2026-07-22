"""
Unit tests for the canonical core model.

Covers the immutable semantic objects defined by CKS-001.

This module tests only the core object model. Validation,
serialization and engine behaviour are tested separately.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from cks.core import (
    CanonicalRelation,
    KnowledgeObject,
    KnowledgeStructure,
    ObjectIdentity,
)


# =============================================================================
# Helper factories
# =============================================================================


def make_object(
    oid: str,
    otype: str = "Definition",
    name: str | None = None,
) -> KnowledgeObject:
    return KnowledgeObject(
        identity=ObjectIdentity(
            id=oid,
            type=otype,
            name=name or oid,
        )
    )


def make_relation(
    oid: str,
    participants: list[str],
    relation_type: str = "depends_on",
) -> CanonicalRelation:
    return CanonicalRelation(
        identity=ObjectIdentity(
            id=oid,
            type="Relation",
            name=oid,
        ),
        participants=participants,
        relation_type=relation_type,
    )


def make_structure() -> KnowledgeStructure:
    return KnowledgeStructure(
        [
            make_object("obj-1"),
            make_object("obj-2"),
            make_relation(
                "rel-1",
                ["obj-1", "obj-2"],
            ),
        ]
    )


# =============================================================================
# ObjectIdentity
# =============================================================================


def test_object_identity_is_immutable():
    identity = ObjectIdentity(
        id="obj",
        type="Definition",
        name="Example",
    )

    with pytest.raises(FrozenInstanceError):
        identity.id = "other"


# =============================================================================
# KnowledgeObject
# =============================================================================


def test_knowledge_object_is_immutable():
    obj = make_object("obj")

    with pytest.raises(FrozenInstanceError):
        obj.identity = ObjectIdentity(
            id="new",
            type="Definition",
            name="New",
        )


# =============================================================================
# CanonicalRelation
# =============================================================================


def test_relation_properties():
    relation = make_relation(
        "rel",
        ["a", "b"],
        "depends_on",
    )

    assert relation.participants == ("a", "b")
    assert isinstance(relation.participants, tuple)
    assert relation.relation_type == "depends_on"


# =============================================================================
# KnowledgeStructure
# =============================================================================


def test_structure_length():
    structure = make_structure()

    assert len(structure) == 3


def test_structure_iteration():
    structure = make_structure()

    identities = [
        obj.identity.id
        for obj in structure
    ]

    assert identities == [
        "obj-1",
        "obj-2",
        "rel-1",
    ]


def test_structure_contains():
    structure = make_structure()

    assert "obj-1" in structure
    assert "obj-2" in structure
    assert "rel-1" in structure

    assert "missing" not in structure


def test_structure_get():
    structure = make_structure()

    obj = structure.get("obj-1")

    assert obj is not None
    assert obj.identity.id == "obj-1"

    assert structure.get("missing") is None


def test_structure_relations():
    structure = make_structure()

    relations = structure.relations()

    assert len(relations) == 1
    assert relations[0].identity.id == "rel-1"


def test_duplicate_identity_raises():
    with pytest.raises(ValueError):
        KnowledgeStructure(
            [
                make_object("dup"),
                make_object("dup"),
            ]
        )


# =============================================================================
# Structural equivalence
# =============================================================================


def test_structurally_equivalent():
    left = make_structure()
    right = make_structure()

    assert left.structurally_equivalent(right)


def test_not_structurally_equivalent():
    left = make_structure()

    right = KnowledgeStructure(
        [
            make_object("obj-1"),
            make_object("obj-3"),
        ]
    )

    assert not left.structurally_equivalent(right)


# =============================================================================
# Identity equivalence
# =============================================================================
#
# identity_equivalent() had no direct test coverage anywhere in the
# suite before this. That gap is exactly how a change to
# KnowledgeStructure._identity_hash's internal construction (caching
# each KnowledgeObject's id hash instead of recomputing it from
# scratch on every KnowledgeStructure.__init__ call) could have
# silently changed its observable behaviour without any test noticing.


def test_identity_equivalent_same_ids_different_content():
    """Same ids, different (non-id) content -> identity-equivalent but not structurally equivalent."""
    left = KnowledgeStructure(
        [make_object("obj-1", name="Alpha")],
    )
    right = KnowledgeStructure(
        [make_object("obj-1", name="Beta")],
    )

    assert left.identity_equivalent(right)
    assert not left.structurally_equivalent(right)


def test_identity_equivalent_different_ids():
    left = KnowledgeStructure([make_object("obj-1")])
    right = KnowledgeStructure([make_object("obj-2")])

    assert not left.identity_equivalent(right)


def test_identity_equivalent_is_order_independent():
    """Same id set, inserted in a different order -> still identity-equivalent."""
    left = KnowledgeStructure(
        [make_object("obj-1"), make_object("obj-2"), make_object("obj-3")],
    )
    right = KnowledgeStructure(
        [make_object("obj-3"), make_object("obj-1"), make_object("obj-2")],
    )

    assert left.identity_equivalent(right)


def test_identity_equivalent_reflexive_for_relations():
    """Relations (which bypass KnowledgeObject.__post_init__ via their own __init__) must also be covered."""
    left = make_structure()
    right = make_structure()

    assert left.identity_equivalent(right)


# =============================================================================
# Representation
# =============================================================================


def test_repr():
    structure = make_structure()

    text = repr(structure)

    assert "KnowledgeStructure" in text
    assert "objects=3" in text
    assert "relations=1" in text


def test_knowledge_object_structure_is_immutable():
    obj = KnowledgeObject(
        identity=ObjectIdentity(
            "obj",
            "Concept",
            "Object",
        ),
        structure={"a": 1},
    )

    with pytest.raises(TypeError):
        obj.structure["b"] = 2

def test_relation_structure_is_immutable():
    relation = CanonicalRelation(
        identity=ObjectIdentity(
            "r",
            "CanonicalRelation",
            "R",
        ),
        participants=["a", "b"],
        relation_type="depends_on",
    )

    with pytest.raises(TypeError):
        relation.structure["x"] = 1

def test_nested_structure_is_deeply_immutable():
    obj = KnowledgeObject(
        identity=ObjectIdentity(
            "obj",
            "Thing",
            "Thing",
        ),
        structure={
            "nested": {
                "value": 1,
            },
        },
    )

    with pytest.raises(TypeError):
        obj.structure["nested"]["x"] = 2

def test_nested_lists_are_converted_to_tuples():
    obj = KnowledgeObject(
        identity=ObjectIdentity(
            "obj",
            "Thing",
            "Thing",
        ),
        structure={
            "nested": {
                "items": [1, 2, 3],
            },
        },
    )

    assert obj.structure["nested"]["items"] == (1, 2, 3)

def test_sets_are_converted_to_frozensets():
    obj = KnowledgeObject(
        identity=ObjectIdentity(
            "obj",
            "Thing",
            "Thing",
        ),
        structure={
            "tags": {"a", "b"},
        },
    )

    assert isinstance(
        obj.structure["tags"],
        frozenset,
    )


# ============================================================================
# Copy / Deepcopy Semantics (regression for MappingProxyType)
# ============================================================================

def test_knowledge_object_deepcopy_does_not_raise():
    from copy import deepcopy
    obj = KnowledgeObject(
        identity=ObjectIdentity("obj", "Thing", "Thing"),
        structure={"nested": {"a": [1, 2, {"b": 3}]}},
    )
    copied = deepcopy(obj)
    assert copied is obj


def test_knowledge_object_copy_returns_self():
    from copy import copy
    obj = KnowledgeObject(
        identity=ObjectIdentity("obj", "Thing", "Thing"),
        structure={"a": 1},
    )
    assert copy(obj) is obj


def test_knowledge_structure_deepcopy_does_not_raise():
    from copy import deepcopy
    obj = KnowledgeObject(
        identity=ObjectIdentity("obj-1", "Thing", "Thing"),
        structure={"content": "hello"},
    )
    structure = KnowledgeStructure([obj])
    copied = deepcopy(structure)
    assert copied is structure
    assert copied == structure


def test_knowledge_object_deepcopy_inside_container_does_not_raise():
    from copy import deepcopy
    obj = KnowledgeObject(
        identity=ObjectIdentity("obj", "Thing", "Thing"),
        structure={"content": "hello"},
    )
    container = {"session_like": {"knowledge_structure": obj}}
    copied = deepcopy(container)
    assert copied["session_like"]["knowledge_structure"] is obj


# ============================================================================
# Merkle Hashing & Structural Diff (v1.7.0)
# ============================================================================

def test_knowledge_object_has_stable_hash():
    """KnowledgeObject._hash must be a 32-byte value computed once."""
    obj = KnowledgeObject(
        identity=ObjectIdentity("obj", "Thing", "Thing"),
        structure={"a": 1},
    )
    assert isinstance(obj._hash, bytes)
    assert len(obj._hash) == 32

def test_knowledge_object_hash_deterministic():
    """Same identity + structure must yield the same hash."""
    obj1 = KnowledgeObject(
        identity=ObjectIdentity("obj", "Thing", "Thing"),
        structure={"a": 1, "b": 2},
    )
    obj2 = KnowledgeObject(
        identity=ObjectIdentity("obj", "Thing", "Thing"),
        structure={"b": 2, "a": 1},  # другой порядок ключей
    )
    assert obj1._hash == obj2._hash

def test_knowledge_object_hash_differs_for_different_structure():
    obj1 = KnowledgeObject(
        identity=ObjectIdentity("obj", "Thing", "Thing"),
        structure={"a": 1},
    )
    obj2 = KnowledgeObject(
        identity=ObjectIdentity("obj", "Thing", "Thing"),
        structure={"a": 2},
    )
    assert obj1._hash != obj2._hash

def test_knowledge_object_has_stable_id_hash():
    """
    KnowledgeObject._id_hash caches the canonical hash of just
    identity.id, computed once in __post_init__, so
    KnowledgeStructure.__init__ can build _identity_hash without
    recomputing a SHA-256 leaf hash per id on every construction.
    """
    obj = KnowledgeObject(
        identity=ObjectIdentity("obj", "Thing", "Thing"),
        structure={"a": 1},
    )
    assert isinstance(obj._id_hash, bytes)
    assert len(obj._id_hash) == 32

def test_knowledge_object_id_hash_depends_only_on_id():
    """_id_hash must be the same for two objects sharing an id, even
    when their type/name/structure differ -- and different for
    different ids, even with everything else identical."""
    same_id_a = KnowledgeObject(identity=ObjectIdentity("obj", "TypeA", "Alpha"), structure={"x": 1})
    same_id_b = KnowledgeObject(identity=ObjectIdentity("obj", "TypeB", "Beta"), structure={"y": 2})
    assert same_id_a._id_hash == same_id_b._id_hash

    different_id = KnowledgeObject(identity=ObjectIdentity("other", "TypeA", "Alpha"), structure={"x": 1})
    assert same_id_a._id_hash != different_id._id_hash

def test_canonical_relation_has_id_hash():
    """CanonicalRelation.__init__ bypasses KnowledgeObject.__post_init__
    entirely (it sets fields via object.__setattr__ directly), so it
    must set _id_hash itself -- otherwise every KnowledgeStructure
    containing a relation would raise AttributeError on construction."""
    relation = make_relation("rel-1", ["obj-1", "obj-2"])
    assert isinstance(relation._id_hash, bytes)
    assert len(relation._id_hash) == 32

def test_knowledge_structure_root_hash_deterministic():
    """Merkle root must be independent of insertion order."""
    a = KnowledgeObject(ObjectIdentity("a", "T", "A"), structure={})
    b = KnowledgeObject(ObjectIdentity("b", "T", "B"), structure={})
    s1 = KnowledgeStructure([a, b])
    s2 = KnowledgeStructure([b, a])
    assert s1.root_hash == s2.root_hash
    assert s1.structurally_equivalent(s2)

def test_knowledge_structure_root_hash_different_content():
    a = KnowledgeObject(ObjectIdentity("a", "T", "A"), structure={})
    b = KnowledgeObject(ObjectIdentity("b", "T", "B"), structure={})
    s1 = KnowledgeStructure([a, b])
    s2 = KnowledgeStructure([a])
    assert s1.root_hash != s2.root_hash
    assert not s1.structurally_equivalent(s2)

def test_knowledge_structure_is_hashable():
    """KnowledgeStructure now implements __hash__ based on root hash."""
    a = KnowledgeObject(ObjectIdentity("a", "T", "A"), structure={})
    b = KnowledgeObject(ObjectIdentity("b", "T", "B"), structure={})
    s1 = KnowledgeStructure([a, b])
    s2 = KnowledgeStructure([b, a])
    s3 = KnowledgeStructure([a])
    assert hash(s1) == hash(s2)
    assert hash(s1) != hash(s3)
    # Must be usable as dictionary key
    d = {s1: "test"}
    assert d[s2] == "test"

def test_diff_identity():
    """diff of identical structures must return empty list."""
    left = make_structure()
    right = make_structure()
    ops = left.diff(right)
    assert ops == []

def test_diff_add_object():
    """Adding an object must produce exactly one AddObject operator."""
    left = make_structure()
    new_obj = make_object("obj-3")
    right = KnowledgeStructure(list(left.objects) + [new_obj])
    ops = left.diff(right)
    assert len(ops) == 1
    from cks.evolution import AddObject
    assert isinstance(ops[0], AddObject)

def test_diff_remove_object():
    """Removing an object must produce RemoveObject (and cascade relations)."""
    left = make_structure()
    # Remove obj-1, which will cascade-delete rel-1 (participants: obj-1, obj-2)
    right = KnowledgeStructure([obj for obj in left.objects if obj.identity.id != "obj-1"])
    ops = left.diff(right)
    from cks.evolution import RemoveObject
    assert any(isinstance(op, RemoveObject) for op in ops)

def test_diff_modified_object_preserves_relations():
    """Modifying an object must cascade-remove and re-add its dependent relations."""
    left = make_structure()
    # Modify obj-1: change structure
    modified_obj = KnowledgeObject(
        identity=ObjectIdentity("obj-1", "Definition", "obj-1"),
        structure={"key": "new_value"},
    )
    right_objects = [modified_obj] + [obj for obj in left.objects if obj.identity.id != "obj-1"]
    right = KnowledgeStructure(right_objects)

    ops = left.diff(right)
    from cks.evolution import compose
    result = compose(left, ops)

    assert result.structurally_equivalent(right)
    # rel-1 must survive the modification
    assert "rel-1" in result


def test_merge_preserves_insertion_order():
    """Порядок объектов после слияния должен определяться порядком в ветках, а не случайным хэшированием."""
    # Базовые объекты
    base_objs = [
        KnowledgeObject(identity=ObjectIdentity(id="1", type="T", name="Base1")),
        KnowledgeObject(identity=ObjectIdentity(id="2", type="T", name="Base2")),
    ]
    base = KnowledgeStructure(base_objs)

    # Ветка A добавляет объекты в определённом порядке: 4, 3 (проверяем, что порядок сохранён)
    branch_a = KnowledgeStructure([
        *base_objs,
        KnowledgeObject(identity=ObjectIdentity(id="4", type="T", name="A4")),
        KnowledgeObject(identity=ObjectIdentity(id="3", type="T", name="A3")),
    ])

    # Ветка B добавляет объект 5
    branch_b = KnowledgeStructure([
        *base_objs,
        KnowledgeObject(identity=ObjectIdentity(id="5", type="T", name="B5")),
    ])

    merged = base.merge(branch_a, branch_b)

    # Ожидаемый порядок: все базовые (в исходном порядке), затем 4, 3, 5
    expected_ids = [obj.identity.id for obj in base.objects] + ["4", "3", "5"]
    actual_ids = [obj.identity.id for obj in merged.objects]
    assert actual_ids == expected_ids, f"Expected order {expected_ids}, got {actual_ids}"