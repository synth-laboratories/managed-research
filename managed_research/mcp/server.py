"""Managed Research MCP server (stdio transport)."""

from __future__ import annotations

import json
import sys
from enum import StrEnum
from typing import Any

from managed_research.auth import get_api_key
from managed_research.errors import SmrApiError
from managed_research.mcp.registry import JSONDict, ToolDefinition
from managed_research.mcp.request_models import (
    ProjectMutationRequest,
    ProviderKeyRequest,
    RunLaunchRequest,
    UsageAnalyticsRequest,
    WorkspaceFileUploadRequest,
    optional_bool,
    optional_int,
    optional_string,
    require_string,
)
from managed_research.mcp.tools.approvals import build_approval_tools
from managed_research.mcp.tools.artifacts import build_artifact_tools
from managed_research.mcp.tools.integrations import build_integration_tools
from managed_research.mcp.tools.logs import build_log_tools
from managed_research.mcp.tools.progress import build_progress_tools
from managed_research.mcp.tools.projects import build_project_tools
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


class _UsageAnalyticsSubjectKind(StrEnum):
    ORG = "org"
    MANAGED_ACCOUNT = "managed_account"


def _resolve_usage_analytics_subject_kind(
    value: str | None,
) -> _UsageAnalyticsSubjectKind:
    if value is None:
        raise ValueError("'subject_kind' is required")
    try:
        return _UsageAnalyticsSubjectKind(value)
    except ValueError as exc:
        raise ValueError("'subject_kind' must be either 'org' or 'managed_account'") from exc


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

    def __init__(self) -> None:
        self._tools = {tool.name: tool for tool in self._build_tools()}

    def available_tool_names(self) -> list[str]:
        return sorted(self._tools.keys())

    def _client_from_args(self, args: JSONDict) -> SmrControlClient:
        return SmrControlClient(
            api_key=optional_string(args, "api_key"),
            backend_base=optional_string(args, "backend_base"),
        )

    def _build_tools(self) -> list[ToolDefinition]:
        return [
            *build_project_tools(self),
            *build_workspace_input_tools(self),
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

    def _tool_create_project(self, args: JSONDict) -> Any:
        request = ProjectMutationRequest.for_create(args)
        with self._client_from_args(args) as client:
            return client.create_project(
                request.config,
                actor_model_assignments=request.actor_model_assignments,
            )

    def _tool_list_projects(self, args: JSONDict) -> Any:
        include_archived = optional_bool(args, "include_archived", default=False)
        limit = optional_int(args, "limit") or 100
        with self._client_from_args(args) as client:
            return client.list_projects(include_archived=include_archived, limit=limit)

    def _tool_get_project(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project(project_id)

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

    def _tool_get_run_start_blockers(self, args: JSONDict) -> Any:
        request = RunLaunchRequest.from_payload(args)
        with self._client_from_args(args) as client:
            return client.get_run_start_blockers(
                request.project_id,
                **request.client_kwargs(),
            )

    def _tool_get_workspace_download_url(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_workspace_download_url(project_id)

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

    def _tool_get_usage_analytics(self, args: JSONDict) -> Any:
        request = UsageAnalyticsRequest.from_payload(args)
        resolved_subject_kind = _resolve_usage_analytics_subject_kind(
            request.subject_kind,
        )
        with self._client_from_args(args) as client:
            if resolved_subject_kind is _UsageAnalyticsSubjectKind.MANAGED_ACCOUNT:
                if not request.managed_account_id:
                    raise ValueError(
                        "'managed_account_id' is required for managed_account usage analytics"
                    )
                subject = client.usage.subject_for_managed_account(request.managed_account_id)
            else:
                if not request.org_id:
                    raise ValueError("'org_id' is required for org usage analytics")
                subject = client.usage.subject_for_org(request.org_id)
            return client.get_usage_analytics(
                subject,
                start_at=request.start_at,
                end_at=request.end_at,
                bucket=request.bucket,
                first=request.first,
                after=request.after,
            )

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

    def _tool_get_project_readiness(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_readiness(project_id)

    def _tool_get_run_progress(self, args: JSONDict) -> Any:
        project_id = require_string(args, "project_id")
        run_id = require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.get_run_progress(project_id, run_id)

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
                    "result": {
                        "tools": [
                            {
                                "name": tool.name,
                                "description": tool.description,
                                "inputSchema": tool.input_schema,
                            }
                            for tool in self._tools.values()
                        ]
                    },
                }
            if method == "tools/call":
                params = request.get("params")
                if not isinstance(params, dict):
                    raise RpcError(-32602, "tools/call requires object params")
                tool_name = params.get("name")
                if not isinstance(tool_name, str) or tool_name not in self._tools:
                    raise RpcError(-32601, f"Unknown tool: {tool_name!r}")
                arguments = params.get("arguments")
                if not isinstance(arguments, dict):
                    arguments = {}
                result = self._tools[tool_name].handler(arguments)
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
