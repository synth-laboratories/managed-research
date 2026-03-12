"""Log search/query SDK namespace."""

from __future__ import annotations

from managed_research.sdk._base import _ClientNamespace


class LogsAPI(_ClientNamespace):
    def get_run_logs(
        self,
        project_id: str,
        run_id: str,
        *,
        task_key: str | None = None,
        component: str | None = None,
        limit: int = 200,
        start: str | None = None,
        end: str | None = None,
    ) -> list[dict]:
        return self._client.get_run_logs(
            project_id,
            run_id,
            task_key=task_key,
            component=component,
            limit=limit,
            start=start,
            end=end,
        )

    def search_project_logs(
        self,
        project_id: str,
        *,
        q: str | None = None,
        run_id: str | None = None,
        service: str | None = None,
        limit: int = 200,
        start: str | None = None,
        end: str | None = None,
    ) -> list[dict]:
        return self._client.search_project_logs(
            project_id,
            q=q,
            run_id=run_id,
            service=service,
            limit=limit,
            start=start,
            end=end,
        )


__all__ = ["LogsAPI"]
