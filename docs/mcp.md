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
- `smr_get_project_setup`
- `smr_prepare_project_setup`
- `smr_get_launch_preflight`
- `smr_trigger_run`
- `smr_get_run`
- `smr_stop_run`

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
