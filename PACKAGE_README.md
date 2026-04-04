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

The package is being structured as a library-first distribution rather than a
standalone CLI product.
