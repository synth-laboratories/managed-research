# SDK

This subtree owns the Python control-plane client and the typed namespace wrappers built on top of it.

Ownership:
- `client.py` owns transport-facing request building and raw backend interaction
- namespace modules such as `progress.py`, `runs.py`, and `workspace_inputs.py` own higher-level typed return surfaces

Guidelines:
- parse and validate request inputs before dispatch
- keep request models typed until the final JSON serialization edge
- avoid heuristic payload-shape probing
- when a backend route has a stable response concept, return a typed model from the namespace API when practical

Current typed namespace returns:
- [`progress.py`](/Users/joshpurtell/Documents/GitHub/managed-research/managed_research/sdk/progress.py)
  - `ProjectSetupAuthority` via `get_project_setup_authority(...)`
  - `LaunchPreflight` via `get_launch_preflight(...)`
- [`runs.py`](/Users/joshpurtell/Documents/GitHub/managed-research/managed_research/sdk/runs.py)
  - `SmrLogicalTimeline` via `get_logical_timeline(project_id, run_id)`
  - `SmrRunBranchResponse` via `branch_from_checkpoint(...)`
- [`workspace_inputs.py`](/Users/joshpurtell/Documents/GitHub/managed-research/managed_research/sdk/workspace_inputs.py)
  - `WorkspaceInputsState`
  - `WorkspaceUploadResult`

Noun-first inspection belongs on the run/project namespaces and direct client
reads such as `get_run(...)`, `list_run_questions(...)`,
`get_run_primary_parent(...)`, and the OEQ/DEO/milestone/experiment list reads.

Raw dict/list compatibility still exists on `SmrControlClient` where MCP and lower-level callers depend on wire-shaped payloads.

Noun-first namespaces now mirror the customer surface:

- org-scoped setup: `client.github`, `client.credentials`, `client.exports`
- project-scoped work/results/status: `client.project(id).repos`, `.datasets`,
  `.files`, `.prs`, `.models`, `.outputs`, and `.readiness()`

Contract posture:

- backend route and schema shape stay authoritative through
  `/Users/joshpurtell/Documents/GitHub/backend/smr_openapi.yaml`
- backend-to-SDK drift is checked with
  `/Users/joshpurtell/Documents/GitHub/backend/scripts/validate_smr_openapi.py`
- legacy names may remain as wrappers, but new noun behavior belongs only on
  the flat namespaces above

Examples:

```python
timeline = client.runs.get_logical_timeline("proj_123", "run_123")

exact_branch = client.runs.branch_from_checkpoint(
    "run_123",
    project_id="proj_123",
    checkpoint_id="ckpt_123",
)

seeded_branch = client.runs.branch_from_checkpoint(
    "run_123",
    project_id="proj_123",
    checkpoint_id="ckpt_123",
    mode="with_message",
    message="Retry this from the checkpoint, but explain the regression first.",
)
```
