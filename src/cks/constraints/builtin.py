"""
CKS Constraints — Built-in Canonical Constraints.

Reference implementations of the canonical constraints defined by the
CKS specifications.

This module serves as a manifest. All constraint implementations reside
in the corresponding domain modules (structural, semantic, derivation,
etc.).
"""

from __future__ import annotations

from .structural import UniqueIdentityConstraint, NoDanglingRelationConstraint
from .semantic import DerivationArityConstraint, DerivationCycleConstraint


# =============================================================================
# Built-in Constraint Set
# =============================================================================

BUILTIN_CONSTRAINTS = (
    # --- Structural Domain ---
    UniqueIdentityConstraint(),
    NoDanglingRelationConstraint(),

    # --- Semantic Domain ---
    DerivationArityConstraint(),
    DerivationCycleConstraint(),
)