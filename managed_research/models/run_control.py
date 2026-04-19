"""Typed public run-control acknowledgement mirrored from the backend contract.

Returned by pause / resume / stop to let callers correlate the control-plane
mutation with its durable runtime-intent message id and ack timestamp, so
replay/idempotence logic can target a specific intent instead of polling
run state.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from managed_research.models.run_state import (
    ManagedResearchRun,
    _require_mapping,
    _optional_string,
)


def _optional_datetime(payload: Mapping[str, object], key: str) -> datetime | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        # fromisoformat accepts the `+00:00` Z-suffix-equivalent the backend emits
        return datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    raise ValueError(f"{key} must be null, a datetime, or an ISO-8601 string")


@dataclass(frozen=True)
class ManagedResearchRunControlAck:
    """Result of a pause/resume/stop call.

    `control_intent_id` is the durable runtime-intent message id; replaying
    the same control with the same intent id is a no-op on the backend.
    `control_intent_ack_at` is when the backend enqueued the intent — not
    when the run actually transitioned.
    """

    run: ManagedResearchRun
    control_intent_id: str | None
    control_intent_ack_at: datetime | None
    raw: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, payload: object) -> ManagedResearchRunControlAck:
        mapping = _require_mapping(payload, label="run control ack")
        return cls(
            run=ManagedResearchRun.from_wire(mapping),
            control_intent_id=_optional_string(mapping, "control_intent_id"),
            control_intent_ack_at=_optional_datetime(mapping, "control_intent_ack_at"),
            raw=dict(mapping),
        )


__all__ = ["ManagedResearchRunControlAck"]
