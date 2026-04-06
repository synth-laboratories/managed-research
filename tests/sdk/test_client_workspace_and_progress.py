from __future__ import annotations

import base64
from pathlib import Path

import pytest
from managed_research import SmrApiError, SmrControlClient


def test_get_workspace_download_url_calls_backend_route(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path: str, **kwargs):
        captured["method"] = method
        captured["path"] = path
        return {"download_url": "https://signed", "commit_sha": "abc", "archive_key": "k1"}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    response = client.get_workspace_download_url("proj_123")

    assert response["commit_sha"] == "abc"
    assert captured == {
        "method": "GET",
        "path": "/smr/projects/proj_123/workspace/download-url",
    }
    client.close()


def test_get_project_git_calls_backend_route(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path: str, **kwargs):
        captured["path"] = path
        return {"current_commit_sha": "deadbeef", "branch": "main"}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    response = client.get_project_git("proj_123")

    assert response["branch"] == "main"
    assert captured["path"] == "/smr/projects/proj_123/git"
    client.close()


def test_project_lifecycle_routes_match_backend_surface(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    seen: list[tuple[str, str]] = []

    def fake_request_json(method: str, path: str, **kwargs):
        del kwargs
        seen.append((method, path))
        return {"ok": True}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    assert client.pause_project("proj_123") == {"ok": True}
    assert client.resume_project("proj_123") == {"ok": True}
    assert client.archive_project("proj_123") == {"ok": True}
    assert client.unarchive_project("proj_123") == {"ok": True}
    assert seen == [
        ("POST", "/smr/projects/proj_123/pause"),
        ("POST", "/smr/projects/proj_123/resume"),
        ("POST", "/smr/projects/proj_123/archive"),
        ("POST", "/smr/projects/proj_123/unarchive"),
    ]
    client.close()


def test_project_notes_routes_match_backend_surface(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: list[tuple[str, str, object | None]] = []

    def fake_request_json(method: str, path: str, **kwargs):
        captured.append((method, path, kwargs.get("json_body")))
        return {"notes": "ok"}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    assert client.get_project_notes("proj_123") == {"notes": "ok"}
    assert client.set_project_notes("proj_123", "fresh notes") == {"notes": "ok"}
    assert client.append_project_notes("proj_123", "delta") == {"notes": "ok"}
    assert captured == [
        ("GET", "/smr/projects/proj_123/notes", None),
        ("PUT", "/smr/projects/proj_123/notes", {"notes": "fresh notes"}),
        ("POST", "/smr/projects/proj_123/notes/append", {"notes": "delta"}),
    ]
    client.close()


def test_download_workspace_archive_writes_stream(monkeypatch, tmp_path: Path) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    out = tmp_path / "out.tar.gz"

    def fake_get_workspace_download_url(project_id: str) -> dict[str, str]:
        assert project_id == "proj_123"
        return {
            "download_url": "https://storage.example/archive.tgz",
            "commit_sha": "abc",
            "archive_key": "key",
        }

    monkeypatch.setattr(client, "get_workspace_download_url", fake_get_workspace_download_url)

    class _FakeStream:
        def __enter__(self) -> _FakeStream:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def raise_for_status(self) -> None:
            return None

        def iter_bytes(self, chunk_size: int = 65536) -> list[bytes]:
            return [b"he", b"llo"]

    class _FakeHttpxClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def __enter__(self) -> _FakeHttpxClient:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def stream(self, method: str, url: str) -> _FakeStream:
            assert method == "GET"
            assert url == "https://storage.example/archive.tgz"
            return _FakeStream()

    monkeypatch.setattr("managed_research.sdk.client.httpx.Client", _FakeHttpxClient)

    result = client.download_workspace_archive("proj_123", out)

    assert out.read_bytes() == b"hello"
    assert result["bytes_written"] == 5
    assert result["commit_sha"] == "abc"
    assert result["output_path"] == str(out.resolve())
    client.close()


def test_attach_source_repo_calls_workspace_input_route(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path: str, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["json_body"] = kwargs.get("json_body")
        return {"ok": True}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    response = client.attach_source_repo(
        "proj_123", "https://github.com/synth/foo", default_branch="main"
    )

    assert response == {"ok": True}
    assert captured["method"] == "PUT"
    assert captured["path"] == "/smr/projects/proj_123/workspace-inputs/source-repo"
    assert captured["json_body"] == {
        "url": "https://github.com/synth/foo",
        "default_branch": "main",
    }
    client.close()


def test_upload_workspace_directory_encodes_binary_files(monkeypatch, tmp_path: Path) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    text_file = tmp_path / "notes.txt"
    text_file.write_text("hello", encoding="utf-8")
    binary_file = tmp_path / "blob.bin"
    binary_file.write_bytes(b"\xff\x00")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path: str, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["json_body"] = kwargs.get("json_body")
        return {"file_count": 2}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    response = client.upload_workspace_directory("proj_123", tmp_path)

    assert response == {"file_count": 2}
    assert captured["method"] == "POST"
    assert captured["path"] == "/smr/projects/proj_123/workspace-inputs/files:upload"
    payload = captured["json_body"]
    assert isinstance(payload, dict)
    files = payload["files"]
    assert files[0]["path"] == "blob.bin"
    assert files[0]["encoding"] == "base64"
    assert files[0]["content"] == base64.b64encode(b"\xff\x00").decode("ascii")
    assert files[1]["path"] == "notes.txt"
    assert files[1]["encoding"] == "utf-8"
    assert files[1]["content"] == "hello"
    client.close()


def test_progress_routes_match_remigration_surface(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    seen: list[tuple[str, str]] = []

    def fake_request_json(method: str, path: str, **kwargs):
        seen.append((method, path))
        return {"ok": True}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    assert client.get_project_readiness("proj_123") == {"ok": True}
    assert client.get_run_progress("proj_123", "run_123") == {"ok": True}
    assert seen == [
        ("GET", "/smr/projects/proj_123/readiness"),
        ("GET", "/smr/projects/proj_123/runs/run_123/progress"),
    ]
    client.close()


def test_capacity_lane_preview_calls_backend_route(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path: str, **kwargs):
        captured["method"] = method
        captured["path"] = path
        return {"resolved_lane": "openai_chatgpt_pool"}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    response = client.get_capacity_lane_preview("proj_123")

    assert response["resolved_lane"] == "openai_chatgpt_pool"
    assert captured == {
        "method": "GET",
        "path": "/smr/projects/proj_123/capacity-lane-preview",
    }
    client.close()


def test_run_start_blockers_uses_trigger_compatible_payload(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path: str, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["json_body"] = kwargs.get("json_body")
        return {"clear_to_trigger": False, "blockers": [{"error_code": "smr_limit_exceeded"}]}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    response = client.get_run_start_blockers(
        "proj_123",
        host_kind="daytona",
        work_mode="directed_effort",
        worker_pool_id="pool_123",
        timebox_seconds=1800,
        agent_profile="ap_worker",
        agent_model="gpt-5.4",
        agent_kind="codex",
        agent_model_params={"reasoning_effort": "high"},
        initial_runtime_messages=[
            {"body": "Check the failing CI lane.", "mode": "queue"},
        ],
        sandbox_override={"image": "synth/smr:latest"},
        idempotency_key_run_create="idem_123",
    )

    assert response["clear_to_trigger"] is False
    assert captured["method"] == "POST"
    assert captured["path"] == "/smr/projects/proj_123/run-start-blockers"
    assert captured["json_body"] == {
        "host_kind": "daytona",
        "work_mode": "directed_effort",
        "worker_pool_id": "pool_123",
        "timebox_seconds": 1800,
        "agent_profile": "ap_worker",
        "agent_model": "gpt-5.4",
        "agent_kind": "codex",
        "agent_model_params": {"reasoning_effort": "high"},
        "initial_runtime_messages": [
            {"body": "Check the failing CI lane.", "mode": "queue"},
        ],
        "sandbox_override": {"image": "synth/smr:latest"},
        "idempotency_key_run_create": "idem_123",
    }
    client.close()


def test_trigger_run_uses_project_trigger_payload(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path: str, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["json_body"] = kwargs.get("json_body")
        return {"run_id": "run_123"}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    response = client.trigger_run(
        "proj_123",
        host_kind="daytona",
        work_mode="directed_effort",
        worker_pool_id="pool_123",
        timebox_seconds=1800,
        agent_profile="ap_worker",
        agent_model="gpt-5.4",
        agent_kind="codex",
        agent_model_params={"reasoning_effort": "high"},
        initial_runtime_messages=[
            {"body": "Start with the highest-confidence repro.", "mode": "queue"},
        ],
        sandbox_override={"image": "synth/smr:latest"},
        idempotency_key="idem_legacy",
    )

    assert response["run_id"] == "run_123"
    assert captured["method"] == "POST"
    assert captured["path"] == "/smr/projects/proj_123/trigger"
    assert captured["json_body"] == {
        "host_kind": "daytona",
        "work_mode": "directed_effort",
        "worker_pool_id": "pool_123",
        "timebox_seconds": 1800,
        "agent_profile": "ap_worker",
        "agent_model": "gpt-5.4",
        "agent_kind": "codex",
        "agent_model_params": {"reasoning_effort": "high"},
        "initial_runtime_messages": [
            {"body": "Start with the highest-confidence repro.", "mode": "queue"},
        ],
        "sandbox_override": {"image": "synth/smr:latest"},
        "idempotency_key": "idem_legacy",
    }
    client.close()


def test_usage_graphql_route_matches_managed_accounts_surface(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path: str, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["json_body"] = kwargs.get("json_body")
        return {
            "data": {
                "usageAnalytics": {
                    "subject": {
                        "kind": "managed_account",
                        "managedAccountId": "acct_123",
                    },
                    "window": {
                        "startAt": "2026-04-01T00:00:00Z",
                        "endAt": "2026-04-02T00:00:00Z",
                        "bucket": "DAY",
                        "resolvedBucket": "DAY",
                    },
                    "totals": {
                        "grossUsageUsd": 5.0,
                        "billedAmountUsd": 0.0,
                        "internalCostUsd": 3.0,
                        "eventCount": 1,
                        "chargedEventCount": 0,
                        "byBillingRoute": {},
                        "byUsageType": {},
                    },
                    "buckets": [],
                    "rows": [],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    response = client.get_usage_analytics(
        client.usage.subject_for_managed_account("acct_123"),
        start_at="2026-04-01T00:00:00Z",
        end_at="2026-04-02T00:00:00Z",
        bucket="DAY",
        first=50,
    )

    assert response.totals.gross_usage_usd == 5.0
    assert response.subject.managed_account_id == "acct_123"
    assert captured["method"] == "POST"
    assert captured["path"] == "/managed-accounts/graphql"
    payload = captured["json_body"]
    assert isinstance(payload, dict)
    assert payload["operationName"] == "UsageAnalytics"
    assert payload["variables"]["subject"] == {
        "kind": "managed_account",
        "managedAccountId": "acct_123",
    }
    assert payload["variables"]["window"]["bucket"] == "DAY"
    assert payload["variables"]["pagination"]["first"] == 50
    client.close()


def test_usage_graphql_errors_raise_smr_api_error(monkeypatch) -> None:
    client = SmrControlClient(api_key="test-key", backend_base="http://localhost:8000")

    def fake_request_json(method: str, path: str, **kwargs):
        del method
        del path
        del kwargs
        return {"errors": [{"message": "orgId subject must match the caller org"}]}

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    with pytest.raises(SmrApiError, match="orgId subject must match the caller org"):
        client.usage.get_usage_analytics(
            client.usage.subject_for_org("org_123"),
            start_at="2026-04-01T00:00:00Z",
            end_at="2026-04-02T00:00:00Z",
            bucket="DAY",
            first=50,
        )

    client.close()
