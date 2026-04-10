# managed-research

Managed Research is Synth's product for applied AI teams that want repeatable,
inspectable research workflows against real repos. Wave 1 is strongest at
verification, eval execution, data assembly, and careful context optimization.
This repository owns the maintained Python SDK and MCP server that sit on top
of the SMR backend control plane.

This repository is library-first:

- no standalone CLI migration
- no Data Factory surface
- no old onboarding / starting-data bootstrap APIs

## Project Notes vs Curated Knowledge

- `project notes` are durable notebook text for operator memory and project
  context. Use `get_project_notes`, `set_project_notes`, and
  `append_project_notes`.
- `curated knowledge` is the PG-backed durable store for org- or
  project-scoped findings you want future work to build from. Use
  `get_org_knowledge`, `set_org_knowledge`, `get_project_knowledge`, and
  `set_project_knowledge`.

The two surfaces are intentionally separate. Project notes are not the same as
curated knowledge.

## Install

```bash
uv add synth-managed-research
```

## Python SDK

```python
from pathlib import Path

from managed_research import (
    SmrActorModelAssignment,
    SmrActorType,
    SmrAgentModel,
    SmrAgentProfileBindings,
    SmrControlClient,
    SmrEnvironmentKind,
    SmrHostKind,
    SmrRunnableProjectRequest,
    SmrRuntimeKind,
    SmrWorkMode,
    SmrWorkerSubtype,
)

client = SmrControlClient(api_key="sk_...")
project = client.create_runnable_project(
    SmrRunnableProjectRequest(
        name="nanohorizon-demo",
        timezone="UTC",
        pool_id="daytona-default",
        runtime_kind=SmrRuntimeKind.SANDBOX_AGENT,
        environment_kind=SmrEnvironmentKind.HARBOR,
        agent_profiles=SmrAgentProfileBindings(
            orchestrator_profile_id="codex_gpt_5_4_medium",
            default_worker_profile_id="codex_gpt_5_4_medium",
        ),
        notes="Operator notebook only. Kickoff intent belongs in runtime messages.",
        scenario="nanohorizon-demo",
    )
)
project_id = project["project_id"]
client.attach_source_repo(
    project_id,
    "https://github.com/synth-laboratories/nanohorizon.git",
    default_branch="main",
)
client.set_project_knowledge(
    project_id,
    "Known scoring constraints, prior prompt findings, and durable research takeaways for NanoHorizon.",
)
knowledge = client.get_project_knowledge(project_id)
kickoff = [
    {
        "body": "Inspect the repo, improve the benchmark-facing workflow, and leave behind evidence that explains what changed.",
        "mode": "queue",
    }
]
client.setup.prepare(project_id)
client.get_capacity_lane_preview(project_id)
preflight = client.get_launch_preflight(
    project_id,
    host_kind=SmrHostKind.DAYTONA,
    work_mode=SmrWorkMode.DIRECTED_EFFORT,
    agent_profile="codex_gpt_5_4_medium",
    initial_runtime_messages=kickoff,
)
if preflight["clear_to_trigger"]:
    run = client.trigger_run(
        project_id,
        host_kind=SmrHostKind.DAYTONA,
        work_mode=SmrWorkMode.DIRECTED_EFFORT,
        agent_profile="codex_gpt_5_4_medium",
        initial_runtime_messages=kickoff,
    )
    client.download_workspace_archive(project_id, Path("nanohorizon-workspace.tar.gz"))
```

If you need org-wide durable context instead of project-scoped knowledge, use
`set_org_knowledge(...)` and `get_org_knowledge()`.

Compatibility note:

- `create_project({...})` remains available for low-level callers
- `get_project_readiness(project_id)` is now a compatibility alias over the pure setup projection

## Launch Models

Use `agent_profile` when you want an exact backend-managed preset. If you need
to pass `agent_model` directly, use one of these public model ids:

- standard Codex models: `gpt-5.3-codex`, `gpt-5.3-codex-spark`, `gpt-5.4`, `gpt-5.4-mini`
- additional first-launch choices: `gpt-5.4-nano`, `gpt-oss-120b`

Shared top-level launch selection is intentionally narrower:

- top-level `agent_model` on `trigger_run(...)` / `get_run_start_blockers(...)` supports `gpt-5.4-mini`, `gpt-5.4`, `gpt-5.4-nano`, and `gpt-oss-120b`
- `gpt-5.3-codex` and `gpt-5.3-codex-spark` are `worker:engineer` only and must be assigned through actor-scoped config

Python callers should use the enum-backed surface:

```python
client.trigger_run(
    project_id,
    host_kind=SmrHostKind.DAYTONA,
    work_mode=SmrWorkMode.DIRECTED_EFFORT,
    agent_model=SmrAgentModel.GPT_OSS_120B,
    initial_runtime_messages=kickoff,
)
```

Actor-scoped engineer selection:

```python
client.trigger_run(
    project_id,
    host_kind=SmrHostKind.DAYTONA,
    work_mode=SmrWorkMode.DIRECTED_EFFORT,
    actor_model_overrides=[
        SmrActorModelAssignment(
            actor_type=SmrActorType.WORKER,
            actor_subtype=SmrWorkerSubtype.ENGINEER,
            agent_model=SmrAgentModel.GPT_5_3_CODEX,
        )
    ],
    initial_runtime_messages=kickoff,
)
```

## MCP

Primary path: use the hosted MCP endpoint:

```bash
codex mcp add managed-research --url https://api.usesynth.ai/mcp
claude mcp add --transport http managed-research https://api.usesynth.ai/mcp
```

Local stdio fallback:

```bash
uv tool install synth-managed-research
managed-research-mcp
```

The maintained MCP surface includes workspace bootstrap, launch preflight,
knowledge, and progress tools such as `smr_create_runnable_project`,
`smr_attach_source_repo`, `smr_upload_workspace_files`, `smr_set_project_notes`,
`smr_append_project_notes`, `smr_get_org_knowledge`,
`smr_set_org_knowledge`, `smr_get_project_knowledge`,
`smr_set_project_knowledge`, `smr_pause_project`, `smr_resume_project`,
`smr_archive_project`, `smr_unarchive_project`,
`smr_get_project_setup`, `smr_prepare_project_setup`,
`smr_get_capacity_lane_preview`, `smr_get_launch_preflight`,
`smr_trigger_run`, `smr_get_run`,
`smr_stop_run`, `smr_curated_knowledge`, `smr_runtime_message_queue`, and
`smr_get_run_progress`.

Project knowledge example:

```json
{
  "tool": "smr_set_project_knowledge",
  "arguments": {
    "project_id": "proj_123",
    "content": "Known benchmark constraints, prior failures, and durable findings for this project."
  }
}
```

```json
{
  "tool": "smr_get_project_knowledge",
  "arguments": {
    "project_id": "proj_123"
  }
}
```

## Launch Contract

Use the same launch payload for blockers and trigger:

- create/select a runnable project
- attach a source repo or upload workspace files
- optionally set project notes or curated knowledge
- prepare setup
- call `smr_get_capacity_lane_preview`
- call `smr_get_launch_preflight`
- call `smr_trigger_run`
- poll with `smr_get_run`
- retrieve the workspace snapshot with `smr_get_workspace_download_url`,
  `smr_download_workspace_archive`, or `smr_get_project_git`

For submission-style demos such as Nanoprogram, the next step after workspace
retrieval is local evaluation of `submission/optimizer.py` with the official
harness.

`smr_get_run_progress` is available on newer remigration surfaces, but the
launch-day walkthrough uses `smr_get_run` because it works across the backend
deployments we rehearse against.

`host_kind` is required for project-scoped launch preflight and trigger.

Compatibility note:

- `smr_create_project` remains available for low-level callers
- `smr_get_project_readiness` is now a compatibility alias over the pure setup projection
- `smr_get_run_start_blockers` is a compatibility alias over the launch-preflight path

Kickoff prose is queue-first:

- use `initial_runtime_messages` for opening intent on blockers and trigger
- do not send the removed `prompt` field
- if you migrated from older integrations, convert `prompt="..."` to
  `initial_runtime_messages=[{"body": "...", "mode": "queue"}]`

Project notebook, curated knowledge, and lifecycle helpers are separate:

- use `get_project_notes`, `set_project_notes`, and `append_project_notes` for
  durable notebook text
- use `get_org_knowledge`, `set_org_knowledge`, `get_project_knowledge`, and
  `set_project_knowledge` for PG-backed curated knowledge
- use `pause_project` / `resume_project` and `archive_project` /
  `unarchive_project` for project lifecycle control

### MCP Trigger Success vs Denial

In MCP clients, `smr_trigger_run` can still return a successful tool call that
means launch failed. Structured denials include:

```json
{
  "error": "smr_limit_exceeded",
  "detail": {"error_code": "smr_limit_exceeded", "resource_id": "agent_daytona"},
  "message": "limit hit",
  "http_status": 429
}
```

Always branch on `result.get("error")` before assuming a run started.

Successful trigger responses carry run data such as:

```json
{
  "run_id": "run_123",
  "state": "queued"
}
```

Some non-structured onboarding or validation failures may still surface as plain
HTTP or MCP errors without a structured `detail.error_code`. Treat the
structured shape as the preferred case, not the only case.

## Repo Layout

- `managed_research/sdk`
- `managed_research/mcp`
- `managed_research/models`
- `managed_research/schema_sync.py`
- `managed_research/transport`
- `managed_research/_internal`
