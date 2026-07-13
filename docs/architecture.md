# Architecture

This document describes the architecture of the Canonical Knowledge Structure (CKS) Python reference implementation.

The implementation follows the architecture defined by the CKS specifications while remaining completely implementation-independent.

The goal of the reference implementation is not merely to provide a working library, but to demonstrate the canonical behaviour expected from every conforming implementation.

---

# Architectural Overview

The CKS architecture is organised as a layered system.

```text
                    Applications
                          │
                          ▼
          Canonical Knowledge Interface
                    (interface.py)
                          │
                          ▼
                Reference Engine
                  (engine.py)
        ┌────────────┼────────────┐
        ▼            ▼            ▼
 Serialization   Validation    Inspection
serialization.py validator.py   engine.py
        │
        ▼
 Core Semantic Model
      (core.py)
```

Each layer has a clearly defined responsibility.

Higher layers never modify lower layers.

---

# Design Principles

The architecture follows five fundamental principles.

## Representation Independence

Knowledge is independent of its representation.

No module assumes that JSON, Python objects, or any storage backend is the primary representation.

---

## Determinism

Every public operation is deterministic.

Identical inputs always produce identical observable outputs.

---

## Observational Purity

Public operations never modify their inputs.

Every operation observes immutable knowledge structures.

---

## Layer Separation

Each module has a single responsibility.

Semantic concepts are isolated from serialization, validation, and public APIs.

---

## Implementation Independence

Every implementation is free to choose its internal algorithms provided that the observable behaviour remains identical.

---

# Core Layer

```
core.py
```

The Core layer defines the immutable semantic model.

It contains the fundamental concepts introduced in the CKS specifications:

* ObjectIdentity
* KnowledgeObject
* CanonicalRelation
* KnowledgeStructure

Every other module depends on this layer.

The Core layer has no knowledge of:

* JSON;
* validation;
* diagnostics;
* engines;
* APIs.

It only defines canonical semantic objects.

---

# Serialization Layer

```
serialization.py
```

The Serialization layer converts between canonical JSON and the semantic model.

Responsibilities include:

* parsing canonical JSON;
* serializing Knowledge Structures;
* enforcing serialization rules;
* preserving round-trip equivalence.

The serializer never performs semantic validation.

---

# Validation Layer

```
validator.py
```

The Validator implements the canonical validation pipeline.

The pipeline consists of three stages:

```text
Structural Validation
          │
          ▼
Semantic Validation
          │
          ▼
Constraint Evaluation
```

Each stage is independent.

Diagnostics produced by every stage are merged into a single ValidationResult.

---

# Constraint Registry

The validation layer includes a constraint registry.

The registry allows implementations to register additional deterministic validation constraints.

```text
Constraint Registry
        │
        ▼
Constraint 1
Constraint 2
Constraint 3
```

Constraints execute after structural and semantic validation.

---

# Reference Engine

```
engine.py
```

The Reference Engine coordinates all canonical operations.

It provides a single implementation-independent interface for:

* construction;
* serialization;
* validation;
* comparison;
* inspection;
* extraction;
* projection;
* evolution.

The engine delegates specialised work to the appropriate modules.

It contains very little domain-specific logic itself.

---

# Public Interface

```
interface.py
```

The public interface exposes the canonical API defined by CKS-007.

Applications are expected to import functions from this module.

Typical usage:

```python
from cks import parse
from cks import validate
from cks import serialize
```

The interface hides implementation details while exposing deterministic canonical behaviour.

---

# Diagnostics

Diagnostics are represented independently of validation.

```
diagnostics.py
```

defines:

* Diagnostic
* DiagnosticSeverity
* DiagnosticCollection

Validation produces diagnostics but does not own their implementation.

This separation allows diagnostics to evolve independently.

---

# Validation Results

```
result.py
```

Validation outcomes are represented using ValidationResult.

A ValidationResult contains:

* validity;
* diagnostics;
* evaluated constraints;
* metadata.

The result object is immutable.

---

# Module Dependencies

The implementation follows a directed dependency graph.

```text
core
 │
 ├────────────┐
 ▼            ▼
serialization validator
      │        │
      └────┬───┘
           ▼
        engine
           │
           ▼
       interface
```

Dependencies always point toward higher abstraction layers.

Circular dependencies are intentionally avoided.

---

# Typical Execution Flow

The following sequence illustrates a typical validation operation.

```text
Application
      │
      ▼
validate()
      │
      ▼
Reference Engine
      │
      ▼
Validator
      │
      ├── Structural Validation
      ├── Semantic Validation
      └── Constraint Evaluation
      │
      ▼
ValidationResult
```

Each step is deterministic and observationally pure.

---

# Repository Structure

The Python reference implementation is organised as follows.

```text
src/
└── cks/
    ├── __init__.py
    ├── interface.py
    ├── engine.py
    ├── core.py
    ├── serialization.py
    ├── validator.py
    ├── diagnostics.py
    ├── result.py
    ├── constraints/
    └── ...
```

Tests, documentation, and examples are maintained separately.

```text
docs/
examples/
tests/
```

---

# Extensibility

The architecture is intentionally modular.

Future versions may introduce additional components such as:

* constraint libraries;
* alternative serialization formats;
* optimisation engines;
* additional language bindings.

These extensions should integrate through the existing canonical interfaces without modifying the semantic model.

---

# Summary

The CKS architecture separates semantic concepts from implementation details.

Every layer has a single responsibility, and every public operation preserves the canonical guarantees defined by the CKS specifications:

* representation independence;
* determinism;
* observational purity;
* implementation independence.

The next document, **API Reference**, describes the complete public interface exposed by the Python reference implementation.
