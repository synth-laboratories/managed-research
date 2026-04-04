from managed_research import SmrControlClient
from managed_research.sdk import (
    ApprovalsAPI,
    ArtifactsAPI,
    IntegrationsAPI,
    LogsAPI,
    ProjectsAPI,
    RunsAPI,
    UsageAPI,
)


def test_namespace_properties_are_stable() -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")

    assert isinstance(client.projects, ProjectsAPI)
    assert isinstance(client.runs, RunsAPI)
    assert isinstance(client.artifacts, ArtifactsAPI)
    assert isinstance(client.approvals, ApprovalsAPI)
    assert isinstance(client.usage, UsageAPI)
    assert isinstance(client.logs, LogsAPI)
    assert isinstance(client.integrations, IntegrationsAPI)
    assert client.projects is client.projects
    assert client.runs is client.runs
    assert client.artifacts is client.artifacts
    assert client.approvals is client.approvals
    assert client.usage is client.usage
    assert client.logs is client.logs
    assert client.integrations is client.integrations

    client.close()


def test_projects_namespace_delegates_to_client(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: dict[str, object] = {}

    def fake_list_projects(**kwargs):
        captured.update(kwargs)
        return [{"project_id": "proj_123"}]

    monkeypatch.setattr(client, "list_projects", fake_list_projects)

    rows = client.projects.list(include_archived=True, limit=5)

    assert rows == [{"project_id": "proj_123"}]
    assert captured["include_archived"] is True
    assert captured["limit"] == 5
    client.close()


def test_runs_namespace_trigger_data_factory_delegates(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: dict[str, object] = {}

    def fake_trigger_data_factory_run(project_id: str, **kwargs):
        captured["project_id"] = project_id
        captured.update(kwargs)
        return {"run_id": "run_123"}

    monkeypatch.setattr(client, "trigger_data_factory_run", fake_trigger_data_factory_run)

    response = client.runs.trigger_data_factory(
        "proj_123",
        work_mode="directed_effort",
        dataset_ref="starting-data/demo",
        bundle_manifest_path="capture_bundle.json",
    )

    assert response == {"run_id": "run_123"}
    assert captured["project_id"] == "proj_123"
    assert captured["work_mode"] == "directed_effort"
    client.close()


def test_integrations_namespace_delegates(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    monkeypatch.setattr(client, "github_org_status", lambda: {"ok": True})

    assert client.integrations.github_org_status() == {"ok": True}
    client.close()
