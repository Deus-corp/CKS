"""
CKS Command-Line Interface.

Canonical entry point for interacting with CKS from the terminal.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from ..serialization import parse as cks_parse, serialize as cks_serialize, SerializationError
from ..validator import validate as cks_validate
from ..diagnostics import DiagnosticSeverity
from ..evolution import compose, StructuralOperator, AddObject, AddRelation, RemoveObject, RemoveRelation
from ..core import KnowledgeObject, CanonicalRelation, ObjectIdentity
from .formatters import format_json, format_text, format_html, format_markdown


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cks",
        description="Canonical Knowledge Structure — CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # validate
    validate_parser = sub.add_parser("validate", help="Validate a Knowledge Structure")
    validate_parser.add_argument("input", type=Path, nargs="+", help="Path(s) to canonical JSON file(s)")
    validate_parser.add_argument("--format", "-f", choices=("text", "json", "html", "markdown"), default="text")
    validate_parser.add_argument("--output", "-o", type=Path, default=None)
    validate_parser.add_argument(
        "--min-severity",
        choices=("error", "warning", "information"),
        default="error",
        help="Minimum severity to consider a structure invalid",
    )

    # parse
    parse_parser = sub.add_parser("parse", help="Parse a canonical JSON file")
    parse_parser.add_argument("input", type=Path)

    # schema
    schema_parser = sub.add_parser("schema", help="Schema-related utilities")
    schema_sub = schema_parser.add_subparsers(dest="schema_command", required=True)
    schema_validate_parser = schema_sub.add_parser("validate", help="Validate a JSON document against the canonical schema")
    schema_validate_parser.add_argument("input", type=Path, help="Path to JSON file")
    schema_validate_parser.set_defaults(func=_run_schema_validate_command)

    # inspect
    inspect_parser = sub.add_parser("inspect", help="Inspect a Knowledge Structure")
    inspect_parser.add_argument("input", type=Path)
    inspect_parser.add_argument("--format", "-f", choices=("text", "json"), default="text")
    inspect_parser.add_argument("--output", "-o", type=Path, default=None)

    # evolve
    evolve_parser = sub.add_parser("evolve", help="Apply structural evolution")
    evolve_parser.add_argument("input", type=Path, help="Path to canonical JSON file")
    evolve_parser.add_argument("operations", type=Path, help="JSON file describing operations")
    evolve_parser.add_argument("--output", "-o", type=Path, default=None, help="Write result to file")

    # plugin
    plugin_parser = sub.add_parser("plugin", help="Manage plugins")
    plugin_sub = plugin_parser.add_subparsers(dest="plugin_command", required=True)
    plugin_list = plugin_sub.add_parser("list", help="List loaded constraints")
    plugin_list.set_defaults(func=_run_plugin_list_command)

    return parser


def _read_structure(path: Path):
    try:
        raw = path.read_text(encoding="utf-8")
        return cks_parse(raw)
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}")
    except SerializationError as exc:
        raise SystemExit(f"Serialization error: {exc}")


def _write_output(content: str, path: Optional[Path]) -> None:
    if path is None:
        print(content)
    else:
        path.write_text(content, encoding="utf-8")


def _parse_operations(ops_data: list[dict]) -> list[StructuralOperator]:
    operators = []
    for op in ops_data:
        op_type = op["type"]
        if op_type == "add_object":
            identity = ObjectIdentity(**op["identity"])
            obj = KnowledgeObject(identity=identity, structure=op.get("structure", {}))
            operators.append(AddObject(obj))
        elif op_type == "add_relation":
            identity = ObjectIdentity(**op["identity"])
            relation = CanonicalRelation(
                identity=identity,
                participants=op["participants"],
                relation_type=op["relation_type"],
                structure=op.get("structure", {}),
            )
            operators.append(AddRelation(relation))
        elif op_type == "remove_object":
            operators.append(RemoveObject(op["object_id"]))
        elif op_type == "remove_relation":
            operators.append(RemoveRelation(op["relation_id"]))
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
    return operators

def _run_plugin_list_command(_args):
    """Print every constraint registered in the global registry."""
    from ..constraints import registry
    constraints = registry.constraints()
    if not constraints:
        print("No constraints registered.")
        return
    for c in constraints:
        print(f"  {c.identity} — {c.description or '(no description)'}")

def _run_schema_validate_command(args):
    """Run schema validation on a JSON file."""
    try:
        raw = args.input.read_text(encoding="utf-8")
        data = json.loads(raw)
    except FileNotFoundError:
        raise SystemExit(f"File not found: {args.input}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {exc}")

    from ..schema import validate_json, SchemaValidationError
    try:
        validate_json(data)
        print("✅ Schema valid")
    except SchemaValidationError as exc:
        print(f"❌ Schema invalid: {exc}")
        sys.exit(1)


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = _create_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        # Determine minimum severity from CLI
        severity_map = {
            "error": DiagnosticSeverity.ERROR,
            "warning": DiagnosticSeverity.WARNING,
            "information": DiagnosticSeverity.INFORMATION,
        }
        min_severity = severity_map.get(args.min_severity, DiagnosticSeverity.ERROR)

        # Map format to formatter
        formatter_map = {
            "json": format_json,
            "text": format_text,
            "html": format_html,
            "markdown": format_markdown,
        }
        formatter = formatter_map.get(args.format, format_text)

        structures = []
        for path in args.input:
            try:
                structures.append(_read_structure(path))
            except SystemExit:
                raise

        if len(structures) == 1:
            # Single file
            result = cks_validate(structures[0], min_severity=min_severity)
            formatted = formatter(result)
            _write_output(formatted, args.output)
            sys.exit(0 if result.is_valid else 1)
        else:
            # Batch mode – aggregate
            from cks.validator import validate_all
            results_list = validate_all(structures, min_severity=min_severity)
            total = len(results_list)
            valid_count = sum(1 for r in results_list if r.is_valid)
            print(f"Files validated: {total}")
            print(f"Valid: {valid_count}")
            print(f"Invalid: {total - valid_count}")
            print()
            for path, result in zip(args.input, results_list):
                status = "✅ Valid" if result.is_valid else "❌ Invalid"
                print(f"{path}: {status}")
            sys.exit(0 if valid_count == total else 1)

    elif args.command == "parse":
        structure = _read_structure(args.input)
        print(f"Objects: {len(structure.objects)}")
        print(f"Relations: {len(structure.relations())}")

    elif args.command == "inspect":
        structure = _read_structure(args.input)
        lines = [
            f"Objects: {len(structure.objects)}",
            f"Relations: {len(structure.relations())}",
            "",
        ]
        for obj in structure.objects:
            lines.append(f"  {obj.identity.type}: {obj.identity.id} ({obj.identity.name})")

        if args.format == "json":
            data = {
                "objects": [
                    {"id": obj.identity.id, "type": obj.identity.type, "name": obj.identity.name}
                    for obj in structure.objects
                ],
                "relations": [
                    {"id": r.identity.id, "type": r.relation_type, "participants": list(r.participants)}
                    for r in structure.relations()
                ],
            }
            formatted = json.dumps(data, indent=2)
        else:
            formatted = "\n".join(lines)
        _write_output(formatted, args.output)

    elif args.command == "evolve":
        structure = _read_structure(args.input)
        ops_data = json.loads(args.operations.read_text(encoding="utf-8"))
        operators = _parse_operations(ops_data)
        new_structure = compose(structure, operators)
        result = cks_serialize(new_structure)
        _write_output(result, args.output)

    elif args.command == "schema":
        args.func(args)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()