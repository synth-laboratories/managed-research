# Managed Research

Hosted AI workers for durable repo and research runs.

**Documentation:** https://docs.usesynth.ai/managed-research/intro

Managed Research lets you start work from Python or MCP, attach repositories and
context, then inspect logs, checkpoints, artifacts, PRs, usage, and final
reports.

## Installation

```bash
uv add managed-research
```

## Authenticate

```bash
export SYNTH_API_KEY="sk_..."
```

## Python Quickstart

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

## MCP Quickstart

Add the hosted Managed Research MCP server to Codex:

```bash
codex mcp add managed-research --url https://api.usesynth.ai/mcp
```

Or add it to Claude Code:

```bash
claude mcp add --transport http managed-research https://api.usesynth.ai/mcp
```

Then ask your agent to list projects or start a run with the Managed Research
tools.

## What You Get

- Durable runs with IDs, states, messages, traces, and artifacts.
- Inspectable evidence: timelines, logs, usage, actor/task counts, questions,
  approvals, and output manifests.
- Recoverable progress through checkpoints and checkpoint branches.
- Python and MCP as the supported public integration paths.
- Configurable harnesses, runbooks, work modes, providers, budgets, and runtime
  limits.

## Links

- [Quickstart](https://docs.usesynth.ai/managed-research/quickstart)
- [MCP quickstart](https://docs.usesynth.ai/managed-research/mcp-quickstart)
- [Python SDK quickstart](https://docs.usesynth.ai/managed-research/sdk-quickstart)
- [Models and harnesses](https://docs.usesynth.ai/managed-research/models-and-harnesses)
- [Runs and evidence](https://docs.usesynth.ai/managed-research/runs-and-evidence)
- [Preflight and errors](https://docs.usesynth.ai/managed-research/preflight-and-errors)
