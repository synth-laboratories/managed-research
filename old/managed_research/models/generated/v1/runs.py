"""Public run models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from managed_research.models.generated.v1.common import _dict_payload, _optional_str


@dataclass(frozen=True)
class SmrRun:
    run_id: str
    org_id: str | None
    project_id: str | None
    trigger: str | None
    state: str | None
    created_at: str | None
    started_at: str | None
    finished_at: str | None
    status_detail: dict[str, Any]
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrRun:
        return cls(
            run_id=str(payload.get("run_id") or ""),
            org_id=_optional_str(payload, "org_id"),
            project_id=_optional_str(payload, "project_id"),
            trigger=_optional_str(payload, "trigger"),
            state=_optional_str(payload, "state"),
            created_at=_optional_str(payload, "created_at"),
            started_at=_optional_str(payload, "started_at"),
            finished_at=_optional_str(payload, "finished_at"),
            status_detail=_dict_payload(payload.get("status_detail")),
            raw=dict(payload),
        )


@dataclass(frozen=True)
class SmrActorStatus:
    actor_id: str
    actor_type: str
    project_id: str
    run_id: str
    state: str
    phase: str | None
    task_id: str | None
    task_key: str | None
    updated_at: str | None
    last_heartbeat_at: str | None
    paused_at: str | None
    error_summary: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrActorStatus:
        return cls(
            actor_id=str(payload.get("actor_id") or ""),
            actor_type=str(payload.get("actor_type") or ""),
            project_id=str(payload.get("project_id") or ""),
            run_id=str(payload.get("run_id") or ""),
            state=str(payload.get("state") or ""),
            phase=_optional_str(payload, "phase"),
            task_id=_optional_str(payload, "task_id"),
            task_key=_optional_str(payload, "task_key"),
            updated_at=_optional_str(payload, "updated_at"),
            last_heartbeat_at=_optional_str(payload, "last_heartbeat_at"),
            paused_at=_optional_str(payload, "paused_at"),
            error_summary=_optional_str(payload, "error_summary"),
            raw=dict(payload),
        )


__all__ = ["SmrActorStatus", "SmrRun"]
