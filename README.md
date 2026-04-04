# managed-research

Canonical public home for Synth Managed Research.

This repository now owns the maintained SMR Python SDK, MCP server modules, and
schema tooling. The package is library-first:

- no standalone CLI migration
- no Data Factory surface
- no old onboarding / starting-data bootstrap APIs

## Install

```bash
uv add synth-managed-research
```

## Python SDK

```python
from managed_research.sdk.client import SmrControlClient

client = SmrControlClient(api_key="sk_...")
project = client.create_project({"name": "SMR demo"})
client.upload_workspace_files(
    project["project_id"],
    [{"path": "README.md", "content": "# Demo\n", "content_type": "text/markdown"}],
)
readiness = client.get_project_readiness(project["project_id"])
```

## MCP

Run the stdio server directly:

```bash
python -m managed_research.mcp
```

The maintained MCP surface includes workspace bootstrap and progress tools such
as `smr_attach_source_repo`, `smr_upload_workspace_files`,
`smr_get_project_readiness`, and `smr_get_run_progress`.

## Repo Layout

- `managed_research/sdk`
- `managed_research/mcp`
- `managed_research/models`
- `managed_research/transport`
- `managed_research/_internal`
- `managed_research/schema_sync.py`

Legacy code from the previous public package remains quarantined under
[`/Users/joshpurtell/Documents/GitHub/managed-research/old`](/Users/joshpurtell/Documents/GitHub/managed-research/old).
