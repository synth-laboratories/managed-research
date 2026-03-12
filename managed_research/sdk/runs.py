"""Run-scoped SDK namespace."""

from __future__ import annotations

from typing import Any

from managed_research.sdk._base import _ClientNamespace


class RunsAPI(_ClientNamespace):
    def trigger(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.trigger_run(project_id, **kwargs)

    def trigger_data_factory(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.trigger_data_factory_run(project_id, **kwargs)

    def data_factory_finalize(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.data_factory_finalize(project_id, **kwargs)

    def data_factory_finalize_status(self, project_id: str, job_id: str) -> dict[str, Any]:
        return self._client.data_factory_finalize_status(project_id, job_id)

    def data_factory_publish(self, project_id: str, job_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.data_factory_publish(project_id, job_id, **kwargs)

    def list(self, project_id: str) -> list[dict[str, Any]]:
        return self._client.list_runs(project_id)

    def list_typed(self, project_id: str) -> list[dict[str, Any]]:
        return self._client.list_runs_typed(project_id)

    def list_jobs(
        self,
        *,
        project_id: str | None = None,
        state: str | None = None,
        active_only: bool = False,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self._client.list_jobs(
            project_id=project_id,
            state=state,
            active_only=active_only,
            limit=limit,
        )

    def get(self, run_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        return self._client.get_run(run_id, project_id=project_id)

    def get_usage(self, run_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        return self._client.get_run_usage(run_id, project_id=project_id)

    def get_actor_status(
        self, project_id: str, *, run_id: str | None = None
    ) -> dict[str, Any]:
        return self._client.get_actor_status(project_id, run_id=run_id)

    def control_actor(self, project_id: str, *, run_id: str, actor_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.control_actor(project_id, run_id=run_id, actor_id=actor_id, **kwargs)

    def pause(self, run_id: str) -> dict[str, Any]:
        return self._client.pause_run(run_id)

    def resume(self, run_id: str) -> dict[str, Any]:
        return self._client.resume_run(run_id)

    def stop(self, run_id: str) -> dict[str, Any]:
        return self._client.stop_run(run_id)

    def get_results(self, project_id: str, run_id: str) -> dict[str, Any]:
        return self._client.get_run_results(project_id, run_id)

    def get_orchestrator_status(self, project_id: str, run_id: str) -> dict[str, Any]:
        return self._client.get_run_orchestrator_status(project_id, run_id)


__all__ = ["RunsAPI"]
