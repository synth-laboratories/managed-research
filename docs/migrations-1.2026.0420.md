# Migration Notes: `1.2026.0420`

## Breaking: `create_checkpoint()` is now blocking and typed

- `RunHandle.create_checkpoint(...)` now returns a typed [`Checkpoint`] object.
- `RunsAPI.create_checkpoint(...)` now returns a typed [`Checkpoint`] object.
- Calls block until the checkpoint reaches a terminal materialization state (`ready`, `failed`, or `pruned`) or timeout.
- New non-blocking escape hatch:
  - `RunHandle.request_checkpoint(...) -> dict`
  - `RunsAPI.request_checkpoint(...) -> dict`
  - `ManagedResearchClient.request_run_checkpoint(...) -> dict`

## New launch contract: native `roles`

- Launch/preflight surfaces now accept `roles=` as a first-class contract:
  - `SmrRoleBindings`
  - `RoleBinding`
  - `WorkerRolePalette`
- Mixed selection styles are rejected:
  - `roles` + `actor_model_overrides`
  - `roles` + shared top-level `agent_*` selectors
- `actor_model_overrides` remains available as compatibility input for one release window.
- Run readback now exposes typed `run.roles` when present.

## New checkpoint noun model

- Added typed checkpoint models:
  - `Checkpoint`
  - `CheckpointCadenceSource`
  - `CheckpointScope`
- `checkpoints()` list APIs now return `list[Checkpoint]`.
- Single-checkpoint fetch is available through:
  - `RunHandle.checkpoint(checkpoint_id)`
  - `RunsAPI.checkpoint(run_id, checkpoint_id, ...)`
  - `ManagedResearchClient.get_run_checkpoint(...)`
