# Noun Surface Contract

Managed Research exposes the same noun-first shape across backend HTTP, Python
SDK, MCP, and frontend.

Stable wire identifiers still use `/smr`, `smr_*` MCP tool names, and `Smr*`
Python compatibility types. Public prose should say Managed Research.

## Global

| Noun | Backend | SDK | MCP | Frontend |
| --- | --- | --- | --- | --- |
| projects | `/smr/projects*`, `/smr/projects:runnable` | `client.projects.*`, `client.project(id)` | `smr_list_projects`, `smr_get_project`, `smr_create_runnable_project` | `/smr` |
| runs | `/smr/runs*`, `/smr/jobs`, `/smr/runs:one-off*` | `client.runs.*` | `smr_start_one_off_run`, `smr_get_run`, `smr_stop_run` | `/smr/jobs` |
| usage | `/smr/limits`, `/smr/runs/{id}/usage`, `/smr/projects/{id}/usage`, `/smr/projects/{id}/economics` | `client.usage.*`, `client.projects.get_usage(...)` | `smr_get_limits`, `smr_get_run_usage`, `smr_get_project_usage`, `smr_get_project_economics` | billing/usage surfaces |

## Setup

| Noun | Backend | SDK | MCP | Frontend |
| --- | --- | --- | --- | --- |
| github | `/smr/github/*` | `client.github.*` | `smr_setup_github_*` | `/integrations/github` |
| exports | `/smr/exports/targets*` | `client.exports.*` | `smr_setup_exports_*` | `/integrations/exports` |
| setup | `/smr/projects/{id}/setup*` | `client.project(id).setup.*`, `client.setup.*` | `smr_get_project_setup`, `smr_prepare_project_setup` | `/smr/[projectId]/onboarding` |
| launch preflight | `/smr/projects/{id}/launch-preflight`, `/smr/runs:one-off/launch-preflight` | `client.project(id).runs.preflight(...)`, `client.projects.get_launch_preflight(...)` | `smr_get_launch_preflight` | launch CTA/onboarding |

## Work

| Noun | Backend | SDK | MCP | Frontend |
| --- | --- | --- | --- | --- |
| repos | `/smr/projects/{id}/repos*` | `client.project(id).repos.*` | `smr_work_repos_*` | `/smr/[projectId]/resources/repositories` |
| external repositories | `/smr/projects/{id}/external-repositories*` | `client.project(id).external_repositories.*` | `smr_*_project_external_repository` | `/smr/[projectId]/resources/repositories` |
| datasets | `/smr/projects/{id}/datasets*` | `client.project(id).datasets.*` | `smr_work_datasets_*` | `/smr/[projectId]/resources/datasets` |
| files | `/smr/projects/{id}/files*` | `client.project(id).files.*` | `smr_work_files_*` | `/smr/[projectId]/resources/files` |
| context | `/smr/projects/{id}/notes*`, `/smr/projects/{id}/knowledge`, `/smr/org/knowledge` | `client.project(id).context.*` | `smr_*_project_notes`, `smr_*_knowledge` | `/smr/[projectId]/resources/context` |
| credentials | `/smr/projects/{id}/credential-refs*` | `client.project(id).credentials.*` | `smr_*_project_credential_ref` | `/smr/[projectId]/resources/connections` |
| workspace inputs | `/smr/projects/{id}/workspace-inputs*` | `client.workspace_inputs.*` | `smr_get_workspace_inputs`, `smr_upload_workspace_files` | `/smr/[projectId]/resources` |
| git | `/smr/projects/{id}/git*` | `client.projects.get_git(...)` | repo/git work tools | project workspace UI |

## Results

| Noun | Backend | SDK | MCP | Frontend |
| --- | --- | --- | --- | --- |
| prs | `/smr/projects/{id}/prs*` | `client.project(id).prs.*` | `smr_results_prs_*` | `/smr/[projectId]/results/prs` |
| models | `/smr/projects/{id}/models*` | `client.project(id).models.*` | `smr_results_models_*` | `/smr/[projectId]/results/models` |
| outputs | `/smr/projects/{id}/outputs` | `client.project(id).outputs.list()` | `smr_results_outputs_list` | `/smr/[projectId]/results/outputs` |
| artifacts | `/smr/runs/{id}/artifacts*`, `/smr/artifacts/{id}*` | `client.runs.download(...)`, `client.files.*` lower-level artifact helpers | `smr_list_run_artifacts`, `smr_get_artifact*` | run artifact/results views |
| trained models | `/smr/trained_models*`, `/smr/runs/{id}/trained_models` | `client.trained_models.*` | `smr_register_trained_model`, `smr_get_trained_model`, `smr_list_trained_models_for_run` | internal/results tooling |

## Status

| Noun | Backend | SDK | MCP | Frontend |
| --- | --- | --- | --- | --- |
| readiness | `/smr/projects/{id}/readiness` | `client.project(id).readiness()` | `smr_status_readiness` | `/smr/[projectId]/onboarding` |
| runtime messages | `/smr/runs/{id}/runtime/messages`, `/smr/projects/{id}/runs/{id}/runtime/messages` | `client.runs.list_runtime_messages(...)`, `run.messages()` | `smr_runtime_message_queue`, runtime read tools | run console |
| runtime intents | `/smr/runs/{id}/runtime/intents*`, `/smr/projects/{id}/runs/{id}/runtime/intents*` | `run.submit_intent(...)`, `run.intents(...)` | `smr_runtime_intents` | run steering |
| questions | `/smr/runs/{id}/questions*`, `/smr/projects/{id}/runs/{id}/questions*` | `client.runs.list_questions(...)`, `client.runs.respond_to_question(...)` | `smr_list_run_questions`, `smr_respond_to_run_question` | run console |
| approvals | `/smr/runs/{id}/approvals*`, `/smr/projects/{id}/runs/{id}/approvals*` | `client.approvals.*`, `client.runs.approve_run_approval(...)` | `smr_list_run_approvals`, `smr_approve_run_approval`, `smr_deny_run_approval` | run console |
| checkpoints/branches | `/smr/runs/{id}/checkpoints*`, `/smr/runs/{id}/branches`, `/smr/checkpoints/branches` | `run.checkpoints()`, `run.branch_from_checkpoint(...)`, `client.runs.branch_from_checkpoint(...)` | `smr_branch_run_from_checkpoint` | run console |
| timeline/traces/actor usage | `/smr/projects/{project_id}/runs/{run_id}/timeline`, `/smr/projects/{project_id}/runs/{run_id}/traces`, `/smr/projects/{project_id}/runs/{run_id}/actors/usage` | `run.timeline()`, `run.traces()`, `run.actor_usage()` | `smr_get_run_logical_timeline`, `smr_get_run_traces`, `smr_get_run_actor_usage` | operator/debug views |
| data infra | `/smr/projects/{project_id}/runs/{run_id}/files`, `/smr/projects/{project_id}/runs/{run_id}/git`, `/smr/projects/{project_id}/runs/{run_id}/task-graph`, `/smr/projects/{project_id}/runs/{run_id}/data-infra` | lower-level client reads, future bound run namespace | MCP data-infra/resource tools | run console |

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
- `SmrControlClient` remains a temporary Python compatibility alias for
  `ManagedResearchClient`.

## Contract Checks

- Backend routes remain the shape authority.
- `backend/scripts/validate_smr_openapi.py` guards backend route, SDK, and MCP
  parity against `backend/smr_openapi.yaml`.
- Frontend generated types continue to read from `backend/smr_openapi.yaml`
  until a fuller cross-repo codegen pipeline lands.
