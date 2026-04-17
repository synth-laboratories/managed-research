"""Usage-oriented SDK namespace."""

from __future__ import annotations

from managed_research.models import (
    BillingEntitlementSnapshot,
    SmrProjectEconomics,
    SmrProjectUsage,
    SmrRunUsage,
)
from managed_research.sdk._base import _ClientNamespace


class UsageAPI(_ClientNamespace):
    """Canonical usage and entitlement helpers."""

    def get_billing_entitlements(self) -> BillingEntitlementSnapshot:
        return BillingEntitlementSnapshot.from_wire(
            self._client._request_json("GET", "/billing/entitlements")
        )

    def get_run_usage(self, run_id: str) -> SmrRunUsage:
        return SmrRunUsage.from_wire(
            self._client._request_json("GET", f"/smr/runs/{run_id}/usage")
        )

    def get_project_usage(self, project_id: str) -> SmrProjectUsage:
        return SmrProjectUsage.from_wire(
            self._client._request_json("GET", f"/smr/projects/{project_id}/usage")
        )

    def get_project_economics(self, project_id: str) -> SmrProjectEconomics:
        return SmrProjectEconomics.from_wire(
            self._client._request_json("GET", f"/smr/projects/{project_id}/economics")
        )

__all__ = ["UsageAPI"]
