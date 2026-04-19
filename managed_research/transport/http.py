"""HTTP transport helpers for the SMR SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx

from managed_research.errors import (
    SmrApiError,
    SmrCheckpointQuotaExceededError,
    SmrFundingLaneInvariantError,
    SmrInsufficientCreditsError,
    SmrLimitExceededError,
    SmrManagedInferenceUnavailableError,
    SmrProjectMonthlyBudgetExhaustedError,
    SmrStructuredDenialError,
)


def _error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except Exception:
        payload = None
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail.strip()
        if isinstance(detail, dict):
            msg = detail.get("message")
            if isinstance(msg, str) and msg.strip():
                return msg.strip()
            err = detail.get("error")
            if isinstance(err, str) and err.strip():
                return err.strip()
    return (
        f"{response.request.method} {response.request.url.path} failed with {response.status_code}"
    )


def _raise_for_error_response(response: httpx.Response) -> None:
    """Map FastAPI ``{"detail": {"error_code": ...}}`` bodies to typed SDK errors."""
    try:
        payload = response.json()
    except Exception:
        payload = None
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, dict):
            code = detail.get("error_code")
            if isinstance(code, str) and code.strip():
                message = _error_message(response)
                status_code = response.status_code
                response_text = response.text
                stripped = code.strip()
                if stripped == "smr_limit_exceeded":
                    raise SmrLimitExceededError(
                        message,
                        status_code=status_code,
                        response_text=response_text,
                        detail=detail,
                    )
                if stripped == "smr_free_tier_routing_violation":
                    raise SmrFundingLaneInvariantError(
                        message,
                        status_code=status_code,
                        response_text=response_text,
                        detail=detail,
                    )
                if stripped == "smr_insufficient_credits":
                    raise SmrInsufficientCreditsError(
                        message,
                        status_code=status_code,
                        response_text=response_text,
                        detail=detail,
                    )
                if stripped == "smr_project_monthly_budget_exhausted":
                    raise SmrProjectMonthlyBudgetExhaustedError(
                        message,
                        status_code=status_code,
                        response_text=response_text,
                        detail=detail,
                    )
                if stripped == "smr_managed_inference_unavailable":
                    raise SmrManagedInferenceUnavailableError(
                        message,
                        status_code=status_code,
                        response_text=response_text,
                        detail=detail,
                    )
                if stripped == "checkpoint_storage_quota_exceeded":
                    raise SmrCheckpointQuotaExceededError(
                        message,
                        status_code=status_code,
                        response_text=response_text,
                        detail=detail,
                    )
                raise SmrStructuredDenialError(
                    message,
                    status_code=status_code,
                    response_text=response_text,
                    detail=detail,
                )
            raise SmrApiError(
                _error_message(response),
                status_code=response.status_code,
                response_text=response.text,
            )
    raise SmrApiError(
        _error_message(response),
        status_code=response.status_code,
        response_text=response.text,
    )


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
            _raise_for_error_response(response)
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
