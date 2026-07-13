"""
CKS Validator — Structural and Semantic Validation.

This module implements the canonical validation pipeline defined in
CKS‑006 (Section 6) and CKS‑005.  It operates on `KnowledgeStructure`
objects produced by `cks.serialization` and returns `ValidationResult`
objects from `cks.result`.

All functions are observationally pure and do not modify their inputs.
"""

from __future__ import annotations

from typing import Callable, List, Set, Tuple

from .core import CanonicalRelation, KnowledgeObject, KnowledgeStructure
from .diagnostics import Diagnostic, DiagnosticCollection, DiagnosticSeverity
from .result import ValidationResult


# ---------------------------------------------------------------------------
# Structural Validation
# ---------------------------------------------------------------------------

def structural_validate(structure: KnowledgeStructure) -> List[Diagnostic]:
    """Perform structural checks on *structure*.

    Checks performed
    ----------------
    1. Every object has a unique canonical identity.
    2. Every `CanonicalRelation` references only existing objects.
    3. Referential integrity holds (no dangling references).
    """
    diagnostics: List[Diagnostic] = []
    seen_ids: Set[str] = set()

    # 1. Unique identities
    for obj in structure.objects:
        oid = obj.identity.id
        if oid in seen_ids:
            diagnostics.append(
                Diagnostic(
                    identity="CKS-STRUCT-DUP-ID",
                    severity=DiagnosticSeverity.ERROR,
                    message=f"Duplicate canonical identity: {oid}",
                    location=oid,
                )
            )
        else:
            seen_ids.add(oid)

    # 2 & 3. Referential integrity of CanonicalRelations
    for rel in structure.relations():
        for participant_id in rel.participants:
            if participant_id not in seen_ids:
                diagnostics.append(
                    Diagnostic(
                        identity="CKS-STRUCT-DANGLING-REF",
                        severity=DiagnosticSeverity.ERROR,
                        message=(
                            f"Relation {rel.identity.id!r} references "
                            f"non‑existent object {participant_id!r}"
                        ),
                        location=rel.identity.id,
                    )
                )

    return diagnostics


# ---------------------------------------------------------------------------
# Semantic Validation
# ---------------------------------------------------------------------------

def semantic_validate(structure: KnowledgeStructure) -> List[Diagnostic]:
    """Perform semantic checks on *structure*.

    Currently verifies that every derivation chain is acyclic (basic
    reachability check).  Additional constraints may be added by
    extending the `cks.constraints` package.
    """
    diagnostics: List[Diagnostic] = []

    # Build adjacency for derivation relations
    adj: dict[str, list[str]] = {}
    for rel in structure.relations():
        if rel.relation_type == "derives":
            # Expects exactly two participants: source → derived
            src, tgt = rel.participants[0], rel.participants[1]
            adj.setdefault(src, []).append(tgt)

    # Detect cycles via depth‑first search
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {obj.identity.id: WHITE for obj in structure.objects}

    def dfs(node: str) -> bool:
        """Return True if a cycle is found."""
        color[node] = GRAY
        for neighbor in adj.get(node, []):
            if color.get(neighbor, WHITE) == GRAY:
                diagnostics.append(
                    Diagnostic(
                        identity="CKS-SEM-CYCLE",
                        severity=DiagnosticSeverity.ERROR,
                        message=f"Derivation cycle detected involving {node!r}",
                        location=node,
                    )
                )
                return True
            if color.get(neighbor, WHITE) == WHITE:
                if dfs(neighbor):
                    return True
        color[node] = BLACK
        return False

    for obj in structure.objects:
        oid = obj.identity.id
        if color[oid] == WHITE and oid in adj:
            dfs(oid)

    return diagnostics


# ---------------------------------------------------------------------------
# Constraint Evaluation (extensible)
# ---------------------------------------------------------------------------

ConstraintFn = Callable[[KnowledgeStructure], List[Diagnostic]]

# Global list of constraint functions – other modules (e.g., cks.constraints.*)
# may register additional constraints here.
_CONSTRAINTS: List[ConstraintFn] = []


def register_constraint(fn: ConstraintFn) -> None:
    """Register a constraint evaluation function."""
    _CONSTRAINTS.append(fn)


def evaluate_constraints(structure: KnowledgeStructure) -> List[Diagnostic]:
    """Run every registered constraint evaluation function on *structure*."""
    diagnostics: List[Diagnostic] = []
    for fn in _CONSTRAINTS:
        diagnostics.extend(fn(structure))
    return diagnostics


# ---------------------------------------------------------------------------
# Main Validation Entry Point
# ---------------------------------------------------------------------------

def validate(structure: KnowledgeStructure) -> ValidationResult:
    """Execute the complete canonical validation pipeline.

    Returns a `ValidationResult` that summarises all checks performed.
    The input *structure* is not modified.
    """
    all_diags: List[Diagnostic] = []
    all_diags.extend(structural_validate(structure))
    all_diags.extend(semantic_validate(structure))
    all_diags.extend(evaluate_constraints(structure))

    is_valid = all(d.severity != DiagnosticSeverity.ERROR for d in all_diags)
    return ValidationResult(
        is_valid=is_valid,
        diagnostics=DiagnosticCollection(diagnostics=tuple(all_diags)),
        evaluated_constraints=[fn.__name__ for fn in _CONSTRAINTS],
        metadata={
            "pipeline": [
                "structural_validate",
                "semantic_validate",
                "evaluate_constraints",
            ]
        },
    )