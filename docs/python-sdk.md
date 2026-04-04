# Python SDK Guide

The maintained SMR SDK ships in this package under the `managed_research`
import namespace.

Install:

```bash
uv add synth-managed-research
```

Import:

```python
from managed_research.sdk.client import SmrControlClient
```

High-leverage public flows:

- `attach_source_repo(project_id, url, default_branch=None)`
- `get_workspace_inputs(project_id)`
- `upload_workspace_files(project_id, files)`
- `upload_workspace_directory(project_id, directory)`
- `get_project_readiness(project_id)`
- `get_run_progress(project_id, run_id)`
