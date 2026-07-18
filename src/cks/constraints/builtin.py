from __future__ import annotations

from .structural import UniqueIdentityConstraint, NoDanglingRelationConstraint
from .semantic import DerivationArityConstraint, DerivationCycleConstraint
from .projection import EmbeddingProjectionIntegrityConstraint


# =============================================================================
# Built-in Constraint Set
# =============================================================================
#
# Normative constraints defined by CKS-001..CKS-008. These are
# auto-registered into the global registry (see constraints/__init__.py)
# and therefore apply to every call to cks.validate() by default.

BUILTIN_CONSTRAINTS = (
    # --- Structural Domain ---
    UniqueIdentityConstraint(),
    NoDanglingRelationConstraint(),
    # --- Semantic Domain ---
    DerivationArityConstraint(),
    DerivationCycleConstraint(),
)


# =============================================================================
# Optional Constraint Set
# =============================================================================
#
# Extensions built on top of the CKS-001..CKS-008 core vocabulary, but
# not themselves part of the normative specifications. NOT auto-registered:
# opt in explicitly, e.g.
#
#     from cks.constraints.builtin import OPTIONAL_CONSTRAINTS
#     from cks.constraints.registry import ConstraintRegistry, registry
#
#     for constraint in OPTIONAL_CONSTRAINTS:
#         registry.register(constraint)   # process-wide, or:
#
#     custom = ConstraintRegistry()
#     for constraint in (*BUILTIN_CONSTRAINTS, *OPTIONAL_CONSTRAINTS):
#         custom.register(constraint)     # scoped to one ReferenceValidator

OPTIONAL_CONSTRAINTS = (
    # --- Projection Domain (CKS-001 "Documents as Structural Projections") ---
    EmbeddingProjectionIntegrityConstraint(),
)