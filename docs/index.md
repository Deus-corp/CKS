# Canonical Knowledge Structure

> A universal, representation-independent foundation for verifiable AI knowledge.

CKS is an open ecosystem that gives LLMs a **canonical knowledge backbone**. Every piece of information must be explicitly structured, validated against formal constraints, and traceable to its origin. This eliminates hallucinations and makes AI-generated knowledge auditable.

---

## How It Works

```
Your LLM (Claude Desktop, etc.)
        │
        ▼
    cks-mcp ─── Model Context Protocol server
        │
        ▼
 cks-runtime ─── Sessions, transactions, version history
        │
        ▼
   cks-core ─── Immutable semantic engine
```

## Key Capabilities

- **Eliminate citation hallucinations** – mechanically detect references to non-existent sources.
- **Ensure verification integrity** – cryptographic signing guarantees that source checks actually happened.
- **Full audit trail** – every operation is captured in an immutable version history.
- **Time-travel debugging** – list versions, compare them, and safely roll back to any previous state.
- **LLM-friendly API** – native MCP server with 7 tools, fully compatible with Claude Desktop and other MCP clients.

## Projects

| Project | Description | Status |
|---------|-------------|--------|
| [cks-core](cks-core/index.md) | Semantic engine – immutable knowledge objects, validation, evolution | Stable v1.7.0 |
| [cks-runtime](cks-runtime/index.md) | Operational environment – sessions, transactions, versioning, events | Stable v1.0.1 |
| [cks-mcp](cks-mcp/index.md) | MCP server – exposes CKS to LLMs | Stable v1.0.4 |

## Get Started in 5 Minutes

```bash
pip install cks-core cks-runtime cks-mcp
```

Then connect to Claude Desktop – see the [Quick Start guide](quickstart.md).

---

## Why CKS?

Today, the same knowledge exists in many incompatible forms – documents, databases, JSON, source code, AI prompts. CKS separates **knowledge itself** from every representation. Representations may change, but canonical knowledge remains the same.
