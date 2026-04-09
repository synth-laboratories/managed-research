# Python SDK Guide

Managed Research is Synth's product for teams that want repeatable,
inspectable research workflows against real repos. Wave 1 is strongest at
verification, eval execution, data assembly, and careful context optimization.
The Python SDK is the public programmatic control surface for creating projects,
storing durable context, and launching runs against that backend control plane.

Install:

```bash
uv add synth-managed-research
```

Import:

```python
from managed_research.sdk.client import SmrControlClient
```

## Project Notes vs Curated Knowledge

- `project notes` are durable notebook text for operator memory and local
  project context
- `curated knowledge` is the PG-backed durable store for org- or
  project-scoped findings you want future work to build from

These are intentionally separate surfaces.

High-leverage public flows:

- `attach_source_repo(project_id, url, default_branch=None)`
- `get_workspace_inputs(project_id)`
- `upload_workspace_files(project_id, files)`
- `upload_workspace_directory(project_id, directory)`
- `set_project_notes(project_id, notes)` / `append_project_notes(project_id, notes)`
- `set_org_knowledge(content)` / `get_org_knowledge()`
- `set_project_knowledge(project_id, content)` /
  `get_project_knowledge(project_id)`
- `pause_project(project_id)` / `resume_project(project_id)`
- `archive_project(project_id)` / `unarchive_project(project_id)`
- `get_project_readiness(project_id)`
- `get_capacity_lane_preview(project_id)`
- `get_run_start_blockers(project_id, host_kind=..., work_mode=...)`
- `trigger_run(project_id, host_kind=..., work_mode=...)`
- `get_run(run_id, project_id=...)`
- `get_run_progress(project_id, run_id)`
- `get_workspace_download_url(project_id)`
- `download_workspace_archive(project_id, output_path)`
- `get_project_git(project_id)`

Namespace helpers under `client.projects` mirror the project-scoped methods,
including `client.projects.get_notes(...)`, `client.projects.set_notes(...)`,
`client.projects.get_knowledge(...)`, and `client.projects.set_knowledge(...)`.

## Recommended Sequence

```python
from pathlib import Path

from managed_research.sdk.client import SmrControlClient

client = SmrControlClient(api_key="sk_...")
project = client.create_project({"name": "nanohorizon-sdk-demo"})
project_id = project["project_id"]
client.attach_source_repo(
    project_id,
    "https://github.com/synth-laboratories/nanohorizon.git",
    default_branch="main",
)
client.set_project_notes(
    project_id,
    "Notebook only. Kickoff intent belongs in runtime messages.",
)
client.set_project_knowledge(
    project_id,
    "Known benchmark constraints, prior failures, and durable findings for this project.",
)
client.get_project_knowledge(project_id)
kickoff = [
    {
        "body": "Inspect the repo, improve the benchmark-facing workflow, and leave behind evidence that explains what changed.",
        "mode": "queue",
    }
]
client.get_project_readiness(project_id)
client.get_capacity_lane_preview(project_id)
blockers = client.get_run_start_blockers(
    project_id,
    host_kind="daytona",
    work_mode="directed_effort",
    agent_kind="codex",
    agent_model="gpt-5.4",
    initial_runtime_messages=kickoff,
)

if blockers["clear_to_trigger"]:
    client.trigger_run(
        project_id,
        host_kind="daytona",
        work_mode="directed_effort",
        agent_kind="codex",
        agent_model="gpt-5.4",
        initial_runtime_messages=kickoff,
    )
    client.download_workspace_archive(project_id, Path("nanohorizon-workspace.tar.gz"))
```

Notes:

- `host_kind` is required for project-scoped trigger and run-start blockers
- kickoff text must go through `initial_runtime_messages`; the legacy `prompt`
  field is not accepted
- project notebook and curated knowledge are separate surfaces
- SDK callers receive non-2xx errors as exceptions. The `result.error` pattern
  applies to MCP clients, not the Python SDK
- for launch-day polling, prefer `get_run(run_id, project_id=project_id)`
- `get_run_progress(project_id, run_id)` is a richer projection on newer
  remigration surfaces, but it is not the stable walkthrough default yet
