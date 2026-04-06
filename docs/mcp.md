# MCP Guide

Run the managed-research stdio MCP server directly from the package:

```bash
python -m managed_research.mcp
```

The maintained remigration surface includes:

- `smr_attach_source_repo`
- `smr_patch_project`
- `smr_get_project_notes`
- `smr_set_project_notes`
- `smr_append_project_notes`
- `smr_pause_project`
- `smr_resume_project`
- `smr_archive_project`
- `smr_unarchive_project`
- `smr_get_workspace_inputs`
- `smr_upload_workspace_files`
- `smr_get_project_readiness`
- `smr_get_capacity_lane_preview`
- `smr_get_run_start_blockers`
- `smr_trigger_run`
- `smr_get_run_progress`
- `smr_get_capabilities`
- `smr_get_project_entitlement`
- `smr_get_limits`
- `smr_get_workspace_download_url`
- `smr_download_workspace_archive`
- `smr_get_project_git`
- checkpoint and log-archive helpers

This package intentionally does not expose the old onboarding/starting-data or
Data Factory tool families.

## Launch Sequence

Use this order for launch-time UX:

1. `smr_health_check`
2. `smr_create_project` or `smr_list_projects`
3. `smr_attach_source_repo` or `smr_upload_workspace_files`
4. optionally `smr_set_project_notes` or `smr_append_project_notes`
5. `smr_get_project_readiness`
6. `smr_get_capacity_lane_preview`
7. `smr_get_run_start_blockers`
8. `smr_trigger_run`
9. `smr_get_run_progress`
10. `smr_get_workspace_download_url`, `smr_download_workspace_archive`, or `smr_get_project_git`

`smr_get_limits` and `smr_get_project_entitlement` are useful hints, but trigger
and blockers remain authoritative for whether a run can launch right now.

Kickoff migration note:

- use `initial_runtime_messages` for opening intent on both blockers and trigger
- do not send the removed `prompt` field

## Trigger Denials

MCP trigger denials do not always appear as protocol-level tool failures.
Structured denials come back as successful tool results with top-level fields:

- `error`
- `detail`
- `message`
- `http_status`

Always branch on `result.get("error")` after `smr_trigger_run`.

Example structured denial:

```json
{
  "error": "smr_free_tier_routing_violation",
  "detail": {
    "error_code": "smr_free_tier_routing_violation",
    "invariant": "ga_free_must_not_use_synth_codex_pool"
  },
  "message": "routing",
  "http_status": 409
}
```

Successful trigger responses instead contain run data such as `run_id` and
`state`.

Some onboarding or validation failures may still arrive as plain errors rather
than structured `detail.error_code` payloads, so do not assume every failure can
be parsed with one schema.

## Workspace Retrieval

- Workspace download URLs are short-lived presigned URLs.
- The snapshot is project-level, not per-run.
- `smr_download_workspace_archive` writes to the machine running the MCP server.
- Use `git pull` only when your deployment actually pushes back to the attached
  repo; otherwise fetch the workspace archive.

## Project Lifecycle And Notebook

- `smr_get_project_notes`, `smr_set_project_notes`, and `smr_append_project_notes`
  manage the durable project notebook.
- `smr_pause_project` and `smr_resume_project` control whether new runs can start.
- `smr_archive_project` and `smr_unarchive_project` expose the project lifecycle
  toggles without needing a raw patch call.
