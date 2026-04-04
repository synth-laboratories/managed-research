"""HTTP transport helpers for the SMR SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx

from managed_research.errors import SmrApiError


def _error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except Exception:
        payload = None
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail.strip()
    return f"{response.request.method} {response.request.url.path} failed with {response.status_code}"


@dataclass
class SmrHttpTransport:
    """Simple JSON HTTP transport used by the rewritten public client."""

    base_url: str
    headers: dict[str, str]
    timeout: float
    client: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.client = httpx.Client(
            base_url=self.base_url.rstrip("/"),
            headers=self.headers,
            timeout=self.timeout,
        )

    def close(self) -> None:
        self.client.close()

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        allow_not_found: bool = False,
    ) -> Any:
        response = self.client.request(
            method,
            path,
            params=params,
            json=json_body,
        )
        if allow_not_found and response.status_code == 404:
            return None
        if response.is_error:
            raise SmrApiError(
                _error_message(response),
                status_code=response.status_code,
                response_text=response.text,
            )
        if not response.content:
            return {}
        try:
            return response.json()
        except Exception as exc:
            raise SmrApiError(
                f"{method} {path} returned a non-JSON response",
                status_code=response.status_code,
                response_text=response.text,
            ) from exc


__all__ = ["SmrHttpTransport"]
