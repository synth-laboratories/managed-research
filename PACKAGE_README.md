# synth-managed-research

Canonical public package for Synth Managed Research.

Current status:

- SDK remigration is active in this repo
- MCP server modules live in `managed_research.mcp`
- standalone CLI migration is intentionally out of scope
- Data Factory and old onboarding/start-data bootstrap APIs are intentionally out of scope

Python import surface:

```python
from managed_research.sdk.client import SmrControlClient
```

Recommended launch flow:

- attach source repo or upload workspace files
- optionally set or append project notebook notes
- check readiness
- preview lane with `get_capacity_lane_preview`
- inspect blockers with `get_run_start_blockers`
- trigger with `trigger_run`
- monitor progress
- retrieve the project workspace snapshot

Kickoff intent is queue-first:

- use `initial_runtime_messages` on blockers and trigger
- the legacy `prompt` field is no longer accepted
- migrate `prompt="..."` to `initial_runtime_messages=[{"body": "...", "mode": "queue"}]`

Project notebook and lifecycle helpers are separate:

- `get_project_notes`, `set_project_notes`, `append_project_notes`
- `pause_project`, `resume_project`, `archive_project`, `unarchive_project`

For MCP callers, `smr_trigger_run` denials may come back as a successful tool
result with top-level `error`, `detail`, `message`, and `http_status`. Always
branch on `result.get("error")`.

The package is being structured as a library-first distribution rather than a
standalone CLI product.
