"""Public approval models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from managed_research.models.generated.v1.common import _dict_payload, _optional_str


@dataclass(frozen=True)
class SmrApproval:
    approval_id: str
    run_id: str
    project_id: str
    kind: str
    status: str
    title: str | None
    body: str | None
    metadata: dict[str, Any]
    created_at: str | None
    resolved_at: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrApproval:
        return cls(
            approval_id=str(payload.get("approval_id") or ""),
            run_id=str(payload.get("run_id") or ""),
            project_id=str(payload.get("project_id") or ""),
            kind=str(payload.get("kind") or ""),
            status=str(payload.get("status") or ""),
            title=_optional_str(payload, "title"),
            body=_optional_str(payload, "body"),
            metadata=_dict_payload(payload.get("metadata")),
            created_at=_optional_str(payload, "created_at"),
            resolved_at=_optional_str(payload, "resolved_at"),
            raw=dict(payload),
        )


__all__ = ["SmrApproval"]
