# Plugin Development Guide

CKS supports external constraint plugins via the standard Python
``entry_points`` mechanism.  This allows domain‑specific constraints
to be distributed as independent packages and loaded automatically
when `cks` is imported.

---

## Quick Start

1. Create a new Python package (e.g., `cks-plugin-example`).
2. Define one or more constraints by subclassing `Constraint` from
   `cks.constraints.base`.
3. Create a factory function that returns a list of your constraint
   instances.
4. Register the factory in `pyproject.toml` under the group
   `cks.constraints`.

### Example

**myplugin.py**

```python
from cks.constraints.base import Constraint

class MyCustomConstraint(Constraint):
    identity = "MY-CUSTOM-CONSTRAINT"
    description = "A custom domain constraint."
    stage = "STRUCTURAL"  # or "SEMANTIC"

    def evaluate(self, structure):
        # your validation logic here
        return []
```

**factory.py**

```python
from .myplugin import MyCustomConstraint

def load():
    return [MyCustomConstraint()]
```

**pyproject.toml**

```toml
[project.entry-points."cks.constraints"]
myplugin = "cks_plugin_example.factory:load"
```

Once the plugin package is installed (`pip install .`), the constraint
appears automatically in the global registry:

```bash
cks plugin list
```

---

## Entry-Point Group

- **Group:** `cks.constraints`
- **Expected return type:** `Iterable[Constraint]`

Each entry-point must reference a zero‑argument callable that returns
an iterable of `Constraint` instances.  Invalid objects or exceptions
are reported to `stderr` without halting the import.

---

## Testing Plugins

Plugin constraints are executed during the standard validation
pipeline.  You can verify them with:

```bash
cks validate my_structure.json
```

Or programmatically:

```python
import cks
result = cks.validate(structure)
```

---

## Distribution

Publish your plugin as a standard PyPI package.  Users only need to
install it (`pip install cks-plugin-example`) – CKS discovers the
constraints automatically on the next import.

---

## See Also

- `cks.constraints` – built‑in constraint reference
- `cks.plugin` – internal discovery module
- CKS‑005 – Validator Specification
