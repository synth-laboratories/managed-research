from managed_research import (
    ManagedResearchProject,
    ManagedResearchRun,
    ManagedResearchRunControlEnqueueStatus,
    SmrControlClient,
)
from managed_research.sdk import (
    CredentialsAPI,
    ExportsAPI,
    GithubAPI,
    ProgressAPI,
    ProjectsAPI,
    RunsAPI,
    UsageAPI,
    WorkspaceInputsAPI,
)


def test_namespace_properties_are_stable() -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")

    assert isinstance(client.projects, ProjectsAPI)
    assert isinstance(client.runs, RunsAPI)
    assert isinstance(client.workspace_inputs, WorkspaceInputsAPI)
    assert isinstance(client.progress, ProgressAPI)
    assert isinstance(client.usage, UsageAPI)
    assert isinstance(client.github, GithubAPI)
    assert isinstance(client.credentials, CredentialsAPI)
    assert isinstance(client.exports, ExportsAPI)
    assert callable(client.projects.get_capacity_lane_preview)
    assert callable(client.projects.get_run_start_blockers)
    assert callable(client.projects.set_provider_key)
    assert callable(client.projects.get_provider_key_status)
    assert callable(client.projects.pause)
    assert callable(client.projects.resume)
    assert callable(client.projects.archive)
    assert callable(client.projects.unarchive)
    assert callable(client.projects.get_notes)
    assert callable(client.projects.set_notes)
    assert callable(client.projects.append_notes)
    assert client.projects is client.projects
    assert client.runs is client.runs
    assert client.workspace_inputs is client.workspace_inputs
    assert client.progress is client.progress
    assert client.usage is client.usage
    assert client.github is client.github
    assert client.credentials is client.credentials
    assert client.exports is client.exports
    assert callable(client.runs.get_logical_timeline)
    assert callable(client.runs.branch_from_checkpoint)
    assert callable(client.github.start_oauth)
    project = client.project("project-123")
    assert callable(project.repos.list)
    assert callable(project.files.list)
    assert callable(project.datasets.list)
    assert callable(project.prs.list)
    assert callable(project.models.list)
    assert callable(project.outputs.list)
    assert callable(project.readiness)

    client.close()


def test_projects_namespace_returns_typed_models(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")

    monkeypatch.setattr(
        client,
        "list_projects",
        lambda **kwargs: [
            {
                "project_id": "proj_123",
                "org_id": "org_123",
                "name": "Alpha",
                "timezone": "UTC",
                "schedule": {},
                "budgets": {},
                "key_policy": {},
                "integrations": {},
                "project_repo": {},
                "repos": ["github.com/synth/example"],
                "onboarding_state": {},
                "research": {},
                "synth_ai": {},
                "policy": {},
                "trial_matrix": {},
                "execution": {},
                "created_at": "2026-04-15T12:00:00Z",
                "updated_at": "2026-04-15T12:30:00Z",
                "archived": False,
            }
        ],
    )
    monkeypatch.setattr(
        client,
        "get_project",
        lambda project_id: {
            "project_id": project_id,
            "org_id": "org_123",
            "name": "Alpha",
            "timezone": "UTC",
            "schedule": {},
            "budgets": {},
            "key_policy": {},
            "integrations": {},
            "project_repo": {},
            "repos": [],
            "onboarding_state": {},
            "research": {},
            "synth_ai": {},
            "policy": {},
            "trial_matrix": {},
            "execution": {},
            "created_at": "2026-04-15T12:00:00Z",
            "updated_at": "2026-04-15T12:30:00Z",
            "archived": False,
        },
    )

    projects = client.projects.list()
    project = client.projects.get("proj_123")

    assert isinstance(projects[0], ManagedResearchProject)
    assert isinstance(project, ManagedResearchProject)
    assert project.project_id == "proj_123"
    client.close()


def test_runs_namespace_get_returns_typed_run(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    monkeypatch.setattr(
        client,
        "get_run",
        lambda run_id, **kwargs: {
            "run_id": run_id,
            "project_id": kwargs.get("project_id") or "proj_123",
            "state": "paused",
            "live_phase": "waiting",
            "state_authority": "backend_public_run_state_projection.v1",
        },
    )

    run = client.runs.get("run_123", project_id="proj_123")

    assert isinstance(run, ManagedResearchRun)
    assert run.run_id == "run_123"
    client.close()


def test_run_handle_pause_resume_stop_are_symmetric(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    calls: list[tuple[str, str, str | None]] = []

    def _ack(run_id: str, *, project_id: str | None = None) -> dict[str, object]:
        calls.append(("control", run_id, project_id))
        return {
            "run_id": run_id,
            "project_id": project_id,
            "state": "paused",
            "control_intent_id": "message:run_123:smr_runtime_control:1",
            "control_intent_ack_at": "2026-04-15T12:00:00Z",
            "enqueue_status": "accepted",
        }

    monkeypatch.setattr(client, "pause_run", _ack)
    monkeypatch.setattr(client, "resume_run", _ack)
    monkeypatch.setattr(client, "stop_run", _ack)

    handle = client.run("proj_123", "run_123")

    paused = handle.pause()
    resumed = handle.resume()
    stopped = handle.stop()

    assert paused.enqueue_status is ManagedResearchRunControlEnqueueStatus.ACCEPTED
    assert resumed.enqueue_status is ManagedResearchRunControlEnqueueStatus.ACCEPTED
    assert stopped.enqueue_status is ManagedResearchRunControlEnqueueStatus.ACCEPTED
    assert calls == [
        ("control", "run_123", "proj_123"),
        ("control", "run_123", "proj_123"),
        ("control", "run_123", "proj_123"),
    ]
    client.close()


def test_runs_namespace_uses_public_runtime_message_listing(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")

    def fail_private(*args, **kwargs):
        raise AssertionError("RunsAPI should not use _list_runtime_messages")

    def list_public(run_id: str, **kwargs):
        return [{"run_id": run_id, "status": kwargs.get("status") or "queued"}]

    monkeypatch.setattr(client, "_list_runtime_messages", fail_private)
    monkeypatch.setattr(client, "list_runtime_messages", list_public)

    messages = client.runs.list_runtime_messages("run_123", status="queued")

    assert messages == [{"run_id": "run_123", "status": "queued"}]
    client.close()
