"""Typed WorkProduct records returned by the Managed Research SDK."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


def _as_dict(value: Mapping[str, object] | None) -> dict[str, object]:
    return dict(value or {})


@dataclass(frozen=True)
class ManagedResearchWorkProductArtifactLink:
    work_product_artifact_id: str
    work_product_id: str
    artifact_id: str
    role: str
    label: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(
        cls,
        payload: Mapping[str, object],
    ) -> ManagedResearchWorkProductArtifactLink:
        return cls(
            work_product_artifact_id=str(payload["work_product_artifact_id"]),
            work_product_id=str(payload["work_product_id"]),
            artifact_id=str(payload["artifact_id"]),
            role=str(payload["role"]),
            label=str(payload["label"]) if payload.get("label") else None,
            metadata=_as_dict(payload.get("metadata")),  # type: ignore[arg-type]
        )


@dataclass(frozen=True)
class ManagedResearchRunWorkProduct:
    work_product_id: str
    org_id: str
    project_id: str
    run_id: str
    kind: str
    title: str
    status: str
    readiness: str
    summary: str | None = None
    subtype_kind: str | None = None
    subtype_id: str | None = None
    artifact_id: str | None = None
    artifact_links: list[ManagedResearchWorkProductArtifactLink] = field(
        default_factory=list
    )
    content_url: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)
    blocker: dict[str, object] | None = None
    latest_export_id: str | None = None

    @classmethod
    def from_wire(cls, payload: Mapping[str, object]) -> ManagedResearchRunWorkProduct:
        return cls(
            work_product_id=str(payload["work_product_id"]),
            org_id=str(payload["org_id"]),
            project_id=str(payload["project_id"]),
            run_id=str(payload["run_id"]),
            kind=str(payload["kind"]),
            title=str(payload["title"]),
            status=str(payload["status"]),
            readiness=str(payload["readiness"]),
            summary=str(payload["summary"]) if payload.get("summary") else None,
            subtype_kind=str(payload["subtype_kind"])
            if payload.get("subtype_kind")
            else None,
            subtype_id=str(payload["subtype_id"]) if payload.get("subtype_id") else None,
            artifact_id=str(payload["artifact_id"]) if payload.get("artifact_id") else None,
            artifact_links=[
                ManagedResearchWorkProductArtifactLink.from_wire(item)
                for item in payload.get("artifact_links", [])
                if isinstance(item, Mapping)
            ],
            content_url=str(payload["content_url"])
            if payload.get("content_url")
            else None,
            metadata=_as_dict(payload.get("metadata")),  # type: ignore[arg-type]
            blocker=_as_dict(payload.get("blocker")) if payload.get("blocker") else None,  # type: ignore[arg-type]
            latest_export_id=str(payload["latest_export_id"])
            if payload.get("latest_export_id")
            else None,
        )


@dataclass(frozen=True)
class ManagedResearchTrainedModel:
    model_id: str
    work_product_id: str | None
    project_id: str
    run_id: str
    base_model: str
    method: str
    tinker_path: str | None
    status: str
    metrics: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, payload: Mapping[str, object]) -> ManagedResearchTrainedModel:
        metrics = {
            "base_metric": payload.get("base_metric"),
            "tuned_metric": payload.get("tuned_metric"),
            "uplift_abs": payload.get("uplift_abs"),
            "train_cost_usd": payload.get("train_cost_usd"),
        }
        return cls(
            model_id=str(payload["model_id"]),
            work_product_id=str(payload["work_product_id"])
            if payload.get("work_product_id")
            else None,
            project_id=str(payload["project_id"]),
            run_id=str(payload["run_id"]),
            base_model=str(payload["base_model"]),
            method=str(payload["method"]),
            tinker_path=str(payload["tinker_path"])
            if payload.get("tinker_path")
            else None,
            status=str(payload["status"]),
            metrics=metrics,
        )


@dataclass(frozen=True)
class ManagedResearchContainerEvalPackage:
    package_id: str
    work_product_id: str | None
    project_id: str
    run_id: str
    kind: str
    name: str
    status: str
    validation_status: str
    version: str | None = None
    manifest: dict[str, object] = field(default_factory=dict)
    validation: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_wire(
        cls,
        payload: Mapping[str, object],
    ) -> ManagedResearchContainerEvalPackage:
        return cls(
            package_id=str(payload["package_id"]),
            work_product_id=str(payload["work_product_id"])
            if payload.get("work_product_id")
            else None,
            project_id=str(payload["project_id"]),
            run_id=str(payload["run_id"]),
            kind=str(payload["kind"]),
            name=str(payload["name"]),
            status=str(payload["status"]),
            validation_status=str(payload["validation_status"]),
            version=str(payload["version"]) if payload.get("version") else None,
            manifest=_as_dict(payload.get("manifest")),  # type: ignore[arg-type]
            validation=_as_dict(payload.get("validation")),  # type: ignore[arg-type]
        )


@dataclass(frozen=True)
class ManagedResearchWorkProductExport:
    export_id: str
    work_product_id: str
    project_id: str
    run_id: str
    destination_kind: str
    destination_summary: dict[str, object]
    idempotency_key: str
    status: str
    error: dict[str, object] | None = None

    @classmethod
    def from_wire(
        cls,
        payload: Mapping[str, object],
    ) -> ManagedResearchWorkProductExport:
        return cls(
            export_id=str(payload["export_id"]),
            work_product_id=str(payload["work_product_id"]),
            project_id=str(payload["project_id"]),
            run_id=str(payload["run_id"]),
            destination_kind=str(payload["destination_kind"]),
            destination_summary=_as_dict(payload.get("destination_summary")),  # type: ignore[arg-type]
            idempotency_key=str(payload["idempotency_key"]),
            status=str(payload["status"]),
            error=_as_dict(payload.get("error")) if payload.get("error") else None,  # type: ignore[arg-type]
        )


__all__ = [
    "ManagedResearchContainerEvalPackage",
    "ManagedResearchRunWorkProduct",
    "ManagedResearchTrainedModel",
    "ManagedResearchWorkProductArtifactLink",
    "ManagedResearchWorkProductExport",
]
