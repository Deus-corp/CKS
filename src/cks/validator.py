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
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .core import KnowledgeStructure
from .diagnostics import Diagnostic, DiagnosticSeverity, DiagnosticCollection
from .result import ValidationResult
from .validation import ValidationStage
from .constraints.base import Constraint
from .constraints.registry import ConstraintRegistry, registry as _registry


ConstraintEvaluator = Callable[[KnowledgeStructure], list[Diagnostic]] | Constraint


@dataclass(frozen=True, slots=True)
class PipelineStage:
    stage: ValidationStage
    evaluator: Callable[[KnowledgeStructure], list[Diagnostic]]


class ValidationPipeline:
    """Ordered deterministic validation pipeline."""

    def __init__(self, stages: Iterable[PipelineStage]) -> None:
        self._stages = tuple(stages)

    @property
    def stages(self) -> tuple[PipelineStage, ...]:
        return self._stages

    def execute(self, structure: KnowledgeStructure) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for stage in self._stages:
            diagnostics.extend(stage.evaluator(structure))
        return diagnostics


class ReferenceValidator:
    """Reference implementation of the Canonical Validator."""

    def __init__(self, registry: ConstraintRegistry | None = None) -> None:
        self._registry = registry or _registry
        self._pipeline = ValidationPipeline([
            PipelineStage(ValidationStage.STRUCTURAL, self.structural_validate),
            PipelineStage(ValidationStage.SEMANTIC, self.semantic_validate),
            PipelineStage(ValidationStage.CONSTRAINTS, self.constraint_validate),
        ])

    # ------------------------------------------------------------------
    # Structural Validation
    # ------------------------------------------------------------------

    def structural_validate(self, structure: KnowledgeStructure) -> list[Diagnostic]:
        return self._registry.evaluate(structure, stage=ValidationStage.STRUCTURAL)

    # ------------------------------------------------------------------
    # Semantic Validation
    # ------------------------------------------------------------------

    def semantic_validate(self, structure: KnowledgeStructure) -> list[Diagnostic]:
        return self._registry.evaluate(structure, stage=ValidationStage.SEMANTIC)

    # ------------------------------------------------------------------
    # Constraint Evaluation
    # ------------------------------------------------------------------

    def constraint_validate(self, structure: KnowledgeStructure) -> list[Diagnostic]:
        return self._registry.evaluate(structure, stage=ValidationStage.CONSTRAINTS)

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    def pipeline(self) -> ValidationPipeline:
        return self._pipeline

    # ------------------------------------------------------------------
    # Execute Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        structure: KnowledgeStructure,
        *,
        min_severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
    ) -> ValidationResult:
        diagnostics_raw: list[Diagnostic] = self._pipeline.execute(structure)
        diagnostics = tuple(sorted(diagnostics_raw, key=Diagnostic.sort_key))
        collection = DiagnosticCollection(diagnostics=diagnostics)
        valid = all(
            d.severity.priority < min_severity.priority
            for d in diagnostics
            if d.severity != DiagnosticSeverity.INFORMATION
        )
        return ValidationResult(
            is_valid=valid,
            diagnostics=collection,
            evaluated_constraints=self._registry.names(),
            metadata={
                "validator": "ReferenceValidator",
                "pipeline": tuple(s.stage.value for s in self._pipeline.stages),
                "min_severity": min_severity.value,
            },
        )


# =============================================================================
# Global Reference Validator
# =============================================================================

_validator = ReferenceValidator()


# =============================================================================
# Public API
# =============================================================================

def register_constraint(fn: Constraint) -> None:
    """Register a canonical validation constraint."""
    _registry.register(fn)


def structural_validate(structure: KnowledgeStructure) -> list[Diagnostic]:
    """Execute only structural validation."""
    return _validator.structural_validate(structure)


def semantic_validate(structure: KnowledgeStructure) -> list[Diagnostic]:
    """Execute only semantic validation."""
    return _validator.semantic_validate(structure)


def evaluate_constraints(structure: KnowledgeStructure) -> list[Diagnostic]:
    """Execute all registered canonical constraints."""
    return _validator.constraint_validate(structure)


def validate(
    structure: KnowledgeStructure,
    *,
    min_severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
) -> ValidationResult:
    """Execute the complete canonical validation pipeline."""
    return _validator.validate(structure, min_severity=min_severity)


def validate_all(
    structures: Iterable[KnowledgeStructure],
    *,
    min_severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
) -> list[ValidationResult]:
    """Validate multiple KnowledgeStructures and return individual results."""
    return [_validator.validate(s, min_severity=min_severity) for s in structures]