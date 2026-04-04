"""Progress-oriented SDK namespace."""

from __future__ import annotations

from typing import Any

from managed_research.sdk._base import _ClientNamespace


class ProgressAPI(_ClientNamespace):
    def get_project_readiness(self, project_id: str) -> dict[str, Any]:
        return self._client.get_project_readiness(project_id)

    def get_run_progress(self, project_id: str, run_id: str) -> dict[str, Any]:
        return self._client.get_run_progress(project_id, run_id)


__all__ = ["ProgressAPI"]
