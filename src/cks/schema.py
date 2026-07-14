"""
CKS Schema — JSON Schema Validation.

This module validates serialized Knowledge Structures against the
canonical JSON Schema (CKS‑003).  It is used by the parser to catch
structural errors early, before semantic validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import jsonschema
from jsonschema import validate as jsonschema_validate

# Path to the canonical schema file, relative to the package root.
_SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "examples" / "json" / "cks-schema.json"

# Load schema once at import time.
with _SCHEMA_PATH.open("r", encoding="utf-8") as _fh:
    _CANONICAL_SCHEMA: Dict[str, Any] = json.load(_fh)


class SchemaValidationError(Exception):
    """Raised when a JSON document fails schema validation."""


def validate_json(data: Dict[str, Any], *, schema: Optional[Dict[str, Any]] = None) -> None:
    """Validate *data* against the canonical CKS JSON Schema.

    Parameters
    ----------
    data
        The JSON document to validate.
    schema
        An optional schema dictionary.  If not provided, the canonical
        CKS schema is used.

    Raises
    ------
    SchemaValidationError
        If *data* does not conform to the schema.
    """
    target = schema if schema is not None else _CANONICAL_SCHEMA
    try:
        jsonschema_validate(instance=data, schema=target)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(str(exc)) from exc