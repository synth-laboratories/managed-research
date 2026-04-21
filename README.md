# managed-research

Managed Research lets you hand repo work to hosted AI workers and inspect what
they do. Start a run from Python or MCP, attach repositories and context, then
read back logs, checkpoints, artifacts, PRs, usage, and final outputs.

It is built for work that should be repeatable instead of one-off chat:

- improve a benchmark or eval harness
- review a codebase and open a focused PR
- run a research task with durable artifacts
- branch from checkpoints when an attempt needs a different direction
- give agents controlled access to project knowledge, files, credentials, and
  integrations

## Install

```bash
uv add managed-research
```

Set an API key:

```bash
export SYNTH_API_KEY="sk_..."
```

## 60-Second Quickstart

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

For project-scoped work:

```python
project = client.projects.create(name="Improve my eval runner")
project.repositories.attach(github_repo="owner/repo")

preflight = project.runs.preflight(
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)

if preflight.clear_to_trigger:
    run = project.runs.start(
        "Inspect the eval runner, fix the highest-leverage issue, and leave evidence.",
        host_kind="daytona",
        work_mode="directed_effort",
        providers=[{"provider": "openrouter"}],
    )
```

## Why Managed Research

- **Durable runs:** every run has an ID, state, runtime messages, traces, and
  artifacts.
- **Inspectable execution:** read task and actor counts, logical timelines,
  logs, usage, questions, approvals, and output manifests.
- **Recoverable progress:** create checkpoints, restore them, or branch from a
  checkpoint with a new message.
- **Harness choice:** run the default Codex harness or opt into OpenCode.
- **Agent-native access:** use the same project/run surface from Python or MCP.

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

## Worker Knowledge

Managed Research workers can already receive project files, repositories,
credentials, notes, and org/project knowledge. The next high-leverage layer is
a curated research index exposed to workers through MCP: papers, datasets,
GitHub repositories, Tinker cookbooks, internal runbooks, and project-specific
material behind one searchable interface.

The detailed design note lives in the Synth specifications tree:
[`specifications/daily/april21_2026/worker-knowledge.md`](../specifications/daily/april21_2026/worker-knowledge.md).

## More

- [`docs/quickstart.md`](./docs/quickstart.md)
- [`docs/python-sdk.md`](./docs/python-sdk.md)
- [`docs/mcp.md`](./docs/mcp.md)
- [`docs/migrations-1.2026.0420.md`](./docs/migrations-1.2026.0420.md)
