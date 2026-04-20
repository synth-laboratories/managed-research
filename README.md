# managed-research

Managed Research is Synth's public Python SDK and MCP package for repeatable,
inspectable repo work. The canonical Python entrypoint is
`ManagedResearchClient`, and the canonical MCP surface mirrors the same
project/run nouns.

## Install

```bash
uv add managed-research
```

## Python SDK

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

You can also use the one-off shortcut:

```python
run = client.runs.start(
    "Review the repo and propose the smallest safe improvement.",
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)
```

`SmrControlClient` remains importable as a compatibility alias for one release.

## OpenCode Harness

Managed Research supports Codex as the default harness and OpenCode as an
opt-in harness choice:

```python
run = client.runs.start(
    "Do a careful bug-hunt and explain the fix.",
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
    agent_harness="opencode_sdk",
    agent_model="anthropic/claude-sonnet-4-6",
)
```

Supported OpenCode models:

- `anthropic/claude-sonnet-4-6`
- `anthropic/claude-haiku-4-5-20251001`
- `x-ai/grok-4.1-fast`

Unsupported `(agent_harness, agent_model)` pairs fail at preflight and run
start with structured denials.

## MCP

Hosted:

```bash
codex mcp add managed-research --url https://api.usesynth.ai/mcp
claude mcp add --transport http managed-research https://api.usesynth.ai/mcp
```

Local stdio:

```bash
uv tool install managed-research
managed-research-mcp
```

Example one-off run:

```json
{
  "tool": "smr_start_one_off_run",
  "arguments": {
    "host_kind": "daytona",
    "work_mode": "directed_effort",
    "providers": [{"provider": "openrouter"}],
    "initial_runtime_messages": [
      {
        "mode": "queue",
        "body": "Inspect the repo, improve the target workflow, and explain the changes."
      }
    ]
  }
}
```

Launch denials are MCP tool errors, not success payloads with embedded error
fields.

## More

- [`docs/quickstart.md`](./docs/quickstart.md)
- [`docs/python-sdk.md`](./docs/python-sdk.md)
- [`docs/mcp.md`](./docs/mcp.md)
