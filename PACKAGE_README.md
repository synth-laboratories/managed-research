# managed-research

Managed Research is Synth's Python SDK and MCP package for repeatable,
inspectable repo work.

## Install

```bash
uv add managed-research
```

## 60-Second Quickstart

```python
from managed_research import ManagedResearchClient

client = ManagedResearchClient(api_key="sk_...")

project = client.projects.default()
run = project.runs.start(
    "Inspect the repo, improve the benchmark path, and explain the changes.",
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)

print(run.id)
```

`ManagedResearchClient` is the canonical entrypoint. `SmrControlClient`
remains available as a compatibility alias for one release.

## Main Ideas

- Use `client.projects` to create or list projects.
- Use `client.project(project_id)` for project-scoped nouns like
  `repositories`, `files`, `outputs`, and `runs`.
- Use `client.runs.start(...)` when you want the default miscellaneous
  project flow.
- Use launch preflight before a manual run when you need to inspect blockers.
- Use `agent_harness="codex"` or `agent_harness="opencode_sdk"` when you want
  to pin the harness explicitly.

## OpenCode Harness

OpenCode is a first-class harness option with this initial model palette:

- `anthropic/claude-sonnet-4-6`
- `anthropic/claude-haiku-4-5-20251001`
- `x-ai/grok-4.1-fast`

For deeper examples, see:

- [`docs/quickstart.md`](./docs/quickstart.md)
- [`docs/python-sdk.md`](./docs/python-sdk.md)
- [`docs/mcp.md`](./docs/mcp.md)
