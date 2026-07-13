# API Reference

This document describes the public API exposed by the Canonical Knowledge Structure (CKS) Python reference implementation.

Applications should use the functions documented here instead of importing implementation modules directly.

The public API is defined by the Canonical Knowledge Interface (CKS-007).

---

# Importing CKS

The recommended import style is:

```python
from cks import (
    construct,
    parse,
    serialize,
    validate,
    diagnose,
    inspect,
    compare,
    extract,
    project,
    evolve,
)
```

All public operations are:

* deterministic;
* observationally pure;
* implementation-independent.

---

# Construction

## construct()

Construct a canonical Knowledge Structure from an iterable of Knowledge Objects.

### Signature

```python
construct(
    objects: Iterable[KnowledgeObject],
) -> KnowledgeStructure
```

### Example

```python
structure = construct(
    [
        object1,
        object2,
        relation,
    ]
)
```

---

# Serialization

## parse()

Parse canonical JSON into a Knowledge Structure.

### Signature

```python
parse(
    source: str | dict,
) -> KnowledgeStructure
```

### Parameters

| Parameter | Description                                  |
| --------- | -------------------------------------------- |
| source    | Canonical JSON string or decoded JSON object |

### Example

```python
structure = parse(json_text)
```

---

## serialize()

Serialize a Knowledge Structure into canonical JSON.

### Signature

```python
serialize(
    structure: KnowledgeStructure,
) -> str
```

### Example

```python
json_text = serialize(structure)
```

The reference implementation guarantees canonical round-trip behaviour.

---

# Validation

## validate()

Execute the complete canonical validation pipeline.

### Signature

```python
validate(
    structure: KnowledgeStructure,
) -> ValidationResult
```

### Validation Stages

1. Structural Validation
2. Semantic Validation
3. Constraint Evaluation

### Example

```python
result = validate(structure)

print(result.is_valid)
```

---

## diagnose()

Return diagnostics without exposing the complete ValidationResult.

### Signature

```python
diagnose(
    structure: KnowledgeStructure,
) -> DiagnosticCollection
```

### Example

```python
diagnostics = diagnose(structure)
```

---

# Inspection

## inspect()

Return an implementation-independent summary of a Knowledge Structure.

### Signature

```python
inspect(
    structure: KnowledgeStructure,
) -> Mapping[str, object]
```

### Example

```python
summary = inspect(structure)
```

Typical summary information includes:

* object count;
* relation count;
* structural metadata.

---

# Comparison

## compare()

Compare two Knowledge Structures.

### Signature

```python
compare(
    left: KnowledgeStructure,
    right: KnowledgeStructure,
) -> Mapping[str, object]
```

### Example

```python
comparison = compare(
    structure1,
    structure2,
)
```

The comparison is based on observable structure rather than implementation details.

---

# Extraction

## extract()

Extract a single Knowledge Object.

### Signature

```python
extract(
    structure: KnowledgeStructure,
    identity: str,
) -> KnowledgeObject | None
```

### Example

```python
obj = extract(
    structure,
    "definition-001",
)
```

Returns `None` when the requested object does not exist.

---

# Projection

## project()

Create a new Knowledge Structure containing only selected objects.

### Signature

```python
project(
    structure: KnowledgeStructure,
    identities: Iterable[str],
) -> KnowledgeStructure
```

### Example

```python
subset = project(
    structure,
    [
        "definition-001",
        "theorem-003",
    ],
)
```

Projection never modifies the original structure.

---

# Evolution

## evolve()

Apply admissible structural transformations.

### Signature

```python
evolve(
    structure: KnowledgeStructure,
    transformations,
) -> KnowledgeStructure
```

### Status

The reference implementation currently exposes the canonical interface.

Complete evolution semantics will be introduced in a future release following CKS-004.

---

# Reference Engine

The public interface internally delegates every operation to the Reference Engine.

Applications normally do not need to instantiate the engine directly.

However, it remains available:

```python
from cks import ReferenceEngine

engine = ReferenceEngine()
```

The engine provides the same canonical operations exposed by the module-level API.

---

# Exceptions

## SerializationError

Raised when canonical serialization cannot be parsed.

Example:

```python
from cks import SerializationError

try:
    structure = parse(text)
except SerializationError:
    ...
```

---

# ValidationResult

The validator returns an immutable `ValidationResult`.

Useful properties include:

| Property          | Description                         |
| ----------------- | ----------------------------------- |
| is_valid          | Overall validation status           |
| diagnostics       | Complete diagnostic collection      |
| error_count       | Number of errors                    |
| warning_count     | Number of warnings                  |
| information_count | Number of informational diagnostics |
| metadata          | Validation metadata                 |

Convenience methods include:

* `has_errors()`
* `has_warnings()`
* `has_information()`
* `summary()`

---

# Public Classes

The following classes are part of the supported public API.

| Class                | Purpose                         |
| -------------------- | ------------------------------- |
| ObjectIdentity       | Canonical identity              |
| KnowledgeObject      | Semantic object                 |
| CanonicalRelation    | Semantic relation               |
| KnowledgeStructure   | Immutable knowledge structure   |
| ValidationResult     | Validation outcome              |
| Diagnostic           | Validation diagnostic           |
| DiagnosticCollection | Immutable diagnostic collection |
| ReferenceEngine      | Reference implementation engine |
| SerializationError   | Serialization exception         |

---

# API Stability

The public API follows semantic versioning.

Within a major version:

* public function names remain stable;
* observable behaviour remains stable;
* canonical semantics remain stable.

Internal implementation details may evolve without affecting user code.

---

# Related Documentation

For additional information, see:

* **Getting Started** — installation and first steps.
* **Concepts** — semantic foundations.
* **Architecture** — implementation design.
* **Examples** — practical usage patterns.
* **Core Specifications** — formal normative definitions.
