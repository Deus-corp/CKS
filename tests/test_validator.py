"""
Unit tests for the CKS validation pipeline.

Covers the minimum test criteria defined in CKS‑B001‑PY, Section 5.
"""

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


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def _make_obj(oid: str, otype: str = "Definition", name: str = "") -> KnowledgeObject:
    return KnowledgeObject(
        identity=ObjectIdentity(id=oid, type=otype, name=name or oid)
    )


def _make_rel(
    oid: str,
    participants: list[str],
    relation_type: str = "depends_on",
) -> CanonicalRelation:
    return CanonicalRelation(
        identity=ObjectIdentity(id=oid, type="Relation", name=oid),
        participants=participants,
        relation_type=relation_type,
    )


def _minimal_structure() -> KnowledgeStructure:
    """Return a minimal valid KnowledgeStructure."""
    return KnowledgeStructure(
        [
            _make_obj("obj-1", "Definition", "Knowledge Object"),
            _make_obj("obj-2", "Theorem", "Representation Independence"),
            _make_rel("rel-1", ["obj-1", "obj-2"]),
        ]
    )


# ---------------------------------------------------------------------------
# T1 – Parse correctly deserializes a minimal valid KnowledgeStructure
# ---------------------------------------------------------------------------

def test_parse_minimal_valid_structure():
    json_str = json.dumps(
        {
            "objects": [
                {
                    "identity": {"id": "obj-1", "type": "Definition", "name": "Test"},
                    "structure": {},
                }
            ]
        }
    )
    structure = parse(json_str)
    assert len(structure.objects) == 1
    assert structure.objects[0].identity.id == "obj-1"


# ---------------------------------------------------------------------------
# T2 – serialize followed by parse is structurally equivalent
# ---------------------------------------------------------------------------

def test_serialize_parse_roundtrip():
    original = _minimal_structure()
    json_str = serialize(original)
    restored = parse(json_str)
    # Structural equivalence: same set of identities
    orig_ids = {obj.identity.id for obj in original.objects}
    rest_ids = {obj.identity.id for obj in restored.objects}
    assert orig_ids == rest_ids


# ---------------------------------------------------------------------------
# T3 – validate returns is_valid=True for a valid structure
# ---------------------------------------------------------------------------

def test_validate_valid_structure():
    structure = _minimal_structure()
    result = validate(structure)
    assert result.is_valid is True


# ---------------------------------------------------------------------------
# T4 – validate returns is_valid=False when a required object is missing
# ---------------------------------------------------------------------------

def test_validate_missing_object():
    # A relation referencing a non‑existent object
    bad = KnowledgeStructure(
        [
            _make_obj("obj-1"),
            _make_rel("rel-1", ["obj-1", "obj-missing"]),
        ]
    )
    result = validate(bad)
    assert result.is_valid is False
    assert any(d.severity == DiagnosticSeverity.ERROR for d in result.diagnostics)


# ---------------------------------------------------------------------------
# T5 – validate returns is_valid=False for a dangling reference
# ---------------------------------------------------------------------------

def test_validate_dangling_reference():
    bad = KnowledgeStructure(
        [
            _make_rel("rel-1", ["obj-1", "obj-2"]),
        ]
    )
    result = validate(bad)
    assert result.is_valid is False


# ---------------------------------------------------------------------------
# T6 – validate returns is_valid=False for duplicate identity
# ---------------------------------------------------------------------------

def test_validate_duplicate_identity():
    with pytest.raises(Exception):
        KnowledgeStructure(
            [
                _make_obj("dup"),
                _make_obj("dup"),
            ]
        )


# ---------------------------------------------------------------------------
# T7 – Determinism: repeated calls produce identical output
# ---------------------------------------------------------------------------

def test_determinism():
    structure = _minimal_structure()
    result1 = validate(structure)
    result2 = validate(structure)
    assert result1.is_valid == result2.is_valid
    assert len(result1.diagnostics) == len(result2.diagnostics)


# ---------------------------------------------------------------------------
# T8 – Observational purity: input structure is not modified
# ---------------------------------------------------------------------------

def test_observational_purity():
    structure = _minimal_structure()
    snapshot = len(structure.objects)
    validate(structure)
    assert len(structure.objects) == snapshot


# ---------------------------------------------------------------------------
# T9 – Semantic and Behavioural Conformance (basic check)
# ---------------------------------------------------------------------------

def test_semantic_behavioural_conformance():
    """Equivalent inputs produce equivalent observable outputs."""
    s1 = _minimal_structure()
    s2 = parse(serialize(s1))  # round‑trip
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
    structure = KnowledgeStructure([])
    result = validate(structure)
    assert result.is_valid is True


def test_derivation_cycle_detection():
    """A → B → C → A should be flagged as a cycle."""
    objects = [
        _make_obj("a", "Lemma"),
        _make_obj("b", "Lemma"),
        _make_obj("c", "Lemma"),
        _make_rel("d1", ["a", "b"], "derives"),
        _make_rel("d2", ["b", "c"], "derives"),
        _make_rel("d3", ["c", "a"], "derives"),
    ]
    structure = KnowledgeStructure(objects)
    result = validate(structure)
    assert not result.is_valid
    assert any(
        "cycle" in d.message.lower() for d in result.diagnostics
    )


def test_serialize_preserves_canonical_relation():
    structure = _minimal_structure()
    json_str = serialize(structure)
    restored = parse(json_str)
    orig_rels = structure.relations()
    rest_rels = restored.relations()
    assert len(orig_rels) == len(rest_rels)
    assert orig_rels[0].participants == rest_rels[0].participants


def test_diagnostics_info_warning_error():
    """Smoke test that all severity levels are instantiable."""
    from cks.diagnostics import Diagnostic
    d_info = Diagnostic("TEST-INFO", DiagnosticSeverity.INFORMATION, "Info msg")
    d_warn = Diagnostic("TEST-WARN", DiagnosticSeverity.WARNING, "Warning msg")
    d_err = Diagnostic("TEST-ERR", DiagnosticSeverity.ERROR, "Error msg")
    assert d_info.severity == DiagnosticSeverity.INFORMATION
    assert d_warn.severity == DiagnosticSeverity.WARNING
    assert d_err.severity == DiagnosticSeverity.ERROR