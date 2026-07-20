# Quick Start

Get CKS up and running with your LLM in under 5 minutes.

---

## 1. Install

One command installs the entire ecosystem:

```bash
pip install cks-mcp
```

This automatically brings in `cks-runtime`, `cks-core`, and all dependencies.

---

## 2. Connect to Claude Desktop

Add `cks-mcp` to your MCP servers.

1. Open Claude Desktop → **Settings** → **Developer** → **Edit Config**.
2. Add this block to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cks-mcp": {
      "command": "cks-mcp"
    }
  }
}
```

3. Save and restart Claude Desktop (Cmd+Q, then reopen).

After restart, a connector icon will appear — **cks-mcp** with seven tools is ready to use.

---

## 3. Your First Experiment

Ask Claude:

> Create a knowledge structure about "Quantum Mechanics" with two concepts (Wave-Particle Duality and Superposition). Link them with a relation. Then validate the structure.

Claude will call `validate_knowledge` and report back whether the structure is valid.

---

## What's Next

- Explore the [cks-core](cks-core/index.md) semantic engine.
- Learn about [cks-runtime](cks-runtime/index.md) sessions and version history.
- Read the [Architecture](cks-mcp/ARCHITECTURE.md) of the MCP server.

---

## Need Help?

- [GitHub Issues](https://github.com/Deus-corp/cks-core/issues)
- [Discussions](https://github.com/Deus-corp/cks-core/discussions)
