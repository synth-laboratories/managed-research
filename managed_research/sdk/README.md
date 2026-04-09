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
  - `ProjectReadiness`
  - `RunProgress`
- [`workspace_inputs.py`](/Users/joshpurtell/Documents/GitHub/managed-research/managed_research/sdk/workspace_inputs.py)
  - `WorkspaceInputsState`
  - `WorkspaceUploadResult`
- [`runs.py`](/Users/joshpurtell/Documents/GitHub/managed-research/managed_research/sdk/runs.py)
  - `RunProgress` for `get_progress(...)`

Raw dict/list compatibility still exists on `SmrControlClient` where MCP and lower-level callers depend on wire-shaped payloads.
