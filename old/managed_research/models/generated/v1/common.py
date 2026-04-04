"""Common model helpers and shared public types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _optional_str(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    return str(value)


def _dict_payload(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


@dataclass(frozen=True)
class SmrCapabilities:
    supports_project_scoped_runs: bool
    supports_run_list_filters: bool
    supports_run_list_cursor: bool
    supports_project_status_snapshot: bool
    supports_unified_actor_status: bool
    actor_status_schema_version: str | None
    supports_actor_control: bool
    supports_encrypted_provider_keys: bool
    supports_run_economics: bool
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrCapabilities:
        return cls(
            supports_project_scoped_runs=bool(payload.get("supports_project_scoped_runs")),
            supports_run_list_filters=bool(payload.get("supports_run_list_filters")),
            supports_run_list_cursor=bool(payload.get("supports_run_list_cursor")),
            supports_project_status_snapshot=bool(payload.get("supports_project_status_snapshot")),
            supports_unified_actor_status=bool(payload.get("supports_unified_actor_status")),
            actor_status_schema_version=_optional_str(payload, "actor_status_schema_version"),
            supports_actor_control=bool(payload.get("supports_actor_control")),
            supports_encrypted_provider_keys=bool(payload.get("supports_encrypted_provider_keys")),
            supports_run_economics=bool(payload.get("supports_run_economics")),
            raw=dict(payload),
        )


__all__ = [
    "SmrCapabilities",
    "_dict_payload",
    "_list_of_dicts",
    "_optional_str",
]
