import pytest
from managed_research.errors import SmrFundingLaneInvariantError, SmrLimitExceededError
from managed_research.mcp.server import ManagedResearchMcpServer


def test_rewritten_mcp_server_exposes_progress_and_workspace_tools() -> None:
    server = ManagedResearchMcpServer()
    names = set(server.available_tool_names())

    assert {
        "smr_append_project_notes",
        "smr_archive_project",
        "smr_attach_source_repo",
        "smr_create_project",
        "smr_get_capacity_lane_preview",
        "smr_get_capabilities",
        "smr_get_project_entitlement",
        "smr_get_project_git",
        "smr_get_project_notes",
        "smr_get_project_readiness",
        "smr_get_run_start_blockers",
        "smr_download_workspace_archive",
        "smr_patch_project",
        "smr_pause_project",
        "smr_get_run_progress",
        "smr_resume_project",
        "smr_set_project_notes",
        "smr_unarchive_project",
        "smr_get_usage_analytics",
        "smr_get_workspace_download_url",
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


def test_trigger_run_returns_structured_payload_on_limit_exceeded(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    detail = {
        "error_code": "smr_limit_exceeded",
        "resource_id": "agent_daytona",
        "window": "daily",
    }

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def trigger_run(self, project_id: str, **kwargs):
            raise SmrLimitExceededError(
                "limit hit",
                status_code=429,
                response_text="{}",
                detail=detail,
            )

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    out = server._tool_trigger_run(
        {"project_id": "proj_1", "host_kind": "daytona", "work_mode": "directed_effort"},
    )
    assert out == {
        "error": "smr_limit_exceeded",
        "detail": detail,
        "message": "limit hit",
        "http_status": 429,
    }


def test_trigger_run_returns_structured_payload_on_routing_invariant(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    detail = {
        "error_code": "smr_free_tier_routing_violation",
        "invariant": "ga_free_must_not_use_synth_codex_pool",
    }

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def trigger_run(self, project_id: str, **kwargs):
            raise SmrFundingLaneInvariantError(
                "routing",
                status_code=409,
                response_text="{}",
                detail=detail,
            )

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    out = server._tool_trigger_run(
        {"project_id": "proj_1", "host_kind": "daytona", "work_mode": "directed_effort"},
    )
    assert out == {
        "error": "smr_free_tier_routing_violation",
        "detail": detail,
        "message": "routing",
        "http_status": 409,
    }


def test_trigger_run_returns_structured_payload_on_insufficient_credits(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    detail = {
        "error_code": "smr_insufficient_credits",
        "message": "Insufficient credits to start a new run.",
    }

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def trigger_run(self, project_id: str, **kwargs):
            from managed_research.errors import SmrInsufficientCreditsError

            raise SmrInsufficientCreditsError(
                "no credits",
                status_code=402,
                response_text="{}",
                detail=detail,
            )

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    out = server._tool_trigger_run(
        {"project_id": "proj_1", "host_kind": "daytona", "work_mode": "directed_effort"},
    )
    assert out == {
        "error": "smr_insufficient_credits",
        "detail": detail,
        "message": "no credits",
        "http_status": 402,
    }


def test_get_workspace_download_url_delegates_to_client(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    captured: dict[str, str] = {}

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def get_workspace_download_url(self, project_id: str) -> dict[str, str]:
            captured["project_id"] = project_id
            return {"download_url": "https://s3.example/presigned", "commit_sha": "abc"}

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    out = server._tool_get_workspace_download_url({"project_id": "pid_1"})
    assert out == {"download_url": "https://s3.example/presigned", "commit_sha": "abc"}
    assert captured["project_id"] == "pid_1"


def test_get_capacity_lane_preview_delegates_to_client(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    captured: dict[str, str] = {}

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def get_capacity_lane_preview(self, project_id: str) -> dict[str, str]:
            captured["project_id"] = project_id
            return {"resolved_lane": "openai_chatgpt_pool"}

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    out = server._tool_get_capacity_lane_preview({"project_id": "pid_1"})
    assert out == {"resolved_lane": "openai_chatgpt_pool"}
    assert captured["project_id"] == "pid_1"


def test_project_patch_and_notes_tools_delegate_to_client(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    captured: dict[str, object] = {}

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def patch_project(self, project_id: str, payload: dict[str, object]):
            captured["patch"] = (project_id, payload)
            return {"project_id": project_id, **payload}

        def get_project_notes(self, project_id: str):
            captured["get_notes"] = project_id
            return {"project_id": project_id, "notes": "remember this"}

        def set_project_notes(self, project_id: str, notes: str):
            captured["set_notes"] = (project_id, notes)
            return {"project_id": project_id, "notes": notes}

        def append_project_notes(self, project_id: str, notes: str):
            captured["append_notes"] = (project_id, notes)
            return {"project_id": project_id, "notes": f"prefix\n{notes}"}

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    assert server._tool_patch_project({"project_id": "pid_1", "config": {"name": "Renamed"}}) == {
        "project_id": "pid_1",
        "name": "Renamed",
    }
    assert server._tool_get_project_notes({"project_id": "pid_1"}) == {
        "project_id": "pid_1",
        "notes": "remember this",
    }
    assert server._tool_set_project_notes({"project_id": "pid_1", "notes": "fresh notes"}) == {
        "project_id": "pid_1",
        "notes": "fresh notes",
    }
    assert server._tool_append_project_notes({"project_id": "pid_1", "notes": "delta"}) == {
        "project_id": "pid_1",
        "notes": "prefix\ndelta",
    }
    assert captured == {
        "patch": ("pid_1", {"name": "Renamed"}),
        "get_notes": "pid_1",
        "set_notes": ("pid_1", "fresh notes"),
        "append_notes": ("pid_1", "delta"),
    }


def test_project_lifecycle_tools_delegate_to_client(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    captured: list[tuple[str, str]] = []

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def pause_project(self, project_id: str):
            captured.append(("pause", project_id))
            return {"project_id": project_id, "state": "paused"}

        def resume_project(self, project_id: str):
            captured.append(("resume", project_id))
            return {"project_id": project_id, "state": "active"}

        def archive_project(self, project_id: str):
            captured.append(("archive", project_id))
            return {"project_id": project_id, "archived": True}

        def unarchive_project(self, project_id: str):
            captured.append(("unarchive", project_id))
            return {"project_id": project_id, "archived": False}

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    assert server._tool_pause_project({"project_id": "pid_1"}) == {
        "project_id": "pid_1",
        "state": "paused",
    }
    assert server._tool_resume_project({"project_id": "pid_1"}) == {
        "project_id": "pid_1",
        "state": "active",
    }
    assert server._tool_archive_project({"project_id": "pid_1"}) == {
        "project_id": "pid_1",
        "archived": True,
    }
    assert server._tool_unarchive_project({"project_id": "pid_1"}) == {
        "project_id": "pid_1",
        "archived": False,
    }
    assert captured == [
        ("pause", "pid_1"),
        ("resume", "pid_1"),
        ("archive", "pid_1"),
        ("unarchive", "pid_1"),
    ]


def test_get_run_start_blockers_delegates_to_client(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    captured: dict[str, object] = {}

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def get_run_start_blockers(self, project_id: str, **kwargs):
            captured["project_id"] = project_id
            captured["kwargs"] = kwargs
            return {"clear_to_trigger": False, "blockers": [{"stage": "limits"}]}

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    out = server._tool_get_run_start_blockers(
        {
            "project_id": "pid_1",
            "host_kind": "daytona",
            "work_mode": "directed_effort",
            "agent_model_params": {"reasoning_effort": "high"},
            "initial_runtime_messages": [{"body": "Check staging first.", "mode": "queue"}],
            "sandbox_override": {"image": "synth/smr:latest"},
        }
    )
    assert out == {"clear_to_trigger": False, "blockers": [{"stage": "limits"}]}
    assert captured["project_id"] == "pid_1"
    assert captured["kwargs"] == {
        "host_kind": "daytona",
        "work_mode": "directed_effort",
        "worker_pool_id": None,
        "timebox_seconds": None,
        "agent_profile": None,
        "agent_model": None,
        "agent_kind": None,
        "agent_model_params": {"reasoning_effort": "high"},
        "initial_runtime_messages": [{"body": "Check staging first.", "mode": "queue"}],
        "workflow": None,
        "sandbox_override": {"image": "synth/smr:latest"},
        "idempotency_key_run_create": None,
        "idempotency_key": None,
    }


def test_trigger_run_delegates_initial_runtime_messages_to_client(monkeypatch) -> None:
    server = ManagedResearchMcpServer()
    captured: dict[str, object] = {}

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def trigger_run(self, project_id: str, **kwargs):
            captured["project_id"] = project_id
            captured["kwargs"] = kwargs
            return {"run_id": "run_123"}

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    out = server._tool_trigger_run(
        {
            "project_id": "pid_1",
            "host_kind": "daytona",
            "work_mode": "directed_effort",
            "initial_runtime_messages": [
                {"body": "Start with the launch blocker.", "mode": "queue"}
            ],
        }
    )

    assert out == {"run_id": "run_123"}
    assert captured["project_id"] == "pid_1"
    assert captured["kwargs"] == {
        "host_kind": "daytona",
        "work_mode": "directed_effort",
        "worker_pool_id": None,
        "timebox_seconds": None,
        "agent_profile": None,
        "agent_model": None,
        "agent_kind": None,
        "agent_model_params": None,
        "initial_runtime_messages": [{"body": "Start with the launch blocker.", "mode": "queue"}],
        "workflow": None,
        "sandbox_override": None,
        "idempotency_key_run_create": None,
        "idempotency_key": None,
    }


def test_trigger_run_rejects_legacy_prompt_arg(monkeypatch) -> None:
    server = ManagedResearchMcpServer()

    class _UnusedClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

    monkeypatch.setattr(server, "_client_from_args", lambda args: _UnusedClient())

    with pytest.raises(ValueError, match="The `prompt` field is no longer supported"):
        server._tool_trigger_run(
            {
                "project_id": "pid_1",
                "host_kind": "daytona",
                "work_mode": "directed_effort",
                "prompt": "Ship it.",
            }
        )


def test_get_run_start_blockers_rejects_legacy_prompt_arg(monkeypatch) -> None:
    server = ManagedResearchMcpServer()

    class _UnusedClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

    monkeypatch.setattr(server, "_client_from_args", lambda args: _UnusedClient())

    with pytest.raises(ValueError, match="The `prompt` field is no longer supported"):
        server._tool_get_run_start_blockers(
            {
                "project_id": "pid_1",
                "host_kind": "daytona",
                "work_mode": "directed_effort",
                "prompt": "Ship it.",
            }
        )


def test_download_workspace_archive_delegates_to_client(monkeypatch, tmp_path) -> None:
    server = ManagedResearchMcpServer()
    out_file = tmp_path / "ws.tar.gz"

    class _FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            del exc_type
            del exc
            del tb

        def download_workspace_archive(self, project_id: str, output_path: str, **kwargs):
            assert project_id == "pid_1"
            assert str(out_file) in output_path or output_path.endswith("ws.tar.gz")
            assert kwargs.get("timeout_seconds") == 120
            return {"output_path": str(out_file), "bytes_written": 3, "commit_sha": "x"}

    monkeypatch.setattr(server, "_client_from_args", lambda args: _FakeClient())

    result = server._tool_download_workspace_archive(
        {
            "project_id": "pid_1",
            "output_path": str(out_file),
            "timeout_seconds": 120,
        }
    )
    assert result["bytes_written"] == 3
    assert result["commit_sha"] == "x"
