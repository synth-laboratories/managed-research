# managed-research

Canonical public home for Synth Managed Research.

This repository now owns the maintained SMR Python SDK, MCP server modules, and
schema tooling. The package is library-first:

- no standalone CLI migration
- no Data Factory surface
- no old onboarding / starting-data bootstrap APIs

## Install

```bash
uv add synth-managed-research
```

## Python SDK

```python
from managed_research.sdk.client import SmrControlClient

client = SmrControlClient(api_key="sk_...")
project = client.create_project({"name": "SMR demo"})
client.upload_workspace_files(
    project["project_id"],
    [{"path": "README.md", "content": "# Demo\n", "content_type": "text/markdown"}],
)
project_id = project["project_id"]
readiness = client.get_project_readiness(project_id)
lane_preview = client.get_capacity_lane_preview(project_id)
blockers = client.get_run_start_blockers(
    project_id,
    host_kind="daytona",
    work_mode="directed_effort",
    agent_kind="codex",
    initial_runtime_messages=[
        {"body": "Start with the highest-confidence blocker and confirm staging status.", "mode": "queue"}
    ],
)
if blockers["clear_to_trigger"]:
    run = client.trigger_run(
        project_id,
        host_kind="daytona",
        work_mode="directed_effort",
        agent_kind="codex",
        initial_runtime_messages=[
            {"body": "Start with the highest-confidence blocker and confirm staging status.", "mode": "queue"}
        ],
    )

client.projects.append_notes(
    project_id,
    "Post-run note: keep notebook updates separate from kickoff queue messages.",
)
```

## MCP

Run the stdio server directly:

```bash
python -m managed_research.mcp
```

The maintained MCP surface includes workspace bootstrap, launch preflight, and
progress tools such as `smr_attach_source_repo`, `smr_upload_workspace_files`,
`smr_set_project_notes`, `smr_append_project_notes`, `smr_pause_project`,
`smr_resume_project`, `smr_archive_project`, `smr_unarchive_project`,
`smr_get_capacity_lane_preview`, `smr_get_run_start_blockers`,
`smr_trigger_run`, `smr_get_project_readiness`, and `smr_get_run_progress`.

## Launch Contract

Use the same launch payload for blockers and trigger:

- create/select project
- attach a source repo or upload workspace files
- check readiness
- call `smr_get_capacity_lane_preview`
- call `smr_get_run_start_blockers`
- call `smr_trigger_run`
- observe progress
- retrieve the workspace snapshot with `smr_get_workspace_download_url`,
  `smr_download_workspace_archive`, or `smr_get_project_git`

`host_kind` is required for project-scoped launch preflight and trigger.

Kickoff prose is queue-first:

- use `initial_runtime_messages` for opening intent on blockers and trigger
- do not send the removed `prompt` field
- if you migrated from older integrations, convert `prompt="..."` to `initial_runtime_messages=[{"body": "...", "mode": "queue"}]`

Project notebook and lifecycle helpers are separate from kickoff:

- use `get_project_notes`, `set_project_notes`, and `append_project_notes` for durable notebook text
- use `pause_project` / `resume_project` and `archive_project` / `unarchive_project` for project lifecycle control

### MCP trigger success vs denial

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
HTTP/MCP errors without a structured `detail.error_code`. Treat the structured
shape as the preferred case, not the only case.

## Repo Layout

- `managed_research/sdk`
- `managed_research/mcp`
- `managed_research/models`
- `managed_research/transport`
- `managed_research/_internal`
- `managed_research/schema_sync.py`

Legacy code from the previous public package remains quarantined under
[`/Users/joshpurtell/Documents/GitHub/managed-research/old`](/Users/joshpurtell/Documents/GitHub/managed-research/old).
