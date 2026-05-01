# MCP Guide

Managed Research exposes a first-class MCP surface alongside the Python SDK.

## Connect

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

## Core Tools

- `smr_get_default_project`
- `smr_start_one_off_run`
- `smr_list_projects`
- `smr_get_project`
- `smr_get_project_workspace`
- `smr_get_project_setup`
- `smr_prepare_project_setup`
- `smr_get_launch_preflight`
- `smr_trigger_run`
- `smr_get_run`
- `smr_get_run_event_log`
- `smr_get_run_authority_readouts`
- `smr_get_run_operator_evidence`
- `smr_control_project_run_actor`
- `smr_stop_run`

`smr_get_project_workspace` returns the backend-owned project workspace
projection: mission/readiness, objectives, runs, actors, operator-facing
events, experiments, curated knowledge, context-pack preview, accepted
canon-change readouts, recommended next actions, review queue, reports, and
launch risks. Runs propose material; review or policy promotion owns durable
project truth.

ChangeSet review tools:

- `smr_list_project_changesets`
- `smr_create_project_changeset`
- `smr_get_project_changeset`
- `smr_decide_project_changeset`

These tools stage proposed project mutations and record review decisions; they
do not give MCP callers direct canon-write authority. Accepted/promoted decisions
apply only backend-supported canon targets such as project knowledge, reviewed
objectives, and experiments. Decision responses include `applied_at` and
`applied_items` when a promotion changed canon state.

`smr_control_project_run_actor` pauses, resumes, or requests interruption for
one actor inside a project-scoped run. It is an operator control surface: it
records a control receipt and audit metadata, but it does not promote project
truth.

## Minimal Launch

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
        "body": "Inspect the repo, improve the target workflow, and explain the changes."
      }
    ]
  }
}
```

## OpenCode Harness

```json
{
  "tool": "smr_start_one_off_run",
  "arguments": {
    "host_kind": "daytona",
    "work_mode": "directed_effort",
    "providers": [{"provider": "openrouter"}],
    "agent_harness": "opencode_sdk",
    "agent_model": "anthropic/claude-sonnet-4-6",
    "initial_runtime_messages": [
      {
        "mode": "queue",
        "body": "Review the repo and propose the smallest safe improvement."
      }
    ]
  }
}
```

Supported OpenCode models:

- `anthropic/claude-sonnet-4-6`
- `anthropic/claude-haiku-4-5-20251001`
- `x-ai/grok-4.1-fast`

## Denials

Launch denials are returned as MCP tool errors, not success payloads with an
embedded `error` field. Agent frameworks should treat these as failed tool
calls and can inspect the structured error `data` for details.
