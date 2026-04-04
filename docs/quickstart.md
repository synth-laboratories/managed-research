# Quickstart

Install the published package:

```bash
uv add synth-managed-research
```

Use the Python SDK:

```python
from managed_research.sdk.client import SmrControlClient

client = SmrControlClient(api_key="sk_...")
project = client.create_project({"name": "quickstart"})
client.upload_workspace_files(
    project["project_id"],
    [{"path": "README.md", "content": "# Quickstart\n", "content_type": "text/markdown"}],
)
client.get_project_readiness(project["project_id"])
```

Run the MCP server over stdio:

```bash
python -m managed_research.mcp
```
