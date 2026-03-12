"""Public usage/economics models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from managed_research.models.generated.v1.common import _dict_payload, _list_of_dicts, _optional_str


@dataclass(frozen=True)
class SmrRunEconomics:
    run_id: str
    org_id: str | None
    project_id: str | None
    summary: dict[str, Any]
    spend_entries: list[dict[str, Any]]
    egress_events: list[dict[str, Any]]
    trace_artifact: dict[str, Any] | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrRunEconomics:
        trace_artifact = payload.get("trace_artifact")
        return cls(
            run_id=str(payload.get("run_id") or ""),
            org_id=_optional_str(payload, "org_id"),
            project_id=_optional_str(payload, "project_id"),
            summary=_dict_payload(payload.get("summary")),
            spend_entries=_list_of_dicts(payload.get("spend_entries")),
            egress_events=_list_of_dicts(payload.get("egress_events")),
            trace_artifact=_dict_payload(trace_artifact) if isinstance(trace_artifact, dict) else None,
            raw=dict(payload),
        )


__all__ = ["SmrRunEconomics"]
