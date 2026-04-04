"""Public project models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from managed_research.models.generated.v1.common import _dict_payload, _list_of_dicts, _optional_str


@dataclass(frozen=True)
class SmrProject:
    project_id: str
    org_id: str | None
    name: str | None
    archived: bool | None
    created_at: str | None
    updated_at: str | None
    onboarding_state: dict[str, Any]
    execution: dict[str, Any]
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrProject:
        return cls(
            project_id=str(payload.get("project_id") or ""),
            org_id=_optional_str(payload, "org_id"),
            name=_optional_str(payload, "name"),
            archived=bool(payload.get("archived")) if payload.get("archived") is not None else None,
            created_at=_optional_str(payload, "created_at"),
            updated_at=_optional_str(payload, "updated_at"),
            onboarding_state=_dict_payload(payload.get("onboarding_state")),
            execution=_dict_payload(payload.get("execution")),
            raw=dict(payload),
        )


@dataclass(frozen=True)
class SmrProjectStatusSnapshot:
    project_id: str
    state: str | None
    active_run_id: str | None
    active_run_state: str | None
    active_runs: list[dict[str, Any]]
    active_actor_summaries: list[dict[str, Any]]
    queue_backlog_counts: dict[str, int]
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrProjectStatusSnapshot:
        queue_counts_raw = payload.get("queue_backlog_counts")
        queue_counts: dict[str, int] = {}
        if isinstance(queue_counts_raw, dict):
            queue_counts = {
                str(key): int(value)
                for key, value in queue_counts_raw.items()
                if key is not None and value is not None
            }
        return cls(
            project_id=str(payload.get("project_id") or ""),
            state=_optional_str(payload, "state"),
            active_run_id=_optional_str(payload, "active_run_id"),
            active_run_state=_optional_str(payload, "active_run_state"),
            active_runs=_list_of_dicts(payload.get("active_runs")),
            active_actor_summaries=_list_of_dicts(payload.get("active_actor_summaries")),
            queue_backlog_counts=queue_counts,
            raw=dict(payload),
        )


__all__ = ["SmrProject", "SmrProjectStatusSnapshot"]
