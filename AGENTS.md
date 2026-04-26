# managed-research — agent notes

Workspace-wide guardrails live at [`../AGENTS.md`](../AGENTS.md).

## CRITICAL: Prod launch checklist

Any `managed-research` PyPI release or MCP server change tied to a launch must
clear the Packages / SDK / MCP sections of
[`../synth-dev/launch_checklist.md`](../synth-dev/launch_checklist.md) —
fresh-venv install smoke, MCP startup with no duplicate-tool errors,
`uv tool install managed-research` resolves the launch version, backend
version-contract parity. Record published version + smoke output as proof.

Version scheme: `1.<year>.<MMDD><HH>` (e.g. `1.2026.42111`).
