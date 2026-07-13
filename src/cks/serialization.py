"""
CKS Serialization — Canonical JSON Serialization.

This module implements the canonical serialization and deserialization
functions defined in CKS‑003 (Canonical Serialization) and CKS‑007
(Canonical Knowledge Interface).

All functions are observationally pure and do not modify their inputs.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Union

from .core import (
    CanonicalRelation,
    KnowledgeObject,
    KnowledgeStructure,
    ObjectIdentity,
)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class SerializationError(Exception):
    """Raised when canonical serialization cannot be parsed or produced."""


def parse(source: Union[str, dict]) -> KnowledgeStructure:
    """Parse a serialized representation into a KnowledgeStructure.

    The *source* must be a valid JSON string or a ``dict`` conforming to
    the canonical serialization model (CKS‑003).

    Returns a KnowledgeStructure semantically equivalent to the
    serialized representation.

    Raises
    ------
    SerializationError
        If *source* cannot be parsed or violates uniqueness constraints.
    """
    try:
        if isinstance(source, str):
            data = json.loads(source)
        else:
            data = source
    except json.JSONDecodeError as exc:
        raise SerializationError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise SerializationError("Top‑level JSON value must be an object")

    if "objects" not in data:
        raise SerializationError("Top‑level JSON object must contain an 'objects' key")

    objects_data: List[Dict[str, Any]] = data.get("objects", [])
    if not isinstance(objects_data, list):
        raise SerializationError("'objects' must be an array")

    objects: List[KnowledgeObject] = []
    seen_ids: set[str] = set()

    for obj_data in objects_data:
        # --- parse identity ---
        ident_data = obj_data.get("identity")
        if not isinstance(ident_data, dict):
            raise SerializationError("Each object must have an 'identity' object")

        oid = ident_data.get("id")
        otype = ident_data.get("type")
        oname = ident_data.get("name")

        if not isinstance(oid, str) or not isinstance(otype, str) or not isinstance(oname, str):
            raise SerializationError(
                "Object identity must contain string fields: id, type, name"
            )

        if oid in seen_ids:
            raise SerializationError(f"Duplicate canonical identity: {oid!r}")
        seen_ids.add(oid)

        identity = ObjectIdentity(id=oid, type=otype, name=oname)

        # --- parse structure ---
        structure_data: Dict[str, Any] = obj_data.get("structure", {})
        if not isinstance(structure_data, dict):
            raise SerializationError("Each object must have a 'structure' object")

        # Determine whether this object is a CanonicalRelation
        is_relation = (
            "participants" in structure_data and "relation_type" in structure_data
        )

        if is_relation:
            participants = structure_data.get("participants", [])
            relation_type = structure_data.get("relation_type", "")
            if not isinstance(participants, list) or not isinstance(relation_type, str):
                raise SerializationError(
                    "CanonicalRelation must have 'participants' (list) and "
                    "'relation_type' (str)"
                )
            obj = CanonicalRelation(
                identity=identity,
                participants=participants,
                relation_type=relation_type,
                structure=structure_data,
            )
        else:
            obj = KnowledgeObject(identity=identity, structure=structure_data)

        objects.append(obj)

    return KnowledgeStructure(objects)


def serialize(structure: KnowledgeStructure) -> str:
    """Serialize a KnowledgeStructure to its canonical JSON representation.

    The resulting string satisfies ``parse(serialize(S)) ≡ S``
    (structural equivalence, CKS‑001, Section 15).
    """
    output_objects: List[Dict[str, Any]] = []
    for obj in structure.objects:
        obj_data: Dict[str, Any] = {
            "identity": {
                "id": obj.identity.id,
                "type": obj.identity.type,
                "name": obj.identity.name,
            },
            "structure": obj.structure,
        }
        output_objects.append(obj_data)

    return json.dumps({"objects": output_objects}, indent=2)