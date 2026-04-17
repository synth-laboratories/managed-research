"""Typed public run-state models mirrored from the backend contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum


class ManagedResearchRunState(StrEnum):
    UNKNOWN = "unknown"
    QUEUED = "queued"
    RUNNING = "running"
    BLOCKED = "blocked"
    PAUSED = "paused"
    FINALIZING = "finalizing"
    DONE = "done"
    FAILED = "failed"
    STOPPED = "stopped"
    CANCELED = "canceled"


class ManagedResearchRunTerminalOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    STOPPED = "stopped"
    CANCELED = "canceled"
    TIMED_OUT = "timed_out"


class ManagedResearchRunLivePhase(StrEnum):
    ACCEPTED = "accepted"
    BOOTSTRAPPING = "bootstrapping"
    QUEUED = "queued"
    WAITING = "waiting"
    WORKING = "working"
    FINALIZING = "finalizing"
    TERMINAL = "terminal"
    UNKNOWN = "unknown"


def _require_mapping(payload: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        raise ValueError(f"{label} must be an object")
    return payload


def _optional_string(payload: Mapping[str, object], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string when provided")
    normalized = value.strip()
    return normalized or None


def _require_string(payload: Mapping[str, object], key: str, *, label: str) -> str:
    value = _optional_string(payload, key)
    if value is None:
        raise ValueError(f"{label} is required")
    return value


def _optional_bool(payload: Mapping[str, object], key: str) -> bool | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean when provided")
    return value


def _optional_object_dict(payload: object, *, label: str = "metadata") -> dict[str, object]:
    if payload is None:
        return {}
    return dict(_require_mapping(payload, label=label))


def _parse_state(value: str | None) -> ManagedResearchRunState:
    if not value:
        return ManagedResearchRunState.UNKNOWN
    return ManagedResearchRunState(value)


def _parse_terminal_outcome(
    value: str | None,
) -> ManagedResearchRunTerminalOutcome | None:
    if not value:
        return None
    return ManagedResearchRunTerminalOutcome(value)


def _parse_live_phase(value: str | None) -> ManagedResearchRunLivePhase:
    if not value:
        return ManagedResearchRunLivePhase.UNKNOWN
    return ManagedResearchRunLivePhase(value)


@dataclass(frozen=True)
class ManagedResearchRun:
    run_id: str
    project_id: str
    state: ManagedResearchRunState
    terminal_outcome: ManagedResearchRunTerminalOutcome | None = None
    live_phase: ManagedResearchRunLivePhase = ManagedResearchRunLivePhase.UNKNOWN
    state_reason: str | None = None
    state_authority: str = "backend_public_run_state_projection.v1"
    work_completed: bool = False
    completion_classifier: str | None = None
    diagnostics: dict[str, object] = field(default_factory=dict)
    raw: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, payload: object) -> ManagedResearchRun:
        mapping = _require_mapping(payload, label="managed research run")
        return cls(
            run_id=_require_string(mapping, "run_id", label="run.run_id"),
            project_id=_require_string(mapping, "project_id", label="run.project_id"),
            state=_parse_state(_require_string(mapping, "state", label="run.state")),
            terminal_outcome=_parse_terminal_outcome(
                _optional_string(mapping, "terminal_outcome")
            ),
            live_phase=_parse_live_phase(_optional_string(mapping, "live_phase")),
            state_reason=_optional_string(mapping, "state_reason"),
            state_authority=(
                _optional_string(mapping, "state_authority")
                or "backend_public_run_state_projection.v1"
            ),
            work_completed=bool(_optional_bool(mapping, "work_completed")),
            completion_classifier=_optional_string(mapping, "completion_classifier"),
            diagnostics=_optional_object_dict(
                mapping.get("diagnostics"),
                label="run.diagnostics",
            ),
            raw=dict(mapping),
        )


__all__ = [
    "ManagedResearchRun",
    "ManagedResearchRunLivePhase",
    "ManagedResearchRunState",
    "ManagedResearchRunTerminalOutcome",
]
