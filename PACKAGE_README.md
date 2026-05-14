# Managed Research

Hosted AI workers for durable repo and research runs.

**Documentation:** https://docs.usesynth.ai/managed-research/intro

Use Managed Research when you want a repeatable run instead of an untraceable
chat transcript: attach repositories and context, launch work from Python or
MCP, and read back logs, checkpoints, artifacts, PRs, usage, and final reports.

Managed Research is currently private beta only. This package requires an
authenticated Synth account with Managed Research beta access; backend
entitlement checks and launch preflight remain authoritative for every run.

## Engineering style

Contributors should follow **Synth Style** (engineering rules for contracts,
errors, and structure). The canonical Markdown copy lives in the **backend**
repository: [`specifications/tanha/references/synthstyle.md`](https://github.com/synth-laboratories/backend/blob/dev/specifications/tanha/references/synthstyle.md).

## Beta Surface

This package is for authenticated private-beta Managed Research integrations.
The Python SDK and MCP server expose the backend catalog for project and run
automation, including the runbook presets, work modes, model catalog, and usage
state the authenticated org is entitled to use.

Beta access is an account/org entitlement, not a client-side tier selection.
Treat backend entitlement checks and launch preflight as the source of truth for
which harnesses, work modes, models, providers, and usage pools are available.
See the customer docs for the current product status:
https://docs.usesynth.ai/managed-research/intro

## Installation

```bash
uv add managed-research
```

Set an API key:

```bash
export SYNTH_API_KEY="sk_..."
```

## Quickstart

```python
import os

from managed_research import ManagedResearchClient, ProjectSelector

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

## Main Ideas

- Use `ManagedResearchClient` as the Python entrypoint.
- Use `client.runs.start(...)` for runs that default to the caller's
  Miscellaneous project.
- Pass `project_id=` or `project=ProjectSelector.from_project_id(...)` when a
  run belongs to a specific existing project.
- Use `client.projects.create(...)` and `client.project(project_id)` for durable
  project-scoped work.
- Run preflight before launch when you want structured launch blockers.
- Inspect runs through messages, timelines, event logs, authority readouts,
  operator evidence, traces, checkpoints, artifacts, usage, questions,
  approvals, and actor/task counts.
- Use MCP from Codex or Claude Code when you want an agent-native interface.

## Resource limits

Managed Research exposes resource limits as first-class run and project state.
Use `resource_limits()` to inspect configured caps and
`progress_toward_resource_limits()` to inspect current usage, active blockers,
and extension posture.

When a spend limit blocks work, call `request_resource_limit_extension(...)`
from a run, project, or `ManagedResearchClient`. Extensions accept either a new
absolute USD limit or an added USD amount, plus optional blocker resolution and
resume behavior. MCP exposes the same flow through
`smr_get_run_resource_limits`, `smr_get_run_progress_toward_resource_limits`,
`smr_get_project_resource_limits`,
`smr_get_project_progress_toward_resource_limits`, and
`smr_request_resource_limit_extension`.

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

## Links

- [Quickstart](https://docs.usesynth.ai/managed-research/quickstart)
- [MCP quickstart](https://docs.usesynth.ai/managed-research/mcp-quickstart)
- [Python SDK quickstart](https://docs.usesynth.ai/managed-research/sdk-quickstart)
- [Launch fields](https://docs.usesynth.ai/managed-research/launch-fields)
- [Models and harnesses](https://docs.usesynth.ai/managed-research/models-and-harnesses)
- [Runs and evidence](https://docs.usesynth.ai/managed-research/runs-and-evidence)
