"""Project-scoped SDK namespace."""

from __future__ import annotations

from typing import Any

from managed_research.sdk._base import _ClientNamespace


class ProjectsAPI(_ClientNamespace):
    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._client.create_project(payload)

    def list(self, *, include_archived: bool = False, limit: int = 100) -> list[dict[str, Any]]:
        return self._client.list_projects(include_archived=include_archived, limit=limit)

    def get(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project(project_id)

    def patch(self, project_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._client.patch_project(project_id, payload)

    def get_status(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_status(project_id)

    def get_status_snapshot(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_status_snapshot(project_id)

    def get_entitlement(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_entitlement(project_id)

    def get_capabilities(self) -> dict[str, Any]:
        return self._client.get_capabilities()

    def get_limits(self) -> dict[str, Any]:
        return self._client.get_limits()


__all__ = ["ProjectsAPI"]
