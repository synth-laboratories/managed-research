"""Workspace-input SDK namespace."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from os import PathLike
from typing import Any

from managed_research.sdk._base import _ClientNamespace


class WorkspaceInputsAPI(_ClientNamespace):
    def attach_source_repo(
        self,
        project_id: str,
        url: str,
        *,
        default_branch: str | None = None,
    ) -> dict[str, Any]:
        return self._client.attach_source_repo(project_id, url, default_branch=default_branch)

    def get(self, project_id: str) -> dict[str, Any]:
        return self._client.get_workspace_inputs(project_id)

    def upload_files(self, project_id: str, files: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
        return self._client.upload_workspace_files(project_id, files)

    def upload_directory(self, project_id: str, directory: str | PathLike[str]) -> dict[str, Any]:
        return self._client.upload_workspace_directory(project_id, directory)


__all__ = ["WorkspaceInputsAPI"]
