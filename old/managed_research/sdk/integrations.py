"""Integration and credential SDK namespace."""

from __future__ import annotations

from typing import Any

from managed_research.models import (
    SmrIntegrationStatus,
    SmrLinearTeamListing,
    SmrOAuthStart,
    SmrProviderKeyStatus,
)
from managed_research.sdk._base import _ClientNamespace


class IntegrationsAPI(_ClientNamespace):
    def link_org_github(self, project_id: str) -> dict[str, Any]:
        return self._client.link_org_github(project_id)

    def github_org_status(self) -> dict[str, Any]:
        return self._client.github_org_status()

    def github_org_status_typed(self) -> SmrIntegrationStatus:
        return self._client.github_org_status_typed()

    def github_org_oauth_start(self, *, redirect_uri: str | None = None) -> dict[str, Any]:
        return self._client.github_org_oauth_start(redirect_uri=redirect_uri)

    def github_org_oauth_start_typed(self, *, redirect_uri: str | None = None) -> SmrOAuthStart:
        return self._client.github_org_oauth_start_typed(redirect_uri=redirect_uri)

    def github_org_oauth_callback(self, **kwargs: Any) -> dict[str, Any]:
        return self._client.github_org_oauth_callback(**kwargs)

    def github_org_disconnect(self) -> dict[str, Any]:
        return self._client.github_org_disconnect()

    def linear_oauth_start(
        self, *, project_id: str, redirect_uri: str | None = None
    ) -> dict[str, Any]:
        return self._client.linear_oauth_start(project_id=project_id, redirect_uri=redirect_uri)

    def linear_oauth_callback(self, **kwargs: Any) -> dict[str, Any]:
        return self._client.linear_oauth_callback(**kwargs)

    def linear_status(self, project_id: str) -> dict[str, Any]:
        return self._client.linear_status(project_id)

    def linear_status_typed(self, project_id: str) -> SmrIntegrationStatus:
        return self._client.linear_status_typed(project_id)

    def linear_disconnect(self, project_id: str) -> dict[str, Any]:
        return self._client.linear_disconnect(project_id)

    def linear_list_teams(self, project_id: str) -> dict[str, Any]:
        return self._client.linear_list_teams(project_id)

    def linear_list_teams_typed(self, project_id: str) -> SmrLinearTeamListing:
        return self._client.linear_list_teams_typed(project_id)

    def set_provider_key(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.set_provider_key(project_id, **kwargs)

    def provider_key_status(self, project_id: str, provider: str, funding_source: str) -> dict[str, Any]:
        return self._client.provider_key_status(project_id, provider, funding_source)

    def provider_key_status_typed(
        self,
        project_id: str,
        provider: str,
        funding_source: str,
    ) -> SmrProviderKeyStatus:
        return self._client.provider_key_status_typed(project_id, provider, funding_source)

    def chatgpt_connection_status(self, *, project_id: str | None = None) -> dict[str, Any]:
        return self._client.chatgpt_connection_status(project_id=project_id)

    def chatgpt_connection_status_typed(
        self, *, project_id: str | None = None
    ) -> SmrIntegrationStatus:
        return self._client.chatgpt_connection_status_typed(project_id=project_id)

    def chatgpt_connect_start(self, **kwargs: Any) -> dict[str, Any]:
        return self._client.chatgpt_connect_start(**kwargs)

    def chatgpt_connect_complete(self, **kwargs: Any) -> dict[str, Any]:
        return self._client.chatgpt_connect_complete(**kwargs)

    def chatgpt_disconnect(self) -> dict[str, Any]:
        return self._client.chatgpt_disconnect()


__all__ = ["IntegrationsAPI"]
