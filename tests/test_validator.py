"""Unit tests for the CKS validation pipeline."""

import json
import pytest
from cks.core import (
    CanonicalRelation,
    KnowledgeObject,
    KnowledgeStructure,
    ObjectIdentity,
)
from cks.serialization import parse, serialize, SerializationError
from cks.validator import validate
from cks.diagnostics import DiagnosticSeverity


def make_object(oid: str, otype: str = "Definition", name: str = "") -> KnowledgeObject:
    return KnowledgeObject(
        identity=ObjectIdentity(id=oid, type=otype, name=name or oid)
    )


def make_relation(
    oid: str,
    participants: list[str],
    relation_type: str = "depends_on",
) -> CanonicalRelation:
    return CanonicalRelation(
        identity=ObjectIdentity(id=oid, type="Relation", name=oid),
        participants=participants,
        relation_type=relation_type,
    )


def make_structure() -> KnowledgeStructure:
    return KnowledgeStructure([
        make_object("obj-1", "Definition", "Knowledge Object"),
        make_object("obj-2", "Theorem", "Representation Independence"),
        make_relation("rel-1", ["obj-1", "obj-2"]),
    ])


# ---------------------------------------------------------------------------
# T1 — Parse correctly deserializes a minimal valid KnowledgeStructure
# ---------------------------------------------------------------------------

def test_parse_minimal_valid_structure():
    json_str = json.dumps({
        "objects": [
            {
                "identity": {"id": "obj-1", "type": "Definition", "name": "Test"},
                "structure": {},
            }
        ]
    })
    structure = parse(json_str)
    assert len(structure.objects) == 1
    assert structure.objects[0].identity.id == "obj-1"


# ---------------------------------------------------------------------------
# T2 — serialize followed by parse is structurally equivalent
# ---------------------------------------------------------------------------

def test_serialize_parse_roundtrip():
    original = make_structure()
    json_str = serialize(original)
    restored = parse(json_str)
    orig_ids = {obj.identity.id for obj in original.objects}
    rest_ids = {obj.identity.id for obj in restored.objects}
    assert orig_ids == rest_ids


# ---------------------------------------------------------------------------
# T3 — validate returns is_valid=True for a valid structure
# ---------------------------------------------------------------------------

def test_valid_structure():
    result = validate(make_structure())
    assert result.is_valid is True


# ---------------------------------------------------------------------------
# T4 — validate returns is_valid=False for a structure with a missing required object
# ---------------------------------------------------------------------------

def test_missing_reference():
    structure = KnowledgeStructure([
        make_object("obj-1"),
        make_relation("rel-1", ["obj-1", "missing"]),
    ])
    result = validate(structure)
    assert not result.is_valid
    # Ошибка: dangling reference
    assert any(d.severity == DiagnosticSeverity.ERROR for d in result.diagnostics)


# ---------------------------------------------------------------------------
# T5 — validate returns is_valid=False for a structure with a dangling reference
# ---------------------------------------------------------------------------

def test_relation_without_existing_objects():
    structure = KnowledgeStructure([
        make_relation("rel", ["a", "b"]),
    ])
    result = validate(structure)
    assert not result.is_valid
    # Ошибки: dangling references (оба участника не существуют)
    assert any(d.severity == DiagnosticSeverity.ERROR for d in result.diagnostics)


# ---------------------------------------------------------------------------
# T6 — validate returns is_valid=False for a structure with a duplicate identity
# ---------------------------------------------------------------------------

def test_validate_duplicate_identity():
    with pytest.raises(ValueError):
        KnowledgeStructure([
            make_object("dup"),
            make_object("dup"),
        ])


# ---------------------------------------------------------------------------
# T7 — Determinism: repeated calls produce identical output
# ---------------------------------------------------------------------------

def test_validation_is_deterministic():
    structure = make_structure()
    result1 = validate(structure)
    result2 = validate(structure)
    assert result1.is_valid == result2.is_valid
    assert len(result1.diagnostics) == len(result2.diagnostics)


# ---------------------------------------------------------------------------
# T8 — Observational purity: input structure is not modified
# ---------------------------------------------------------------------------

def test_validation_does_not_modify_structure():
    structure = make_structure()
    before = tuple(obj.identity.id for obj in structure.objects)
    validate(structure)
    after = tuple(obj.identity.id for obj in structure.objects)
    assert before == after


# ---------------------------------------------------------------------------
# T9 — Semantic and Behavioural Conformance (basic check)
# ---------------------------------------------------------------------------

def test_semantic_behavioural_conformance():
    s1 = make_structure()
    s2 = parse(serialize(s1))
    r1 = validate(s1)
    r2 = validate(s2)
    assert r1.is_valid == r2.is_valid
    assert len(r1.diagnostics) == len(r2.diagnostics)
    assert r1.evaluated_constraints == r2.evaluated_constraints


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------

def test_parse_invalid_json():
    with pytest.raises(SerializationError):
        parse("not json")


def test_parse_missing_objects_key():
    with pytest.raises(SerializationError):
        parse("{}")


def test_parse_duplicate_ids():
    data = {
        "objects": [
            {"identity": {"id": "dup", "type": "X", "name": "x"}, "structure": {}},
            {"identity": {"id": "dup", "type": "Y", "name": "y"}, "structure": {}},
        ]
    }
    with pytest.raises(SerializationError):
        parse(data)


def test_empty_structure_is_valid():
    result = validate(KnowledgeStructure([]))
    assert result.is_valid is True


def test_derivation_cycle():
    structure = KnowledgeStructure([
        make_object("a"),
        make_object("b"),
        make_object("c"),
        make_relation("d1", ["a", "b"], "derives"),
        make_relation("d2", ["b", "c"], "derives"),
        make_relation("d3", ["c", "a"], "derives"),
    ])
    result = validate(structure)
    assert not result.is_valid
    assert any("cycle" in d.message.lower() for d in result.diagnostics)


def test_serialize_preserves_canonical_relation():
    structure = make_structure()
    json_str = serialize(structure)
    restored = parse(json_str)
    orig_rels = structure.relations()
    rest_rels = restored.relations()
    assert len(orig_rels) == len(rest_rels)
    assert orig_rels[0].participants == rest_rels[0].participants


def test_diagnostics_info_warning_error():
    from cks.diagnostics import Diagnostic
    d_info = Diagnostic("TEST-INFO", DiagnosticSeverity.INFORMATION, "Info msg")
    d_warn = Diagnostic("TEST-WARN", DiagnosticSeverity.WARNING, "Warning msg")
    d_err = Diagnostic("TEST-ERR", DiagnosticSeverity.ERROR, "Error msg")
    assert d_info.severity == DiagnosticSeverity.INFORMATION
    assert d_warn.severity == DiagnosticSeverity.WARNING
    assert d_err.severity == DiagnosticSeverity.ERROR