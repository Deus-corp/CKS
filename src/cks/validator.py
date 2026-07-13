"""
CKS Validator — Reference Validator Implementation.

Reference implementation of the Canonical Validator defined by

    • CKS-005 — Validator Specification
    • CKS-006 — Reference Engine
    • CKS-007 — Canonical Knowledge Interface
    • CKS-008 — Reference Conformance Specification

The validator is intentionally implementation-independent.

Validation is organised as a deterministic pipeline consisting of
independent validation stages.

Each stage:

    • observes the KnowledgeStructure
    • never modifies it
    • produces zero or more Diagnostics

The validator itself is observationally pure.

Identical inputs always produce identical ValidationResults.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable
from typing import Iterable

from .core import KnowledgeStructure

from .diagnostics import Diagnostic
from .diagnostics import DiagnosticCollection
from .diagnostics import DiagnosticSeverity

from .result import ValidationResult


# =============================================================================
# Public Types
# =============================================================================

ConstraintFunction = Callable[[KnowledgeStructure], list[Diagnostic]]


# =============================================================================
# Validation Stage
# =============================================================================


class ValidationStage(Enum):
    """
    Canonical validation pipeline stages.

    The order follows CKS-006 Section 6.
    """

    STRUCTURAL = "structural"

    SEMANTIC = "semantic"

    CONSTRAINTS = "constraints"


# =============================================================================
# Constraint Registry
# =============================================================================


class ConstraintRegistry:
    """
    Registry of canonical validation constraints.

    Constraint functions are deterministic.

    Registration preserves insertion order.

    Duplicate registrations are ignored.
    """

    def __init__(self) -> None:

        self._constraints: list[ConstraintFunction] = []

    # ------------------------------------------------------------------

    def register(self, fn: ConstraintFunction) -> None:
        """
        Register a canonical constraint.
        """

        if fn not in self._constraints:
            self._constraints.append(fn)

    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove every registered constraint.

        Mostly useful for testing.
        """

        self._constraints.clear()

    # ------------------------------------------------------------------

    def constraints(self) -> tuple[ConstraintFunction, ...]:
        """
        Immutable view.
        """

        return tuple(self._constraints)

    # ------------------------------------------------------------------

    def names(self) -> tuple[str, ...]:
        """
        Return the canonical names of every registered constraint.
        """

        return tuple(
            fn.__name__
            for fn in self._constraints
        )

    # ------------------------------------------------------------------

    def evaluate(
        self,
        structure: KnowledgeStructure,
    ) -> list[Diagnostic]:

        diagnostics: list[Diagnostic] = []

        for constraint in self._constraints:
            diagnostics.extend(constraint(structure))

        return diagnostics


# Global registry
_registry = ConstraintRegistry()


# =============================================================================
# Validation Pipeline Stage
# =============================================================================


@dataclass(frozen=True, slots=True)
class PipelineStage:

    stage: ValidationStage

    evaluator: Callable[[KnowledgeStructure], list[Diagnostic]]


# =============================================================================
# Validation Pipeline
# =============================================================================


class ValidationPipeline:
    """
    Ordered deterministic validation pipeline.

    Stages are executed sequentially.

    Every stage is observationally pure.
    """

    def __init__(
        self,
        stages: Iterable[PipelineStage],
    ) -> None:

        self._stages = tuple(stages)

    # ------------------------------------------------------------------

    @property
    def stages(self) -> tuple[PipelineStage, ...]:

        return self._stages

    # ------------------------------------------------------------------

    def execute(
        self,
        structure: KnowledgeStructure,
    ) -> list[Diagnostic]:

        diagnostics: list[Diagnostic] = []

        for stage in self._stages:

            diagnostics.extend(stage.evaluator(structure))

        return diagnostics


# =============================================================================
# Helper Utilities
# =============================================================================


def _error(
    *,
    identity: str,
    message: str,
    location: str | None = None,
) -> Diagnostic:

    return Diagnostic(
        identity=identity,
        severity=DiagnosticSeverity.ERROR,
        message=message,
        location=location,
    )


def _warning(
    *,
    identity: str,
    message: str,
    location: str | None = None,
) -> Diagnostic:

    return Diagnostic(
        identity=identity,
        severity=DiagnosticSeverity.WARNING,
        message=message,
        location=location,
    )


def _information(
    *,
    identity: str,
    message: str,
    location: str | None = None,
) -> Diagnostic:

    return Diagnostic(
        identity=identity,
        severity=DiagnosticSeverity.INFORMATION,
        message=message,
        location=location,
    )

# =============================================================================
# Reference Validator
# =============================================================================


class ReferenceValidator:
    """
    Reference implementation of the Canonical Validator.

    The validator itself contains no mutable validation state.

    Validation is deterministic and observationally pure.
    """

    # ------------------------------------------------------------------
    # Structural Validation
    # ------------------------------------------------------------------

    def structural_validate(
        self,
        structure: KnowledgeStructure,
    ) -> list[Diagnostic]:

        diagnostics: list[Diagnostic] = []

        seen: set[str] = set()

        # --------------------------------------------------------------
        # Unique identities
        # --------------------------------------------------------------

        for obj in structure.objects:

            identity = obj.identity.id

            if identity in seen:

                diagnostics.append(
                    _error(
                        identity="CKS-STRUCT-DUPLICATE-IDENTITY",
                        message=(
                            f"Duplicate canonical identity '{identity}'."
                        ),
                        location=identity,
                    )
                )

            else:
                seen.add(identity)

        # --------------------------------------------------------------
        # Referential integrity
        # --------------------------------------------------------------

        for relation in structure.relations():

            for participant in relation.participants:

                if participant not in seen:

                    diagnostics.append(
                        _error(
                            identity="CKS-STRUCT-DANGLING-REF",
                            message=(
                                f"Relation '{relation.identity.id}' "
                                f"references unknown object "
                                f"'{participant}'."
                            ),
                            location=relation.identity.id,
                        )
                    )

        return diagnostics

    # ------------------------------------------------------------------
    # Semantic Validation
    # ------------------------------------------------------------------

    def semantic_validate(
        self,
        structure: KnowledgeStructure,
    ) -> list[Diagnostic]:

        diagnostics: list[Diagnostic] = []

        adjacency: dict[str, list[str]] = {}

        # --------------------------------------------------------------
        # Build derivation graph
        # --------------------------------------------------------------

        for relation in structure.relations():

            if relation.relation_type != "derives":
                continue

            participants = relation.participants

            if len(participants) != 2:

                diagnostics.append(
                    _error(
                        identity="CKS-SEM-DERIVATION-ARITY",
                        message=(
                            "A derivation relation shall contain "
                            "exactly two participants."
                        ),
                        location=relation.identity.id,
                    )
                )

                continue

            source, target = participants

            adjacency.setdefault(source, []).append(target)

        # --------------------------------------------------------------
        # Cycle detection
        # --------------------------------------------------------------

        WHITE = 0
        GRAY = 1
        BLACK = 2

        colour = {
            obj.identity.id: WHITE
            for obj in structure.objects
        }

        def dfs(node: str) -> None:

            colour[node] = GRAY

            for neighbour in adjacency.get(node, ()):

                state = colour[neighbour]

                if state == GRAY:

                    diagnostics.append(
                        _error(
                            identity="CKS-SEM-CYCLE",
                            message=(
                                "A derivation cycle was detected."
                            ),
                            location=node,
                        )
                    )

                    continue

                if state == WHITE:
                    dfs(neighbour)

            colour[node] = BLACK

        for node in list(adjacency.keys()):

            if colour[node] == WHITE:
                dfs(node)

        return diagnostics

    # ------------------------------------------------------------------
    # Constraint Evaluation
    # ------------------------------------------------------------------

    def constraint_validate(
        self,
        structure: KnowledgeStructure,
    ) -> list[Diagnostic]:

        return _registry.evaluate(structure)

    # ------------------------------------------------------------------
    # Pipeline Construction
    # ------------------------------------------------------------------

    def pipeline(self) -> ValidationPipeline:

        return ValidationPipeline(
            (
                PipelineStage(
                    ValidationStage.STRUCTURAL,
                    self.structural_validate,
                ),
                PipelineStage(
                    ValidationStage.SEMANTIC,
                    self.semantic_validate,
                ),
                PipelineStage(
                    ValidationStage.CONSTRAINTS,
                    self.constraint_validate,
                ),
            )
        )

    # ------------------------------------------------------------------
    # Execute Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        structure: KnowledgeStructure,
    ) -> ValidationResult:

        pipeline = self.pipeline()

        diagnostics = pipeline.execute(structure)

        diagnostics = sorted(
            diagnostics,
            key=lambda d: (
                d.identity,
                d.severity.value,
                d.location or "",
                d.message,
            ),
        )

        collection = DiagnosticCollection(
            diagnostics=tuple(diagnostics),
        )

        valid = all(
            d.severity != DiagnosticSeverity.ERROR
            for d in diagnostics
        )

        return ValidationResult(
            is_valid=valid,
            diagnostics=collection,
            evaluated_constraints=_registry.names(),
            metadata={
                "validator": "ReferenceValidator",
                "pipeline": tuple(
                    stage.stage.value
                    for stage in pipeline.stages
                ),
            },
        )

# =============================================================================
# Global Reference Validator
# =============================================================================

_validator = ReferenceValidator()


# =============================================================================
# Public API
# =============================================================================

def register_constraint(fn: ConstraintFunction) -> None:
    """
    Register a canonical validation constraint.

    The constraint will be executed during the Constraint Evaluation
    stage of the validation pipeline.
    """
    _registry.register(fn)


def structural_validate(
    structure: KnowledgeStructure,
) -> list[Diagnostic]:
    """
    Execute only structural validation.

    This function is observationally pure.
    """
    return _validator.structural_validate(structure)


def semantic_validate(
    structure: KnowledgeStructure,
) -> list[Diagnostic]:
    """
    Execute only semantic validation.

    This function is observationally pure.
    """
    return _validator.semantic_validate(structure)


def evaluate_constraints(
    structure: KnowledgeStructure,
) -> list[Diagnostic]:
    """
    Execute all registered canonical constraints.
    """
    return _validator.constraint_validate(structure)


def validate(
    structure: KnowledgeStructure,
) -> ValidationResult:
    """
    Execute the complete canonical validation pipeline.

    Pipeline:

        Structural Validation
            ↓
        Semantic Validation
            ↓
        Constraint Evaluation
            ↓
        Validation Result

    This is the canonical validator defined by CKS-005 and CKS-006.

    The input KnowledgeStructure is never modified.
    """

    return _validator.validate(structure)

