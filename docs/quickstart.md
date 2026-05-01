# Quickstart

This guide starts a Managed Research run from Python, waits for it to finish,
and inspects the useful evidence it leaves behind.

## 1. Install

```bash
uv add managed-research
export SYNTH_API_KEY="sk_..."
```

## 2. Start A Misc Project Run

Use this when you want the fastest path: one objective, one hosted worker, one
durable run in the caller's Miscellaneous project.

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

print("project:", run.project_id)
print("run:", run.run_id)
```

Pass `project_id=` or `project=ProjectSelector.from_project_id(...)` when the run
belongs to a specific existing project. If no project is provided, the SDK uses
the Miscellaneous project.

## 3. Wait And Inspect

`runs.start(...)` returns a `RunHandle`. The handle keeps the project and run IDs
together so follow-up reads stay simple.

```python
result = run.wait(timeout=60 * 60, poll_interval=15)

print("state:", result.state.value)
print("stop reason:", result.stop_reason_message or result.stop_reason)
print("tasks:", run.task_counts())
print("actors:", run.actor_counts())
```

Read the runtime messages and artifacts:

```python
for message in run.messages(limit=20):
    print(message.get("role"), message.get("status"), message.get("body", "")[:120])

manifest = run.artifact_manifest()
print("output files:", [artifact.path for artifact in manifest.output_files])

for artifact in run.artifacts():
    print(artifact.artifact_id, artifact.artifact_type, artifact.title)

evidence = run.operator_evidence()
print("evidence keys:", sorted(evidence.keys()))
```

## 4. Use A Project When Context Matters

Projects are the right shape when a worker needs repo bindings, uploaded files,
datasets, credentials, notes, or reusable knowledge.

```python
project = client.projects.create(name="Improve my eval runner")
project.repositories.attach(github_repo="owner/repo")

project.context.set_project_knowledge(
    "Focus on benchmark reliability, reproducibility, and clear run evidence."
)

preflight = project.runs.preflight(
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)

if not preflight.clear_to_trigger:
    raise RuntimeError(preflight.resolution_reason or "Run is not ready to start")

run = project.runs.start(
    "Inspect the eval runner, fix the highest-leverage issue, and explain the evidence.",
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)
```

## 5. Recover Or Branch From A Checkpoint

Longer work benefits from explicit recovery points.

```python
checkpoint = run.create_checkpoint(reason="before trying a riskier refactor")

retry = run.branch_from_checkpoint(
    checkpoint_id=checkpoint.checkpoint_id,
    mode="with_message",
    message="Try again from this checkpoint, but optimize for the smallest patch.",
)

print("branched run:", retry.child_run_id)
```

## OpenCode Harness

Codex is the default harness. OpenCode can be selected explicitly:

```python
run = client.runs.start(
    "Review the repo and propose the smallest high-impact fix.",
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

If the requested `(agent_harness, agent_model)` pair is unsupported, launch
preflight and run start fail loudly with structured denials.

## MCP Equivalent

Use hosted MCP when the caller is an agent framework rather than Python code:

```bash
codex mcp add managed-research --url https://api.usesynth.ai/mcp
```

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
        "body": "Review the project context and propose the smallest high-impact improvement."
      }
    ]
  }
}
```
