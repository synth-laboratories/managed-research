"""Public log/archive models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from managed_research.models.generated.v1.common import _dict_payload, _optional_str


@dataclass(frozen=True)
class SmrRunLogArchive:
    log_archive_id: str
    run_id: str
    project_id: str
    storage_backend: str | None
    record_count: int
    session_count: int
    created_at: str | None
    metadata: dict[str, Any]
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrRunLogArchive:
        return cls(
            log_archive_id=str(payload.get("log_archive_id") or ""),
            run_id=str(payload.get("run_id") or ""),
            project_id=str(payload.get("project_id") or ""),
            storage_backend=_optional_str(payload, "storage_backend"),
            record_count=int(payload.get("record_count") or 0),
            session_count=int(payload.get("session_count") or 0),
            created_at=_optional_str(payload, "created_at"),
            metadata=_dict_payload(payload.get("metadata")),
            raw=dict(payload),
        )


__all__ = ["SmrRunLogArchive"]
