# MCP Guide

Run the managed-research stdio MCP server directly from the package:

```bash
python -m managed_research.mcp
```

The maintained remigration surface includes:

- `smr_attach_source_repo`
- `smr_get_workspace_inputs`
- `smr_upload_workspace_files`
- `smr_get_project_readiness`
- `smr_get_run_progress`
- `smr_get_capabilities`
- `smr_get_project_entitlement`
- checkpoint and log-archive helpers

This package intentionally does not expose the old onboarding/starting-data or
Data Factory tool families.
