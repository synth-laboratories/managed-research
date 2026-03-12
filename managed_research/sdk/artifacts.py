"""Artifact-scoped SDK namespace."""

from __future__ import annotations

from managed_research.sdk._base import _ClientNamespace


class ArtifactsAPI(_ClientNamespace):
    def list_run_artifacts(self, run_id: str, *, project_id: str | None = None) -> list[dict]:
        return self._client.list_run_artifacts(run_id, project_id=project_id)

    def list_run_artifacts_typed(
        self, run_id: str, *, project_id: str | None = None
    ) -> list[dict]:
        return self._client.list_run_artifacts_typed(run_id, project_id=project_id)

    def get(self, artifact_id: str) -> dict:
        return self._client.get_artifact(artifact_id)

    def get_content_bytes(
        self,
        artifact_id: str,
        *,
        disposition: str = "inline",
        follow_redirects: bool = True,
    ) -> bytes:
        return self._client.get_artifact_content_bytes(
            artifact_id,
            disposition=disposition,
            follow_redirects=follow_redirects,
        )

    def list_run_pull_requests(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        return self._client.list_run_pull_requests(run_id, project_id=project_id, limit=limit)

    def get_project_git_status(self, project_id: str) -> dict:
        return self._client.get_project_git_status(project_id)


__all__ = ["ArtifactsAPI"]
