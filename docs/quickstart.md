# Quickstart

Install the published package:

```bash
uv add synth-managed-research
```

Use the Python SDK:

```python
from managed_research.sdk.client import SmrControlClient

client = SmrControlClient(api_key="sk_...")
project = client.create_project({"name": "quickstart"})
client.upload_workspace_files(
    project["project_id"],
    [{"path": "README.md", "content": "# Quickstart\n", "content_type": "text/markdown"}],
)
project_id = project["project_id"]
client.set_project_notes(
    project_id,
    "Notebook only. Use runtime messages for kickoff intent.",
)
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

Kickoff migration note:

- use `initial_runtime_messages` for opening intent
- do not send the removed `prompt` field
- project notebook text is managed separately through `set_project_notes` / `append_project_notes`

Run the MCP server over stdio:

```bash
python -m managed_research.mcp
```

For MCP clients, the equivalent flow is:

1. `smr_health_check`
2. `smr_create_project` or `smr_list_projects`
3. `smr_attach_source_repo` or `smr_upload_workspace_files`
4. optionally `smr_set_project_notes`
5. `smr_get_project_readiness`
6. `smr_get_capacity_lane_preview`
7. `smr_get_run_start_blockers`
8. `smr_trigger_run`
9. `smr_get_run_progress`
10. `smr_get_workspace_download_url` or `smr_download_workspace_archive`
