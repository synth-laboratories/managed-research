Generated public schema artifacts live here.

Expected source:

- backend export artifact produced outside this repo

Sync command:

```bash
uv run python scripts/sync_public_schemas.py --source /path/to/exported/schemas
```

The current checkout does not include the backend export source of truth, so this
directory may be empty until that artifact is published.
