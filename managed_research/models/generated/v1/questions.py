"""Public question models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from managed_research.models.generated.v1.common import _dict_payload, _optional_str


@dataclass(frozen=True)
class SmrQuestion:
    question_id: str
    run_id: str
    project_id: str
    status: str
    prompt: str
    metadata: dict[str, Any]
    response_text: str | None
    created_at: str | None
    responded_at: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrQuestion:
        return cls(
            question_id=str(payload.get("question_id") or ""),
            run_id=str(payload.get("run_id") or ""),
            project_id=str(payload.get("project_id") or ""),
            status=str(payload.get("status") or ""),
            prompt=str(payload.get("prompt") or ""),
            metadata=_dict_payload(payload.get("metadata")),
            response_text=_optional_str(payload, "response_text"),
            created_at=_optional_str(payload, "created_at"),
            responded_at=_optional_str(payload, "responded_at"),
            raw=dict(payload),
        )


__all__ = ["SmrQuestion"]
