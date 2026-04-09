# MCP Guide

Managed Research is Synth's product for teams that want repeatable,
inspectable research workflows against real repos. Wave 1 is strongest at
verification, eval execution, data assembly, and careful context optimization.
The MCP server is the public tool surface for launching, inspecting, and
capturing durable context around those workflows.

Run the managed-research stdio MCP server directly from the package:

```bash
python -m managed_research.mcp
```

## Project Notes vs Curated Knowledge

- `smr_get_project_notes`, `smr_set_project_notes`, and
  `smr_append_project_notes` manage the durable project notebook
- `smr_get_org_knowledge`, `smr_set_org_knowledge`,
  `smr_get_project_knowledge`, and `smr_set_project_knowledge` manage the
  PG-backed curated knowledge store

Project notes and curated knowledge are intentionally separate.

## Maintained Surface

The maintained remigration surface includes:

- `smr_attach_source_repo`
- `smr_patch_project`
- `smr_get_project_notes`
- `smr_set_project_notes`
- `smr_append_project_notes`
- `smr_get_org_knowledge`
- `smr_set_org_knowledge`
- `smr_get_project_knowledge`
- `smr_set_project_knowledge`
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
- `smr_get_run`
- `smr_get_run_progress`
- `smr_get_capabilities`
- `smr_get_project_entitlement`
- `smr_get_limits`
- `smr_get_workspace_download_url`
- `smr_download_workspace_archive`
- `smr_get_project_git`
- checkpoint and log-archive helpers

This package intentionally does not expose the old onboarding or starting-data
surface and does not expose Data Factory tool families.

## Project Knowledge Example

Set project-scoped curated knowledge:

```json
{
  "tool": "smr_set_project_knowledge",
  "arguments": {
    "project_id": "proj_123",
    "content": "Known benchmark constraints, prior failures, and durable findings for this project."
  }
}
```

Read project-scoped curated knowledge:

```json
{
  "tool": "smr_get_project_knowledge",
  "arguments": {
    "project_id": "proj_123"
  }
}
```

Use org-scoped knowledge when the durable context should apply across multiple
projects rather than one project notebook or one repo.

## Launch Sequence

Use this order for launch-time UX:

1. `smr_health_check`
2. `smr_create_project` or `smr_list_projects`
3. `smr_attach_source_repo` or `smr_upload_workspace_files`
4. optionally `smr_set_project_notes`
5. optionally `smr_set_project_knowledge`
6. `smr_get_project_readiness`
7. `smr_get_capacity_lane_preview`
8. `smr_get_run_start_blockers`
9. `smr_trigger_run`
10. `smr_get_run`
11. `smr_get_workspace_download_url`, `smr_download_workspace_archive`, or `smr_get_project_git`

`smr_get_limits` and `smr_get_project_entitlement` are useful hints, but trigger
and blockers remain authoritative for whether a run can launch right now.

Kickoff migration note:

- use `initial_runtime_messages` for opening intent on both blockers and trigger
- do not send the removed `prompt` field

## Nanoprogram-Style Walkthrough

The launch-day public demo uses this exact shape:

1. `smr_create_project`
2. `smr_attach_source_repo` with the repo you want to work on
3. optionally `smr_set_project_notes`
4. optionally `smr_set_project_knowledge`
5. `smr_get_project_readiness`
6. `smr_get_capacity_lane_preview`
7. `smr_get_run_start_blockers`
8. `smr_trigger_run`
9. `smr_get_run`
10. `smr_download_workspace_archive`
11. run the project-specific evaluator or verifier locally

Use the same payload for blockers and trigger, typically:

- `host_kind="daytona"`
- `work_mode="directed_effort"`
- `agent_kind="codex"`
- kickoff text in `initial_runtime_messages`

Valid `host_kind` values are `local`, `docker`, and `daytona`.
Valid `work_mode` values are `open_ended_discovery` and `directed_effort`.
Valid public `agent_kind` values are just `codex`.

`smr_get_run_progress` remains available on newer remigration surfaces, but the
launch-day walkthrough uses `smr_get_run` because it is supported across the
current backend deployments we rehearse against.

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
than structured `detail.error_code` payloads, so do not assume every failure
can be parsed with one schema.

## Workspace Retrieval

- workspace download URLs are short-lived presigned URLs
- the snapshot is project-level, not per-run
- `smr_download_workspace_archive` writes to the machine running the MCP server
- use `git pull` only when your deployment actually pushes back to the attached
  repo; otherwise fetch the workspace archive

For the launch walkthrough, archive retrieval is the default path because it
leads directly to local inspection and evaluation.
