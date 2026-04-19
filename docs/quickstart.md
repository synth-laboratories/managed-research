# Quickstart

Managed Research is Synth's product for teams that want repeatable,
inspectable research workflows against real repos. Wave 1 is strongest at
verification, eval execution, data assembly, and careful context optimization.
The Python SDK and MCP server are the public control surfaces for launching and
inspecting that work.

## Project Notes vs Curated Knowledge

- `project notes` are durable notebook text for operator memory inside a
  project
- `curated knowledge` is the PG-backed durable store for org- or
  project-scoped findings you want future runs to inherit

These are intentionally separate surfaces.

Install the published package:

```bash
uv add managed-research
```

Use the Python SDK. The durable setup flow is readiness-driven:

1. Connect org-level setup nouns such as GitHub and exports.
2. Add project work nouns such as repos, datasets, and files.
3. Check `project.readiness()` until the project is unblocked.
4. Trigger runs, then inspect result nouns such as PRs, models, and outputs.

Use the Python SDK:

```python
from pathlib import Path

from managed_research import (
    LaunchPreflight,
    ProjectSetupAuthority,
    SmrActorModelAssignment,
    SmrActorType,
    SmrAgentProfileBindings,
    SmrControlClient,
    SmrEnvironmentKind,
    SmrHostKind,
    SmrProjectSetupStatus,
    SmrRunnableProjectRequest,
    SmrRuntimeKind,
    SmrWorkMode,
    SmrWorkerSubtype,
)

client = SmrControlClient(api_key="sk_...")
project = client.create_runnable_project(
    SmrRunnableProjectRequest(
        name="nanohorizon-quickstart",
        timezone="UTC",
        pool_id="daytona-default",
        runtime_kind=SmrRuntimeKind.SANDBOX_AGENT,
        environment_kind=SmrEnvironmentKind.HARBOR,
        agent_profiles=SmrAgentProfileBindings(
            orchestrator_profile_id="codex_gpt_5_4_medium",
            default_worker_profile_id="codex_gpt_5_4_medium",
        ),
        notes="Notebook only. Use runtime messages for kickoff intent.",
        scenario="nanohorizon-quickstart",
    )
)
project_id = project["project_id"]
project_client = client.project(project_id)
client.github.start_oauth()
project_client.repos.attach(github_repo="synth-laboratories/nanohorizon")
project_client.files.upload("constraints.md", name="constraints.md")
readiness = project_client.readiness()
if not readiness.get("ready"):
    raise RuntimeError(f"project not ready: {readiness}")
kickoff = [
    {
        "body": "Inspect the repo, improve the benchmark-facing workflow, and leave behind evidence that explains what changed.",
        "mode": "queue",
    }
]
setup_authority: ProjectSetupAuthority = client.progress.get_project_setup_authority(
    project_id
)
if setup_authority.state is not SmrProjectSetupStatus.READY:
    setup_authority = client.progress.prepare_project_setup_authority(project_id)
client.get_capacity_lane_preview(project_id)
preflight: LaunchPreflight = client.progress.get_launch_preflight(
    project_id,
    host_kind=SmrHostKind.DAYTONA,
    work_mode=SmrWorkMode.DIRECTED_EFFORT,
    agent_profile="codex_gpt_5_4_medium",
    initial_runtime_messages=kickoff,
)
if preflight.clear_to_trigger:
    client.trigger_run(
        project_id,
        host_kind=SmrHostKind.DAYTONA,
        work_mode=SmrWorkMode.DIRECTED_EFFORT,
        agent_profile="codex_gpt_5_4_medium",
        initial_runtime_messages=kickoff,
    )
    prs = project_client.prs.list()
    models = project_client.models.list()
    outputs = project_client.outputs.list()
    export_targets = client.exports.list_targets()
```

If you need org-wide durable context instead, use `set_org_knowledge(...)` and
`get_org_knowledge()`.

Supported public `agent_model` ids:

- `gpt-5.3-codex`
- `gpt-5.3-codex-spark`
- `gpt-5.4`
- `gpt-5.4-mini`
- `gpt-5.4-nano`
- `gpt-oss-120b`

Launch grouping:

- standard Codex models: `gpt-5.3-codex`, `gpt-5.3-codex-spark`, `gpt-5.4`, `gpt-5.4-mini`
- additional first-launch choices: `gpt-5.4-nano`, `gpt-oss-120b`

Shared top-level launch selection is intentionally narrower:

- top-level `agent_model` supports `gpt-5.4-mini`, `gpt-5.4`, `gpt-5.4-nano`, and `gpt-oss-120b`
- `gpt-5.3-codex` and `gpt-5.3-codex-spark` are `worker:engineer` only and must be assigned through actor-scoped config

When you need a raw model override in Python, use the enum surface:

```python
client.trigger_run(
    project_id,
    host_kind=SmrHostKind.DAYTONA,
    work_mode=SmrWorkMode.DIRECTED_EFFORT,
    agent_model=SmrAgentModel.GPT_5_4_NANO,
    initial_runtime_messages=kickoff,
)
```

Actor-scoped engineer selection:

```python
client.trigger_run(
    project_id,
    host_kind=SmrHostKind.DAYTONA,
    work_mode=SmrWorkMode.DIRECTED_EFFORT,
    actor_model_overrides=[
        SmrActorModelAssignment(
            actor_type=SmrActorType.WORKER,
            actor_subtype=SmrWorkerSubtype.ENGINEER,
            agent_model=SmrAgentModel.GPT_5_3_CODEX,
        )
    ],
    initial_runtime_messages=kickoff,
)
```

After extracting the archive, validate the submission with the project-specific
harness you are targeting.

Kickoff migration note:

- use `initial_runtime_messages` for opening intent
- do not send the removed `prompt` field
- project notebook text is managed separately through `set_project_notes` /
  `append_project_notes`
- curated knowledge is managed through `set_org_knowledge`,
  `get_org_knowledge`, `set_project_knowledge`, and `get_project_knowledge`
- project context can also include uploaded files/directories, datasets,
  linked GitHub repos, external context repos, and credential refs

Use the hosted MCP endpoint:

```bash
codex mcp add managed-research --url https://api.usesynth.ai/mcp
claude mcp add --transport http managed-research https://api.usesynth.ai/mcp
```

Local stdio fallback:

```bash
uv tool install managed-research
managed-research-mcp
```

For MCP clients, the equivalent flow is readiness-first as well:

1. `smr_health_check`
2. `smr_create_runnable_project` or `smr_list_projects`
3. `smr_setup_github_start_oauth`
4. `smr_work_repos_attach` or `smr_work_files_upload`
5. optionally `smr_work_datasets_upload`, `smr_create_project_external_repository`,
   or `smr_create_project_credential_ref`
6. optionally `smr_set_project_notes`
7. optionally `smr_set_project_knowledge`
8. `smr_prepare_project_setup`
9. `smr_get_capacity_lane_preview`
10. `smr_get_launch_preflight`
11. `smr_trigger_run`
12. `smr_results_prs_list`, `smr_results_models_list`, and `smr_results_outputs_list`
13. `smr_get_workspace_download_url`, `smr_download_workspace_archive`, or `smr_get_project_git`
