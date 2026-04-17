"""Managed Research MCP server (stdio transport)."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, is_dataclass
from typing import Any

from managed_research.auth import get_api_key
from managed_research.errors import SmrApiError
from managed_research.mcp.registry import (
    JSONDict,
    ToolDefinition,
    build_tool_registry,
    call_tool,
    list_tool_payload,
)
from managed_research.mcp.request_models import (
    ProjectMutationRequest,
    ProviderKeyRequest,
    RunnableProjectCreateRequest,
    RunLaunchRequest,
    WorkspaceFileUploadRequest,
    optional_bool,
    optional_int,
    optional_string,
    parse_branch_run_request,
    require_string,
)
from managed_research.mcp.tools.approvals import build_approval_tools
from managed_research.mcp.tools.artifacts import build_artifact_tools
from managed_research.mcp.tools.integrations import build_integration_tools
from managed_research.mcp.tools.logs import build_log_tools
from managed_research.mcp.tools.progress import build_progress_tools
from managed_research.mcp.tools.projects import build_project_tools
from managed_research.mcp.tools.resources import build_resource_tools
from managed_research.mcp.tools.runs import build_run_tools
from managed_research.mcp.tools.usage import build_usage_tools
from managed_research.mcp.tools.workspace_inputs import build_workspace_input_tools
from managed_research.sdk.client import SmrControlClient
from managed_research.version import __version__

SUPPORTED_PROTOCOL_VERSIONS = ("2025-06-18", "2024-11-05")
DEFAULT_PROTOCOL_VERSION = SUPPORTED_PROTOCOL_VERSIONS[0]
SERVER_NAME = "managed-research"


def _mcp_structured_trigger_error_payload(exc: BaseException) -> dict[str, Any] | None:
    """If *exc* carries a FastAPI-style ``detail`` dict with ``error_code``, shape an MCP result."""
    detail = getattr(exc, "detail", None)
    if not isinstance(detail, dict):
        return None
    code = detail.get("error_code")
    if not isinstance(code, str) or not code.strip():
        return None
    out: dict[str, Any] = {
        "error": code.strip(),
        "detail": detail,
        "message": str(exc),
    }
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        out["http_status"] = status
    return out


class RpcError(Exception):
    def __init__(self, code: int, message: str, data: Any | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


def _read_message(stream: Any) -> tuple[JSONDict, str] | None:
    """Read either JSONL or content-length framed JSON-RPC from stdin."""

    first = stream.readline()
    if not first:
        return None
    if first.startswith(b"Content-Length:"):
        length = int(first.decode("ascii").split(":", 1)[1].strip())
        while True:
            line = stream.readline()
            if line in {b"\r\n", b"\n", b""}:
                break
        payload = json.loads(stream.read(length).decode("utf-8"))
        return payload, "content-length"
    payload = json.loads(first.decode("utf-8"))
    return payload, "jsonl"


def _write_message(stream: Any, payload: JSONDict, *, framing: str) -> None:
    encoded = json.dumps(payload).encode("utf-8")
    if framing == "content-length":
        stream.write(f"Content-Length: {len(encoded)}\r\n\r\n".encode("ascii"))
        stream.write(encoded)
    else:
        stream.write(encoded + b"\n")
    stream.flush()


class ManagedResearchMcpServer:
    """Minimal MCP server for the rewritten remigration surface."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        backend_base: str | None = None,
    ) -> None:
        self._default_api_key = api_key
        self._default_backend_base = backend_base
        self._tools = build_tool_registry(self._build_tools())

    def available_tool_names(self) -> list[str]:
        return sorted(self._tools.keys())

    def tool_definitions(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def get_tool_definition(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def list_tool_payload(self) -> list[JSONDict]:
        return list_tool_payload(self._tools)

    def call_tool(self, name: str, arguments: JSONDict | None = None) -> Any:
        return call_tool(self._tools, name, arguments)

    def _client_from_args(self, args: JSONDict) -> SmrControlClient:
        resolved_api_key = optional_string(args, "api_key") or self._default_api_key
        resolved_backend_base = (
            optional_string(args, "backend_base") or self._default_backend_base
        )
        return SmrControlClient(
            api_key=resolved_api_key,
            backend_base=resolved_backend_base,
        )

    def _build_tools(self) -> list[ToolDefinition]:
        return [
            *build_project_tools(self),
            *build_workspace_input_tools(self),
            *build_resource_tools(self),
            *build_run_tools(self),
            *build_progress_tools(self),
            *build_log_tools(self),
            *build_approval_tools(self),
            *build_artifact_tools(self),
            *build_integration_tools(self),
            *build_usage_tools(self),
        ]

    def _tool_health_check(self, args: JSONDict) -> Any:
        project_id = optional_string(args, "project_id")
        checks: dict[str, Any] = {}
        try:
            api_key = optional_string(args, "api_key") or get_api_key(required=False)
            checks["api_key"] = {
                "status": "pass" if api_key else "warn",
                "configured": bool(api_key),
            }
        except ValueError as exc:
            checks["api_key"] = {
                "status": "fail",
                "configured": False,
                "message": str(exc),
            }
            api_key = None
        with self._client_from_args(args) as client:
            capabilities = client.get_capabilities()
            checks["backend_ping"] = {
                "status": "pass",
                "backend_version": str(capabilities.get("version") or __version__),
            }
            if project_id:
                checks["project_status"] = client.get_project_status(project_id)
        return {"ok": True, "checks": checks}

    def _tool_create_runnable_project(self, args: JSONDict) -> Any:
        request = RunnableProjectCreateRequest.from_payload(args)
        with self._client_from_args(args) as client:
            return client.create_runnable_project(request.request)

    def _tool_list_projects(self, args: JSONDict) -> Any:
        include_archived = optional_bool(args, "include_archived", default=False)
        limit = optional_int(args, "limit") or 100
        with self._client_from_args(args) as client:
            return client.list_projects(include_archived=include_archived, limit=limit)

    def _tool_get_project(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project(project_id)

    def _tool_rename_project(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        name = require_string(args, "name").strip()
        if not name:
            raise ValueError("'name' must be non-empty")
        with self._client_from_args(args) as client:
            return client.rename_project(project_id, name)

    def _tool_patch_project(self, args: JSONDict) -> Any:
        request = ProjectMutationRequest.for_patch(args)
        with self._client_from_args(args) as client:
            return client.patch_project(
                request.project_id,
                request.config,
                actor_model_assignments=request.actor_model_assignments,
            )

    def _tool_get_project_status(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_status(project_id)

    def _tool_get_project_entitlement(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_entitlement(project_id)

    def _tool_get_project_setup(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_setup(project_id)

    def _tool_prepare_project_setup(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.prepare_project_setup(project_id)

    def _tool_get_project_notes(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_notes(project_id)

    def _tool_set_project_notes(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        notes = require_string(args, "notes")
        with self._client_from_args(args) as client:
            return client.set_project_notes(project_id, notes)

    def _tool_append_project_notes(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        notes = require_string(args, "notes")
        with self._client_from_args(args) as client:
            return client.append_project_notes(project_id, notes)

    def _tool_get_org_knowledge(self, args: JSONDict) -> Any:
        with self._client_from_args(args) as client:
            return client.get_org_knowledge()

    def _tool_set_org_knowledge(self, args: JSONDict) -> Any:
        content = require_string(args, "content")
        with self._client_from_args(args) as client:
            return client.set_org_knowledge(content)

    def _tool_get_project_knowledge(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_knowledge(project_id)

    def _tool_set_project_knowledge(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        content = require_string(args, "content")
        with self._client_from_args(args) as client:
            return client.set_project_knowledge(project_id, content)

    def _tool_curated_knowledge(self, args: JSONDict) -> Any:
        operation = require_string(args, "operation").strip().lower()
        if operation not in {"get", "set"}:
            raise ValueError("'operation' must be either 'get' or 'set'")
        scope = require_string(args, "scope").strip().lower()
        if scope not in {"org", "project"}:
            raise ValueError("'scope' must be either 'org' or 'project'")
        project_id = require_string(args, "project_id") if scope == "project" else None
        if scope == "org" and optional_string(args, "project_id") is not None:
            raise ValueError("'project_id' must not be set when scope is 'org'")

        with self._client_from_args(args) as client:
            if operation == "get":
                if scope == "org":
                    return client.get_org_knowledge()
                return client.get_project_knowledge(project_id)

            content = require_string(args, "content")
            if scope == "org":
                return client.set_org_knowledge(content)
            return client.set_project_knowledge(project_id, content)

    def _tool_pause_project(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.pause_project(project_id)

    def _tool_resume_project(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.resume_project(project_id)

    def _tool_archive_project(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.archive_project(project_id)

    def _tool_unarchive_project(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.unarchive_project(project_id)

    def _tool_get_capabilities(self, args: JSONDict) -> Any:
        with self._client_from_args(args) as client:
            return client.get_capabilities()

    def _tool_get_limits(self, args: JSONDict) -> Any:
        with self._client_from_args(args) as client:
            return client.get_limits()

    def _tool_get_capacity_lane_preview(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_capacity_lane_preview(project_id)

    def _tool_set_provider_key(self, args: JSONDict) -> Any:
        request = ProviderKeyRequest.from_payload(args)
        with self._client_from_args(args) as client:
            return client.set_provider_key(
                request.project_id,
                provider=request.provider,
                funding_source=request.funding_source,
                api_key=request.api_key,
                encrypted_key_b64=request.encrypted_key_b64,
            )

    def _tool_get_provider_key_status(self, args: JSONDict) -> Any:
        request = ProviderKeyRequest.from_payload(args)
        with self._client_from_args(args) as client:
            return client.get_provider_key_status(
                request.project_id,
                provider=request.provider,
                funding_source=request.funding_source,
            )

    def _tool_get_workspace_download_url(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_workspace_download_url(project_id)

    def _tool_get_billing_entitlements(self, args: JSONDict) -> Any:
        with self._client_from_args(args) as client:
            result = client.get_billing_entitlements()
            return asdict(result) if is_dataclass(result) else result

    def _tool_get_run_usage(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        with self._client_from_args(args) as client:
            result = client.get_run_usage(run_id)
            return asdict(result) if is_dataclass(result) else result

    def _tool_get_project_usage(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            result = client.get_project_usage(project_id)
            return asdict(result) if is_dataclass(result) else result

    def _tool_get_project_economics(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            result = client.get_project_economics(project_id)
            return asdict(result) if is_dataclass(result) else result

    def _tool_get_project_git(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_git(project_id)

    def _tool_download_workspace_archive(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        output_path = require_string(args, "output_path")
        timeout_raw = optional_int(args, "timeout_seconds")
        timeout_seconds = float(timeout_raw) if timeout_raw is not None else None
        with self._client_from_args(args) as client:
            if timeout_seconds is not None:
                return client.download_workspace_archive(
                    project_id,
                    output_path,
                    timeout_seconds=timeout_seconds,
                )
            return client.download_workspace_archive(project_id, output_path)

    def _tool_attach_source_repo(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        url = require_string(args, "url")
        default_branch = optional_string(args, "default_branch")
        with self._client_from_args(args) as client:
            return client.attach_source_repo(project_id, url, default_branch=default_branch)

    def _tool_get_workspace_inputs(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_workspace_inputs(project_id)

    def _tool_upload_workspace_files(self, args: JSONDict) -> Any:
        request = WorkspaceFileUploadRequest.from_payload(args)
        with self._client_from_args(args) as client:
            return client.upload_workspace_files(request.project_id, request.files)

    def _tool_list_project_files(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        visibility = optional_string(args, "visibility")
        limit = optional_int(args, "limit")
        with self._client_from_args(args) as client:
            return client.list_project_files(
                project_id,
                visibility=visibility,
                limit=limit,
            )

    def _tool_create_project_files(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        files = args.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError("'files' must be a non-empty array")
        with self._client_from_args(args) as client:
            return client.create_project_files(project_id, files)

    def _tool_get_project_file(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        file_id = require_string(args, "file_id")
        with self._client_from_args(args) as client:
            return client.get_project_file(project_id, file_id)

    def _tool_get_file_content(self, args: JSONDict) -> Any:
        file_id = require_string(args, "file_id")
        with self._client_from_args(args) as client:
            return client.get_file_content(file_id)

    def _tool_list_run_file_mounts(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.list_run_file_mounts(run_id)

    def _tool_upload_run_files(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        files = args.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError("'files' must be a non-empty array")
        with self._client_from_args(args) as client:
            return client.upload_run_files(run_id, files)

    def _tool_list_run_output_files(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        artifact_type = optional_string(args, "artifact_type")
        limit = optional_int(args, "limit")
        with self._client_from_args(args) as client:
            return client.list_run_output_files(
                run_id,
                artifact_type=artifact_type,
                limit=limit,
            )

    def _tool_get_run_output_file_content(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        artifact_id = require_string(args, "artifact_id")
        disposition = optional_string(args, "disposition") or "inline"
        with self._client_from_args(args) as client:
            return client.get_run_output_file_content(
                run_id,
                artifact_id,
                disposition=disposition,
            )

    def _tool_list_project_external_repositories(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.list_project_external_repositories(project_id)

    def _tool_create_project_external_repository(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        name = require_string(args, "name")
        url = require_string(args, "url")
        default_branch = optional_string(args, "default_branch")
        role = optional_string(args, "role")
        metadata = args.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("'metadata' must be an object when provided")
        with self._client_from_args(args) as client:
            return client.create_project_external_repository(
                project_id,
                name=name,
                url=url,
                default_branch=default_branch,
                role=role,
                metadata=metadata,
            )

    def _tool_patch_project_external_repository(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        repository_id = require_string(args, "repository_id")
        metadata = args.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("'metadata' must be an object when provided")
        with self._client_from_args(args) as client:
            return client.patch_project_external_repository(
                project_id,
                repository_id,
                url=optional_string(args, "url"),
                default_branch=optional_string(args, "default_branch"),
                role=optional_string(args, "role"),
                metadata=metadata,
            )

    def _tool_list_run_repository_mounts(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.list_run_repository_mounts(run_id)

    def _tool_create_run_repository_mount(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        repository_id = require_string(args, "repository_id")
        mount_name = optional_string(args, "mount_name")
        with self._client_from_args(args) as client:
            return client.create_run_repository_mount(
                run_id,
                repository_id=repository_id,
                mount_name=mount_name,
            )

    def _tool_list_project_credential_refs(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        kind = optional_string(args, "kind")
        with self._client_from_args(args) as client:
            return client.list_project_credential_refs(project_id, kind=kind)

    def _tool_create_project_credential_ref(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        kind = require_string(args, "kind")
        label = require_string(args, "label")
        metadata = args.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("'metadata' must be an object when provided")
        with self._client_from_args(args) as client:
            return client.create_project_credential_ref(
                project_id,
                kind=kind,
                label=label,
                provider=optional_string(args, "provider"),
                funding_source=optional_string(args, "funding_source"),
                credential_name=optional_string(args, "credential_name"),
                metadata=metadata,
            )

    def _tool_patch_project_credential_ref(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        credential_ref_id = require_string(args, "credential_ref_id")
        metadata = args.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("'metadata' must be an object when provided")
        with self._client_from_args(args) as client:
            return client.patch_project_credential_ref(
                project_id,
                credential_ref_id,
                provider=optional_string(args, "provider"),
                funding_source=optional_string(args, "funding_source"),
                credential_name=optional_string(args, "credential_name"),
                metadata=metadata,
            )

    def _tool_list_run_credential_bindings(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.list_run_credential_bindings(run_id)

    def _tool_create_run_credential_binding(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        credential_ref_id = require_string(args, "credential_ref_id")
        with self._client_from_args(args) as client:
            return client.create_run_credential_binding(
                run_id,
                credential_ref_id=credential_ref_id,
            )

    def _tool_trigger_run(self, args: JSONDict) -> Any:
        request = RunLaunchRequest.from_payload(args)
        try:
            with self._client_from_args(args) as client:
                return client.trigger_run(
                    request.project_id,
                    **request.client_kwargs(),
                )
        except SmrApiError as exc:
            payload = _mcp_structured_trigger_error_payload(exc)
            if payload is not None:
                return payload
            raise

    def _tool_list_runs(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        active_only = optional_bool(args, "active_only", default=False)
        state = optional_string(args, "state")
        limit = optional_int(args, "limit") or 50
        with self._client_from_args(args) as client:
            return client.list_runs(
                project_id,
                active_only=active_only,
                state=state,
                limit=limit,
            )

    def _tool_get_run(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_run(run_id, project_id=project_id)

    def _tool_get_run_primary_parent(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.get_run_primary_parent(run_id)

    def _tool_stop_run(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.stop_run(run_id, project_id=project_id)

    def _tool_pause_run(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.pause_run(run_id, project_id=project_id)

    def _tool_resume_run(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.resume_run(run_id, project_id=project_id)

    def _tool_get_run_logical_timeline(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        run_id = require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.get_run_logical_timeline(project_id, run_id)

    def _tool_get_run_traces(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            if project_id:
                return client.get_project_run_traces(project_id, run_id)
            return client.get_run_traces(run_id)

    def _tool_get_run_actor_usage(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            if project_id:
                return client.get_project_run_actor_usage(project_id, run_id)
            return client.get_run_actor_usage(run_id)

    def _tool_branch_run_from_checkpoint(self, args: JSONDict) -> Any:
        run_id = optional_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        request = parse_branch_run_request(args)
        with self._client_from_args(args) as client:
            return client.branch_run_from_checkpoint(
                run_id,
                project_id=project_id,
                checkpoint_id=request.checkpoint_id,
                checkpoint_record_id=request.checkpoint_record_id,
                checkpoint_uri=request.checkpoint_uri,
                mode=request.mode,
                message=request.message,
                reason=request.reason,
                title=request.title,
                source_node_id=request.source_node_id,
            )

    def _tool_runtime_message_queue(self, args: JSONDict) -> Any:
        operation = require_string(args, "operation").strip().lower()
        if operation not in {"list", "enqueue"}:
            raise ValueError("'operation' must be either 'list' or 'enqueue'")
        run_id = require_string(args, "run_id")
        with self._client_from_args(args) as client:
            if operation == "list":
                status = optional_string(args, "status")
                viewer_role = optional_string(args, "viewer_role")
                limit = optional_int(args, "limit")
                raw_viewer_target = args.get("viewer_target")
                viewer_target: str | list[str] | None = None
                if isinstance(raw_viewer_target, str) and raw_viewer_target.strip():
                    viewer_target = raw_viewer_target.strip()
                elif isinstance(raw_viewer_target, list):
                    cleaned_targets = [
                        str(item).strip()
                        for item in raw_viewer_target
                        if str(item).strip()
                    ]
                    viewer_target = cleaned_targets or None
                return client.list_runtime_messages(
                    run_id,
                    status=status,
                    viewer_role=viewer_role,
                    viewer_target=viewer_target,
                    limit=limit,
                )

            payload = args.get("payload")
            if payload is not None and not isinstance(payload, dict):
                raise ValueError("'payload' must be an object when provided")
            return client.enqueue_runtime_message(
                run_id,
                topic=optional_string(args, "topic"),
                causation_id=optional_string(args, "causation_id"),
                mode=optional_string(args, "mode"),
                spawn_policy=optional_string(args, "spawn_policy"),
                sender=optional_string(args, "sender"),
                target=optional_string(args, "target"),
                participant_session_id=optional_string(args, "participant_session_id"),
                action=optional_string(args, "action"),
                body=optional_string(args, "body"),
                payload=payload,
            )

    def _tool_list_active_runs(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.list_active_runs(project_id)

    def _tool_list_run_questions(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        status_filter = optional_string(args, "status_filter")
        limit = optional_int(args, "limit") or 100
        with self._client_from_args(args) as client:
            return client.list_run_questions(
                run_id,
                project_id=project_id,
                status_filter=status_filter,
                limit=limit,
            )

    def _tool_respond_to_run_question(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        question_id = require_string(args, "question_id")
        project_id = optional_string(args, "project_id")
        response_text = require_string(args, "response_text")
        with self._client_from_args(args) as client:
            return client.respond_to_run_question(
                run_id,
                question_id,
                project_id=project_id,
                response_text=response_text,
            )

    def _tool_list_run_approvals(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        status_filter = optional_string(args, "status_filter")
        limit = optional_int(args, "limit") or 100
        with self._client_from_args(args) as client:
            return client.list_run_approvals(
                run_id,
                project_id=project_id,
                status_filter=status_filter,
                limit=limit,
            )

    def _tool_approve_run_approval(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        approval_id = require_string(args, "approval_id")
        project_id = optional_string(args, "project_id")
        comment = optional_string(args, "comment")
        with self._client_from_args(args) as client:
            return client.approve_run_approval(
                run_id,
                approval_id,
                project_id=project_id,
                comment=comment,
            )

    def _tool_deny_run_approval(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        approval_id = require_string(args, "approval_id")
        project_id = optional_string(args, "project_id")
        comment = optional_string(args, "comment")
        with self._client_from_args(args) as client:
            return client.deny_run_approval(
                run_id,
                approval_id,
                project_id=project_id,
                comment=comment,
            )

    def _tool_create_run_checkpoint(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        checkpoint_id = optional_string(args, "checkpoint_id")
        reason = optional_string(args, "reason")
        with self._client_from_args(args) as client:
            return client.create_run_checkpoint(
                run_id,
                project_id=project_id,
                checkpoint_id=checkpoint_id,
                reason=reason,
            )

    def _tool_list_run_checkpoints(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.list_run_checkpoints(run_id, project_id=project_id)

    def _tool_restore_run_checkpoint(self, args: JSONDict) -> Any:
        run_id = require_string(args, "run_id")
        project_id = optional_string(args, "project_id")
        checkpoint_id = optional_string(args, "checkpoint_id")
        reason = optional_string(args, "reason")
        with self._client_from_args(args) as client:
            return client.restore_run_checkpoint(
                run_id,
                project_id=project_id,
                checkpoint_id=checkpoint_id,
                reason=reason,
            )

    def _tool_list_run_log_archives(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        run_id = require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.list_run_log_archives(project_id, run_id)

    def _tool_get_launch_preflight(self, args: JSONDict) -> Any:
        request = RunLaunchRequest.from_payload(args)
        with self._client_from_args(args) as client:
            return client.get_launch_preflight(
                request.project_id,
                **request.client_kwargs(),
            )

    def _tool_open_ended_questions(self, args: JSONDict) -> Any:
        operation = require_string(args, "operation").strip().lower()
        project_id = require_string(args, "project_id")
        objective_id = optional_string(args, "objective_id")
        payload = args.get("payload")
        if payload is not None and not isinstance(payload, dict):
            raise ValueError("'payload' must be an object when provided")
        with self._client_from_args(args) as client:
            if operation == "list":
                return client.list_open_ended_questions(
                    project_id, run_id=optional_string(args, "run_id")
                )
            if operation == "create":
                return client.create_open_ended_question(project_id, payload or {})
            if operation == "get":
                if objective_id is None:
                    raise ValueError("'objective_id' is required for get")
                return client.get_open_ended_question(project_id, objective_id)
            if operation == "patch":
                if objective_id is None:
                    raise ValueError("'objective_id' is required for patch")
                return client.patch_open_ended_question(
                    project_id, objective_id, payload or {}
                )
            if operation == "transition":
                if objective_id is None:
                    raise ValueError("'objective_id' is required for transition")
                return client.transition_open_ended_question(
                    project_id, objective_id, payload or {}
                )
        raise ValueError("'operation' must be list, create, get, patch, or transition")

    def _tool_directed_effort_outcomes(self, args: JSONDict) -> Any:
        operation = require_string(args, "operation").strip().lower()
        project_id = require_string(args, "project_id")
        objective_id = optional_string(args, "objective_id")
        payload = args.get("payload")
        if payload is not None and not isinstance(payload, dict):
            raise ValueError("'payload' must be an object when provided")
        with self._client_from_args(args) as client:
            if operation == "list":
                return client.list_directed_effort_outcomes(
                    project_id, run_id=optional_string(args, "run_id")
                )
            if operation == "create":
                return client.create_directed_effort_outcome(project_id, payload or {})
            if operation == "get":
                if objective_id is None:
                    raise ValueError("'objective_id' is required for get")
                return client.get_directed_effort_outcome(project_id, objective_id)
            if operation == "patch":
                if objective_id is None:
                    raise ValueError("'objective_id' is required for patch")
                return client.patch_directed_effort_outcome(
                    project_id, objective_id, payload or {}
                )
            if operation == "transition":
                if objective_id is None:
                    raise ValueError("'objective_id' is required for transition")
                return client.transition_directed_effort_outcome(
                    project_id, objective_id, payload or {}
                )
        raise ValueError("'operation' must be list, create, get, patch, or transition")

    def serve_stdio(self) -> None:
        framing = "jsonl"
        while True:
            message = _read_message(sys.stdin.buffer)
            if message is None:
                return
            request, framing = message
            response = self._handle_message(request)
            if response is None:
                continue
            _write_message(sys.stdout.buffer, response, framing=framing)

    def _handle_message(self, request: JSONDict) -> JSONDict | None:
        method = request.get("method")
        request_id = request.get("id")
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": DEFAULT_PROTOCOL_VERSION,
                        "serverInfo": {"name": SERVER_NAME, "version": __version__},
                        "capabilities": {"tools": {}},
                    },
                }
            if method == "ping":
                return {"jsonrpc": "2.0", "id": request_id, "result": {}}
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": self.list_tool_payload()},
                }
            if method == "tools/call":
                params = request.get("params")
                if not isinstance(params, dict):
                    raise RpcError(-32602, "tools/call requires object params")
                tool_name = params.get("name")
                if not isinstance(tool_name, str) or tool_name not in self._tools:
                    raise RpcError(-32601, f"Unknown tool: {tool_name!r}")
                arguments = params.get("arguments")
                if arguments is not None and not isinstance(arguments, dict):
                    raise RpcError(-32602, "tools/call arguments must be an object")
                result = self.call_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, sort_keys=True)}],
                        "structuredContent": result,
                    },
                }
            if method in {"shutdown", "exit"}:
                return {"jsonrpc": "2.0", "id": request_id, "result": {}}
            if method in {"initialized", "notifications/initialized"}:
                return None
            raise RpcError(-32601, f"Unsupported method: {method!r}")
        except RpcError as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": exc.code, "message": exc.message, "data": exc.data},
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(exc)},
            }


def main() -> None:
    """CLI entrypoint for the stdio MCP server."""
    ManagedResearchMcpServer().serve_stdio()


__all__ = [
    "DEFAULT_PROTOCOL_VERSION",
    "ManagedResearchMcpServer",
    "SERVER_NAME",
    "SUPPORTED_PROTOCOL_VERSIONS",
    "_read_message",
    "main",
]
