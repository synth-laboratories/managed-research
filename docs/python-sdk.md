# Python SDK Guide

Managed Research is Synth's product for teams that want repeatable,
inspectable research workflows against real repos. Wave 1 is strongest at
verification, eval execution, data assembly, and careful context optimization.
The Python SDK is the public programmatic control surface for creating projects,
storing durable context, and launching runs against that backend control plane.

Install:

```bash
uv add managed-research
```

Import:

```python
from managed_research import (
    SmrActorModelAssignment,
    SmrActorType,
    SmrAgentModel,
    SmrAgentProfileBindings,
    SmrControlClient,
    SmrEnvironmentKind,
    SmrHostKind,
    SmrRunnableProjectRequest,
    SmrRuntimeKind,
    SmrWorkMode,
    SmrWorkerSubtype,
)
```

## Project Notes vs Curated Knowledge

- `project notes` are durable notebook text for operator memory and local
  project context
- `curated knowledge` is the PG-backed durable store for org- or
  project-scoped findings you want future work to build from

These are intentionally separate surfaces.

High-leverage public flows:

- `create_runnable_project(SmrRunnableProjectRequest(...))`
- `rename_project(project_id, name)` / `client.projects.rename(project_id, name)`
- `attach_source_repo(project_id, url, default_branch=None)`
- `get_workspace_inputs(project_id)`
- `upload_workspace_files(project_id, files)`
- `upload_workspace_directory(project_id, directory)`
- `set_project_notes(project_id, notes)` / `append_project_notes(project_id, notes)`
- `set_org_knowledge(content)` / `get_org_knowledge()`
- `set_project_knowledge(project_id, content)` /
  `get_project_knowledge(project_id)`
- `pause_project(project_id)` / `resume_project(project_id)`
- `archive_project(project_id)` / `unarchive_project(project_id)`
- `setup.get(project_id)` / `setup.prepare(project_id)`
- `get_capacity_lane_preview(project_id)`
- `get_launch_preflight(project_id, host_kind=..., work_mode=SmrWorkMode...)`
- `trigger_run(project_id, host_kind=..., work_mode=SmrWorkMode...)`
- `get_run(run_id, project_id=...)`
- `client.runs.get_traces(run_id, project_id=...)`
- `client.runs.get_actor_usage(run_id, project_id=...)`
- `client.projects.create_open_ended_question(...)` / `list_open_ended_questions(...)`
- `client.projects.create_directed_effort_outcome(...)` / `list_directed_effort_outcomes(...)`
- `client.runs.get_primary_parent(run_id)` / `list_primary_parent_milestones(run_id)`
- `client.files.list_project(...)` / `create_project(...)` / `list_outputs(...)`
- `client.repositories.list_project(...)` / `create_project(...)`
- `client.credentials.list_project(...)` / `create_project(...)`
- `get_workspace_download_url(project_id)`
- `download_workspace_archive(project_id, output_path)`
- `get_project_git(project_id)`

For staged SMR flows, `get_launch_preflight(...)` and `trigger_run(...)` also
accept `kickoff_contract=...`. That staged kickoff contract becomes the
authoritative run-owned contract, and the backend derives the opening
orchestrator kickoff message from it.

Namespace helpers under `client.projects` mirror the project-scoped methods,
including `client.projects.get_notes(...)`, `client.projects.set_notes(...)`,
`client.projects.get_knowledge(...)`, and `client.projects.set_knowledge(...)`.

Rename a generated project name without changing runs, repos, tasks, or artifacts:

```python
client.projects.rename(project_id, "Retry transient eval failures")
```

Read operator-facing run chronology, traces, and actor usage:

```python
timeline = client.runs.get_logical_timeline(project_id, run_id)
traces = client.runs.get_traces(run_id, project_id=project_id)
actor_usage = client.runs.get_actor_usage(run_id, project_id=project_id)
```

Wrapper-driven provider usage for OpenRouter, Tinker, and Modal still lands on
those same canonical read surfaces. Use:

- logical timeline for chronology
- run usage for totals
- actor usage for truthful per-actor provider/model attribution
- traces and execution record for evidence

## Phase 3 Resources

Phase 3 adds first-class file, repository, and credential surfaces without
changing the internal Synth-managed project repo invariant.

- `client.files` manages durable uploaded files, run file mounts, and early
  run output retrieval
- `client.repositories` manages optional external repositories; these are
  additive context repos and do not replace the internal project repo
- `client.credentials` manages project-scoped credential refs and run bindings

Trigger-time runs may now also carry `resource_bindings=...` to choose which
project repos and credential refs a run should use, plus one-off inline
external repos for that run.

## Recommended Sequence

```python
from pathlib import Path

from managed_research import (
    SmrAgentProfileBindings,
    SmrControlClient,
    SmrEnvironmentKind,
    SmrHostKind,
    SmrRunnableProjectRequest,
    SmrRuntimeKind,
    SmrWorkMode,
)

client = SmrControlClient(api_key="sk_...")
project = client.create_runnable_project(
    SmrRunnableProjectRequest(
        name="nanohorizon-sdk-demo",
        timezone="UTC",
        pool_id="daytona-default",
        runtime_kind=SmrRuntimeKind.SANDBOX_AGENT,
        environment_kind=SmrEnvironmentKind.HARBOR,
        agent_profiles=SmrAgentProfileBindings(
            orchestrator_profile_id="codex_gpt_5_4_medium",
            default_worker_profile_id="codex_gpt_5_4_medium",
        ),
        notes="Notebook only. Kickoff intent belongs in runtime messages.",
        scenario="nanohorizon-sdk-demo",
    )
)
project_id = project["project_id"]
client.attach_source_repo(
    project_id,
    "https://github.com/synth-laboratories/nanohorizon.git",
    default_branch="main",
)
client.set_project_knowledge(
    project_id,
    "Known benchmark constraints, prior failures, and durable findings for this project.",
)
client.get_project_knowledge(project_id)
kickoff = [
    {
        "body": "Inspect the repo, improve the benchmark-facing workflow, and leave behind evidence that explains what changed.",
        "mode": "queue",
    }
]
client.setup.prepare(project_id)
client.get_capacity_lane_preview(project_id)
preflight = client.get_launch_preflight(
    project_id,
    host_kind=SmrHostKind.DAYTONA,
    work_mode=SmrWorkMode.DIRECTED_EFFORT,
    agent_profile="codex_gpt_5_4_medium",
    initial_runtime_messages=kickoff,
)

if preflight["clear_to_trigger"]:
    client.trigger_run(
        project_id,
        host_kind=SmrHostKind.DAYTONA,
        work_mode=SmrWorkMode.DIRECTED_EFFORT,
        agent_profile="codex_gpt_5_4_medium",
        initial_runtime_messages=kickoff,
    )
    client.download_workspace_archive(project_id, Path("nanohorizon-workspace.tar.gz"))
```

Notes:

- prefer `create_runnable_project(...)` for new SDK integrations and eval launchers
- prefer `agent_profile` when you want an exact backend-managed preset
- public `agent_model` ids are `gpt-5.3-codex`, `gpt-5.3-codex-spark`,
  `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano`, and `gpt-oss-120b`
- standard Codex models are `gpt-5.3-codex`, `gpt-5.3-codex-spark`,
  `gpt-5.4`, and `gpt-5.4-mini`
- additional first-launch choices are `gpt-5.4-nano` and `gpt-oss-120b`
- shared top-level `agent_model` selection is limited to `gpt-5.4-mini`,
  `gpt-5.4`, `gpt-5.4-nano`, and `gpt-oss-120b`
- `gpt-5.3-codex` and `gpt-5.3-codex-spark` are `worker:engineer` only and
  must be selected through actor-scoped config
- Python callers should pass `agent_model` as `SmrAgentModel`, for example
  `SmrAgentModel.GPT_OSS_120B` or `SmrAgentModel.GPT_5_4_NANO`
- Python callers should pass `host_kind` as `SmrHostKind`, for example
  `SmrHostKind.DAYTONA`, `SmrHostKind.LOCAL`, or `SmrHostKind.DOCKER`
- Python callers should pass `work_mode` as `SmrWorkMode`, for example
  `SmrWorkMode.DIRECTED_EFFORT` or `SmrWorkMode.OPEN_ENDED_DISCOVERY`
- `host_kind` is required for project-scoped trigger and launch preflight
- kickoff text must go through `initial_runtime_messages`; the legacy `prompt`
  field is not accepted
- parent-bound runs may specify either:
  - `primary_parent_ref={"kind": "...", "id": "..."}`
  - or `primary_parent={...}` for inline run-scoped OEQ/DEO creation
- milestone rows are now parent-owned and carry `parent_kind`, `parent_id`, and
  `milestone_kind`
- project notebook and curated knowledge are separate surfaces
- SDK callers receive non-2xx errors as exceptions. The `result.error` pattern
  applies to MCP clients, not the Python SDK
- for launch-day polling, prefer `get_run(run_id, project_id=project_id)`
- for richer inspection, compose noun reads like run questions, primary-parent
  milestones, OEQs, DEOs, experiments, and runtime messages

Actor-scoped engineer assignment example:

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
        ),
        SmrActorModelAssignment(
            actor_type=SmrActorType.WORKER,
            actor_subtype=SmrWorkerSubtype.RESEARCHER,
            agent_model=SmrAgentModel.GPT_5_4_MINI,
        ),
    ],
)
```

Phase 3 resource example:

```python
from managed_research import RunResourceBindings, InlineExternalRepositoryBinding

client.files.create_project(
    project_id,
    [
        {
            "path": "inputs/task.md",
            "content": "# Task\nUse the staged files and produce a report.",
            "visibility": "model",
        },
        {
            "path": "verifier/RUBRIC.json",
            "content": "{\"pass\": true}",
            "visibility": "verifier",
        },
    ],
)

primary_repo = client.repositories.create_project(
    project_id,
    name="nanohorizon",
    url="https://github.com/synth-laboratories/nanohorizon.git",
    default_branch="main",
    role="primary",
)

github_ref = client.credentials.create_project(
    project_id,
    kind="github",
    label="project_github",
    credential_name="smr-github-oauth-project-credential",
)

client.trigger_run(
    project_id,
    host_kind=SmrHostKind.DAYTONA,
    work_mode=SmrWorkMode.DIRECTED_EFFORT,
    resource_bindings=RunResourceBindings(
        external_repository_ids=[primary_repo.repository_id],
        credential_ref_ids=[github_ref.credential_ref_id],
        external_repositories=[
            InlineExternalRepositoryBinding(
                name="reference-docs",
                url="https://github.com/example/reference-docs.git",
                role="dependency",
            )
        ],
    ),
)
```

Parent-objective example:

```python
deo = client.projects.create_directed_effort_outcome(
    project_id,
    {
        "title": "Improve the no-model-update lane",
        "description": "Drive benchmark-facing improvement without changing the model.",
        "scope": "Prompt, context, harness-facing artifacts, and reviewable evidence.",
        "outcome_text": "Increase evaluator-facing quality while preserving harness compatibility.",
        "success_criteria": ["Preserve harness invariants", "Produce a reviewable artifact bundle"],
        "deliverable_requirements": ["artifact report", "workspace diff"],
    },
)

client.trigger_run(
    project_id,
    host_kind=SmrHostKind.DAYTONA,
    work_mode=SmrWorkMode.DIRECTED_EFFORT,
    primary_parent_ref={
        "kind": "directed_effort_outcome",
        "id": deo["directed_effort_outcome_id"],
    },
    initial_runtime_messages=kickoff,
)
```

Durable project-level assignment example:

```python
client.create_runnable_project(
    SmrRunnableProjectRequest(
        name="nanohorizon-sdk-demo",
        timezone="UTC",
        pool_id="daytona-default",
        runtime_kind=SmrRuntimeKind.SANDBOX_AGENT,
        environment_kind=SmrEnvironmentKind.HARBOR,
        agent_profiles=SmrAgentProfileBindings(
            orchestrator_profile_id="codex_gpt_5_4_medium",
            default_worker_profile_id="codex_gpt_5_4_medium",
        ),
        actor_model_assignments=[
            SmrActorModelAssignment(
                actor_type=SmrActorType.WORKER,
                actor_subtype=SmrWorkerSubtype.ENGINEER,
                agent_model=SmrAgentModel.GPT_5_3_CODEX_SPARK,
            )
        ],
    )
)
```
