# cks-mcp

> Model Context Protocol server for Canonical Knowledge Structure.

`cks-mcp` provides LLMs with structured, verifiable knowledge operations through the CKS ecosystem. It exposes seven tools backed by the deterministic, immutable semantics of `cks-core` and the operational management of `cks-runtime`.

## Why cks-mcp?

LLMs generate plausible but unverified statements. `cks-mcp` gives them a **canonical knowledge backbone**: every piece of information must be explicitly structured, validated against formal constraints, and traceable to its origin.

## Tools

| Tool | Description |
|------|-------------|
| `validate_knowledge` | Validate a Knowledge Structure and return diagnostics. Supports opt‑in extensions. |
| `serialize_knowledge` | Serialize a Knowledge Structure into canonical JSON. |
| `explain_knowledge` | Produce a semantic explanation of a Knowledge Structure. |
| `evolve_knowledge` | Apply Genesis/Decay operators to evolve a structure. |
| `verify_source` | Perform a real HTTP check and create a cryptographically signed `VerificationRecord`. |
| `list_versions` | List all available versions of a session's history. |
| `compare_versions` | Compute the structural diff between two versions with explicit `direction`. |
| `revert_version` | Revert a session's Knowledge Structure to a specific previous version. |

## Anti-Hallucination Features

- **Citation verification** — `embedding_projection` extension mechanically detects references to non-existent sources.
- **Verification integrity** — `verify_source` performs real HTTP checks and signs the result. Hand‑written `VerificationRecord` objects are automatically rejected.
- **Provenance enforcement** — even if a model forgets to request it, every `VerificationRecord` is unconditionally checked for a valid signature.

## Quick Example

```json
{
  "method": "tools/call",
  "params": {
    "name": "validate_knowledge",
    "arguments": {
      "json_data": "{\"objects\":[{\"identity\":{\"id\":\"obj-1\",\"type\":\"Definition\",\"name\":\"Test\"},\"structure\":{}}]}"
    }
  }
}
```

Response:

```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"valid\": true, \"version_id\": \"...\", \"session_id\": \"...\", \"diagnostics\": []}"
      }
    ]
  }
}
```

## Learn More

- [Quick Start Guide](../quickstart.md)
- [MCP Server Architecture](ARCHITECTURE.md)