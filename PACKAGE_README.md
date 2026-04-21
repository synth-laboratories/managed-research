# managed-research

Managed Research lets you start hosted AI workers from Python or MCP and inspect
their work as durable runs. It is for repo and research tasks where you want
logs, checkpoints, artifacts, approvals, usage, and final outputs instead of an
untraceable chat transcript.

## Install

```bash
uv add managed-research
```

```bash
export SYNTH_API_KEY="sk_..."
```

## Quickstart

```python
import os

from managed_research import ManagedResearchClient

client = ManagedResearchClient(api_key=os.environ["SYNTH_API_KEY"])

run = client.runs.start(
    "Review the project context and propose the smallest high-impact improvement.",
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)

print("run:", run.run_id)

result = run.wait(timeout=60 * 60, poll_interval=15)
print("state:", result.state.value)
print("artifacts:", [artifact.title for artifact in run.artifacts()])
```

`ManagedResearchClient` is the canonical entrypoint. `SmrControlClient`
remains available as a compatibility alias for one release.

## Main Ideas

- Use `client.runs.start(...)` for a one-off run on the default project.
- Use `client.projects.create(...)` and `client.project(project_id)` for durable
  project-scoped work.
- Attach repositories, files, datasets, credentials, notes, and knowledge before
  starting a run.
- Use preflight when you want launch blockers as structured data before spending
  runtime.
- Inspect runs through messages, timeline, traces, checkpoints, artifacts,
  usage, questions, approvals, and actor/task counts.
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
