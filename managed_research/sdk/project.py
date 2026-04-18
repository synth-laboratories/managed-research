"""Bound project handle for the flatter noun-first SDK surface."""

from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _guess_content_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


@dataclass
class _BoundProjectReposAPI:
    _client: Any
    project_id: str

    def list(self) -> list[dict[str, Any]]:
        return self._client.list_project_repo_bindings(self.project_id)

    def attach(
        self,
        *,
        github_repo: str,
        pr_write_enabled: bool = False,
    ) -> dict[str, Any]:
        return self._client.attach_project_repo(
            self.project_id,
            repo=github_repo,
            pr_write_enabled=pr_write_enabled,
        )

    def detach(self, *, github_repo: str) -> dict[str, Any]:
        return self._client.detach_project_repo(self.project_id, repo=github_repo)


@dataclass
class _BoundProjectFilesAPI:
    _client: Any
    project_id: str

    def list(
        self,
        *,
        visibility: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return self._client.list_project_files(
            self.project_id,
            visibility=visibility,
            limit=limit,
        )

    def upload(
        self,
        path: str | Path,
        *,
        name: str | None = None,
        visibility: str = "model",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        file_path = Path(path)
        raw_bytes = file_path.read_bytes()
        payload = {
            "path": name or file_path.name,
            "content": base64.b64encode(raw_bytes).decode("ascii"),
            "content_type": _guess_content_type(file_path),
            "encoding": "base64",
            "visibility": visibility,
            "metadata": dict(metadata or {}),
        }
        return self._client.create_project_files(self.project_id, [payload])

    def content(self, file_id: str) -> dict[str, Any]:
        return self._client.get_project_file_content(self.project_id, file_id)


@dataclass
class _BoundProjectDatasetsAPI:
    _client: Any
    project_id: str

    def list(self) -> list[dict[str, Any]]:
        return self._client.list_project_datasets(self.project_id)

    def upload(
        self,
        path: str | Path,
        *,
        name: str | None = None,
        format: str | None = None,
        row_count: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        file_path = Path(path)
        raw_bytes = file_path.read_bytes()
        return self._client.upload_project_dataset(
            self.project_id,
            {
                "name": name or file_path.name,
                "content": base64.b64encode(raw_bytes).decode("ascii"),
                "encoding": "base64",
                "content_type": _guess_content_type(file_path),
                "format": format,
                "row_count": row_count,
                "metadata": dict(metadata or {}),
            },
        )

    def download(
        self,
        dataset_id: str,
        *,
        to: str | Path | None = None,
    ) -> dict[str, Any]:
        payload = self._client.download_project_dataset(self.project_id, dataset_id)
        destination = Path(to) if to is not None else None
        if destination is not None:
            if payload.get("encoding") == "base64":
                destination.write_bytes(base64.b64decode(str(payload["content"])))
            else:
                destination.write_text(str(payload["content"]), encoding="utf-8")
        return payload


@dataclass
class _BoundProjectOutputsAPI:
    _client: Any
    project_id: str

    def list(self) -> list[dict[str, Any]]:
        return self._client.list_project_outputs(self.project_id)


@dataclass
class _BoundProjectPrsAPI:
    _client: Any
    project_id: str

    def list(self) -> list[dict[str, Any]]:
        return self._client.list_project_prs(self.project_id)

    def get(self, pr_id: str) -> dict[str, Any]:
        return self._client.get_project_pr(self.project_id, pr_id)


@dataclass
class _BoundProjectModelsAPI:
    _client: Any
    project_id: str

    def list(self) -> list[dict[str, Any]]:
        return self._client.list_project_models(self.project_id)

    def get(self, model_id: str) -> dict[str, Any]:
        return self._client.get_project_model(self.project_id, model_id)

    def download(
        self,
        model_id: str,
        *,
        to: str | Path | None = None,
    ) -> dict[str, Any]:
        payload = self._client.download_project_model(self.project_id, model_id)
        destination = Path(to) if to is not None else None
        if destination is not None:
            if payload.get("encoding") == "base64":
                destination.write_bytes(base64.b64decode(str(payload["content"])))
            else:
                destination.write_text(str(payload["content"]), encoding="utf-8")
        return payload

    def export(self, model_id: str) -> dict[str, Any]:
        return self._client.export_project_model(self.project_id, model_id)


@dataclass
class ManagedResearchProjectClient:
    _client: Any
    project_id: str
    _repos_api: _BoundProjectReposAPI | None = field(init=False, default=None, repr=False)
    _files_api: _BoundProjectFilesAPI | None = field(init=False, default=None, repr=False)
    _datasets_api: _BoundProjectDatasetsAPI | None = field(
        init=False,
        default=None,
        repr=False,
    )
    _outputs_api: _BoundProjectOutputsAPI | None = field(
        init=False,
        default=None,
        repr=False,
    )
    _prs_api: _BoundProjectPrsAPI | None = field(init=False, default=None, repr=False)
    _models_api: _BoundProjectModelsAPI | None = field(
        init=False,
        default=None,
        repr=False,
    )

    @property
    def repos(self) -> _BoundProjectReposAPI:
        if self._repos_api is None:
            self._repos_api = _BoundProjectReposAPI(self._client, self.project_id)
        return self._repos_api

    @property
    def files(self) -> _BoundProjectFilesAPI:
        if self._files_api is None:
            self._files_api = _BoundProjectFilesAPI(self._client, self.project_id)
        return self._files_api

    @property
    def datasets(self) -> _BoundProjectDatasetsAPI:
        if self._datasets_api is None:
            self._datasets_api = _BoundProjectDatasetsAPI(self._client, self.project_id)
        return self._datasets_api

    @property
    def outputs(self) -> _BoundProjectOutputsAPI:
        if self._outputs_api is None:
            self._outputs_api = _BoundProjectOutputsAPI(self._client, self.project_id)
        return self._outputs_api

    @property
    def prs(self) -> _BoundProjectPrsAPI:
        if self._prs_api is None:
            self._prs_api = _BoundProjectPrsAPI(self._client, self.project_id)
        return self._prs_api

    @property
    def models(self) -> _BoundProjectModelsAPI:
        if self._models_api is None:
            self._models_api = _BoundProjectModelsAPI(self._client, self.project_id)
        return self._models_api

    def readiness(self) -> dict[str, Any]:
        return self._client.get_project_readiness(self.project_id)


__all__ = ["ManagedResearchProjectClient"]
