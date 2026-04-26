# Python SDK Guide

`ManagedResearchClient` is the canonical Python entrypoint:

```python
from managed_research import ManagedResearchClient, ProjectSelector

client = ManagedResearchClient(api_key="sk_...")
```

`SmrControlClient` is still importable as a compatibility alias, but the
documentation now treats it as legacy.

## Noun-First Navigation

```python
project = client.projects.default()

project.repositories.attach(github_repo="owner/repo")
project.files.list()
project.outputs.list()

readiness = project.readiness()
setup = project.setup.get()
preflight = project.runs.preflight(
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)
run = project.runs.start(
    "Inspect the repo, improve the target workflow, and leave behind evidence.",
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)
```

## Misc Default Project Flow

```python
run = client.runs.start(
    "Triage the repo and propose the smallest safe fix.",
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
)
```

This route resolves the caller's default miscellaneous project automatically.
Pass `project_id=` or `project=ProjectSelector.from_project_id(...)` to route a
run to a specific existing project instead.

## Launch Controls

Shared launch fields:

- `host_kind`
- `work_mode`
- `providers`
- `agent_profile`
- `agent_harness`
- `agent_model`
- `agent_model_params`
- `initial_runtime_messages`

Canonical harness values:

- `codex`
- `opencode_sdk`

Canonical OpenCode launch models:

- `anthropic/claude-sonnet-4-6`
- `anthropic/claude-haiku-4-5-20251001`
- `x-ai/grok-4.1-fast`

Example:

```python
run = client.runs.start(
    "Do a careful bug-hunt and explain the fix.",
    host_kind="daytona",
    work_mode="directed_effort",
    providers=[{"provider": "openrouter"}],
    agent_harness="opencode_sdk",
    agent_model="anthropic/claude-sonnet-4-6",
)
```

Role-based launch policy is now first-class:

- `roles=SmrRoleBindings(...)`
- `RoleBinding(model=..., params=..., agent_harness=...)`
- `WorkerRolePalette(permitted_models=[...], default_model=..., subtypes={...})`

`roles` cannot be combined with `actor_model_overrides` or shared top-level `agent_*` selectors.
`actor_model_overrides` remains as compatibility plumbing for one release window.

## Checkpoints

- `run.create_checkpoint(...) -> Checkpoint` is now blocking/typed.
- `run.request_checkpoint(...) -> dict` is the non-blocking control-ack escape hatch.
- `run.checkpoints() -> list[Checkpoint]`.
- `run.checkpoint(checkpoint_id) -> Checkpoint`.

## Typed Errors

The SDK raises typed exceptions instead of relying on success-shaped payloads.
For launch-time denials, inspect the exception message and any structured
`detail` on the error instance.
