"""Usage-oriented SDK namespace."""

from __future__ import annotations

from collections.abc import Mapping

from managed_research.errors import SmrApiError
from managed_research.models import (
    BillingEntitlementSnapshot,
    SmrProjectEconomics,
    SmrProjectUsage,
    SmrRunUsage,
)
from managed_research.sdk._base import _ClientNamespace


def _raise_on_error_payload(payload: object) -> object:
    if not isinstance(payload, Mapping):
        return payload
    errors = payload.get("errors")
    if not isinstance(errors, list) or not errors:
        return payload
    first = errors[0]
    if isinstance(first, Mapping):
        message = first.get("message")
        if isinstance(message, str) and message.strip():
            raise SmrApiError(message.strip())
    raise SmrApiError("Managed Research usage request failed")


class UsageAPI(_ClientNamespace):
    """Canonical usage and entitlement helpers."""

    def get_billing_entitlements(self) -> BillingEntitlementSnapshot:
        return BillingEntitlementSnapshot.from_wire(
            _raise_on_error_payload(self._client._request_json("GET", "/billing/entitlements"))
        )

    def get_run_usage(self, run_id: str) -> SmrRunUsage:
        return SmrRunUsage.from_wire(
            _raise_on_error_payload(
                self._client._request_json("GET", f"/smr/runs/{run_id}/usage")
            )
        )

    def get_project_usage(self, project_id: str) -> SmrProjectUsage:
        return SmrProjectUsage.from_wire(
            _raise_on_error_payload(
                self._client._request_json("GET", f"/smr/projects/{project_id}/usage")
            )
        )

    def get_project_economics(self, project_id: str) -> SmrProjectEconomics:
        return SmrProjectEconomics.from_wire(
            _raise_on_error_payload(
                self._client._request_json("GET", f"/smr/projects/{project_id}/economics")
            )
        )

__all__ = ["UsageAPI"]
