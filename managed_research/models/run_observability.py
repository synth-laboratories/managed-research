"""Typed run observability models for rich SMR polling."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from managed_research.models.run_state import (
    ManagedResearchRun,
    ManagedResearchRunLivePhase,
    ManagedResearchRunState,
    ManagedResearchRunTerminalOutcome,
)


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


def _optional_int(payload: Mapping[str, object], key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer when provided")
    return value


def _optional_bool(payload: Mapping[str, object], key: str) -> bool | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean when provided")
    return value


def _optional_object_dict(payload: object) -> dict[str, object]:
    if payload is None:
        return {}
    mapping = _require_mapping(payload, label="metadata")
    return dict(mapping)


def _optional_dict_list(payload: object, *, label: str) -> list[dict[str, object]]:
    if payload is None:
        return []
    if not isinstance(payload, list):
        raise ValueError(f"{label} must be an array when provided")
    rows: list[dict[str, object]] = []
    for item in payload:
        rows.append(dict(_require_mapping(item, label=label)))
    return rows


def _optional_string_int_map(payload: object, *, label: str) -> dict[str, int]:
    if payload is None:
        return {}
    mapping = _require_mapping(payload, label=label)
    normalized: dict[str, int] = {}
    for key, value in mapping.items():
        if not isinstance(key, str):
            raise ValueError(f"{label} keys must be strings")
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{label}.{key} must be an integer")
        normalized[key] = value
    return normalized


class CandidatePublicationOutcome(StrEnum):
    RUNNING = "running"
    PR_PUBLISHED = "pr_published"
    AWAITING_PR_BINDING = "awaiting_pr_binding"
    FAILED_BEFORE_BRANCH = "failed_before_branch"
    FAILED_AFTER_BRANCH_NO_PR = "failed_after_branch_no_pr"


class RunAnomalyKind(StrEnum):
    RUNNING_WITHOUT_LIVE_ACTORS = "running_without_live_actors"
    RUNNING_WITHOUT_NONTERMINAL_TASKS = "running_without_nonterminal_tasks"
    RUN_TERMINAL_WITH_NONTERMINAL_TASKS = "run_terminal_with_nonterminal_tasks"
    RUN_TERMINAL_WITH_PENDING_RUNTIME_INTENTS = "run_terminal_with_pending_runtime_intents"
    MCP_UNREACHABLE = "mcp_unreachable"
    TERMINAL_WITHOUT_PUBLICATION_VERDICT = "terminal_without_publication_verdict"


@dataclass(frozen=True)
class RunObservationCursor:
    latest_event_seq: int | None = None
    latest_runtime_message_seq: int | None = None
    latest_runtime_event_id: str | None = None
    generated_at: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> RunObservationCursor:
        mapping = _require_mapping(payload, label="run observation cursor")
        return cls(
            latest_event_seq=_optional_int(mapping, "latest_event_seq"),
            latest_runtime_message_seq=_optional_int(mapping, "latest_runtime_message_seq"),
            latest_runtime_event_id=_optional_string(mapping, "latest_runtime_event_id"),
            generated_at=_optional_string(mapping, "generated_at"),
        )

    def to_query_params(self) -> dict[str, object]:
        params: dict[str, object] = {}
        if self.latest_event_seq is not None:
            params["since_event_seq"] = self.latest_event_seq
        if self.latest_runtime_message_seq is not None:
            params["latest_runtime_message_seq"] = self.latest_runtime_message_seq
        if self.latest_runtime_event_id is not None:
            params["latest_runtime_event_id"] = self.latest_runtime_event_id
        return params


@dataclass(frozen=True)
class RunLifecycleLocalExecution:
    slot_id: str
    runtime_id: str
    dispatch_pool: str
    host_kind: str
    requires_hosted_capacity: bool = False

    @classmethod
    def from_wire(cls, payload: object) -> RunLifecycleLocalExecution:
        mapping = _require_mapping(payload, label="run lifecycle local execution")
        return cls(
            slot_id=_require_string(mapping, "slot_id", label="local_execution.slot_id"),
            runtime_id=_require_string(mapping, "runtime_id", label="local_execution.runtime_id"),
            dispatch_pool=_require_string(mapping, "dispatch_pool", label="local_execution.dispatch_pool"),
            host_kind=_require_string(mapping, "host_kind", label="local_execution.host_kind"),
            requires_hosted_capacity=bool(mapping.get("requires_hosted_capacity") or False),
        )


@dataclass(frozen=True)
class RunLifecycleDispatch:
    owner: str
    pool_id: str
    host_kind: str
    local_execution: RunLifecycleLocalExecution | None = None

    @classmethod
    def from_wire(cls, payload: object) -> RunLifecycleDispatch:
        mapping = _require_mapping(payload, label="run lifecycle dispatch")
        local_execution = mapping.get("local_execution")
        return cls(
            owner=_require_string(mapping, "owner", label="dispatch.owner"),
            pool_id=_require_string(mapping, "pool_id", label="dispatch.pool_id"),
            host_kind=_require_string(mapping, "host_kind", label="dispatch.host_kind"),
            local_execution=(
                RunLifecycleLocalExecution.from_wire(local_execution)
                if local_execution is not None
                else None
            ),
        )


@dataclass(frozen=True)
class RunLifecycleFailure:
    family: str
    detail: str
    reason: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> RunLifecycleFailure:
        mapping = _require_mapping(payload, label="run lifecycle failure")
        return cls(
            family=_require_string(mapping, "family", label="failure.family"),
            detail=_require_string(mapping, "detail", label="failure.detail"),
            reason=_optional_string(mapping, "reason"),
        )


@dataclass(frozen=True)
class RunLifecycleView:
    authority_phase: str
    bootstrap_phase: str | None
    terminal_phase: str
    terminal_outcome: str | None
    dispatch: RunLifecycleDispatch
    failure: RunLifecycleFailure | None = None
    metadata: dict[str, object] = field(default_factory=dict)
    updated_at: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> RunLifecycleView:
        mapping = _require_mapping(payload, label="run lifecycle")
        failure = mapping.get("failure")
        return cls(
            authority_phase=_require_string(mapping, "authority_phase", label="lifecycle.authority_phase"),
            bootstrap_phase=_optional_string(mapping, "bootstrap_phase"),
            terminal_phase=_require_string(mapping, "terminal_phase", label="lifecycle.terminal_phase"),
            terminal_outcome=_optional_string(mapping, "terminal_outcome"),
            dispatch=RunLifecycleDispatch.from_wire(mapping.get("dispatch")),
            failure=RunLifecycleFailure.from_wire(failure) if failure is not None else None,
            metadata=_optional_object_dict(mapping.get("metadata")),
            updated_at=_optional_string(mapping, "updated_at"),
        )


@dataclass(frozen=True)
class CandidatePublicationView:
    outcome: CandidatePublicationOutcome
    branch_name: str | None = None
    head_commit_sha: str | None = None
    pr_url: str | None = None
    pr_number: int | None = None
    repo: str | None = None
    base_branch: str | None = None
    failure_code: str | None = None
    failure_detail: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> CandidatePublicationView:
        mapping = _require_mapping(payload, label="candidate publication")
        outcome_raw = _require_string(mapping, "outcome", label="candidate_publication.outcome")
        return cls(
            outcome=CandidatePublicationOutcome(outcome_raw),
            branch_name=_optional_string(mapping, "branch_name"),
            head_commit_sha=_optional_string(mapping, "head_commit_sha"),
            pr_url=_optional_string(mapping, "pr_url"),
            pr_number=_optional_int(mapping, "pr_number"),
            repo=_optional_string(mapping, "repo"),
            base_branch=_optional_string(mapping, "base_branch"),
            failure_code=_optional_string(mapping, "failure_code"),
            failure_detail=_optional_string(mapping, "failure_detail"),
        )


@dataclass(frozen=True)
class ActorSnapshot:
    actor_id: str
    actor_type: str
    state: str
    participant_role: str | None = None
    phase: str | None = None
    live_session: bool = False
    session_status: str | None = None
    task_id: str | None = None
    task_key: str | None = None
    runtime_source: str | None = None
    started_at: str | None = None
    updated_at: str | None = None
    completed_at: str | None = None
    last_heartbeat_at: str | None = None
    labels: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, payload: object) -> ActorSnapshot:
        mapping = _require_mapping(payload, label="actor snapshot")
        return cls(
            actor_id=_require_string(mapping, "actor_id", label="actor.actor_id"),
            actor_type=_require_string(mapping, "actor_type", label="actor.actor_type"),
            state=_require_string(mapping, "state", label="actor.state"),
            participant_role=_optional_string(mapping, "participant_role"),
            phase=_optional_string(mapping, "phase"),
            live_session=bool(_optional_bool(mapping, "live_session")),
            session_status=_optional_string(mapping, "session_status"),
            task_id=_optional_string(mapping, "task_id"),
            task_key=_optional_string(mapping, "task_key"),
            runtime_source=_optional_string(mapping, "runtime_source"),
            started_at=_optional_string(mapping, "started_at"),
            updated_at=_optional_string(mapping, "updated_at"),
            completed_at=_optional_string(mapping, "completed_at"),
            last_heartbeat_at=_optional_string(mapping, "last_heartbeat_at"),
            labels=_optional_object_dict(mapping.get("labels")),
        )


@dataclass(frozen=True)
class ActorCollectionSnapshot:
    total_count: int
    counts_by_state: dict[str, int] = field(default_factory=dict)
    counts_by_role: dict[str, int] = field(default_factory=dict)
    items: list[ActorSnapshot] = field(default_factory=list)
    latest_transitions: list[ActorSnapshot] = field(default_factory=list)

    @classmethod
    def from_wire(cls, payload: object) -> ActorCollectionSnapshot:
        mapping = _require_mapping(payload, label="actor collection")
        return cls(
            total_count=_optional_int(mapping, "total_count") or 0,
            counts_by_state=_optional_string_int_map(mapping.get("counts_by_state"), label="actors.counts_by_state"),
            counts_by_role=_optional_string_int_map(mapping.get("counts_by_role"), label="actors.counts_by_role"),
            items=[ActorSnapshot.from_wire(item) for item in _optional_dict_list(mapping.get("items"), label="actors.items")],
            latest_transitions=[
                ActorSnapshot.from_wire(item)
                for item in _optional_dict_list(mapping.get("latest_transitions"), label="actors.latest_transitions")
            ],
        )


@dataclass(frozen=True)
class TaskSnapshot:
    task_id: str
    task_key: str
    kind: str
    state: str
    execution_owner: str
    claimed_by: str | None = None
    worker_pool: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    updated_at: str | None = None
    status_detail: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, payload: object) -> TaskSnapshot:
        mapping = _require_mapping(payload, label="task snapshot")
        return cls(
            task_id=_require_string(mapping, "task_id", label="task.task_id"),
            task_key=_require_string(mapping, "task_key", label="task.task_key"),
            kind=_require_string(mapping, "kind", label="task.kind"),
            state=_require_string(mapping, "state", label="task.state"),
            execution_owner=_require_string(mapping, "execution_owner", label="task.execution_owner"),
            claimed_by=_optional_string(mapping, "claimed_by"),
            worker_pool=_optional_string(mapping, "worker_pool"),
            started_at=_optional_string(mapping, "started_at"),
            finished_at=_optional_string(mapping, "finished_at"),
            updated_at=_optional_string(mapping, "updated_at"),
            status_detail=_optional_object_dict(mapping.get("status_detail")),
        )


@dataclass(frozen=True)
class TaskCollectionSnapshot:
    total_count: int
    counts_by_state: dict[str, int] = field(default_factory=dict)
    counts_by_owner: dict[str, int] = field(default_factory=dict)
    items: list[TaskSnapshot] = field(default_factory=list)
    latest_transitions: list[TaskSnapshot] = field(default_factory=list)

    @classmethod
    def from_wire(cls, payload: object) -> TaskCollectionSnapshot:
        mapping = _require_mapping(payload, label="task collection")
        return cls(
            total_count=_optional_int(mapping, "total_count") or 0,
            counts_by_state=_optional_string_int_map(mapping.get("counts_by_state"), label="tasks.counts_by_state"),
            counts_by_owner=_optional_string_int_map(mapping.get("counts_by_owner"), label="tasks.counts_by_owner"),
            items=[TaskSnapshot.from_wire(item) for item in _optional_dict_list(mapping.get("items"), label="tasks.items")],
            latest_transitions=[
                TaskSnapshot.from_wire(item)
                for item in _optional_dict_list(mapping.get("latest_transitions"), label="tasks.latest_transitions")
            ],
        )


@dataclass(frozen=True)
class RuntimeMessageView:
    message_id: str
    created_at: str
    seq: int
    mode: str
    sender: str
    target: str | None = None
    action: str | None = None
    body: str | None = None
    status: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> RuntimeMessageView:
        mapping = _require_mapping(payload, label="runtime message")
        return cls(
            message_id=_require_string(mapping, "message_id", label="runtime.message_id"),
            created_at=_require_string(mapping, "created_at", label="runtime.created_at"),
            seq=_optional_int(mapping, "seq") or 0,
            mode=_require_string(mapping, "mode", label="runtime.mode"),
            sender=_require_string(mapping, "sender", label="runtime.sender"),
            target=_optional_string(mapping, "target"),
            action=_optional_string(mapping, "action"),
            body=_optional_string(mapping, "body"),
            status=_optional_string(mapping, "status"),
        )


@dataclass(frozen=True)
class RuntimeDeliveryView:
    message_id: str
    created_at: str
    mode: str
    sender: str
    target: str | None = None
    status: str | None = None
    error: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> RuntimeDeliveryView:
        mapping = _require_mapping(payload, label="runtime delivery")
        return cls(
            message_id=_require_string(mapping, "message_id", label="delivery.message_id"),
            created_at=_require_string(mapping, "created_at", label="delivery.created_at"),
            mode=_require_string(mapping, "mode", label="delivery.mode"),
            sender=_require_string(mapping, "sender", label="delivery.sender"),
            target=_optional_string(mapping, "target"),
            status=_optional_string(mapping, "status"),
            error=_optional_string(mapping, "error"),
        )


@dataclass(frozen=True)
class RuntimeEventView:
    event_id: str
    created_at: str
    kind: str
    source: str
    summary: str
    task_id: str | None = None
    task_key: str | None = None
    worker_id: str | None = None
    state: str | None = None
    detail: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, payload: object) -> RuntimeEventView:
        mapping = _require_mapping(payload, label="runtime event")
        return cls(
            event_id=_require_string(mapping, "event_id", label="runtime.event_id"),
            created_at=_require_string(mapping, "created_at", label="runtime.created_at"),
            kind=_require_string(mapping, "kind", label="runtime.kind"),
            source=_require_string(mapping, "source", label="runtime.source"),
            summary=_require_string(mapping, "summary", label="runtime.summary"),
            task_id=_optional_string(mapping, "task_id"),
            task_key=_optional_string(mapping, "task_key"),
            worker_id=_optional_string(mapping, "worker_id"),
            state=_optional_string(mapping, "state"),
            detail=_optional_object_dict(mapping.get("detail")),
        )


@dataclass(frozen=True)
class RuntimeObservability:
    last_progress_at: str | None = None
    latest_kind: str | None = None
    latest_summary: str | None = None
    failure_summary: str | None = None
    messages: list[RuntimeMessageView] = field(default_factory=list)
    deliveries: list[RuntimeDeliveryView] = field(default_factory=list)
    events: list[RuntimeEventView] = field(default_factory=list)

    @classmethod
    def from_wire(cls, payload: object) -> RuntimeObservability:
        mapping = _require_mapping(payload, label="runtime observability")
        return cls(
            last_progress_at=_optional_string(mapping, "last_progress_at"),
            latest_kind=_optional_string(mapping, "latest_kind"),
            latest_summary=_optional_string(mapping, "latest_summary"),
            failure_summary=_optional_string(mapping, "failure_summary"),
            messages=[
                RuntimeMessageView.from_wire(item)
                for item in _optional_dict_list(mapping.get("messages"), label="runtime.messages")
            ],
            deliveries=[
                RuntimeDeliveryView.from_wire(item)
                for item in _optional_dict_list(mapping.get("deliveries"), label="runtime.deliveries")
            ],
            events=[
                RuntimeEventView.from_wire(item)
                for item in _optional_dict_list(mapping.get("events"), label="runtime.events")
            ],
        )


@dataclass(frozen=True)
class RunAnomaly:
    kind: RunAnomalyKind
    detail: str

    @classmethod
    def from_wire(cls, payload: object) -> RunAnomaly:
        mapping = _require_mapping(payload, label="run anomaly")
        return cls(
            kind=RunAnomalyKind(_require_string(mapping, "kind", label="anomaly.kind")),
            detail=_require_string(mapping, "detail", label="anomaly.detail"),
        )


@dataclass(frozen=True)
class RunObservabilitySnapshot:
    schema_version: str
    project_id: str
    run_id: str
    generated_at: str
    run: ManagedResearchRun
    lifecycle: RunLifecycleView
    run_state: ManagedResearchRunState
    terminal_outcome: ManagedResearchRunTerminalOutcome | None
    live_phase: ManagedResearchRunLivePhase
    state_reason: str | None
    state_authority: str
    work_completed: bool
    completion_classifier: str | None
    candidate_publication: CandidatePublicationView
    actors: ActorCollectionSnapshot
    tasks: TaskCollectionSnapshot
    runtime: RuntimeObservability
    recent_project_events: list[dict[str, object]] = field(default_factory=list)
    latest_event_seq: int | None = None
    open_questions: list[dict[str, object]] = field(default_factory=list)
    anomalies: list[RunAnomaly] = field(default_factory=list)
    cursor: RunObservationCursor = field(default_factory=RunObservationCursor)

    @classmethod
    def from_wire(cls, payload: object) -> RunObservabilitySnapshot:
        mapping = _require_mapping(payload, label="run observability snapshot")
        return cls(
            schema_version=_require_string(mapping, "schema_version", label="snapshot.schema_version"),
            project_id=_require_string(mapping, "project_id", label="snapshot.project_id"),
            run_id=_require_string(mapping, "run_id", label="snapshot.run_id"),
            generated_at=_require_string(mapping, "generated_at", label="snapshot.generated_at"),
            run=ManagedResearchRun.from_wire(mapping.get("run")),
            lifecycle=RunLifecycleView.from_wire(mapping.get("lifecycle")),
            run_state=ManagedResearchRunState(
                _require_string(mapping, "run_state", label="snapshot.run_state")
            ),
            terminal_outcome=(
                ManagedResearchRunTerminalOutcome(
                    _require_string(
                        mapping,
                        "terminal_outcome",
                        label="snapshot.terminal_outcome",
                    )
                )
                if _optional_string(mapping, "terminal_outcome") is not None
                else None
            ),
            live_phase=ManagedResearchRunLivePhase(
                _optional_string(mapping, "live_phase") or "unknown"
            ),
            state_reason=_optional_string(mapping, "state_reason"),
            state_authority=(
                _optional_string(mapping, "state_authority")
                or "backend_public_run_state_projection.v1"
            ),
            work_completed=bool(_optional_bool(mapping, "work_completed")),
            completion_classifier=_optional_string(mapping, "completion_classifier"),
            candidate_publication=CandidatePublicationView.from_wire(mapping.get("candidate_publication")),
            actors=ActorCollectionSnapshot.from_wire(mapping.get("actors")),
            tasks=TaskCollectionSnapshot.from_wire(mapping.get("tasks")),
            runtime=RuntimeObservability.from_wire(mapping.get("runtime")),
            recent_project_events=_optional_dict_list(
                mapping.get("recent_project_events"),
                label="snapshot.recent_project_events",
            ),
            latest_event_seq=_optional_int(mapping, "latest_event_seq"),
            open_questions=_optional_dict_list(
                mapping.get("open_questions"),
                label="snapshot.open_questions",
            ),
            anomalies=[
                RunAnomaly.from_wire(item)
                for item in _optional_dict_list(mapping.get("anomalies"), label="snapshot.anomalies")
            ],
            cursor=RunObservationCursor.from_wire(mapping.get("cursor")),
        )


__all__ = [
    "ActorCollectionSnapshot",
    "ActorSnapshot",
    "CandidatePublicationOutcome",
    "CandidatePublicationView",
    "ManagedResearchRun",
    "ManagedResearchRunLivePhase",
    "ManagedResearchRunState",
    "ManagedResearchRunTerminalOutcome",
    "RunAnomaly",
    "RunAnomalyKind",
    "RunLifecycleDispatch",
    "RunLifecycleFailure",
    "RunLifecycleLocalExecution",
    "RunLifecycleView",
    "RunObservationCursor",
    "RunObservabilitySnapshot",
    "RuntimeDeliveryView",
    "RuntimeEventView",
    "RuntimeMessageView",
    "RuntimeObservability",
    "TaskCollectionSnapshot",
    "TaskSnapshot",
]
