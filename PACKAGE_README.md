# synth-managed-research

Managed Research is Synth's product for applied AI teams that want repeatable,
inspectable research workflows against real repos. Wave 1 is strongest at
verification, eval execution, data assembly, and careful context optimization.
The package exposes the SMR Python SDK and MCP server as the public control
surface on top of the backend control plane.

Current status:

- SDK remigration is active in this repo
- MCP server modules live in `managed_research.mcp`
- standalone CLI migration is intentionally out of scope
- Data Factory and old onboarding or starting-data bootstrap APIs are
  intentionally out of scope

## Project Notes vs Curated Knowledge

- `project notes` are durable notebook text for operator memory and local
  project context
- `curated knowledge` is the PG-backed durable store for org- or
  project-scoped findings you want later work to inherit

These are intentionally separate surfaces.

Python import surface:

```python
from managed_research.sdk.client import SmrControlClient
```

Recommended launch flow:

- attach source repo or upload workspace files
- optionally set or append project notebook notes
- optionally set org or project curated knowledge
- check readiness
- preview lane with `get_capacity_lane_preview`
- inspect blockers with `get_run_start_blockers`
- trigger with `trigger_run`
- monitor progress
- retrieve the project workspace snapshot

Kickoff intent is queue-first:

- use `initial_runtime_messages` on blockers and trigger
- the legacy `prompt` field is no longer accepted
- migrate `prompt="..."` to
  `initial_runtime_messages=[{"body": "...", "mode": "queue"}]`

Project notebook, curated knowledge, and lifecycle helpers are separate:

- `get_project_notes`, `set_project_notes`, `append_project_notes`
- `get_org_knowledge`, `set_org_knowledge`, `get_project_knowledge`,
  `set_project_knowledge`
- `pause_project`, `resume_project`, `archive_project`, `unarchive_project`

For MCP callers, `smr_trigger_run` denials may come back as a successful tool
result with top-level `error`, `detail`, `message`, and `http_status`. Always
branch on `result.get("error")`.

The package is structured as a library-first distribution rather than a
standalone CLI product.

## MCP

Primary path:

```bash
codex mcp add managed-research --url https://api.usesynth.ai/mcp
claude mcp add --transport http managed-research https://api.usesynth.ai/mcp
```

Local stdio fallback:

```bash
uv tool install synth-managed-research
managed-research-mcp
```

The canonical MCP surface is owned by this package and is shared by the local
stdio server and the hosted backend transport.
