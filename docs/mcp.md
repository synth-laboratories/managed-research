# MCP Guide

Managed Research is Synth's product for teams that want repeatable,
inspectable research workflows against real repos. Wave 1 is strongest at
verification, eval execution, data assembly, and careful context optimization.
The MCP server is the public tool surface for launching, inspecting, and
capturing durable context around those workflows.

Hosted first:

```bash
codex mcp add managed-research --url https://api.usesynth.ai/mcp
claude mcp add --transport http managed-research https://api.usesynth.ai/mcp
```

Local stdio fallback:

```bash
uv tool install managed-research
managed-research-mcp
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

- `smr_create_runnable_project`
- `smr_attach_source_repo`
- `smr_rename_project`
- `smr_patch_project`
- `smr_get_project_notes`
- `smr_set_project_notes`
- `smr_append_project_notes`
- `smr_get_org_knowledge`
- `smr_set_org_knowledge`
- `smr_get_project_knowledge`
- `smr_set_project_knowledge`
- `smr_curated_knowledge`
- `smr_pause_project`
- `smr_resume_project`
- `smr_archive_project`
- `smr_unarchive_project`
- `smr_get_workspace_inputs`
- `smr_upload_workspace_files`
- `smr_list_project_files`
- `smr_create_project_files`
- `smr_list_run_file_mounts`
- `smr_upload_run_files`
- `smr_list_run_output_files`
- `smr_list_project_external_repositories`
- `smr_create_project_external_repository`
- `smr_list_run_repository_mounts`
- `smr_list_project_credential_refs`
- `smr_create_project_credential_ref`
- `smr_list_run_credential_bindings`
- `smr_get_project_setup`
- `smr_prepare_project_setup`
- `smr_get_capacity_lane_preview`
- `smr_get_launch_preflight`
- `smr_trigger_run`
- `smr_stop_run`
- `smr_runtime_message_queue`
- `smr_get_run`
- `smr_get_run_logical_timeline`
- `smr_get_run_traces`
- `smr_get_run_actor_usage`
- `smr_get_run_primary_parent`
- `smr_open_ended_questions`
- `smr_directed_effort_outcomes`
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

Rename a project when the generated name is not operator-friendly:

```json
{
  "tool": "smr_rename_project",
  "arguments": {
    "project_id": "proj_123",
    "name": "Retry transient eval failures"
  }
}
```

Use `smr_patch_project` for broader configuration updates; use
`smr_rename_project` for name-only changes.

Recommended operator-read flow for an active run:

1. `smr_get_run_logical_timeline` for chronology
2. `smr_get_run_actor_usage` for truthful per-actor spend/model activity
3. `smr_get_run_traces` for downloadable execution traces

When worker code uses the backend-staged provider wrappers for OpenRouter,
Tinker, or Modal, that usage is still read back through the same canonical
usage surfaces. Do not look for wrapper-private usage APIs.

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
2. `smr_create_runnable_project` or `smr_list_projects`
3. `smr_attach_source_repo` or `smr_upload_workspace_files`
4. optionally `smr_set_project_notes`
5. optionally `smr_set_project_knowledge`
6. `smr_prepare_project_setup`
7. `smr_get_capacity_lane_preview`
8. `smr_get_launch_preflight`
9. `smr_trigger_run`
10. `smr_get_run` plus noun reads such as `smr_list_run_questions`,
    `smr_open_ended_questions`, `smr_directed_effort_outcomes`, and milestone or experiment reads
11. `smr_get_workspace_download_url`, `smr_download_workspace_archive`, or `smr_get_project_git`

`smr_get_limits` and `smr_get_project_entitlement` are useful hints, but setup
authority and launch preflight remain authoritative for whether a run can
launch right now.

Kickoff migration note:

- use `initial_runtime_messages` for opening intent on both launch preflight and trigger
- do not send the removed `prompt` field
- staged runs may set `kickoff_contract` so the run stores one authoritative
  staged kickoff package and the backend derives the opening orchestrator
  kickoff message from that contract
- staged and non-staged runs may set `resource_bindings` to choose external
  repos and credential refs for the run, plus optional inline external repos
- parent-bound runs may set:
  - `primary_parent_ref` for an existing project-scoped OEQ/DEO
  - `primary_parent` for inline run-scoped parent creation at trigger time

Phase 3 resource note:

- every project still has one automatic internal Synth-managed writable repo
- external repos are optional context resources, not the canonical workspace
- `smr_list_run_output_files` is the early-output surface; workspace archive
  download remains a convenience export rather than the only way to retrieve
  results

## Nanoprogram-Style Walkthrough

The launch-day public demo uses this exact shape:

1. `smr_create_runnable_project`
2. `smr_attach_source_repo` with the repo you want to work on
3. optionally `smr_set_project_notes`
4. optionally `smr_set_project_knowledge`
5. `smr_prepare_project_setup`
6. `smr_get_capacity_lane_preview`
7. `smr_get_launch_preflight`
8. `smr_trigger_run`
9. `smr_get_run` plus noun reads such as OEQs, DEOs, milestones, experiments, or pending questions
10. `smr_download_workspace_archive`
11. run the project-specific evaluator or verifier locally

Use the same payload for launch preflight and trigger, typically:

- `host_kind="daytona"`
- `work_mode="directed_effort"`
- `agent_kind="codex"`
- kickoff text in `initial_runtime_messages`
- or, for staged flows, a canonical `kickoff_contract`
- optionally `primary_parent_ref` when the run should advance a predeclared DEO/OEQ

Valid `host_kind` values are `local`, `docker`, and `daytona`.
Valid `work_mode` values are `open_ended_discovery` and `directed_effort`.
Valid public `agent_kind` values are just `codex`.

For inspection, prefer `smr_get_run` plus noun reads such as
`smr_list_run_questions`, `smr_get_run_primary_parent`,
`smr_open_ended_questions`, and `smr_directed_effort_outcomes`.

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
