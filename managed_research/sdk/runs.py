"""Run-scoped SDK namespace."""

from __future__ import annotations

from typing import Any

from managed_research.models.types import RunProgress
from managed_research.sdk._base import _ClientNamespace


class RunsAPI(_ClientNamespace):
    def trigger(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.trigger_run(project_id, **kwargs)

    def list(self, project_id: str, *, active_only: bool = False, **kwargs: Any) -> list[dict[str, Any]]:
        return self._client.list_runs(project_id, active_only=active_only, **kwargs)

    def list_active(self, project_id: str) -> list[dict[str, Any]]:
        return self._client.list_active_runs(project_id)

    def get(self, run_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        return self._client.get_run(run_id, project_id=project_id)

    def get_progress(self, project_id: str, run_id: str) -> RunProgress:
        return RunProgress.from_wire(self._client.get_run_progress(project_id, run_id))

    def list_questions(self, run_id: str, *, project_id: str | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        return self._client.list_run_questions(run_id, project_id=project_id, **kwargs)

    def create_checkpoint(self, run_id: str, *, project_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return self._client.create_run_checkpoint(run_id, project_id=project_id, **kwargs)

    def list_checkpoints(self, run_id: str, *, project_id: str | None = None) -> list[dict[str, Any]]:
        return self._client.list_run_checkpoints(run_id, project_id=project_id)

    def restore_checkpoint(self, run_id: str, *, project_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
        return self._client.restore_run_checkpoint(run_id, project_id=project_id, **kwargs)


__all__ = ["RunsAPI"]
