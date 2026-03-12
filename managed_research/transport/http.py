"""Shared HTTP transport for SMR public API requests."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

from managed_research.errors import SmrApiError
from managed_research.transport.retries import (
    RetryPolicy,
    backoff_delay_seconds,
    is_retryable_exception,
    is_retryable_status,
)

_DEFAULT_RETRYABLE_METHODS = frozenset({"DELETE", "GET", "HEAD", "OPTIONS"})


def _raise_for_error(method: str, path: str, response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    snippet = response.text[:500] if response.text else ""
    raise SmrApiError(f"{method.upper()} {path} failed ({response.status_code}): {snippet}")


class SmrHttpTransport:
    """Thin wrapper around ``httpx.Client`` with SMR error semantics."""

    def __init__(
        self,
        *,
        base_url: str,
        headers: dict[str, str],
        timeout: float,
        client: httpx.Client | None = None,
        retry_policy: RetryPolicy | None = None,
        sleep: Callable[[float], None] | None = None,
    ) -> None:
        self._client = client or httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )
        self._retry_policy = retry_policy or RetryPolicy()
        self._sleep = sleep or time.sleep

    @property
    def client(self) -> httpx.Client:
        return self._client

    def close(self) -> None:
        self._client.close()

    def _should_retry(
        self,
        method: str,
        *,
        retryable: bool | None,
        response: httpx.Response | None = None,
        exc: BaseException | None = None,
    ) -> bool:
        if retryable is False:
            return False
        if retryable is None and method.upper() not in _DEFAULT_RETRYABLE_METHODS:
            return False
        if response is not None:
            return is_retryable_status(response.status_code)
        if exc is not None:
            return is_retryable_exception(exc)
        return False

    def _request_with_retries(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        follow_redirects: bool = False,
        retryable: bool | None = None,
    ) -> httpx.Response:
        for attempt in range(1, self._retry_policy.max_attempts + 1):
            try:
                response = self._client.request(
                    method.upper(),
                    path,
                    params=params,
                    json=json_body,
                    follow_redirects=follow_redirects,
                )
            except Exception as exc:
                if (
                    attempt >= self._retry_policy.max_attempts
                    or not self._should_retry(method, retryable=retryable, exc=exc)
                ):
                    raise
                self._sleep(
                    backoff_delay_seconds(
                        attempt,
                        base_delay_seconds=self._retry_policy.base_delay_seconds,
                        max_delay_seconds=self._retry_policy.max_delay_seconds,
                    )
                )
                continue

            if (
                response.status_code < 400
                or attempt >= self._retry_policy.max_attempts
                or not self._should_retry(method, retryable=retryable, response=response)
            ):
                return response

            self._sleep(
                backoff_delay_seconds(
                    attempt,
                    base_delay_seconds=self._retry_policy.base_delay_seconds,
                    max_delay_seconds=self._retry_policy.max_delay_seconds,
                )
            )

        raise AssertionError("retry loop must return or raise before exhaustion")

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        follow_redirects: bool = False,
        retryable: bool | None = None,
    ) -> httpx.Response:
        response = self._request_with_retries(
            method,
            path,
            params=params,
            json_body=json_body,
            follow_redirects=follow_redirects,
            retryable=retryable,
        )
        _raise_for_error(method, path, response)
        return response

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        allow_not_found: bool = False,
        retryable: bool | None = None,
    ) -> Any:
        response = self._request_with_retries(
            method,
            path,
            params=params,
            json_body=json_body,
            retryable=retryable,
        )
        if allow_not_found and response.status_code == 404:
            return None
        _raise_for_error(method, path, response)
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}


__all__ = ["SmrHttpTransport"]
