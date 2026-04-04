"""Usage-oriented SDK namespace."""

from __future__ import annotations

from managed_research.errors import SmrApiError
from managed_research.models import UsageAnalyticsPayload, UsageAnalyticsSubject
from managed_research.sdk._base import _ClientNamespace

_USAGE_ANALYTICS_QUERY = """
query UsageAnalytics(
  $subject: UsageAnalyticsSubjectInput!,
  $window: UsageAnalyticsWindowInput!,
  $pagination: UsageAnalyticsPaginationInput!
) {
  usageAnalytics(subject: $subject, window: $window, pagination: $pagination) {
    subject
    window
    totals
    buckets
    rows
    pageInfo
  }
}
""".strip()


class UsageAPI(_ClientNamespace):
    """Usage analytics helpers for the remigration surface."""

    def subject_for_org(self, org_id: str) -> UsageAnalyticsSubject:
        return UsageAnalyticsSubject.for_org(str(org_id))

    def subject_for_managed_account(
        self, managed_account_id: str
    ) -> UsageAnalyticsSubject:
        return UsageAnalyticsSubject.for_managed_account(str(managed_account_id))

    def get_usage_analytics(
        self,
        subject: UsageAnalyticsSubject,
        *,
        start_at: str,
        end_at: str,
        bucket: str,
        first: int,
        after: str | None = None,
    ) -> UsageAnalyticsPayload:
        envelope = self._client._request_json(
            "POST",
            "/managed-accounts/graphql",
            json_body={
                "query": _USAGE_ANALYTICS_QUERY,
                "operationName": "UsageAnalytics",
                "variables": {
                    "subject": subject.to_wire(),
                    "window": {
                        "startAt": str(start_at).strip(),
                        "endAt": str(end_at).strip(),
                        "bucket": str(bucket).strip().upper(),
                    },
                    "pagination": {
                        "first": int(first),
                        "after": after,
                    },
                },
            },
        )
        if not isinstance(envelope, dict):
            raise SmrApiError("Expected object response for get_usage_analytics")
        errors = envelope.get("errors")
        if isinstance(errors, list) and errors:
            first_error = errors[0]
            if isinstance(first_error, dict):
                message_value = first_error.get("message")
                if not isinstance(message_value, str) or not message_value.strip():
                    raise SmrApiError(
                        "Usage analytics GraphQL error payload is missing a message"
                    )
                message = message_value.strip()
            else:
                raise SmrApiError(
                    "Usage analytics GraphQL error payload is malformed"
                )
            raise SmrApiError(message)
        data = envelope.get("data")
        if not isinstance(data, dict):
            raise SmrApiError("Usage analytics response missing GraphQL data payload")
        payload = data.get("usageAnalytics")
        if not isinstance(payload, dict):
            raise SmrApiError("Usage analytics response missing usageAnalytics payload")
        return UsageAnalyticsPayload.from_wire(payload)

__all__ = ["UsageAPI"]
