# Changelog

All notable changes to the Canonical Knowledge Structure (CKS) project are documented in this file.

The project follows a semantic versioning strategy where practical.

---

## [0.8.0] - 2026-07-14

### Added

#### Plugin Architecture

- External constraint discovery via `importlib.metadata` entry points.
- `cks.plugin` module for loading plugins at import time.
- `cks plugin list` CLI command to inspect registered constraints.
- `docs/plugins.md` — guide for creating and distributing constraint plugins.

#### API Stabilization

- Evolution operators (`AddObject`, `AddRelation`, `RemoveObject`, `RemoveRelation`, `compose`) promoted to public API.
- Full `__all__` declarations across all public modules.
- `cks.interface.evolve` now accepts `operators` instead of `add`/`remove` keyword arguments.

#### Documentation

- Added `docs/plugins.md` (Plugin Development Guide).
- Updated `docs/api.md` with evolution operators and plugin references.

#### Testing

- All 110 tests passing.

---

## [0.7.0] - 2026-07-14

### Added

#### CLI (Command-Line Interface)

- `cks validate` command with `--format` (text/json) and `--output` options.
- `cks parse` command for quick structural inspection.
- `cks inspect` command with text and JSON output modes.
- `cks evolve` command applying structural evolution from JSON operation files.
- Structured `cks.cli` package with extensible formatters (`formatters.py`).

#### Structural Evolution (CKS-004)

- `StructuralOperator` abstract base class with `OperatorContract`.
- `AddObject` and `AddRelation` (Genesis operators).
- `RemoveObject` and `RemoveRelation` (Decay operators).
- `compose()` for chaining multiple operators.
- Integration into `ReferenceEngine.evolve()`.

#### Constraints Refactoring

- Moved constraint implementations to domain-specific modules (`structural.py`, `semantic.py`) matching Validation Domains (CKS‑005).
- Converted `builtin.py` into a manifest that imports and instantiates canonical constraints.
- Removed duplicate registration logic; constraints are now registered exclusively through `builtin.py`.

#### Reference Corpus

- Initial canonical examples under `examples/corpus/`:
  - `valid_theory_example.json`
  - `invalid_duplicate_id.json`
  - `invalid_dangling_reference.json`
  - `invalid_derivation_cycle.json`

#### Documentation

- Updated `README`, `ROADMAP`, `CHANGELOG`, `CONTRIBUTING`.
- Updated `docs/`: Getting Started, API Reference, Architecture, Concepts, Examples, Index.
- Added CLI usage and evolution to all documentation.

#### Testing

- 11 unit tests for `evolution.py`.
- 13 CLI integration tests (`tests/test_cli.py`) covering all commands and formats.
- Total test suite: 116 tests passing.

---

## [0.1.0] - 2026-07-13

### Added

#### Core Implementation

* Initial immutable implementation of `ObjectIdentity`
* Initial immutable implementation of `KnowledgeObject`
* Initial implementation of `CanonicalRelation`
* Initial implementation of `KnowledgeStructure`
* Structural equivalence support

#### Serialization

* Canonical JSON serializer
* Canonical JSON deserializer
* Round-trip serialization support
* Canonical serialization validation
* `SerializationError`

#### Validation

* Reference validation pipeline
* Structural validation
* Semantic validation
* Referential integrity validation
* Derivation cycle detection
* Constraint registry
* Immutable `ValidationResult`
* Canonical diagnostics

#### Reference Engine

* Initial `ReferenceEngine`
* Knowledge construction
* Inspection
* Comparison
* Projection
* Extraction
* Evolution interface
* Validation integration

#### Public API

* Canonical public interface (`cks.interface`)
* Stable package exports
* Public construction API
* Public serialization API
* Public validation API
* Public inspection API

#### Testing

* Comprehensive unit test suite
* Core tests
* Serialization tests
* Validator tests
* Engine tests
* Public interface tests

#### Documentation

* Complete README
* CONTRIBUTING guide
* Repository metadata
* Public API documentation
* Project overview

---

### Notes

This is the first public release of the Canonical Knowledge Structure (CKS) reference implementation.

The implementation provides the initial executable realization of the CKS Core Specifications and establishes the foundation for future development of canonical constraints, reference corpora, documentation, and additional language implementations.