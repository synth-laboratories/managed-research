"""Project-scoped SDK namespace."""

from __future__ import annotations

from typing import Any

from managed_research.sdk._base import _ClientNamespace


class ProjectsAPI(_ClientNamespace):
    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._client.create_project(payload)

    def list(
        self,
        *,
        include_archived: bool = False,
        created_after: str | None = None,
        created_before: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_projects(
            include_archived=include_archived,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            cursor=cursor,
        )

    def list_typed(
        self,
        *,
        include_archived: bool = False,
        created_after: str | None = None,
        created_before: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_projects_typed(
            include_archived=include_archived,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            cursor=cursor,
        )

    def get(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project(project_id)

    def get_typed(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_typed(project_id)

    def get_status(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_status(project_id)

    def get_status_snapshot(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_status_snapshot(project_id)

    def get_binding(self, project_id: str, *, run_id: str | None = None) -> dict[str, Any]:
        return self._client.get_binding(project_id, run_id=run_id)

    def promote_binding(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.promote_binding(project_id, **kwargs)

    def get_pool_context(
        self,
        project_id: str,
        *,
        run_id: str | None = None,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        return self._client.get_pool_context(project_id, run_id=run_id, task_id=task_id)

    def get_repos(self, project_id: str) -> list[dict[str, Any]]:
        return self._client.get_project_repos(project_id)

    def pause(self, project_id: str) -> dict[str, Any]:
        return self._client.pause_project(project_id)

    def resume(self, project_id: str) -> dict[str, Any]:
        return self._client.resume_project(project_id)

    def archive(self, project_id: str) -> dict[str, Any]:
        return self._client.archive_project(project_id)

    def unarchive(self, project_id: str) -> dict[str, Any]:
        return self._client.unarchive_project(project_id)


__all__ = ["ProjectsAPI"]
