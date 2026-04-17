"""Typed SMR logical timeline and checkpoint-branching models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


def _require_text(value: str | None, *, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} is required")
    return text


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_datetime(value: Any, *, field_name: str) -> datetime:
    if isinstance(value, datetime):
        return value
    text = _require_text(str(value) if value is not None else None, field_name=field_name)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 datetime") from exc


def _coerce_string_dict(value: Any, *, field_name: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    normalized: dict[str, str] = {}
    for key, item in value.items():
        normalized[str(key)] = str(item)
    return normalized


class SmrBranchMode(StrEnum):
    EXACT = "exact"
    WITH_MESSAGE = "with_message"


@dataclass(frozen=True, slots=True)
class SmrRunBranchRequest:
    checkpoint_id: str | None = None
    checkpoint_record_id: str | None = None
    checkpoint_uri: str | None = None
    mode: SmrBranchMode = SmrBranchMode.EXACT
    message: str | None = None
    reason: str | None = None
    title: str | None = None
    source_node_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "checkpoint_id", _optional_text(self.checkpoint_id))
        object.__setattr__(
            self, "checkpoint_record_id", _optional_text(self.checkpoint_record_id)
        )
        object.__setattr__(self, "checkpoint_uri", _optional_text(self.checkpoint_uri))
        object.__setattr__(self, "message", _optional_text(self.message))
        object.__setattr__(self, "reason", _optional_text(self.reason))
        object.__setattr__(self, "title", _optional_text(self.title))
        object.__setattr__(self, "source_node_id", _optional_text(self.source_node_id))
        reference_count = sum(
            1
            for value in (
                self.checkpoint_id,
                self.checkpoint_record_id,
                self.checkpoint_uri,
            )
            if value is not None
        )
        if reference_count != 1:
            raise ValueError(
                "exactly one of checkpoint_id, checkpoint_record_id, or checkpoint_uri is required"
            )
        if self.mode == SmrBranchMode.WITH_MESSAGE and self.message is None:
            raise ValueError("message is required when mode is with_message")
        if self.mode == SmrBranchMode.EXACT and self.message is not None:
            raise ValueError("message must be omitted when mode is exact")

    def to_wire(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"mode": self.mode.value}
        for key in (
            "checkpoint_id",
            "checkpoint_record_id",
            "checkpoint_uri",
            "message",
            "reason",
            "title",
            "source_node_id",
        ):
            value = getattr(self, key)
            if value is not None:
                payload[key] = value
        return payload


@dataclass(frozen=True, slots=True)
class SmrRunBranchResponse:
    accepted: bool
    parent_run_id: str
    child_run_id: str
    source_checkpoint_id: str
    source_checkpoint_record_id: str | None = None
    source_node_id: str | None = None
    branch_message_id: str | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "parent_run_id", _require_text(self.parent_run_id, field_name="parent_run_id")
        )
        object.__setattr__(
            self, "child_run_id", _require_text(self.child_run_id, field_name="child_run_id")
        )
        object.__setattr__(
            self,
            "source_checkpoint_id",
            _require_text(self.source_checkpoint_id, field_name="source_checkpoint_id"),
        )
        object.__setattr__(
            self,
            "source_checkpoint_record_id",
            _optional_text(self.source_checkpoint_record_id),
        )
        object.__setattr__(self, "source_node_id", _optional_text(self.source_node_id))
        object.__setattr__(
            self, "branch_message_id", _optional_text(self.branch_message_id)
        )

    @classmethod
    def from_wire(cls, payload: dict[str, Any]) -> SmrRunBranchResponse:
        return cls(
            accepted=bool(payload.get("accepted")),
            parent_run_id=_require_text(
                payload.get("parent_run_id"), field_name="parent_run_id"
            ),
            child_run_id=_require_text(
                payload.get("child_run_id"), field_name="child_run_id"
            ),
            source_checkpoint_id=_require_text(
                payload.get("source_checkpoint_id"), field_name="source_checkpoint_id"
            ),
            source_checkpoint_record_id=_optional_text(
                payload.get("source_checkpoint_record_id")
            ),
            source_node_id=_optional_text(payload.get("source_node_id")),
            branch_message_id=_optional_text(payload.get("branch_message_id")),
            created_at=_parse_datetime(payload.get("created_at"), field_name="created_at")
            if payload.get("created_at") is not None
            else None,
        )


@dataclass(frozen=True, slots=True)
class SmrLogicalTimelineNode:
    node_id: str
    run_id: str
    created_at: datetime
    logical_index: int
    kind: str
    source: str
    title: str
    summary: str
    state: str | None = None
    actor_id: str | None = None
    actor_type: str | None = None
    participant_role: str | None = None
    task_id: str | None = None
    task_key: str | None = None
    worker_id: str | None = None
    checkpoint_id: str | None = None
    checkpoint_record_id: str | None = None
    checkpoint_uri: str | None = None
    checkpoint_boundary_kind: str | None = None
    message_id: str | None = None
    delivery_id: str | None = None
    artifact_id: str | None = None
    launch_id: str | None = None
    parent_node_id: str | None = None
    branch_parent_run_id: str | None = None
    branch_child_run_id: str | None = None
    branchable: bool = False
    steerable: bool = False
    live: bool = False
    detail: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "node_id", _require_text(self.node_id, field_name="node_id"))
        object.__setattr__(self, "run_id", _require_text(self.run_id, field_name="run_id"))
        object.__setattr__(self, "kind", _require_text(self.kind, field_name="kind"))
        object.__setattr__(self, "source", _require_text(self.source, field_name="source"))
        object.__setattr__(self, "title", _require_text(self.title, field_name="title"))
        object.__setattr__(self, "summary", _require_text(self.summary, field_name="summary"))
        object.__setattr__(self, "state", _optional_text(self.state))
        object.__setattr__(self, "actor_id", _optional_text(self.actor_id))
        object.__setattr__(self, "actor_type", _optional_text(self.actor_type))
        object.__setattr__(self, "participant_role", _optional_text(self.participant_role))
        object.__setattr__(self, "task_id", _optional_text(self.task_id))
        object.__setattr__(self, "task_key", _optional_text(self.task_key))
        object.__setattr__(self, "worker_id", _optional_text(self.worker_id))
        object.__setattr__(self, "checkpoint_id", _optional_text(self.checkpoint_id))
        object.__setattr__(
            self, "checkpoint_record_id", _optional_text(self.checkpoint_record_id)
        )
        object.__setattr__(self, "checkpoint_uri", _optional_text(self.checkpoint_uri))
        object.__setattr__(
            self,
            "checkpoint_boundary_kind",
            _optional_text(self.checkpoint_boundary_kind),
        )
        object.__setattr__(self, "message_id", _optional_text(self.message_id))
        object.__setattr__(self, "delivery_id", _optional_text(self.delivery_id))
        object.__setattr__(self, "artifact_id", _optional_text(self.artifact_id))
        object.__setattr__(self, "launch_id", _optional_text(self.launch_id))
        object.__setattr__(self, "parent_node_id", _optional_text(self.parent_node_id))
        object.__setattr__(
            self, "branch_parent_run_id", _optional_text(self.branch_parent_run_id)
        )
        object.__setattr__(
            self, "branch_child_run_id", _optional_text(self.branch_child_run_id)
        )
        object.__setattr__(
            self, "detail", _coerce_string_dict(self.detail, field_name="detail")
        )
        if self.logical_index < 0:
            raise ValueError("logical_index must be >= 0")

    @classmethod
    def from_wire(cls, payload: dict[str, Any]) -> SmrLogicalTimelineNode:
        return cls(
            node_id=_require_text(payload.get("node_id"), field_name="node_id"),
            run_id=_require_text(payload.get("run_id"), field_name="run_id"),
            created_at=_parse_datetime(payload.get("created_at"), field_name="created_at"),
            logical_index=int(payload.get("logical_index") or 0),
            kind=_require_text(payload.get("kind"), field_name="kind"),
            source=_require_text(payload.get("source"), field_name="source"),
            title=_require_text(payload.get("title"), field_name="title"),
            summary=_require_text(payload.get("summary"), field_name="summary"),
            state=_optional_text(payload.get("state")),
            actor_id=_optional_text(payload.get("actor_id")),
            actor_type=_optional_text(payload.get("actor_type")),
            participant_role=_optional_text(payload.get("participant_role")),
            task_id=_optional_text(payload.get("task_id")),
            task_key=_optional_text(payload.get("task_key")),
            worker_id=_optional_text(payload.get("worker_id")),
            checkpoint_id=_optional_text(payload.get("checkpoint_id")),
            checkpoint_record_id=_optional_text(payload.get("checkpoint_record_id")),
            checkpoint_uri=_optional_text(payload.get("checkpoint_uri")),
            checkpoint_boundary_kind=_optional_text(payload.get("checkpoint_boundary_kind")),
            message_id=_optional_text(payload.get("message_id")),
            delivery_id=_optional_text(payload.get("delivery_id")),
            artifact_id=_optional_text(payload.get("artifact_id")),
            launch_id=_optional_text(payload.get("launch_id")),
            parent_node_id=_optional_text(payload.get("parent_node_id")),
            branch_parent_run_id=_optional_text(payload.get("branch_parent_run_id")),
            branch_child_run_id=_optional_text(payload.get("branch_child_run_id")),
            branchable=bool(payload.get("branchable")),
            steerable=bool(payload.get("steerable")),
            live=bool(payload.get("live")),
            detail=_coerce_string_dict(payload.get("detail"), field_name="detail"),
        )


@dataclass(frozen=True, slots=True)
class SmrLogicalTimeline:
    project_id: str
    run_id: str
    generated_at: datetime
    run_state: str
    latest_node_id: str | None = None
    nodes: list[SmrLogicalTimelineNode] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "project_id", _require_text(self.project_id, field_name="project_id")
        )
        object.__setattr__(self, "run_id", _require_text(self.run_id, field_name="run_id"))
        object.__setattr__(
            self, "run_state", _require_text(self.run_state, field_name="run_state")
        )
        object.__setattr__(self, "latest_node_id", _optional_text(self.latest_node_id))

    @classmethod
    def from_wire(cls, payload: dict[str, Any]) -> SmrLogicalTimeline:
        raw_nodes = payload.get("nodes")
        if raw_nodes is None:
            nodes: list[SmrLogicalTimelineNode] = []
        elif isinstance(raw_nodes, list):
            nodes = [
                SmrLogicalTimelineNode.from_wire(item)
                for item in raw_nodes
                if isinstance(item, dict)
            ]
        else:
            raise ValueError("nodes must be a list")
        return cls(
            project_id=_require_text(payload.get("project_id"), field_name="project_id"),
            run_id=_require_text(payload.get("run_id"), field_name="run_id"),
            generated_at=_parse_datetime(payload.get("generated_at"), field_name="generated_at"),
            run_state=_require_text(payload.get("run_state"), field_name="run_state"),
            latest_node_id=_optional_text(payload.get("latest_node_id")),
            nodes=nodes,
        )


__all__ = [
    "SmrBranchMode",
    "SmrLogicalTimeline",
    "SmrLogicalTimelineNode",
    "SmrRunBranchRequest",
    "SmrRunBranchResponse",
]
