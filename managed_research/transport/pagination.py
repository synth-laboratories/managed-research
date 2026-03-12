"""Pagination helpers for SMR public API query params."""

from __future__ import annotations

from typing import Any


def build_query_params(
    *,
    limit: int | None = None,
    cursor: str | None = None,
    **params: Any,
) -> dict[str, Any]:
    """Build a query-param dict while omitting null and blank-string values."""
    query: dict[str, Any] = {}
    if limit is not None:
        query["limit"] = int(limit)
    if cursor is not None and cursor.strip():
        query["cursor"] = cursor.strip()
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                continue
            query[key] = stripped
            continue
        query[key] = value
    return query


def extract_next_cursor(payload: Any) -> str | None:
    """Read a next-page cursor from a typical list response payload."""
    if not isinstance(payload, dict):
        return None
    for key in ("next_cursor", "cursor", "next"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    meta = payload.get("meta")
    if isinstance(meta, dict):
        next_cursor = meta.get("next_cursor")
        if isinstance(next_cursor, str) and next_cursor.strip():
            return next_cursor.strip()
    return None


__all__ = ["build_query_params", "extract_next_cursor"]
