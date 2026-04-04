from managed_research.mcp.server import ManagedResearchMcpServer


def test_rewritten_mcp_server_exposes_progress_and_workspace_tools() -> None:
    server = ManagedResearchMcpServer()
    names = set(server.available_tool_names())

    assert {
        "smr_attach_source_repo",
        "smr_create_project",
        "smr_get_capabilities",
        "smr_get_project_entitlement",
        "smr_get_project_readiness",
        "smr_get_run_progress",
        "smr_get_usage_analytics",
        "smr_get_workspace_inputs",
        "smr_list_active_runs",
        "smr_list_run_checkpoints",
        "smr_list_run_log_archives",
        "smr_list_run_questions",
        "smr_restore_run_checkpoint",
        "smr_upload_workspace_files",
    }.issubset(names)

    assert "smr_upload_starting_data" not in names
    assert "smr_get_starting_data_upload_urls" not in names
    assert "smr_trigger_data_factory" not in names
    assert "smr_data_factory_finalize" not in names
    assert "smr_data_factory_publish" not in names


def test_usage_tool_requires_explicit_managed_account_subject(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    captured: dict[str, object] = {}

    class _FakeUsage:
        def subject_for_managed_account(self, managed_account_id: str):
            captured["managed_account_id"] = managed_account_id
            return {"kind": "managed_account", "managedAccountId": managed_account_id}

    class _FakeClient:
        def __init__(self) -> None:
            self.usage = _FakeUsage()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def get_usage_analytics(self, subject, **kwargs):
            captured["subject"] = subject
            captured["kwargs"] = kwargs
            return {"ok": True}

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    response = server._tool_get_usage_analytics(
        {
            "subject_kind": "managed_account",
            "managed_account_id": "acct_123",
            "start_at": "2026-04-01T00:00:00Z",
            "end_at": "2026-04-02T00:00:00Z",
            "bucket": "DAY",
            "first": 25,
        }
    )

    assert response == {"ok": True}
    assert captured["managed_account_id"] == "acct_123"
    assert captured["subject"] == {
        "kind": "managed_account",
        "managedAccountId": "acct_123",
    }
