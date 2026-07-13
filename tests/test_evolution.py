import pytest

from cks import construct
from cks.core import (
    KnowledgeObject,
    ObjectIdentity,
)
from cks.engine import ReferenceEngine


def make_object(identity: str) -> KnowledgeObject:
    return KnowledgeObject(
        identity=ObjectIdentity(
            id=identity,
            type="entity",
            name=identity,
        ),
    )


def test_evolve_add():
    engine = ReferenceEngine()

    structure = construct(
        [
            make_object("a"),
        ]
    )

    new_structure = engine.evolve(
        structure,
        add=[
            make_object("b"),
        ],
    )

    assert len(structure.objects) == 1
    assert len(new_structure.objects) == 2

    assert structure.get("b") is None
    assert new_structure.get("b") is not None


def test_evolve_remove():
    engine = ReferenceEngine()

    structure = construct(
        [
            make_object("a"),
            make_object("b"),
        ]
    )

    new_structure = engine.evolve(
        structure,
        remove=["a"],
    )

    assert structure.get("a") is not None
    assert new_structure.get("a") is None


def test_evolve_duplicate_identity():
    engine = ReferenceEngine()

    structure = construct(
        [
            make_object("a"),
        ]
    )

    with pytest.raises(ValueError):
        engine.evolve(
            structure,
            add=[
                make_object("a"),
            ],
        )


def test_evolve_is_pure():
    engine = ReferenceEngine()

    structure = construct(
        [
            make_object("a"),
        ]
    )

    evolved = engine.evolve(
        structure,
        add=[make_object("b")],
    )

    assert structure is not evolved
    assert len(structure.objects) == 1
    assert len(evolved.objects) == 2