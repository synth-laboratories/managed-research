from managed_research import SmrControlClient
from managed_research.sdk import (
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

    client.close()
