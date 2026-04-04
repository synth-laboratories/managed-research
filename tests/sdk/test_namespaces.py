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
    assert client.projects is client.projects
    assert client.runs is client.runs
    assert client.workspace_inputs is client.workspace_inputs
    assert client.progress is client.progress
    assert client.usage is client.usage

    client.close()
