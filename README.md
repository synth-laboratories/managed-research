# managed-research

Pure-Python public SMR surfaces for Managed Research.

Current scope:

- SMR API client
- SMR MCP stdio server
- generated-schema sync path for public SMR contracts

Out of scope for this slice:

- runtime internals
- sandbox/session control
- private backend models

## Install

```bash
pip install -U managed-research
```

For local development:

```bash
uv sync --extra dev
```

## Run the MCP server

```bash
uv run managed-research-mcp
```

The package reads `SYNTH_API_KEY` and `SYNTH_BACKEND_URL` from the environment.

Python API surface:

```python
from managed_research import ManagedResearchClient

client = ManagedResearchClient(api_key="sk_...")
projects = client.list_projects()
```

## Sync exported public schemas

```bash
uv run python scripts/sync_public_schemas.py --source /path/to/exported/schemas
```

If you prefer environment configuration, set `MANAGED_RESEARCH_SCHEMA_SOURCE`
instead of passing `--source`.

There is also a console entrypoint:

```bash
uv run managed-research-sync-schemas --source /path/to/exported/schemas
```
