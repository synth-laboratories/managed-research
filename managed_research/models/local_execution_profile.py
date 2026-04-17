"""Typed local execution profile and publication readiness models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any, Mapping


LOCAL_EXECUTION_PROFILE_SCHEMA_VERSION = "2026-04-14-local-execution-profile-v2"


def _required_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{key} is required")
    return normalized


def _optional_string(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string when provided")
    normalized = value.strip()
    return normalized or None


def _capabilities(payload: Mapping[str, Any]) -> dict[str, bool]:
    raw = payload.get("capabilities")
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ValueError("capabilities must be an object")
    return {
        str(key).strip(): bool(value)
        for key, value in raw.items()
        if str(key).strip()
    }


@dataclass(frozen=True)
class LocalExecutionProfile:
    schema_version: str
    profile_id: str
    product: str
    host_kind: str
    docker_image: str | None
    daytona_snapshot: str | None
    required_runtime_kind: str
    required_repo: str
    local_source_kind: str
    capabilities: dict[str, bool]

    @classmethod
    def from_wire(cls, payload: Mapping[str, Any]) -> "LocalExecutionProfile":
        profile = cls(
            schema_version=_required_string(payload, "schema_version"),
            profile_id=_required_string(payload, "profile_id"),
            product=_required_string(payload, "product"),
            host_kind=_required_string(payload, "host_kind"),
            docker_image=_optional_string(payload, "docker_image"),
            daytona_snapshot=_optional_string(payload, "daytona_snapshot"),
            required_runtime_kind=_required_string(payload, "required_runtime_kind"),
            required_repo=_required_string(payload, "required_repo"),
            local_source_kind=_required_string(payload, "local_source_kind"),
            capabilities=_capabilities(payload),
        )
        profile.validate()
        return profile

    def validate(self) -> None:
        if self.schema_version != LOCAL_EXECUTION_PROFILE_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported local execution profile schema_version: {self.schema_version}"
            )
        host_kind = self.host_kind.strip().lower()
        if host_kind not in {"docker", "daytona"}:
            raise ValueError(f"unsupported host_kind: {self.host_kind}")
        if host_kind == "docker" and not self.docker_image:
            raise ValueError(f"profile {self.profile_id} requires docker_image")
        if host_kind == "daytona" and not self.daytona_snapshot:
            raise ValueError(f"profile {self.profile_id} requires daytona_snapshot")
        if self.local_source_kind not in {"slot_git_mirror", "external_repo"}:
            raise ValueError(
                f"unsupported local_source_kind: {self.local_source_kind}"
            )

    def to_wire(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "profile_id": self.profile_id,
            "product": self.product,
            "host_kind": self.host_kind,
            "docker_image": self.docker_image,
            "daytona_snapshot": self.daytona_snapshot,
            "required_runtime_kind": self.required_runtime_kind,
            "required_repo": self.required_repo,
            "local_source_kind": self.local_source_kind,
            "capabilities": dict(self.capabilities),
        }

    def to_request_wire(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "profile_id": self.profile_id,
            "product": self.product,
            "host_kind": self.host_kind,
            "docker_image": self.docker_image,
            "daytona_snapshot": self.daytona_snapshot,
            "required_runtime_kind": self.required_runtime_kind,
            "required_repo": self.required_repo,
            "local_source_kind": self.local_source_kind,
            "capabilities": dict(self.capabilities),
        }


@dataclass(frozen=True)
class LocalPublicationReadiness:
    ready: bool
    status: str
    repo: str | None
    credential_name: str | None
    writable_repo_binding_present: bool
    project_connected: bool

    @classmethod
    def from_wire(cls, payload: Mapping[str, Any]) -> "LocalPublicationReadiness":
        return cls(
            ready=bool(payload.get("ready")),
            status=_required_string(payload, "status"),
            repo=_optional_string(payload, "repo"),
            credential_name=_optional_string(payload, "credential_name"),
            writable_repo_binding_present=bool(
                payload.get("writable_repo_binding_present")
            ),
            project_connected=bool(payload.get("project_connected")),
        )


def load_local_execution_profiles(path: Path) -> list[LocalExecutionProfile]:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise ValueError(f"missing local execution profile manifest: {resolved}")
    payload = tomllib.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"invalid local execution profile manifest: {resolved}")
    schema_version = _required_string(payload, "schema_version")
    raw_profiles = payload.get("profiles")
    if not isinstance(raw_profiles, list):
        raise ValueError("local execution profile manifest must contain [[profiles]]")
    profiles: list[LocalExecutionProfile] = []
    for item in raw_profiles:
        if not isinstance(item, Mapping):
            raise ValueError("local execution profile entries must be objects")
        normalized = dict(item)
        normalized.setdefault("schema_version", schema_version)
        profiles.append(LocalExecutionProfile.from_wire(normalized))
    if not profiles:
        raise ValueError(f"local execution profile manifest has no profiles: {resolved}")
    return profiles


def load_local_execution_profile(path: Path, *, profile_id: str) -> LocalExecutionProfile:
    requested = str(profile_id or "").strip()
    if not requested:
        raise ValueError("profile_id is required")
    for profile in load_local_execution_profiles(path):
        if profile.profile_id == requested:
            return profile
    raise ValueError(
        f"missing local execution profile {requested!r} in manifest {path.expanduser().resolve()}"
    )
