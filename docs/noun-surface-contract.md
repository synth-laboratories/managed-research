# Noun Surface Contract

Managed Research exposes the same noun-first shape across backend HTTP, Python
SDK, MCP, and frontend.

## Setup

| Noun | Backend | SDK | MCP | Frontend |
| --- | --- | --- | --- | --- |
| github | `/smr/github/*` | `client.github.*` | `smr_setup_github_*` | `/integrations/github` |
| exports | `/smr/exports/targets*` | `client.exports.*` | `smr_setup_exports_*` | `/integrations/exports` |

## Work

| Noun | Backend | SDK | MCP | Frontend |
| --- | --- | --- | --- | --- |
| repos | `/smr/projects/{id}/repos*` | `client.project(id).repos.*` | `smr_work_repos_*` | `/smr/[projectId]/resources/repositories` |
| external repositories | `/smr/projects/{id}/external-repositories*` | `client.project(id).external_repositories.*` | `smr_*_project_external_repository` | `/smr/[projectId]/resources/repositories` |
| datasets | `/smr/projects/{id}/datasets*` | `client.project(id).datasets.*` | `smr_work_datasets_*` | `/smr/[projectId]/resources/datasets` |
| files | `/smr/projects/{id}/files*` | `client.project(id).files.*` | `smr_work_files_*` | `/smr/[projectId]/resources/files` |
| context | `/smr/projects/{id}/notes*`, `/smr/projects/{id}/knowledge`, `/smr/org/knowledge` | `client.project(id).context.*` | `smr_*_project_notes`, `smr_*_knowledge` | `/smr/[projectId]/resources/context` |
| credentials | `/smr/projects/{id}/credential-refs*` | `client.project(id).credentials.*` | `smr_*_project_credential_ref` | `/smr/[projectId]/resources/connections` |

## Results

| Noun | Backend | SDK | MCP | Frontend |
| --- | --- | --- | --- | --- |
| prs | `/smr/projects/{id}/prs*` | `client.project(id).prs.*` | `smr_results_prs_*` | `/smr/[projectId]/results/prs` |
| models | `/smr/projects/{id}/models*` | `client.project(id).models.*` | `smr_results_models_*` | `/smr/[projectId]/results/models` |
| outputs | `/smr/projects/{id}/outputs` | `client.project(id).outputs.list()` | `smr_results_outputs_list` | `/smr/[projectId]/results/outputs` |

## Status

| Noun | Backend | SDK | MCP | Frontend |
| --- | --- | --- | --- | --- |
| readiness | `/smr/projects/{id}/readiness` | `client.project(id).readiness()` | `smr_status_readiness` | `/smr/[projectId]/onboarding` |

## Rules

- Flat nouns own behavior. Legacy compatibility paths may delegate, but they do
  not define new behavior.
- Taxonomy belongs in navigation and namespaces, not in wire paths.
- If a noun gains a new verb, add it across backend, SDK, MCP, and frontend in
  the same change.

## Deprecated Compatibility Aliases

- `/smr/integrations/github/org/*` delegates to the flat `github` noun.
- `/smr/projects/{id}/resources/*` aggregates flat project nouns for setup UX
  and delegates mutations to the noun-owned routes.
- `/smr/files/{file_id}/content` remains a compatibility wrapper over the flat
  project-scoped file content read.

## Contract Checks

- Backend routes remain the shape authority.
- `backend/scripts/validate_smr_openapi.py` guards backend route, SDK, and MCP
  parity against `backend/smr_openapi.yaml`.
- Frontend generated types continue to read from `backend/smr_openapi.yaml`
  until a fuller cross-repo codegen pipeline lands.
