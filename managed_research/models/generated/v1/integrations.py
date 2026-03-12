"""Public integration models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from managed_research.models.generated.v1.common import _list_of_dicts, _optional_str


@dataclass(frozen=True)
class SmrIntegrationStatus:
    provider: str | None
    status: str | None
    connected: bool | None
    project_id: str | None
    org_id: str | None
    authorize_url: str | None
    external_account_hint: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrIntegrationStatus:
        connected_raw = payload.get("connected")
        connected = bool(connected_raw) if connected_raw is not None else None
        return cls(
            provider=_optional_str(payload, "provider"),
            status=_optional_str(payload, "status"),
            connected=connected,
            project_id=_optional_str(payload, "project_id"),
            org_id=_optional_str(payload, "org_id"),
            authorize_url=_optional_str(payload, "authorize_url"),
            external_account_hint=_optional_str(payload, "external_account_hint"),
            raw=dict(payload),
        )


@dataclass(frozen=True)
class SmrOAuthStart:
    authorize_url: str | None
    instructions: str | None
    state: str | None
    expires_at: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrOAuthStart:
        return cls(
            authorize_url=_optional_str(payload, "authorize_url"),
            instructions=_optional_str(payload, "instructions"),
            state=_optional_str(payload, "state"),
            expires_at=_optional_str(payload, "expires_at"),
            raw=dict(payload),
        )


@dataclass(frozen=True)
class SmrLinearTeam:
    team_id: str | None
    key: str | None
    name: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrLinearTeam:
        return cls(
            team_id=_optional_str(payload, "id") or _optional_str(payload, "team_id"),
            key=_optional_str(payload, "key"),
            name=_optional_str(payload, "name"),
            raw=dict(payload),
        )


@dataclass(frozen=True)
class SmrLinearTeamListing:
    teams: list[SmrLinearTeam]
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_payload(cls, payload: dict[str, Any] | list[dict[str, Any]]) -> SmrLinearTeamListing:
        if isinstance(payload, dict):
            team_rows = payload.get("teams")
            if not isinstance(team_rows, list):
                team_rows = payload.get("items")
            raw = dict(payload)
        else:
            team_rows = payload
            raw = {"teams": payload}
        rows = _list_of_dicts(team_rows)
        return cls(
            teams=[SmrLinearTeam.from_dict(row) for row in rows],
            raw=raw,
        )


@dataclass(frozen=True)
class SmrProviderKeyStatus:
    project_id: str | None
    provider: str | None
    funding_source: str | None
    configured: bool | None
    status: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SmrProviderKeyStatus:
        configured_raw = payload.get("configured")
        configured = bool(configured_raw) if configured_raw is not None else None
        return cls(
            project_id=_optional_str(payload, "project_id"),
            provider=_optional_str(payload, "provider"),
            funding_source=_optional_str(payload, "funding_source"),
            configured=configured,
            status=_optional_str(payload, "status"),
            raw=dict(payload),
        )


__all__ = [
    "SmrIntegrationStatus",
    "SmrLinearTeam",
    "SmrLinearTeamListing",
    "SmrOAuthStart",
    "SmrProviderKeyStatus",
]
