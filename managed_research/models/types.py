"""Public models for the remigration surface."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum


def _require_mapping(payload: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        raise ValueError(f"{label} must be an object")
    return payload


def _optional_string(
    payload: Mapping[str, object],
    key: str,
) -> str | None:
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


def _float_value(payload: Mapping[str, object], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be numeric")
    return float(value)


def _int_value(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _object_dict(payload: object) -> dict[str, object]:
    mapping = _require_mapping(payload, label="metadata")
    return dict(mapping)


def _optional_object_dict(payload: object) -> dict[str, object]:
    if payload is None:
        return {}
    return _object_dict(payload)


def _require_array(payload: Mapping[str, object], key: str, *, label: str) -> list[object]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def _optional_array(payload: Mapping[str, object], key: str) -> list[object]:
    value = payload.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{key} must be an array when provided")
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


@dataclass(frozen=True)
class RecommendedAction:
    tool_name: str | None = None
    arguments: dict[str, object] = field(default_factory=dict)
    description: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> RecommendedAction:
        mapping = _require_mapping(payload, label="recommended action")
        return cls(
            tool_name=_optional_string(mapping, "tool_name"),
            arguments=_optional_object_dict(mapping.get("arguments")),
            description=_optional_string(mapping, "description"),
        )


@dataclass(frozen=True)
class WorkspaceSourceRepo:
    kind: str | None = None
    url: str | None = None
    display_url: str | None = None
    default_branch: str | None = None
    public: bool | None = None
    auth_mode: str | None = None
    bootstrap_mode: str | None = None
    remote_name: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> WorkspaceSourceRepo | None:
        if payload is None:
            return None
        mapping = _require_mapping(payload, label="workspace source repo")
        return cls(
            kind=_optional_string(mapping, "kind"),
            url=_optional_string(mapping, "url"),
            display_url=_optional_string(mapping, "display_url"),
            default_branch=_optional_string(mapping, "default_branch"),
            public=_optional_bool(mapping, "public"),
            auth_mode=_optional_string(mapping, "auth_mode"),
            bootstrap_mode=_optional_string(mapping, "bootstrap_mode"),
            remote_name=_optional_string(mapping, "remote_name"),
        )


@dataclass(frozen=True)
class WorkspaceFileInput:
    path: str | None = None
    content: str | None = None
    content_type: str | None = None
    encoding: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> WorkspaceFileInput:
        mapping = _require_mapping(payload, label="workspace file input")
        return cls(
            path=_optional_string(mapping, "path"),
            content=_optional_string(mapping, "content"),
            content_type=_optional_string(mapping, "content_type"),
            encoding=_optional_string(mapping, "encoding"),
        )


@dataclass(frozen=True)
class WorkspaceInputsState:
    project_id: str | None = None
    state: str | None = None
    source_repo: WorkspaceSourceRepo | None = None
    files: list[WorkspaceFileInput] = field(default_factory=list)
    file_count: int | None = None
    project_repo: dict[str, object] = field(default_factory=dict)
    updated_at: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> WorkspaceInputsState:
        mapping = _require_mapping(payload, label="workspace inputs state")
        files_payload = _optional_array(mapping, "files")
        return cls(
            project_id=_optional_string(mapping, "project_id"),
            state=_optional_string(mapping, "state"),
            source_repo=WorkspaceSourceRepo.from_wire(mapping.get("source_repo")),
            files=[WorkspaceFileInput.from_wire(item) for item in files_payload],
            file_count=_optional_int(mapping, "file_count"),
            project_repo=_optional_object_dict(mapping.get("project_repo")),
            updated_at=_optional_string(mapping, "updated_at"),
        )


@dataclass(frozen=True)
class WorkspaceUploadResult:
    project_id: str | None = None
    file_count: int | None = None
    bytes_uploaded: int | None = None
    uploaded_files: list[WorkspaceFileInput] = field(default_factory=list)

    @classmethod
    def from_wire(cls, payload: object) -> WorkspaceUploadResult:
        mapping = _require_mapping(payload, label="workspace upload result")
        uploaded_files_payload = _optional_array(mapping, "uploaded_files")
        return cls(
            project_id=_optional_string(mapping, "project_id"),
            file_count=_optional_int(mapping, "file_count"),
            bytes_uploaded=_optional_int(mapping, "bytes_uploaded"),
            uploaded_files=[
                WorkspaceFileInput.from_wire(item) for item in uploaded_files_payload
            ],
        )


@dataclass(frozen=True)
class ProviderKeyStatus:
    ok: bool | None = None
    project_id: str | None = None
    provider: str | None = None
    funding_source: str | None = None
    configured: bool | None = None
    required: bool | None = None
    auth_mechanism: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> ProviderKeyStatus:
        mapping = _require_mapping(payload, label="provider key status")
        return cls(
            ok=_optional_bool(mapping, "ok"),
            project_id=_optional_string(mapping, "project_id"),
            provider=_optional_string(mapping, "provider"),
            funding_source=_optional_string(mapping, "funding_source"),
            configured=_optional_bool(mapping, "configured"),
            required=_optional_bool(mapping, "required"),
            auth_mechanism=_optional_string(mapping, "auth_mechanism"),
        )


@dataclass(frozen=True)
class ProjectReadiness:
    project_id: str | None = None
    state: str | None = None
    blockers: list[str] = field(default_factory=list)
    recommended_actions: list[RecommendedAction] = field(default_factory=list)
    entitlement: dict[str, object] = field(default_factory=dict)
    capabilities: dict[str, object] = field(default_factory=dict)
    workspace_inputs: WorkspaceInputsState | None = None
    provider_key_status: ProviderKeyStatus | None = None
    repo_status: dict[str, object] = field(default_factory=dict)
    run_target: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, payload: object) -> ProjectReadiness:
        mapping = _require_mapping(payload, label="project readiness")
        blockers_payload = _optional_array(mapping, "blockers")
        recommended_actions_payload = _optional_array(mapping, "recommended_actions")
        return cls(
            project_id=_optional_string(mapping, "project_id"),
            state=_optional_string(mapping, "state"),
            blockers=[str(item) for item in blockers_payload if isinstance(item, str)],
            recommended_actions=[
                RecommendedAction.from_wire(item) for item in recommended_actions_payload
            ],
            entitlement=_optional_object_dict(mapping.get("entitlement")),
            capabilities=_optional_object_dict(mapping.get("capabilities")),
            workspace_inputs=(
                WorkspaceInputsState.from_wire(mapping.get("workspace_inputs"))
                if mapping.get("workspace_inputs") is not None
                else None
            ),
            provider_key_status=(
                ProviderKeyStatus.from_wire(mapping.get("provider_key_status"))
                if mapping.get("provider_key_status") is not None
                else None
            ),
            repo_status=_optional_object_dict(mapping.get("repo_status")),
            run_target=_optional_object_dict(mapping.get("run_target")),
        )


@dataclass(frozen=True)
class RunProgress:
    state: str | None = None
    phase: str | None = None
    stalled_reason: str | None = None
    last_progress_at: str | None = None
    blocked_task_count: int | None = None
    pending_approval_ids: list[str] = field(default_factory=list)
    pending_question_ids: list[str] = field(default_factory=list)
    recent_artifact_ids: list[str] = field(default_factory=list)
    recent_event_summary: list[dict[str, object]] = field(default_factory=list)
    recommended_actions: list[RecommendedAction] = field(default_factory=list)

    @classmethod
    def from_wire(cls, payload: object) -> RunProgress:
        mapping = _require_mapping(payload, label="run progress")
        recommended_actions_payload = _optional_array(mapping, "recommended_actions")
        pending_approval_ids = _optional_array(mapping, "pending_approval_ids")
        pending_question_ids = _optional_array(mapping, "pending_question_ids")
        recent_artifact_ids = _optional_array(mapping, "recent_artifact_ids")
        recent_event_summary = _optional_array(mapping, "recent_event_summary")
        return cls(
            state=_optional_string(mapping, "state"),
            phase=_optional_string(mapping, "phase"),
            stalled_reason=_optional_string(mapping, "stalled_reason"),
            last_progress_at=_optional_string(mapping, "last_progress_at"),
            blocked_task_count=_optional_int(mapping, "blocked_task_count"),
            pending_approval_ids=[
                str(item) for item in pending_approval_ids if isinstance(item, str)
            ],
            pending_question_ids=[
                str(item) for item in pending_question_ids if isinstance(item, str)
            ],
            recent_artifact_ids=[
                str(item) for item in recent_artifact_ids if isinstance(item, str)
            ],
            recent_event_summary=[
                _object_dict(item) for item in recent_event_summary if isinstance(item, Mapping)
            ],
            recommended_actions=[
                RecommendedAction.from_wire(item) for item in recommended_actions_payload
            ],
        )


class UsageAnalyticsSubjectKind(StrEnum):
    ORG = "org"
    MANAGED_ACCOUNT = "managed_account"


@dataclass(frozen=True)
class UsageAnalyticsSubject:
    kind: UsageAnalyticsSubjectKind
    org_id: str | None = None
    managed_account_id: str | None = None

    @classmethod
    def for_org(cls, org_id: str) -> UsageAnalyticsSubject:
        normalized = org_id.strip()
        if not normalized:
            raise ValueError("org_id is required")
        return cls(kind=UsageAnalyticsSubjectKind.ORG, org_id=normalized)

    @classmethod
    def for_managed_account(
        cls, managed_account_id: str
    ) -> UsageAnalyticsSubject:
        normalized = managed_account_id.strip()
        if not normalized:
            raise ValueError("managed_account_id is required")
        return cls(
            kind=UsageAnalyticsSubjectKind.MANAGED_ACCOUNT,
            managed_account_id=normalized,
        )

    @classmethod
    def from_wire(cls, payload: object) -> UsageAnalyticsSubject:
        mapping = _require_mapping(payload, label="usage analytics subject")
        kind_value = _optional_string(mapping, "kind")
        if kind_value is None:
            raise ValueError("usage analytics subject.kind is required")
        try:
            kind = UsageAnalyticsSubjectKind(kind_value)
        except ValueError as exc:
            raise ValueError(
                "usage analytics subject.kind must be 'org' or 'managed_account'"
            ) from exc
        org_id = _optional_string(mapping, "orgId")
        managed_account_id = _optional_string(mapping, "managedAccountId")
        if kind is UsageAnalyticsSubjectKind.ORG and (
            org_id is None or managed_account_id is not None
        ):
            raise ValueError(
                "usage analytics org subject requires orgId and forbids managedAccountId"
            )
        if kind is UsageAnalyticsSubjectKind.MANAGED_ACCOUNT and (
            managed_account_id is None or org_id is not None
        ):
            raise ValueError(
                "usage analytics managed_account subject requires managedAccountId and forbids orgId"
            )
        return cls(
            kind=kind,
            org_id=org_id,
            managed_account_id=managed_account_id,
        )

    def to_wire(self) -> dict[str, str]:
        payload = {"kind": self.kind.value}
        if self.org_id is not None:
            payload["orgId"] = self.org_id
        if self.managed_account_id is not None:
            payload["managedAccountId"] = self.managed_account_id
        return payload


@dataclass(frozen=True)
class UsageAnalyticsWindow:
    start_at: str
    end_at: str
    bucket: str
    resolved_bucket: str | None = None

    @classmethod
    def from_wire(cls, payload: object) -> UsageAnalyticsWindow:
        mapping = _require_mapping(payload, label="usage analytics window")
        return cls(
            start_at=_require_string(
                mapping, "startAt", label="usage analytics window.startAt"
            ),
            end_at=_require_string(
                mapping, "endAt", label="usage analytics window.endAt"
            ),
            bucket=_require_string(
                mapping, "bucket", label="usage analytics window.bucket"
            ),
            resolved_bucket=_optional_string(mapping, "resolvedBucket"),
        )


@dataclass(frozen=True)
class UsageAnalyticsBreakdown:
    gross_usage_usd: float
    billed_amount_usd: float
    internal_cost_usd: float
    event_count: int

    @classmethod
    def from_wire(cls, payload: object) -> UsageAnalyticsBreakdown:
        mapping = _require_mapping(payload, label="usage analytics breakdown")
        return cls(
            gross_usage_usd=_float_value(mapping, "grossUsageUsd"),
            billed_amount_usd=_float_value(mapping, "billedAmountUsd"),
            internal_cost_usd=_float_value(mapping, "internalCostUsd"),
            event_count=_int_value(mapping, "eventCount"),
        )


@dataclass(frozen=True)
class UsageAnalyticsTotals:
    gross_usage_usd: float
    billed_amount_usd: float
    internal_cost_usd: float
    event_count: int
    charged_event_count: int
    by_billing_route: dict[str, UsageAnalyticsBreakdown]
    by_usage_type: dict[str, UsageAnalyticsBreakdown]

    @classmethod
    def from_wire(cls, payload: object) -> UsageAnalyticsTotals:
        mapping = _require_mapping(payload, label="usage analytics totals")
        billing_route_payload = _require_mapping(
            mapping.get("byBillingRoute"),
            label="usage analytics totals.byBillingRoute",
        )
        usage_type_payload = _require_mapping(
            mapping.get("byUsageType"),
            label="usage analytics totals.byUsageType",
        )
        return cls(
            gross_usage_usd=_float_value(mapping, "grossUsageUsd"),
            billed_amount_usd=_float_value(mapping, "billedAmountUsd"),
            internal_cost_usd=_float_value(mapping, "internalCostUsd"),
            event_count=_int_value(mapping, "eventCount"),
            charged_event_count=_int_value(mapping, "chargedEventCount"),
            by_billing_route={
                str(key): UsageAnalyticsBreakdown.from_wire(value)
                for key, value in billing_route_payload.items()
            },
            by_usage_type={
                str(key): UsageAnalyticsBreakdown.from_wire(value)
                for key, value in usage_type_payload.items()
            },
        )


@dataclass(frozen=True)
class UsageAnalyticsBucket:
    bucket_start: str
    bucket_end: str
    gross_usage_usd: float
    billed_amount_usd: float
    internal_cost_usd: float
    event_count: int

    @classmethod
    def from_wire(cls, payload: object) -> UsageAnalyticsBucket:
        mapping = _require_mapping(payload, label="usage analytics bucket")
        return cls(
            bucket_start=_require_string(
                mapping, "bucketStart", label="usage analytics bucket.bucketStart"
            ),
            bucket_end=_require_string(
                mapping, "bucketEnd", label="usage analytics bucket.bucketEnd"
            ),
            gross_usage_usd=_float_value(mapping, "grossUsageUsd"),
            billed_amount_usd=_float_value(mapping, "billedAmountUsd"),
            internal_cost_usd=_float_value(mapping, "internalCostUsd"),
            event_count=_int_value(mapping, "eventCount"),
        )


@dataclass(frozen=True)
class UsageAnalyticsRow:
    event_id: str
    occurred_at: str
    usage_type: str
    provider: str
    model: str | None
    run_id: str | None
    project_id: str | None
    actor_id: str | None
    billing_route: str
    charged: bool
    gross_usage_usd: float
    billed_amount_usd: float
    internal_cost_usd: float
    quantity: float | None
    quantity_unit: str | None
    metadata: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, payload: object) -> UsageAnalyticsRow:
        mapping = _require_mapping(payload, label="usage analytics row")
        event_id = _require_string(
            mapping, "eventId", label="usage analytics row.eventId"
        )
        occurred_at = _require_string(
            mapping, "occurredAt", label="usage analytics row.occurredAt"
        )
        usage_type = _require_string(
            mapping, "usageType", label="usage analytics row.usageType"
        )
        provider = _require_string(
            mapping, "provider", label="usage analytics row.provider"
        )
        billing_route = _require_string(
            mapping, "billingRoute", label="usage analytics row.billingRoute"
        )
        charged = mapping.get("charged")
        if not isinstance(charged, bool):
            raise ValueError("usage analytics row.charged must be a boolean")
        quantity_value = mapping.get("quantity")
        if quantity_value is None:
            quantity = None
        elif isinstance(quantity_value, bool) or not isinstance(
            quantity_value, (int, float)
        ):
            raise ValueError("usage analytics row.quantity must be numeric when provided")
        else:
            quantity = float(quantity_value)
        return cls(
            event_id=event_id,
            occurred_at=occurred_at,
            usage_type=usage_type,
            provider=provider,
            model=_optional_string(mapping, "model"),
            run_id=_optional_string(mapping, "runId"),
            project_id=_optional_string(mapping, "projectId"),
            actor_id=_optional_string(mapping, "actorId"),
            billing_route=billing_route,
            charged=charged,
            gross_usage_usd=_float_value(mapping, "grossUsageUsd"),
            billed_amount_usd=_float_value(mapping, "billedAmountUsd"),
            internal_cost_usd=_float_value(mapping, "internalCostUsd"),
            quantity=quantity,
            quantity_unit=_optional_string(mapping, "quantityUnit"),
            metadata=_object_dict(mapping.get("metadata")),
        )


@dataclass(frozen=True)
class UsageAnalyticsPageInfo:
    has_next_page: bool
    end_cursor: str | None

    @classmethod
    def from_wire(cls, payload: object) -> UsageAnalyticsPageInfo:
        mapping = _require_mapping(payload, label="usage analytics page info")
        has_next_page = mapping.get("hasNextPage")
        if not isinstance(has_next_page, bool):
            raise ValueError("usage analytics pageInfo.hasNextPage must be a boolean")
        return cls(
            has_next_page=has_next_page,
            end_cursor=_optional_string(mapping, "endCursor"),
        )


@dataclass(frozen=True)
class UsageAnalyticsPayload:
    subject: UsageAnalyticsSubject
    window: UsageAnalyticsWindow
    totals: UsageAnalyticsTotals
    buckets: list[UsageAnalyticsBucket]
    rows: list[UsageAnalyticsRow]
    page_info: UsageAnalyticsPageInfo

    @classmethod
    def from_wire(cls, payload: object) -> UsageAnalyticsPayload:
        mapping = _require_mapping(payload, label="usage analytics payload")
        buckets_payload = _require_array(
            mapping, "buckets", label="usage analytics payload.buckets"
        )
        rows_payload = _require_array(
            mapping, "rows", label="usage analytics payload.rows"
        )
        return cls(
            subject=UsageAnalyticsSubject.from_wire(mapping.get("subject")),
            window=UsageAnalyticsWindow.from_wire(mapping.get("window")),
            totals=UsageAnalyticsTotals.from_wire(mapping.get("totals")),
            buckets=[
                UsageAnalyticsBucket.from_wire(bucket_payload)
                for bucket_payload in buckets_payload
            ],
            rows=[UsageAnalyticsRow.from_wire(row_payload) for row_payload in rows_payload],
            page_info=UsageAnalyticsPageInfo.from_wire(mapping.get("pageInfo")),
        )


__all__ = [
    "ProjectReadiness",
    "ProviderKeyStatus",
    "RecommendedAction",
    "RunProgress",
    "UsageAnalyticsBreakdown",
    "UsageAnalyticsBucket",
    "UsageAnalyticsPageInfo",
    "UsageAnalyticsPayload",
    "UsageAnalyticsRow",
    "UsageAnalyticsSubject",
    "UsageAnalyticsTotals",
    "UsageAnalyticsWindow",
    "WorkspaceFileInput",
    "WorkspaceInputsState",
    "WorkspaceSourceRepo",
    "WorkspaceUploadResult",
]
