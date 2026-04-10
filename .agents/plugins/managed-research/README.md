# Managed Research Codex Plugin

This repo ships the canonical local plugin metadata for Managed Research MCP.

Preferred hosted install:

- `codex mcp add managed-research --url https://api.usesynth.ai/mcp`
- `claude mcp add --transport http managed-research https://api.usesynth.ai/mcp`

Local stdio fallback:

- repo-local plugin metadata uses `uv run --quiet managed-research-mcp`
- package install path is `uv tool install synth-managed-research`

Included surface:

- `MCP`: `managed-research`

The MCP tool names, schemas, descriptions, and required scopes are owned by
this repository's `managed_research.mcp` package.
