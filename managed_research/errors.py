"""Package error types."""

from __future__ import annotations

from typing import Any


class SmrApiError(RuntimeError):
    """Raised when the SMR API returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class SmrLimitExceededError(SmrApiError):
    """Raised when the backend rejects a request with ``smr_limit_exceeded`` (HTTP 429)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_text=response_text)
        self.detail = dict(detail) if detail else {}


class SmrFundingLaneInvariantError(SmrApiError):
    """Raised when the backend rejects with ``smr_free_tier_routing_violation`` (HTTP 409)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_text=response_text)
        self.detail = dict(detail) if detail else {}


class SmrInsufficientCreditsError(SmrApiError):
    """Raised when run start is blocked for credit headroom (HTTP 402, ``smr_insufficient_credits``)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_text=response_text)
        self.detail = dict(detail) if detail else {}


class SmrProjectMonthlyBudgetExhaustedError(SmrApiError):
    """Raised when the project monthly budget is exhausted (HTTP 402, ``smr_project_monthly_budget_exhausted``)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_text=response_text)
        self.detail = dict(detail) if detail else {}


class SmrManagedInferenceUnavailableError(SmrApiError):
    """Raised when managed Nemotron (or similar) is unreachable at run materialization (HTTP 503)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_text=response_text)
        self.detail = dict(detail) if detail else {}


class SmrCheckpointQuotaExceededError(SmrApiError):
    """Raised when checkpoint storage quota prevents restore or branch recovery."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_text=response_text)
        self.detail = dict(detail) if detail else {}


class SmrStructuredDenialError(SmrApiError):
    """Raised for other JSON error bodies that include a string ``error_code`` (forward-compatible)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_text=response_text)
        self.detail = dict(detail) if detail else {}


ManagedResearchError = SmrApiError


__all__ = [
    "ManagedResearchError",
    "SmrApiError",
    "SmrCheckpointQuotaExceededError",
    "SmrFundingLaneInvariantError",
    "SmrInsufficientCreditsError",
    "SmrLimitExceededError",
    "SmrManagedInferenceUnavailableError",
    "SmrProjectMonthlyBudgetExhaustedError",
    "SmrStructuredDenialError",
]
