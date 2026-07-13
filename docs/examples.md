# Examples

The CKS reference implementation includes a collection of executable examples demonstrating the canonical operations defined by the CKS specifications.

The examples are intended to complement the API documentation by showing complete workflows rather than isolated function calls.

All examples can be found in the project's `examples/` directory.

---

# Running Examples

Clone the repository and install the package in editable mode.

```bash
pip install -e .
```

Examples can then be executed directly.

```bash
python examples/01_basic_validation.py
```

---

# Example Overview

| Example                 | Description                                         |
| ----------------------- | --------------------------------------------------- |
| 01_basic_validation.py  | Construct and validate a simple Knowledge Structure |
| 02_serialization.py     | Serialize and deserialize canonical JSON            |
| 03_constraints.py       | Execute the validation pipeline with constraints    |
| 04_reference_engine.py  | Interact directly with the Reference Engine         |
| 05_custom_constraint.py | Register and execute a custom validation constraint |

---

# Example 1 — Basic Validation

File:

```text
examples/01_basic_validation.py
```

This example demonstrates the minimal workflow for creating and validating a Knowledge Structure.

Topics covered:

* creating Knowledge Objects;
* constructing a Knowledge Structure;
* validating the structure;
* inspecting the ValidationResult.

Typical workflow:

```text
Knowledge Objects
        │
        ▼
Knowledge Structure
        │
        ▼
validate()
        │
        ▼
ValidationResult
```

This is the recommended starting point for new users.

---

# Example 2 — Serialization

File:

```text
examples/02_serialization.py
```

This example demonstrates canonical serialization.

Topics covered:

* parsing canonical JSON;
* serializing Knowledge Structures;
* canonical round-trip behaviour.

Workflow:

```text
Knowledge Structure
        │
        ▼
serialize()
        │
        ▼
Canonical JSON
        │
        ▼
parse()
        │
        ▼
Knowledge Structure
```

The resulting structure is structurally equivalent to the original.

---

# Example 3 — Validation Constraints

File:

```text
examples/03_constraints.py
```

This example illustrates the canonical validation pipeline.

Topics include:

* structural validation;
* semantic validation;
* constraint evaluation;
* diagnostics.

The example demonstrates how multiple validation stages contribute to a single ValidationResult.

---

# Example 4 — Reference Engine

File:

```text
examples/04_reference_engine.py
```

Although most applications use the public interface, the Reference Engine is also available directly.

This example demonstrates:

* constructing the engine;
* executing canonical operations;
* inspecting results.

Typical workflow:

```python
from cks import ReferenceEngine

engine = ReferenceEngine()

result = engine.validate(structure)
```

---

# Example 5 — Custom Constraints

File:

```text
examples/05_custom_constraint.py
```

The reference validator supports deterministic custom constraints.

This example demonstrates:

* defining a constraint;
* registering it;
* executing validation;
* inspecting custom diagnostics.

Example outline:

```python
register_constraint(my_constraint)

result = validate(structure)
```

Custom constraints execute during the Constraint Evaluation stage of the validation pipeline.

---

# Canonical Workflow

Most applications follow the same sequence of operations.

```text
Construct
      │
      ▼
Validate
      │
      ▼
Inspect
      │
      ▼
Serialize
      │
      ▼
Exchange
```

Each operation is deterministic and observationally pure.

---

# Extending the Examples

The examples are intentionally minimal.

They are designed to be copied and modified for experimentation.

Future releases will include additional examples covering:

* larger Knowledge Structures;
* projection and extraction;
* structural comparison;
* evolution workflows;
* domain-specific constraint libraries;
* interoperability with external systems.

---

# Related Documentation

For detailed explanations of the concepts demonstrated here, see:

* **Getting Started**
* **Concepts**
* **Architecture**
* **API Reference**

For the formal definitions of the canonical behaviour, consult the CKS Core Specifications.
