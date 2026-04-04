"""Rewritten SMR control-plane client focused on the remigration surface."""

from __future__ import annotations

import base64
import mimetypes
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from managed_research.auth import BACKEND_URL_BASE, get_api_key, normalize_backend_base
from managed_research.errors import SmrApiError
from managed_research.models import UsageAnalyticsPayload, UsageAnalyticsSubject
from managed_research.sdk.approvals import ApprovalsAPI
from managed_research.sdk.artifacts import ArtifactsAPI
from managed_research.sdk.integrations import IntegrationsAPI
from managed_research.sdk.logs import LogsAPI
from managed_research.sdk.progress import ProgressAPI
from managed_research.sdk.projects import ProjectsAPI
from managed_research.sdk.runs import RunsAPI
from managed_research.sdk.usage import UsageAPI
from managed_research.sdk.workspace_inputs import WorkspaceInputsAPI
from managed_research.transport.http import SmrHttpTransport
from managed_research.transport.pagination import build_query_params

ACTIVE_RUN_STATES = {"queued", "planning", "executing", "blocked", "finalizing", "running"}
DEFAULT_TIMEOUT_SECONDS = 30.0

__all__ = [
    "ACTIVE_RUN_STATES",
    "DEFAULT_TIMEOUT_SECONDS",
    "ManagedResearchClient",
    "SmrControlClient",
    "first_id",
]


def _resolve_backend_base(backend_base: str | None) -> str:
    candidate = str(backend_base or os.getenv("SYNTH_BACKEND_URL") or BACKEND_URL_BASE).strip()
    if not candidate:
        candidate = "https://api.usesynth.ai"
    return normalize_backend_base(candidate).rstrip("/")


def _resolve_api_key(api_key: str | None) -> str:
    if api_key and api_key.strip():
        return api_key.strip()
    resolved = get_api_key("SYNTH_API_KEY", required=True)
    if not resolved:
        raise ValueError("api_key is required (provide api_key or set SYNTH_API_KEY)")
    return resolved


def _auth_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def _coerce_dict(payload: Any, *, label: str) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    raise SmrApiError(f"Expected object response for {label}, received {type(payload).__name__}")


def _coerce_list(payload: Any, *, label: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in (
            "items",
            "data",
            "results",
            "projects",
            "runs",
            "questions",
            "artifacts",
            "approvals",
            "uploaded_files",
        ):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                return [item for item in candidate if isinstance(item, dict)]
    raise SmrApiError(f"Expected list response for {label}, received {type(payload).__name__}")


def _guess_content_type(path: str) -> str:
    guessed, _ = mimetypes.guess_type(path)
    return guessed or "application/octet-stream"


def _normalize_uploaded_file(entry: Mapping[str, Any]) -> dict[str, Any]:
    path = str(entry.get("path") or "").strip()
    if not path:
        raise ValueError("workspace file entries require a non-empty path")
    content = entry.get("content")
    content_path = entry.get("content_path")
    encoding = str(entry.get("encoding") or "").strip().lower() or None
    if content_path is not None:
        file_path = Path(str(content_path))
        raw_bytes = file_path.read_bytes()
        try:
            content = raw_bytes.decode("utf-8")
            encoding = encoding or "utf-8"
        except UnicodeDecodeError:
            content = base64.b64encode(raw_bytes).decode("ascii")
            encoding = encoding or "base64"
    if content is None:
        raise ValueError("workspace file entries require either content or content_path")
    if isinstance(content, bytes):
        content = base64.b64encode(content).decode("ascii")
        encoding = encoding or "base64"
    if not isinstance(content, str):
        raise ValueError("workspace file content must be text or bytes")
    return {
        "path": path,
        "content": content,
        "content_type": str(entry.get("content_type") or _guess_content_type(path)).strip(),
        "encoding": encoding or "utf-8",
    }


@dataclass
class SmrControlClient:
    """Public SMR control-plane client for the remigration surface."""

    api_key: str | None = None
    backend_base: str | None = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    _transport: SmrHttpTransport = field(init=False, repr=False)
    _projects_api: ProjectsAPI | None = field(init=False, default=None, repr=False)
    _runs_api: RunsAPI | None = field(init=False, default=None, repr=False)
    _workspace_inputs_api: WorkspaceInputsAPI | None = field(init=False, default=None, repr=False)
    _progress_api: ProgressAPI | None = field(init=False, default=None, repr=False)
    _approvals_api: ApprovalsAPI | None = field(init=False, default=None, repr=False)
    _artifacts_api: ArtifactsAPI | None = field(init=False, default=None, repr=False)
    _logs_api: LogsAPI | None = field(init=False, default=None, repr=False)
    _integrations_api: IntegrationsAPI | None = field(init=False, default=None, repr=False)
    _usage_api: UsageAPI | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        resolved_api_key = _resolve_api_key(self.api_key)
        resolved_backend_base = _resolve_backend_base(self.backend_base)
        self.api_key = resolved_api_key
        self.backend_base = resolved_backend_base
        self._transport = SmrHttpTransport(
            base_url=resolved_backend_base,
            headers=_auth_headers(resolved_api_key),
            timeout=self.timeout_seconds,
        )

    def __enter__(self) -> SmrControlClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        self._transport.close()

    @property
    def projects(self) -> ProjectsAPI:
        if self._projects_api is None:
            self._projects_api = ProjectsAPI(self)
        return self._projects_api

    @property
    def runs(self) -> RunsAPI:
        if self._runs_api is None:
            self._runs_api = RunsAPI(self)
        return self._runs_api

    @property
    def workspace_inputs(self) -> WorkspaceInputsAPI:
        if self._workspace_inputs_api is None:
            self._workspace_inputs_api = WorkspaceInputsAPI(self)
        return self._workspace_inputs_api

    @property
    def progress(self) -> ProgressAPI:
        if self._progress_api is None:
            self._progress_api = ProgressAPI(self)
        return self._progress_api

    @property
    def approvals(self) -> ApprovalsAPI:
        if self._approvals_api is None:
            self._approvals_api = ApprovalsAPI(self)
        return self._approvals_api

    @property
    def artifacts(self) -> ArtifactsAPI:
        if self._artifacts_api is None:
            self._artifacts_api = ArtifactsAPI(self)
        return self._artifacts_api

    @property
    def logs(self) -> LogsAPI:
        if self._logs_api is None:
            self._logs_api = LogsAPI(self)
        return self._logs_api

    @property
    def integrations(self) -> IntegrationsAPI:
        if self._integrations_api is None:
            self._integrations_api = IntegrationsAPI(self)
        return self._integrations_api

    @property
    def usage(self) -> UsageAPI:
        if self._usage_api is None:
            self._usage_api = UsageAPI(self)
        return self._usage_api

    def get_usage_analytics(
        self,
        subject: UsageAnalyticsSubject,
        *,
        start_at: str,
        end_at: str,
        bucket: str = "AUTO",
        first: int = 100,
        after: str | None = None,
    ) -> UsageAnalyticsPayload:
        return self.usage.get_usage_analytics(
            subject,
            start_at=start_at,
            end_at=end_at,
            bucket=bucket,
            first=first,
            after=after,
        )

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        allow_not_found: bool = False,
    ) -> Any:
        return self._transport.request_json(
            method,
            path,
            params=params,
            json_body=json_body,
            allow_not_found=allow_not_found,
        )

    def create_project(self, payload: dict[str, Any]) -> dict[str, Any]:
        return _coerce_dict(self._request_json("POST", "/smr/projects", json_body=payload), label="create_project")

    def list_projects(
        self,
        *,
        include_archived: bool = False,
        limit: int = 100,
        cursor: str | None = None,
    ) -> list[dict[str, Any]]:
        params = build_query_params(
            include_archived=include_archived,
            limit=limit,
            cursor=cursor,
        )
        return _coerce_list(self._request_json("GET", "/smr/projects", params=params), label="list_projects")

    def get_project(self, project_id: str) -> dict[str, Any]:
        return _coerce_dict(self._request_json("GET", f"/smr/projects/{project_id}"), label="get_project")

    def patch_project(self, project_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return _coerce_dict(
            self._request_json("PATCH", f"/smr/projects/{project_id}", json_body=payload),
            label="patch_project",
        )

    def get_project_status(self, project_id: str) -> dict[str, Any]:
        return _coerce_dict(
            self._request_json("GET", f"/smr/projects/{project_id}/status"),
            label="get_project_status",
        )

    def get_project_status_snapshot(self, project_id: str) -> dict[str, Any]:
        return self.get_project_status(project_id)

    def get_project_entitlement(self, project_id: str) -> dict[str, Any]:
        return _coerce_dict(
            self._request_json(
                "GET",
                f"/smr/projects/{project_id}/entitlements/managed_research",
            ),
            label="get_project_entitlement",
        )

    def get_capabilities(self) -> dict[str, Any]:
        return _coerce_dict(self._request_json("GET", "/smr/capabilities"), label="get_capabilities")

    def get_limits(self) -> dict[str, Any]:
        return _coerce_dict(self._request_json("GET", "/smr/limits"), label="get_limits")

    def attach_source_repo(
        self,
        project_id: str,
        url: str,
        *,
        default_branch: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"url": str(url).strip()}
        if default_branch and default_branch.strip():
            payload["default_branch"] = default_branch.strip()
        return _coerce_dict(
            self._request_json(
                "PUT",
                f"/smr/projects/{project_id}/workspace-inputs/source-repo",
                json_body=payload,
            ),
            label="attach_source_repo",
        )

    def get_workspace_inputs(self, project_id: str) -> dict[str, Any]:
        return _coerce_dict(
            self._request_json("GET", f"/smr/projects/{project_id}/workspace-inputs"),
            label="get_workspace_inputs",
        )

    def upload_workspace_files(
        self,
        project_id: str,
        files: Iterable[Mapping[str, Any]],
    ) -> dict[str, Any]:
        normalized_files = [_normalize_uploaded_file(entry) for entry in files]
        if not normalized_files:
            raise ValueError("upload_workspace_files requires at least one file")
        return _coerce_dict(
            self._request_json(
                "POST",
                f"/smr/projects/{project_id}/workspace-inputs/files:upload",
                json_body={"files": normalized_files},
            ),
            label="upload_workspace_files",
        )

    def upload_workspace_directory(
        self,
        project_id: str,
        directory: str | os.PathLike[str],
    ) -> dict[str, Any]:
        root = Path(directory).resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"workspace directory does not exist: {root}")
        files: list[dict[str, Any]] = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            files.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "content_path": path,
                    "content_type": _guess_content_type(path.name),
                }
            )
        return self.upload_workspace_files(project_id, files)

    def get_project_readiness(self, project_id: str) -> dict[str, Any]:
        return _coerce_dict(
            self._request_json("GET", f"/smr/projects/{project_id}/readiness"),
            label="get_project_readiness",
        )

    def trigger_run(
        self,
        project_id: str,
        *,
        work_mode: str,
        timebox_seconds: int | None = None,
        agent_model: str | None = None,
        agent_kind: str | None = None,
        prompt: str | None = None,
        workflow: dict[str, Any] | None = None,
        sandbox_override: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"work_mode": work_mode}
        if timebox_seconds is not None:
            payload["timebox_seconds"] = int(timebox_seconds)
        if agent_model and agent_model.strip():
            payload["agent_model"] = agent_model.strip()
        if agent_kind and agent_kind.strip():
            payload["agent_kind"] = agent_kind.strip()
        if prompt and prompt.strip():
            payload["prompt"] = prompt.strip()
        if workflow:
            payload["workflow"] = workflow
        if sandbox_override:
            payload["sandbox_override"] = sandbox_override
        return _coerce_dict(
            self._request_json("POST", f"/smr/projects/{project_id}/trigger", json_body=payload),
            label="trigger_run",
        )

    def list_runs(
        self,
        project_id: str,
        *,
        active_only: bool = False,
        state: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> list[dict[str, Any]]:
        if active_only:
            return self.list_active_runs(project_id)
        params = build_query_params(state=state, limit=limit, cursor=cursor)
        return _coerce_list(
            self._request_json("GET", f"/smr/projects/{project_id}/runs", params=params),
            label="list_runs",
        )

    def list_active_runs(self, project_id: str) -> list[dict[str, Any]]:
        return _coerce_list(
            self._request_json("GET", f"/smr/projects/{project_id}/runs/active"),
            label="list_active_runs",
        )

    def get_run(self, run_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        if project_id:
            scoped = self._request_json(
                "GET",
                f"/smr/projects/{project_id}/runs/{run_id}",
                allow_not_found=True,
            )
            if scoped is not None:
                return _coerce_dict(scoped, label="get_project_run")
        return _coerce_dict(self._request_json("GET", f"/smr/runs/{run_id}"), label="get_run")

    def get_run_progress(self, project_id: str, run_id: str) -> dict[str, Any]:
        return _coerce_dict(
            self._request_json("GET", f"/smr/projects/{project_id}/runs/{run_id}/progress"),
            label="get_run_progress",
        )

    def list_run_questions(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
        status_filter: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> list[dict[str, Any]]:
        params = build_query_params(status_filter=status_filter, limit=limit, cursor=cursor)
        if project_id:
            scoped = self._request_json(
                "GET",
                f"/smr/projects/{project_id}/runs/{run_id}/questions",
                params=params,
                allow_not_found=True,
            )
            if scoped is not None:
                return _coerce_list(scoped, label="list_project_run_questions")
        return _coerce_list(
            self._request_json("GET", f"/smr/runs/{run_id}/questions", params=params),
            label="list_run_questions",
        )

    def create_run_checkpoint(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
        checkpoint_id: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        payload = build_query_params(checkpoint_id=checkpoint_id, reason=reason)
        if project_id:
            return _coerce_dict(
                self._request_json(
                    "POST",
                    f"/smr/projects/{project_id}/runs/{run_id}/checkpoints",
                    json_body=payload or {},
                ),
                label="create_project_run_checkpoint",
            )
        return _coerce_dict(
            self._request_json("POST", f"/smr/runs/{run_id}/checkpoints", json_body=payload or {}),
            label="create_run_checkpoint",
        )

    def list_run_checkpoints(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        if project_id:
            return _coerce_list(
                self._request_json("GET", f"/smr/projects/{project_id}/runs/{run_id}/checkpoints"),
                label="list_project_run_checkpoints",
            )
        return _coerce_list(
            self._request_json("GET", f"/smr/runs/{run_id}/checkpoints"),
            label="list_run_checkpoints",
        )

    def restore_run_checkpoint(
        self,
        run_id: str,
        *,
        project_id: str | None = None,
        checkpoint_id: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        payload = build_query_params(checkpoint_id=checkpoint_id, reason=reason)
        if project_id:
            return _coerce_dict(
                self._request_json(
                    "POST",
                    f"/smr/projects/{project_id}/runs/{run_id}/restore",
                    json_body=payload or {},
                ),
                label="restore_project_run_checkpoint",
            )
        return _coerce_dict(
            self._request_json("POST", f"/smr/runs/{run_id}/restore", json_body=payload or {}),
            label="restore_run_checkpoint",
        )

    def list_run_log_archives(self, project_id: str, run_id: str) -> list[dict[str, Any]]:
        return _coerce_list(
            self._request_json("GET", f"/smr/projects/{project_id}/runs/{run_id}/logs/archives"),
            label="list_run_log_archives",
        )


ManagedResearchClient = SmrControlClient


def first_id(items: Iterable[dict[str, Any]], key: str) -> str | None:
    for item in items:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None
