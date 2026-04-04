from managed_research.mcp.server import ManagedResearchMcpServer


def test_available_tool_names_have_no_duplicates() -> None:
    server = ManagedResearchMcpServer()

    names = server.available_tool_names()

    assert len(names) == len(set(names))
    assert "smr_create_project" in names
    assert "smr_trigger_run" in names
    assert "smr_list_project_questions" in names
    assert "smr_get_ops_status" in names
    assert "smr_get_run_usage" in names
    assert "smr_github_org_status" in names
    assert "smr_get_artifact_content" in names
