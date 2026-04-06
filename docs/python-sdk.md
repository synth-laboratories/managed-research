# Python SDK Guide

The maintained SMR SDK ships in this package under the `managed_research`
import namespace.

Install:

```bash
uv add synth-managed-research
```

Import:

```python
from managed_research.sdk.client import SmrControlClient
```

High-leverage public flows:

- `attach_source_repo(project_id, url, default_branch=None)`
- `get_workspace_inputs(project_id)`
- `upload_workspace_files(project_id, files)`
- `upload_workspace_directory(project_id, directory)`
- `set_project_notes(project_id, notes)` / `append_project_notes(project_id, notes)`
- `pause_project(project_id)` / `resume_project(project_id)`
- `archive_project(project_id)` / `unarchive_project(project_id)`
- `get_project_readiness(project_id)`
- `get_capacity_lane_preview(project_id)`
- `get_run_start_blockers(project_id, host_kind=..., work_mode=...)`
- `trigger_run(project_id, host_kind=..., work_mode=...)`
- `get_run_progress(project_id, run_id)`
- `get_workspace_download_url(project_id)`
- `download_workspace_archive(project_id, output_path)`
- `get_project_git(project_id)`

Recommended sequence:

```python
from managed_research.sdk.client import SmrControlClient

client = SmrControlClient(api_key="sk_...")
project_id = "proj_123"

client.set_project_notes(project_id, "Notebook only. Kickoff intent belongs in runtime messages.")
client.get_project_readiness(project_id)
client.get_capacity_lane_preview(project_id)
blockers = client.get_run_start_blockers(
    project_id,
    host_kind="daytona",
    work_mode="directed_effort",
    agent_kind="codex",
    initial_runtime_messages=[
        {"body": "Start with the launch blocker and confirm staging first.", "mode": "queue"}
    ],
)

if blockers["clear_to_trigger"]:
    client.trigger_run(
        project_id,
        host_kind="daytona",
        work_mode="directed_effort",
        agent_kind="codex",
        initial_runtime_messages=[
            {"body": "Start with the launch blocker and confirm staging first.", "mode": "queue"}
        ],
    )
```

Notes:

- `host_kind` is required for project-scoped trigger and run-start blockers.
- kickoff text must go through `initial_runtime_messages`; the legacy `prompt` field is not accepted.
- project notebook and lifecycle helpers also hang off `client.projects.*` as namespace methods.
- SDK callers receive non-2xx errors as exceptions. The `result.error` pattern
  applies to MCP clients, not the Python SDK.
