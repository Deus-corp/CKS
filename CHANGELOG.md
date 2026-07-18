# Changelog

All notable changes to the Canonical Knowledge Structure (CKS) project are documented in this file.

The project follows a semantic versioning strategy where practical.

---

## [1.3.0] - 2026-07-18

### Fixed
- **Severity comparison** now uses numeric priority instead of lexicographic string comparison, so warnings no longer incorrectly invalidate structures (bug #4).
- **DerivationCycleConstraint** no longer crashes with `KeyError` when a `derives` relation references a non-existent participant — dangling references are now safely ignored by the cycle detector (bug #3).
- **Schema CLI** (`cks schema validate`) now works after `pip install cks-core` — the canonical JSON schema is bundled as package data and loaded via `importlib.resources` (bug #5).

### Changed
- Schema file moved from `examples/json/` to `src/cks/schemas/` and declared as package data in `pyproject.toml`.

---

## [1.2.2] - 2026-07-18

### Added
- Public function `parse_operations` in `cks.evolution` for deserializing JSON operation descriptors into `StructuralOperator` objects. Used by CLI, `cks-mcp`, and any other adapter that receives evolution requests over the wire.

---

## [1.2.1] - 2026-07-18

### Fixed
- Validation pipeline no longer double‑counts diagnostics. The `CONSTRAINTS` stage now evaluates only constraints tagged with that stage, instead of re‑evaluating all registered constraints.

---

## [1.2.0] - 2026-07-18

### Fixed
- `copy.deepcopy` no longer raises `TypeError` for `KnowledgeObject` and `KnowledgeStructure` (resolved `cannot pickle 'mappingproxy' object`). These immutable types now return `self` on copy, which is safe and fixes integration with `cks-runtime`'s `InMemoryStorage`.
- Added 4 regression tests for copy/deepcopy behaviour.

---

## [1.1.2] - 2026-07-17

### Changed
- Repository renamed from `CKS` to `cks-core`.
- Updated all internal and ecosystem links to new repository URL.
- Added "Ecosystem" table to README.

---

## [1.1.1] - 2026-07-14

### Changed

- Renamed PyPI distribution package from `canonical-ks` to `cks-core`
  to align with the `cks-*` ecosystem naming convention.
  Python import remains `import cks`.

---

## [1.1.0] - 2026-07-14

### Added

- `--strict` flag for CLI to fail on plugin loading errors.
- `mypy` static type checking in CI/CD (strict for core modules).
- `docs/contracts.md` — formal contract chain documentation.
- `_normalize_structure()` in `core.py` for explicit structural comparison.
- Contract tests for plugin system (`tests/test_plugin.py`).
- Type annotations for core modules.

### Changed

- `CanonicalRelation` now validates `participants` and `relation_type` explicitly.
- CLI refactored into modular commands (`cli/commands/`).
- Plugin system replaced `stderr print` with structured `logging`.
- Removed Python <3.9 fallback from `plugin.py`.
- `mypy` configuration: strict only for core modules.
- Development status updated to `Production/Stable` in `pyproject.toml`.

### Fixed

- CanonicalRelation no longer silently ignores conflicting structure keys.
- CLI error handling improved for missing files and invalid operations.
- mypy type errors resolved across core modules.

### Testing

- All 119 tests passing.

---

## [1.0.1] - 2026-07-14

### Added

#### Import/Export Adapters

- JSON‑LD → CKS converter (`cks convert`).
- CKS → JSON‑LD converter (`cks export`).
- Turtle → CKS converter (`cks convert`).
- CKS → Turtle converter (`cks export`).
- RDF/XML → CKS converter (`cks convert`).
- CKS → RDF/XML converter (`cks export`).

#### CI/CD and Developer Tooling

- Pre-commit hooks for automatic CKS validation.
- CI pipeline with test matrix (Python 3.12, 3.13, 3.14).
- Linting with ruff.
- Pre-commit checks in CI.

### Changed

- Public API stabilised for 1.0.0 release.
- Package renamed to `canonical-ks` on PyPI (import remains `cks`).

### Testing

- All 114 tests passing.

---

## [0.9.0] - 2026-07-14

### Added

#### Advanced Validation

- `validate_all()` — batch validation of multiple Knowledge Structures.
- `--min-severity` option (error/warning/information) for configurable severity thresholds.
- HTML output formatter (`--format html`).
- Markdown output formatter (`--format markdown`).

#### CLI Improvements

- `validate` command now accepts multiple input files (`nargs="+"`).
- Severity map and formatter map integrated into CLI pipeline.
- Batch mode aggregates results across all input files.

### Changed

- `validate()` signature extended with optional `min_severity` parameter.
- `validate_all()` accepts `min_severity` parameter.
- `interface.py` exposes new `validate_all` function.

### Fixed

- Various import and name resolution issues in `interface.py`.

### Testing

- All 110 tests passing.

---

## [0.8.6] - 2026-07-14

### Changed

- Renamed PyPI distribution package to `canonical-ks` (Python import remains `import cks`).
- Updated `pyproject.toml` with correct package name and dependencies.

### Fixed

- Resolved PyPI publication name conflict by renaming distribution to `canonical-ks`.

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