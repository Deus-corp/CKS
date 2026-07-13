"""
Unit tests for the canonical validation pipeline.

Covers the Validator defined by CKS-005.

Only validation behaviour is tested here.
Serialization, engine and interface are tested separately.
"""

from __future__ import annotations

import pytest

from cks.core import (
    CanonicalRelation,
    KnowledgeObject,
    KnowledgeStructure,
    ObjectIdentity,
)
from cks.diagnostics import DiagnosticSeverity
from cks.validator import validate


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
# Valid structures
# =============================================================================


def test_valid_structure():
    result = validate(
        make_structure(),
    )

    assert result.is_valid
    assert result.error_count == 0
    assert len(result.errors()) == 0


def test_empty_structure_is_valid():
    result = validate(
        KnowledgeStructure([]),
    )

    assert result.is_valid


# =============================================================================
# Referential integrity
# =============================================================================


def test_missing_reference():
    structure = KnowledgeStructure(
        [
            make_object("obj-1"),
            make_relation(
                "rel-1",
                ["obj-1", "missing"],
            ),
        ]
    )

    result = validate(structure)

    assert not result.is_valid
    assert result.error_count == 1

    error = result.errors()[0]

    assert error.identity == "CKS-STRUCT-DANGLING-REF"
    assert error.severity is DiagnosticSeverity.ERROR


def test_relation_without_existing_objects():
    structure = KnowledgeStructure(
        [
            make_relation(
                "rel",
                ["a", "b"],
            ),
        ]
    )

    result = validate(structure)

    assert not result.is_valid
    assert result.error_count == 2


# =============================================================================
# Semantic validation
# =============================================================================


def test_derivation_cycle():
    structure = KnowledgeStructure(
        [
            make_object("a"),
            make_object("b"),
            make_object("c"),

            make_relation(
                "d1",
                ["a", "b"],
                "derives",
            ),

            make_relation(
                "d2",
                ["b", "c"],
                "derives",
            ),

            make_relation(
                "d3",
                ["c", "a"],
                "derives",
            ),
        ]
    )

    result = validate(structure)

    assert not result.is_valid

    assert any(
        diagnostic.identity == "CKS-SEM-CYCLE"
        for diagnostic in result.errors()
    )


# =============================================================================
# Determinism
# =============================================================================


def test_validation_is_deterministic():
    structure = make_structure()

    result1 = validate(structure)
    result2 = validate(structure)

    assert result1 == result2


# =============================================================================
# Observational purity
# =============================================================================


def test_validation_does_not_modify_structure():
    structure = make_structure()

    before = tuple(
        obj.identity.id
        for obj in structure
    )

    validate(structure)

    after = tuple(
        obj.identity.id
        for obj in structure
    )

    assert before == after


# =============================================================================
# Constraint execution
# =============================================================================


def test_constraint_pipeline_metadata():
    result = validate(
        make_structure(),
    )

    assert "pipeline" in result.metadata

    pipeline = result.metadata["pipeline"]

    assert pipeline == (
        "structural",
        "semantic",
        "constraints",
    )


# =============================================================================
# Diagnostic collections
# =============================================================================


def test_error_collection():
    structure = KnowledgeStructure(
        [
            make_relation(
                "rel",
                ["missing"],
            ),
        ]
    )

    result = validate(structure)

    assert result.error_count > 0
    assert len(result.errors()) == result.error_count


def test_warning_collection_is_tuple():
    result = validate(
        make_structure(),
    )

    assert isinstance(result.warnings(), tuple)


def test_information_collection_is_tuple():
    result = validate(
        make_structure(),
    )

    assert isinstance(result.information(), tuple)