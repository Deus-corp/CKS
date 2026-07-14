"""
CKS CLI — Output Formatters.

Formatters convert validation results and inspection summaries into
machine‑readable (JSON) or human‑readable (Plain Text) representations.
"""
from __future__ import annotations

import json
from typing import Optional

from ..result import ValidationResult
from ..diagnostics import DiagnosticSeverity


def format_json(result: ValidationResult, *, indent: int = 2) -> str:
    """Return a JSON string suitable for machine processing."""
    data = {
        "valid": result.is_valid,
        "error_count": result.error_count,
        "warning_count": result.warning_count,
        "information_count": result.information_count,
        "constraints_evaluated": list(result.evaluated_constraints),
        "diagnostics": [
            {
                "identity": d.identity,
                "severity": d.severity.value,
                "message": d.message,
                "location": d.location,
            }
            for d in result.diagnostics
        ],
    }
    return json.dumps(data, indent=indent, ensure_ascii=False)


def format_text(result: ValidationResult) -> str:
    """Return a human‑readable plain‑text summary."""
    lines = []
    if result.is_valid:
        lines.append("✅ Valid")
    else:
        lines.append("❌ Invalid")
        for d in result.diagnostics:
            prefix = {
                DiagnosticSeverity.ERROR: "  [ERROR]",
                DiagnosticSeverity.WARNING: "  [WARN] ",
                DiagnosticSeverity.INFORMATION: "  [INFO] ",
            }.get(d.severity, "  [????]")
            lines.append(f"{prefix} {d.message}")
    lines.append(
        f"\nErrors: {result.error_count}  "
        f"Warnings: {result.warning_count}  "
        f"Info: {result.information_count}"
    )
    return "\n".join(lines)