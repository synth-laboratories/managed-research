"""Public artifact models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from managed_research.models.generated.v1.common import _dict_payload, _optional_str


@dataclass(frozen=True)
class SmrArtifact:
    artifact_id: str
    run_id: str
    project_id: str
    artifact_type: str
    title: str | None
    uri: str | None
    digest: str | None
    metadata: dict[str, Any]
    created_at: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrArtifact:
        return cls(
            artifact_id=str(payload.get("artifact_id") or ""),
            run_id=str(payload.get("run_id") or ""),
            project_id=str(payload.get("project_id") or ""),
            artifact_type=str(payload.get("artifact_type") or ""),
            title=_optional_str(payload, "title"),
            uri=_optional_str(payload, "uri"),
            digest=_optional_str(payload, "digest"),
            metadata=_dict_payload(payload.get("metadata")),
            created_at=_optional_str(payload, "created_at"),
            raw=dict(payload),
        )


__all__ = ["SmrArtifact"]
