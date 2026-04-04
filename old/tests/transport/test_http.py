import httpx
import pytest
from managed_research.errors import SmrApiError
from managed_research.transport.http import SmrHttpTransport
from managed_research.transport.retries import RetryPolicy


def _transport_for(
    handler: httpx.MockTransport,
    *,
    retry_policy: RetryPolicy | None = None,
) -> SmrHttpTransport:
    client = httpx.Client(
        transport=handler,
        base_url="https://api.example.test",
        headers={"Authorization": "Bearer test"},
        timeout=5.0,
    )
    return SmrHttpTransport(
        base_url="https://api.example.test",
        headers={"Authorization": "Bearer test"},
        timeout=5.0,
        client=client,
        retry_policy=retry_policy,
        sleep=lambda _: None,
    )


def test_request_json_returns_payload() -> None:
    transport = _transport_for(
        httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True}))
    )

    assert transport.request_json("GET", "/smr/projects") == {"ok": True}
    transport.close()


def test_request_json_allow_not_found_returns_none() -> None:
    transport = _transport_for(httpx.MockTransport(lambda request: httpx.Response(404)))

    assert transport.request_json("GET", "/smr/projects/missing", allow_not_found=True) is None
    transport.close()


def test_request_json_raises_smr_api_error_on_http_failure() -> None:
    transport = _transport_for(
        httpx.MockTransport(lambda request: httpx.Response(500, text="backend down"))
    )

    with pytest.raises(SmrApiError, match="GET /smr/projects failed \\(500\\): backend down"):
        transport.request_json("GET", "/smr/projects")
    transport.close()


def test_request_json_returns_raw_text_when_response_is_not_json() -> None:
    transport = _transport_for(
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                text="plain text",
                headers={"content-type": "text/plain"},
            )
        )
    )

    assert transport.request_json("GET", "/smr/projects") == {"raw": "plain text"}
    transport.close()


def test_request_json_retries_retryable_get_status_failures() -> None:
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] == 1:
            return httpx.Response(503, text="temporarily unavailable")
        return httpx.Response(200, json={"ok": True})

    transport = _transport_for(
        httpx.MockTransport(handler),
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=0.001, max_delay_seconds=0.001),
    )

    assert transport.request_json("GET", "/smr/projects") == {"ok": True}
    assert attempts["count"] == 2
    transport.close()


def test_request_json_retries_retryable_get_exceptions() -> None:
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise httpx.ReadTimeout("timeout")
        return httpx.Response(200, json={"ok": True})

    transport = _transport_for(
        httpx.MockTransport(handler),
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=0.001, max_delay_seconds=0.001),
    )

    assert transport.request_json("GET", "/smr/projects") == {"ok": True}
    assert attempts["count"] == 2
    transport.close()


def test_request_json_does_not_retry_non_idempotent_post_by_default() -> None:
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        return httpx.Response(503, text="backend down")

    transport = _transport_for(
        httpx.MockTransport(handler),
        retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0.001, max_delay_seconds=0.001),
    )

    with pytest.raises(SmrApiError, match="POST /smr/projects failed \\(503\\): backend down"):
        transport.request_json("POST", "/smr/projects", json_body={"name": "demo"})

    assert attempts["count"] == 1
    transport.close()
