"""Project repo namespace for the flatter noun-first SDK surface."""

from __future__ import annotations

from typing import Any

from managed_research.sdk._base import _ClientNamespace


class ReposAPI(_ClientNamespace):
    def list(self, project_id: str) -> list[dict[str, Any]]:
        return self._client.list_project_repo_bindings(project_id)

    def attach(
        self,
        project_id: str,
        *,
        github_repo: str,
        pr_write_enabled: bool = False,
    ) -> dict[str, Any]:
        return self._client.attach_project_repo(
            project_id,
            repo=github_repo,
            pr_write_enabled=pr_write_enabled,
        )

    def detach(self, project_id: str, *, github_repo: str) -> dict[str, Any]:
        return self._client.detach_project_repo(project_id, repo=github_repo)


__all__ = ["ReposAPI"]
