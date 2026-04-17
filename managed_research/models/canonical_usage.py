"""Canonical SMR usage and entitlement models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from managed_research.models.types import (
    _float_value,
    _int_value,
    _object_dict,
    _optional_array,
    _optional_string,
    _require_mapping,
    _require_string,
)


def _optional_int_value(mapping: dict[str, object], key: str) -> int | None:
    if mapping.get(key) is None:
        return None
    return _int_value(mapping, key)


def _optional_float_value(mapping: dict[str, object], key: str) -> float | None:
    if mapping.get(key) is None:
        return None
    return _float_value(mapping, key)


def _optional_object_dict(payload: object) -> dict[str, object]:
    if payload is None:
        return {}
    return _object_dict(payload)


@dataclass(frozen=True)
class BillingEntitlementProfile:
    code: str
    display_name: str
    source_product_ids: list[str]
    source_product_names: list[str]
    is_paid: bool

    @classmethod
    def from_wire(cls, payload: object) -> BillingEntitlementProfile:
        mapping = _require_mapping(payload, label="billing entitlement profile")
        return cls(
            code=_require_string(mapping, "code", label="billing entitlement profile.code"),
            display_name=_require_string(
                mapping,
                "display_name",
                label="billing entitlement profile.display_name",
            ),
            source_product_ids=[
                str(item).strip()
                for item in _optional_array(mapping, "source_product_ids")
                if str(item).strip()
            ],
            source_product_names=[
                str(item).strip()
                for item in _optional_array(mapping, "source_product_names")
                if str(item).strip()
            ],
            is_paid=bool(mapping.get("is_paid")),
        )


@dataclass(frozen=True)
class BillingEntitlementAsset:
    asset_id: str
    display_name: str
    kind: str
    included: bool
    enabled: bool
    source_feature_id: str | None
    balance_cents: int | None
    used_cents: int | None
    limit_cents: int | None
    remaining_cents: int | None
    limit_value: float | None
    used_value: float | None
    remaining_value: float | None
    quantity_unit: str | None
    next_reset_at: str | None

    @classmethod
    def from_wire(cls, payload: object) -> BillingEntitlementAsset:
        mapping = _require_mapping(payload, label="billing entitlement asset")
        return cls(
            asset_id=_require_string(mapping, "asset_id", label="billing entitlement asset.asset_id"),
            display_name=_require_string(
                mapping,
                "display_name",
                label="billing entitlement asset.display_name",
            ),
            kind=_require_string(mapping, "kind", label="billing entitlement asset.kind"),
            included=bool(mapping.get("included")),
            enabled=bool(mapping.get("enabled")),
            source_feature_id=_optional_string(mapping, "source_feature_id"),
            balance_cents=_optional_int_value(mapping, "balance_cents"),
            used_cents=_optional_int_value(mapping, "used_cents"),
            limit_cents=_optional_int_value(mapping, "limit_cents"),
            remaining_cents=_optional_int_value(mapping, "remaining_cents"),
            limit_value=_optional_float_value(mapping, "limit_value"),
            used_value=_optional_float_value(mapping, "used_value"),
            remaining_value=_optional_float_value(mapping, "remaining_value"),
            quantity_unit=_optional_string(mapping, "quantity_unit"),
            next_reset_at=_optional_string(mapping, "next_reset_at"),
        )


@dataclass(frozen=True)
class BillingEntitlementSnapshot:
    org_id: str
    provider: str
    profile: BillingEntitlementProfile
    assets: list[BillingEntitlementAsset]
    fetched_at: str

    @classmethod
    def from_wire(cls, payload: object) -> BillingEntitlementSnapshot:
        mapping = _require_mapping(payload, label="billing entitlement snapshot")
        return cls(
            org_id=_require_string(mapping, "org_id", label="billing entitlement snapshot.org_id"),
            provider=_require_string(mapping, "provider", label="billing entitlement snapshot.provider"),
            profile=BillingEntitlementProfile.from_wire(mapping.get("profile")),
            assets=[
                BillingEntitlementAsset.from_wire(item)
                for item in _optional_array(mapping, "assets")
            ],
            fetched_at=_require_string(
                mapping,
                "fetched_at",
                label="billing entitlement snapshot.fetched_at",
            ),
        )


@dataclass(frozen=True)
class SmrRunCostTotals:
    total_cents: int
    charged_cents: int
    internal_cost_cents: int

    @classmethod
    def from_wire(cls, payload: object) -> SmrRunCostTotals:
        mapping = _require_mapping(payload, label="run cost totals")
        return cls(
            total_cents=_int_value(mapping, "total_cents"),
            charged_cents=_int_value(mapping, "charged_cents"),
            internal_cost_cents=_int_value(mapping, "internal_cost_cents"),
        )


@dataclass(frozen=True)
class SmrRunUsage:
    run_id: str
    project_id: str
    cost: SmrRunCostTotals
    totals: dict[str, int]
    tokens: dict[str, object]
    breakdown: dict[str, object]
    entries: list[dict[str, object]]
    rows: list[dict[str, object]]

    @classmethod
    def from_wire(cls, payload: object) -> SmrRunUsage:
        mapping = _require_mapping(payload, label="run usage")
        totals_mapping = _object_dict(mapping.get("totals"))
        return cls(
            run_id=_require_string(mapping, "run_id", label="run usage.run_id"),
            project_id=_require_string(mapping, "project_id", label="run usage.project_id"),
            cost=SmrRunCostTotals.from_wire(mapping.get("cost")),
            totals={str(key): int(value) for key, value in totals_mapping.items()},
            tokens=_optional_object_dict(mapping.get("tokens")),
            breakdown=_optional_object_dict(mapping.get("breakdown")),
            entries=[
                _object_dict(item)
                for item in _optional_array(mapping, "entries")
            ],
            rows=[
                _object_dict(item)
                for item in _optional_array(mapping, "rows")
            ],
        )


@dataclass(frozen=True)
class SmrProjectUsage:
    project_id: str
    month_to_date: dict[str, object]
    last_7_days: dict[str, object]
    per_run: list[dict[str, object]]
    budgets: dict[str, object]

    @classmethod
    def from_wire(cls, payload: object) -> SmrProjectUsage:
        mapping = _require_mapping(payload, label="project usage")
        return cls(
            project_id=_require_string(mapping, "project_id", label="project usage.project_id"),
            month_to_date=_optional_object_dict(mapping.get("month_to_date")),
            last_7_days=_optional_object_dict(mapping.get("last_7_days")),
            per_run=[
                _object_dict(item)
                for item in _optional_array(mapping, "per_run")
            ],
            budgets=_optional_object_dict(mapping.get("budgets")),
        )


@dataclass(frozen=True)
class SmrProjectEntitlementOverlay:
    resolved_lane: str
    free_mode_enabled: bool
    free_tier_eligible: bool

    @classmethod
    def from_wire(cls, payload: object) -> SmrProjectEntitlementOverlay:
        mapping = _require_mapping(payload, label="project entitlement overlay")
        return cls(
            resolved_lane=_require_string(
                mapping,
                "resolved_lane",
                label="project entitlement overlay.resolved_lane",
            ),
            free_mode_enabled=bool(mapping.get("free_mode_enabled")),
            free_tier_eligible=bool(mapping.get("free_tier_eligible")),
        )


@dataclass(frozen=True)
class SmrProjectEconomics:
    project_id: str
    usage: SmrProjectUsage
    entitlements: BillingEntitlementSnapshot
    project_overlay: SmrProjectEntitlementOverlay
    budgets: dict[str, object]

    @classmethod
    def from_wire(cls, payload: object) -> SmrProjectEconomics:
        mapping = _require_mapping(payload, label="project economics")
        return cls(
            project_id=_require_string(
                mapping,
                "project_id",
                label="project economics.project_id",
            ),
            usage=SmrProjectUsage.from_wire(mapping.get("usage")),
            entitlements=BillingEntitlementSnapshot.from_wire(
                mapping.get("entitlements")
            ),
            project_overlay=SmrProjectEntitlementOverlay.from_wire(
                mapping.get("project_overlay")
            ),
            budgets=_optional_object_dict(mapping.get("budgets")),
        )


__all__ = [
    "BillingEntitlementAsset",
    "BillingEntitlementProfile",
    "BillingEntitlementSnapshot",
    "SmrProjectEconomics",
    "SmrProjectEntitlementOverlay",
    "SmrProjectUsage",
    "SmrRunCostTotals",
    "SmrRunUsage",
]
