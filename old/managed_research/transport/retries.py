"""Retry-policy helpers for SMR public HTTP operations."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

RETRYABLE_STATUS_CODES = frozenset({408, 409, 425, 429, 500, 502, 503, 504})


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.25
    max_delay_seconds: float = 4.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay_seconds <= 0:
            raise ValueError("base_delay_seconds must be positive")
        if self.max_delay_seconds <= 0:
            raise ValueError("max_delay_seconds must be positive")


def is_retryable_status(status_code: int) -> bool:
    return status_code in RETRYABLE_STATUS_CODES


def is_retryable_exception(exc: BaseException) -> bool:
    return isinstance(
        exc,
        (
            httpx.ConnectError,
            httpx.ReadError,
            httpx.ReadTimeout,
            httpx.RemoteProtocolError,
            httpx.WriteError,
            httpx.WriteTimeout,
        ),
    )


def backoff_delay_seconds(
    attempt: int,
    *,
    base_delay_seconds: float = 0.25,
    max_delay_seconds: float = 4.0,
) -> float:
    if attempt < 1:
        raise ValueError("attempt must be at least 1")
    if base_delay_seconds <= 0:
        raise ValueError("base_delay_seconds must be positive")
    if max_delay_seconds <= 0:
        raise ValueError("max_delay_seconds must be positive")
    delay = base_delay_seconds * (2 ** (attempt - 1))
    return min(delay, max_delay_seconds)


__all__ = [
    "RETRYABLE_STATUS_CODES",
    "RetryPolicy",
    "backoff_delay_seconds",
    "is_retryable_exception",
    "is_retryable_status",
]
