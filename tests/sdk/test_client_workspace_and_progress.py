from __future__ import annotations

import base64
from pathlib import Path

import pytest

from managed_research import SmrApiError
from managed_research import SmrControlClient


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
        def __enter__(self) -> "_FakeStream":
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

        def __enter__(self) -> "_FakeHttpxClient":
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

    response = client.attach_source_repo("proj_123", "https://github.com/synth/foo", default_branch="main")

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
