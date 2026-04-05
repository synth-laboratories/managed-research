"""Managed Research MCP server (stdio transport)."""

from __future__ import annotations

import json
import sys
from enum import Enum
from typing import Any

from managed_research.auth import get_api_key
from managed_research.mcp.registry import JSONDict, ToolDefinition
from managed_research.mcp.tools.approvals import build_approval_tools
from managed_research.mcp.tools.artifacts import build_artifact_tools
from managed_research.mcp.tools.integrations import build_integration_tools
from managed_research.mcp.tools.logs import build_log_tools
from managed_research.mcp.tools.progress import build_progress_tools
from managed_research.mcp.tools.projects import build_project_tools
from managed_research.mcp.tools.runs import build_run_tools
from managed_research.mcp.tools.usage import build_usage_tools
from managed_research.mcp.tools.workspace_inputs import build_workspace_input_tools
from managed_research.errors import SmrApiError
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


class _UsageAnalyticsSubjectKind(str, Enum):
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
        raise ValueError(
            "'subject_kind' must be either 'org' or 'managed_account'"
        ) from exc


class RpcError(Exception):
    def __init__(self, code: int, message: str, data: Any | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


def _require_string(payload: JSONDict, key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{key}' is required and must be a non-empty string")
    return value.strip()


def _optional_string(payload: JSONDict, key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"'{key}' must be a string when provided")
    stripped = value.strip()
    return stripped or None


def _optional_int(payload: JSONDict, key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"'{key}' must be an integer when provided")
    return value


def _optional_bool(payload: JSONDict, key: str, *, default: bool = False) -> bool:
    value = payload.get(key)
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError(f"'{key}' must be a boolean when provided")
    return value


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
            api_key=_optional_string(args, "api_key"),
            backend_base=_optional_string(args, "backend_base"),
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
        project_id = _optional_string(args, "project_id")
        checks: dict[str, Any] = {}
        try:
            api_key = _optional_string(args, "api_key") or get_api_key(required=False)
        except Exception:
            api_key = None
        checks["api_key"] = {
            "status": "pass" if api_key else "warn",
            "configured": bool(api_key),
        }
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
        payload = args.get("config")
        config = dict(payload) if isinstance(payload, dict) else {}
        name = _optional_string(args, "name")
        if name:
            config["name"] = name
        with self._client_from_args(args) as client:
            return client.create_project(config)

    def _tool_list_projects(self, args: JSONDict) -> Any:
        include_archived = _optional_bool(args, "include_archived", default=False)
        limit = _optional_int(args, "limit") or 100
        with self._client_from_args(args) as client:
            return client.list_projects(include_archived=include_archived, limit=limit)

    def _tool_get_project(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project(project_id)

    def _tool_get_project_status(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_status(project_id)

    def _tool_get_project_entitlement(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_entitlement(project_id)

    def _tool_get_capabilities(self, args: JSONDict) -> Any:
        with self._client_from_args(args) as client:
            return client.get_capabilities()

    def _tool_get_limits(self, args: JSONDict) -> Any:
        with self._client_from_args(args) as client:
            return client.get_limits()

    def _tool_get_workspace_download_url(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_workspace_download_url(project_id)

    def _tool_get_project_git(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_git(project_id)

    def _tool_download_workspace_archive(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        output_path = _require_string(args, "output_path")
        timeout_raw = _optional_int(args, "timeout_seconds")
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
        subject_kind = _optional_string(args, "subject_kind")
        org_id = _optional_string(args, "org_id")
        managed_account_id = _optional_string(args, "managed_account_id")
        start_at = _require_string(args, "start_at")
        end_at = _require_string(args, "end_at")
        bucket = _require_string(args, "bucket").upper()
        first = _optional_int(args, "first")
        if first is None:
            raise ValueError("'first' is required")
        after = _optional_string(args, "after")
        resolved_subject_kind = _resolve_usage_analytics_subject_kind(
            subject_kind,
        )
        with self._client_from_args(args) as client:
            if resolved_subject_kind is _UsageAnalyticsSubjectKind.MANAGED_ACCOUNT:
                if not managed_account_id:
                    raise ValueError(
                        "'managed_account_id' is required for managed_account usage analytics"
                    )
                subject = client.usage.subject_for_managed_account(managed_account_id)
            else:
                if not org_id:
                    raise ValueError("'org_id' is required for org usage analytics")
                subject = client.usage.subject_for_org(org_id)
            return client.get_usage_analytics(
                subject,
                start_at=start_at,
                end_at=end_at,
                bucket=bucket,
                first=first,
                after=after,
            )

    def _tool_attach_source_repo(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        url = _require_string(args, "url")
        default_branch = _optional_string(args, "default_branch")
        with self._client_from_args(args) as client:
            return client.attach_source_repo(project_id, url, default_branch=default_branch)

    def _tool_get_workspace_inputs(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_workspace_inputs(project_id)

    def _tool_upload_workspace_files(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        files = args.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError("'files' must be a non-empty array")
        normalized: list[JSONDict] = []
        for item in files:
            if not isinstance(item, dict):
                raise ValueError("each file entry must be an object")
            normalized.append(item)
        with self._client_from_args(args) as client:
            return client.upload_workspace_files(project_id, normalized)

    def _tool_trigger_run(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        work_mode = _require_string(args, "work_mode")
        timebox_seconds = _optional_int(args, "timebox_seconds")
        agent_model = _optional_string(args, "agent_model")
        agent_kind = _optional_string(args, "agent_kind")
        prompt = _optional_string(args, "prompt")
        workflow = args.get("workflow") if isinstance(args.get("workflow"), dict) else None
        sandbox_override = (
            args.get("sandbox_override") if isinstance(args.get("sandbox_override"), dict) else None
        )
        try:
            with self._client_from_args(args) as client:
                return client.trigger_run(
                    project_id,
                    work_mode=work_mode,
                    timebox_seconds=timebox_seconds,
                    agent_model=agent_model,
                    agent_kind=agent_kind,
                    prompt=prompt,
                    workflow=workflow,
                    sandbox_override=sandbox_override,
                )
        except SmrApiError as exc:
            payload = _mcp_structured_trigger_error_payload(exc)
            if payload is not None:
                return payload
            raise

    def _tool_list_runs(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        active_only = _optional_bool(args, "active_only", default=False)
        state = _optional_string(args, "state")
        limit = _optional_int(args, "limit") or 50
        with self._client_from_args(args) as client:
            return client.list_runs(
                project_id,
                active_only=active_only,
                state=state,
                limit=limit,
            )

    def _tool_get_run(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        project_id = _optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_run(run_id, project_id=project_id)

    def _tool_list_active_runs(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.list_active_runs(project_id)

    def _tool_list_run_questions(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        project_id = _optional_string(args, "project_id")
        status_filter = _optional_string(args, "status_filter")
        limit = _optional_int(args, "limit") or 100
        with self._client_from_args(args) as client:
            return client.list_run_questions(
                run_id,
                project_id=project_id,
                status_filter=status_filter,
                limit=limit,
            )

    def _tool_create_run_checkpoint(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        project_id = _optional_string(args, "project_id")
        checkpoint_id = _optional_string(args, "checkpoint_id")
        reason = _optional_string(args, "reason")
        with self._client_from_args(args) as client:
            return client.create_run_checkpoint(
                run_id,
                project_id=project_id,
                checkpoint_id=checkpoint_id,
                reason=reason,
            )

    def _tool_list_run_checkpoints(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        project_id = _optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.list_run_checkpoints(run_id, project_id=project_id)

    def _tool_restore_run_checkpoint(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        project_id = _optional_string(args, "project_id")
        checkpoint_id = _optional_string(args, "checkpoint_id")
        reason = _optional_string(args, "reason")
        with self._client_from_args(args) as client:
            return client.restore_run_checkpoint(
                run_id,
                project_id=project_id,
                checkpoint_id=checkpoint_id,
                reason=reason,
            )

    def _tool_list_run_log_archives(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        run_id = _require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.list_run_log_archives(project_id, run_id)

    def _tool_get_project_readiness(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_readiness(project_id)

    def _tool_get_run_progress(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        run_id = _require_string(args, "run_id")
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


__all__ = [
    "DEFAULT_PROTOCOL_VERSION",
    "ManagedResearchMcpServer",
    "SERVER_NAME",
    "SUPPORTED_PROTOCOL_VERSIONS",
    "_read_message",
]
