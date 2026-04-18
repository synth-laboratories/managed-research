from managed_research import SmrControlClient
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
