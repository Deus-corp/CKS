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

    assert relation.participants == ["a", "b"]
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
# Representation
# =============================================================================


def test_repr():
    structure = make_structure()

    text = repr(structure)

    assert "KnowledgeStructure" in text
    assert "objects=3" in text
    assert "relations=1" in text