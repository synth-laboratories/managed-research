import httpx
import pytest
from managed_research.transport.pagination import build_query_params, extract_next_cursor
from managed_research.transport.retries import (
    RetryPolicy,
    backoff_delay_seconds,
    is_retryable_exception,
    is_retryable_status,
)
from managed_research.transport.streaming import preview_binary_payload


def test_build_query_params_omits_empty_values() -> None:
    assert build_query_params(
        limit=25,
        cursor=" cursor_123 ",
        created_after="",
        created_before=None,
        project_id=" proj_123 ",
        include_archived=0,
    ) == {
        "limit": 25,
        "cursor": "cursor_123",
        "project_id": "proj_123",
        "include_archived": 0,
    }


def test_extract_next_cursor_reads_common_shapes() -> None:
    assert extract_next_cursor({"next_cursor": "cursor_123"}) == "cursor_123"
    assert extract_next_cursor({"meta": {"next_cursor": "cursor_456"}}) == "cursor_456"
    assert extract_next_cursor({"items": []}) is None


def test_retry_helpers_cover_common_http_cases() -> None:
    policy = RetryPolicy()

    assert policy.max_attempts == 3
    assert is_retryable_status(429) is True
    assert is_retryable_status(404) is False
    assert is_retryable_exception(httpx.ReadTimeout("timeout")) is True
    assert is_retryable_exception(ValueError("bad")) is False
    assert backoff_delay_seconds(1) == pytest.approx(0.25)
    assert backoff_delay_seconds(4) == pytest.approx(2.0)


def test_preview_binary_payload_prefers_utf8_and_truncates() -> None:
    preview = preview_binary_payload(b"hello world", max_bytes=5)

    assert preview.encoding == "utf-8"
    assert preview.content == "hello"
    assert preview.truncated is True
    assert preview.content_bytes_returned == 5
    assert preview.content_bytes_total == 11


def test_preview_binary_payload_falls_back_to_base64() -> None:
    preview = preview_binary_payload(b"\xff\x00", max_bytes=10)

    assert preview.encoding == "base64"
    assert preview.content == "/wA="
    assert preview.truncated is False
