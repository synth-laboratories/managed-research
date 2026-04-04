"""Managed Research MCP server (stdio transport).

This server exposes managed-research control operations as MCP tools so external
agents can control SMR projects and runs through the public SMR API.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from managed_research.auth import get_api_key
from managed_research.mcp.registry import JSONDict, ToolDefinition, tool_schema
from managed_research.mcp.tools.approvals import build_approval_tools
from managed_research.mcp.tools.artifacts import build_artifact_tools
from managed_research.mcp.tools.integrations import build_integration_tools
from managed_research.mcp.tools.logs import build_log_tools
from managed_research.mcp.tools.projects import build_project_tools
from managed_research.mcp.tools.runs import build_run_tools
from managed_research.mcp.tools.usage import build_usage_tools
from managed_research.sdk.client import SmrControlClient
from managed_research.transport.streaming import preview_binary_payload
from managed_research.version import __version__

SUPPORTED_PROTOCOL_VERSIONS = ("2025-06-18", "2024-11-05")
DEFAULT_PROTOCOL_VERSION = SUPPORTED_PROTOCOL_VERSIONS[0]
SERVER_NAME = "managed-research"


_tool_schema = tool_schema


class RpcError(Exception):
    """JSON-RPC error wrapper."""

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


def _optional_bool(payload: JSONDict, key: str, default: bool = False) -> bool:
    value = payload.get(key)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raise ValueError(f"'{key}' must be a boolean when provided")


def _optional_int(payload: JSONDict, key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"'{key}' must be an integer when provided")
    return value


def _optional_object(payload: JSONDict, key: str) -> JSONDict | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"'{key}' must be an object when provided")
    return value


class ManagedResearchMcpServer:
    """Minimal MCP server for managed research control."""

    def __init__(self) -> None:
        self._tools = {tool.name: tool for tool in self._build_tools()}

    def available_tool_names(self) -> list[str]:
        """Return sorted MCP tool names exposed by this server."""
        return sorted(self._tools.keys())

    def _client_from_args(self, args: JSONDict) -> SmrControlClient:
        return SmrControlClient(
            api_key=_optional_string(args, "api_key"),
            backend_base=_optional_string(args, "backend_base"),
        )

    def _build_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="smr_health_check",
                description="Return a setup and connectivity health report for the managed research MCP server.",
                input_schema=_tool_schema(
                    {
                        "project_id": {
                            "type": "string",
                            "description": "Optional project id to validate project status access.",
                        }
                    },
                    required=[],
                ),
                handler=self._tool_health_check,
            ),
            *build_project_tools(self),
            *build_run_tools(self),
            *build_usage_tools(self),
            *build_approval_tools(self),
            *build_integration_tools(self),
            *build_log_tools(self),
            *build_artifact_tools(self),
        ]

    # Tool handlers -----------------------------------------------------

    def _tool_list_projects(self, args: JSONDict) -> Any:
        include_archived = _optional_bool(args, "include_archived", default=False)
        with self._client_from_args(args) as client:
            return client.list_projects(include_archived=include_archived)

    def _tool_get_project(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project(project_id)

    def _tool_get_project_status(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_status(project_id)

    def _tool_get_binding(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        run_id = _optional_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.get_binding(project_id, run_id=run_id)

    def _tool_promote_binding(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        pool_id = _require_string(args, "pool_id")
        dataset_revision = _require_string(args, "dataset_revision")
        expected_revision = _optional_int(args, "expected_revision")
        if expected_revision is None:
            raise ValueError("'expected_revision' is required")
        runtime_kind = _optional_string(args, "runtime_kind")
        environment_kind = _optional_string(args, "environment_kind")
        published_by_run_id = _optional_string(args, "published_by_run_id")
        reason = _optional_string(args, "reason")
        idempotency_key = _optional_string(args, "idempotency_key")
        with self._client_from_args(args) as client:
            return client.promote_binding(
                project_id,
                pool_id=pool_id,
                dataset_revision=dataset_revision,
                expected_revision=expected_revision,
                runtime_kind=runtime_kind,
                environment_kind=environment_kind,
                published_by_run_id=published_by_run_id,
                reason=reason,
                idempotency_key=idempotency_key,
            )

    def _tool_get_pool_context(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        run_id = _optional_string(args, "run_id")
        task_id = _optional_string(args, "task_id")
        with self._client_from_args(args) as client:
            return client.get_pool_context(project_id, run_id=run_id, task_id=task_id)

    def _tool_get_starting_data_upload_urls(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        dataset_ref = _optional_string(args, "dataset_ref")
        idempotency_key_upload = _optional_string(
            args, "idempotency_key_upload"
        ) or _optional_string(args, "idempotency_key")
        files = args.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError("'files' must be a non-empty array")

        normalized_files: list[JSONDict] = []
        for entry in files:
            if not isinstance(entry, dict):
                raise ValueError("each file entry must be an object")
            path = _require_string(entry, "path")
            normalized: JSONDict = {"path": path}
            content_type = _optional_string(entry, "content_type")
            if content_type:
                normalized["content_type"] = content_type
            normalized_files.append(normalized)

        with self._client_from_args(args) as client:
            return client.get_starting_data_upload_urls(
                project_id,
                files=normalized_files,
                dataset_ref=dataset_ref,
                idempotency_key_upload=idempotency_key_upload,
            )

    def _tool_upload_starting_data(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        dataset_ref = _optional_string(args, "dataset_ref")
        idempotency_key_upload = _optional_string(
            args, "idempotency_key_upload"
        ) or _optional_string(args, "idempotency_key")
        files = args.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError("'files' must be a non-empty array")

        normalized_files: list[JSONDict] = []
        for entry in files:
            if not isinstance(entry, dict):
                raise ValueError("each file entry must be an object")
            path = _require_string(entry, "path")
            content = entry.get("content")
            if not isinstance(content, str):
                raise ValueError("each file entry requires string 'content'")
            normalized: JSONDict = {"path": path, "content": content}
            content_type = _optional_string(entry, "content_type")
            if content_type:
                normalized["content_type"] = content_type
            normalized_files.append(normalized)

        with self._client_from_args(args) as client:
            kwargs: JSONDict = {
                "files": normalized_files,
                "dataset_ref": dataset_ref,
            }
            if idempotency_key_upload:
                kwargs["idempotency_key_upload"] = idempotency_key_upload
            return client.upload_starting_data_files(project_id, **kwargs)

    def _tool_trigger_run(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        timebox_seconds = _optional_int(args, "timebox_seconds")
        agent_model = _optional_string(args, "agent_model")
        agent_kind = _optional_string(args, "agent_kind")
        work_mode = _require_string(args, "work_mode")
        workflow = _optional_object(args, "workflow")
        idempotency_key_run_create = _optional_string(
            args, "idempotency_key_run_create"
        ) or _optional_string(args, "idempotency_key")
        with self._client_from_args(args) as client:
            return client.trigger_run(
                project_id,
                timebox_seconds=timebox_seconds,
                agent_model=agent_model,
                agent_kind=agent_kind,
                work_mode=work_mode,
                workflow=workflow,
                idempotency_key_run_create=idempotency_key_run_create,
            )

    def _tool_trigger_data_factory(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        dataset_ref = _require_string(args, "dataset_ref")
        bundle_manifest_path = _require_string(args, "bundle_manifest_path")
        work_mode = _require_string(args, "work_mode")
        profile = _optional_string(args, "profile") or "founder_default"
        source_mode = _optional_string(args, "source_mode") or "synth_mcp_local"
        template = _optional_string(args, "template")
        preferred_target = _optional_string(args, "preferred_target") or "harbor"
        strictness_mode = _optional_string(args, "strictness_mode") or "warn"
        timebox_seconds = _optional_int(args, "timebox_seconds")

        raw_targets = args.get("targets")
        targets: list[str] | None = None
        if raw_targets is not None:
            if not isinstance(raw_targets, list) or not raw_targets:
                raise ValueError("'targets' must be a non-empty array when provided")
            parsed_targets: list[str] = []
            for value in raw_targets:
                if not isinstance(value, str) or not value.strip():
                    raise ValueError("each targets entry must be a non-empty string")
                parsed_targets.append(value.strip())
            targets = parsed_targets

        runtime_kind = _optional_string(args, "runtime_kind")
        environment_kind = _optional_string(args, "environment_kind")
        session_id = _optional_string(args, "session_id")
        session_state = _optional_string(args, "session_state")
        session_title = _optional_string(args, "session_title")
        session_notes = _optional_string(args, "session_notes")
        idempotency_key_run_create = _optional_string(
            args, "idempotency_key_run_create"
        ) or _optional_string(args, "idempotency_key")

        with self._client_from_args(args) as client:
            return client.trigger_data_factory_run(
                project_id,
                work_mode=work_mode,
                dataset_ref=dataset_ref,
                bundle_manifest_path=bundle_manifest_path,
                template=template,
                profile=profile,
                source_mode=source_mode,
                targets=targets,
                preferred_target=preferred_target,
                runtime_kind=runtime_kind,
                environment_kind=environment_kind,
                session_id=session_id,
                session_state=session_state,
                session_title=session_title,
                session_notes=session_notes,
                strictness_mode=strictness_mode,
                timebox_seconds=timebox_seconds,
                idempotency_key_run_create=idempotency_key_run_create,
            )

    def _tool_data_factory_finalize(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        dataset_ref = _optional_string(args, "dataset_ref") or "starting-data"
        bundle_manifest_path = (
            _optional_string(args, "bundle_manifest_path") or "capture_bundle.json"
        )
        template = _optional_string(args, "template")
        finalizer_profile = _optional_string(args, "finalizer_profile") or "founder_default"
        source_mode = _optional_string(args, "source_mode") or "synth_mcp_local"
        preferred_target = _optional_string(args, "preferred_target") or "harbor"
        strictness_mode = _optional_string(args, "strictness_mode") or "warn"
        runtime_kind = _optional_string(args, "runtime_kind")
        environment_kind = _optional_string(args, "environment_kind")
        timebox_seconds = _optional_int(args, "timebox_seconds")
        idempotency_key_run_create = _optional_string(
            args, "idempotency_key_run_create"
        ) or _optional_string(args, "idempotency_key")

        raw_target_formats = args.get("target_formats")
        target_formats: list[str] | None = None
        if raw_target_formats is not None:
            if not isinstance(raw_target_formats, list) or not raw_target_formats:
                raise ValueError("'target_formats' must be a non-empty array when provided")
            parsed_target_formats: list[str] = []
            for value in raw_target_formats:
                if not isinstance(value, str) or not value.strip():
                    raise ValueError("each target_formats entry must be a non-empty string")
                parsed_target_formats.append(value.strip())
            target_formats = parsed_target_formats

        with self._client_from_args(args) as client:
            return client.data_factory_finalize(
                project_id,
                dataset_ref=dataset_ref,
                bundle_manifest_path=bundle_manifest_path,
                template=template,
                target_formats=target_formats,
                preferred_target=preferred_target,
                finalizer_profile=finalizer_profile,
                source_mode=source_mode,
                runtime_kind=runtime_kind,
                environment_kind=environment_kind,
                strictness_mode=strictness_mode,
                timebox_seconds=timebox_seconds,
                idempotency_key_run_create=idempotency_key_run_create,
            )

    def _tool_data_factory_finalize_status(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        job_id = _require_string(args, "job_id")
        with self._client_from_args(args) as client:
            return client.data_factory_finalize_status(project_id, job_id)

    def _tool_data_factory_publish(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        job_id = _require_string(args, "job_id")
        reason = _optional_string(args, "reason") or "manual_publish"
        idempotency_key_publish = _optional_string(
            args, "idempotency_key_publish"
        ) or _optional_string(args, "idempotency_key")
        with self._client_from_args(args) as client:
            return client.data_factory_publish(
                project_id,
                job_id,
                reason=reason,
                idempotency_key_publish=idempotency_key_publish,
            )

    def _tool_set_agent_config(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        model = _optional_string(args, "model")
        agent_kind = _optional_string(args, "agent_kind")
        if model is None and agent_kind is None:
            raise ValueError("at least one of 'model' or 'agent_kind' is required")
        with self._client_from_args(args) as client:
            return client.set_agent_config(project_id, model=model, agent_kind=agent_kind)

    def _tool_list_runs(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        active_only = _optional_bool(args, "active_only", default=False)
        with self._client_from_args(args) as client:
            if active_only:
                return client.list_active_runs(project_id)
            return client.list_runs(project_id)

    def _tool_list_jobs(self, args: JSONDict) -> Any:
        project_id = _optional_string(args, "project_id")
        state = _optional_string(args, "state")
        active_only = _optional_bool(args, "active_only", default=False)
        limit = _optional_int(args, "limit") or 50
        with self._client_from_args(args) as client:
            return client.list_jobs(
                project_id=project_id,
                state=state,
                active_only=active_only,
                limit=limit,
            )

    def _tool_get_run(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        project_id = _optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_run(run_id, project_id=project_id)

    def _tool_get_run_usage(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        project_id = _optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_run_usage(run_id, project_id=project_id)

    def _tool_get_actor_status(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        run_id = _optional_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.get_actor_status(project_id, run_id=run_id)

    def _tool_control_actor(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        run_id = _require_string(args, "run_id")
        actor_id = _require_string(args, "actor_id")
        action = _require_string(args, "action")
        if action not in {"pause", "resume"}:
            raise ValueError("'action' must be 'pause' or 'resume'")
        reason = _optional_string(args, "reason")
        idempotency_key = _optional_string(args, "idempotency_key")
        with self._client_from_args(args) as client:
            return client.control_actor(
                project_id,
                run_id,
                actor_id,
                action=action,  # type: ignore[arg-type]
                reason=reason,
                idempotency_key=idempotency_key,
            )

    def _tool_pause_run(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.pause_run(run_id)

    def _tool_resume_run(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.resume_run(run_id)

    def _tool_stop_run(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.stop_run(run_id)

    def _tool_list_project_questions(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        status_filter = _optional_string(args, "status_filter") or "pending"
        with self._client_from_args(args) as client:
            return client.list_project_questions(project_id, status_filter=status_filter)

    def _tool_respond_question(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        question_id = _require_string(args, "question_id")
        response_text = _require_string(args, "response_text")
        project_id = _optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.respond_question(
                run_id,
                question_id,
                response_text=response_text,
                project_id=project_id,
            )

    def _tool_list_project_approvals(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        status_filter = _optional_string(args, "status_filter") or "pending"
        with self._client_from_args(args) as client:
            return client.list_project_approvals(project_id, status_filter=status_filter)

    def _tool_resolve_approval(self, args: JSONDict) -> Any:
        decision = _require_string(args, "decision")
        run_id = _require_string(args, "run_id")
        approval_id = _require_string(args, "approval_id")
        comment = _optional_string(args, "comment")
        project_id = _optional_string(args, "project_id")

        with self._client_from_args(args) as client:
            if decision == "approve":
                return client.approve(run_id, approval_id, comment=comment, project_id=project_id)
            if decision == "deny":
                return client.deny(run_id, approval_id, comment=comment, project_id=project_id)
        raise ValueError("'decision' must be 'approve' or 'deny'")

    def _tool_get_usage(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_usage(project_id)

    def _tool_get_ops_status(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        include_done_tasks = args.get("include_done_tasks")
        if include_done_tasks is not None and not isinstance(include_done_tasks, bool):
            raise ValueError("'include_done_tasks' must be a boolean when provided")
        with self._client_from_args(args) as client:
            return client.get_ops_status(project_id, include_done_tasks=include_done_tasks)

    def _tool_codex_subscription_status(self, args: JSONDict) -> Any:
        project_id = _optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.chatgpt_connection_status(project_id=project_id)

    def _tool_codex_subscription_connect_start(self, args: JSONDict) -> Any:
        sandbox_agent_url = _optional_string(args, "sandbox_agent_url")
        provider_id = _optional_string(args, "provider_id")
        external_account_hint = _optional_string(args, "external_account_hint")
        with self._client_from_args(args) as client:
            return client.chatgpt_connect_start(
                sandbox_agent_url=sandbox_agent_url,
                provider_id=provider_id,
                external_account_hint=external_account_hint,
            )

    def _tool_codex_subscription_connect_complete(self, args: JSONDict) -> Any:
        code = _optional_string(args, "code")
        sandbox_agent_url = _optional_string(args, "sandbox_agent_url")
        with self._client_from_args(args) as client:
            return client.chatgpt_connect_complete(code=code, sandbox_agent_url=sandbox_agent_url)

    def _tool_codex_subscription_disconnect(self, args: JSONDict) -> Any:
        with self._client_from_args(args) as client:
            return client.chatgpt_disconnect()

    def _tool_github_org_status(self, args: JSONDict) -> Any:
        with self._client_from_args(args) as client:
            return client.github_org_status()

    def _tool_github_org_oauth_start(self, args: JSONDict) -> Any:
        redirect_uri = _optional_string(args, "redirect_uri")
        with self._client_from_args(args) as client:
            return client.github_org_oauth_start(redirect_uri=redirect_uri)

    def _tool_github_org_oauth_callback(self, args: JSONDict) -> Any:
        code = _require_string(args, "code")
        state = _optional_string(args, "state")
        redirect_uri = _optional_string(args, "redirect_uri")
        with self._client_from_args(args) as client:
            return client.github_org_oauth_callback(
                code=code,
                state=state,
                redirect_uri=redirect_uri,
            )

    def _tool_github_org_disconnect(self, args: JSONDict) -> Any:
        with self._client_from_args(args) as client:
            return client.github_org_disconnect()

    def _tool_linear_status(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.linear_status(project_id)

    def _tool_linear_oauth_start(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        redirect_uri = _optional_string(args, "redirect_uri")
        with self._client_from_args(args) as client:
            return client.linear_oauth_start(project_id=project_id, redirect_uri=redirect_uri)

    def _tool_linear_oauth_callback(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        code = _require_string(args, "code")
        state = _optional_string(args, "state")
        redirect_uri = _optional_string(args, "redirect_uri")
        with self._client_from_args(args) as client:
            return client.linear_oauth_callback(
                project_id=project_id,
                code=code,
                state=state,
                redirect_uri=redirect_uri,
            )

    def _tool_linear_disconnect(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.linear_disconnect(project_id)

    def _tool_linear_list_teams(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.linear_list_teams(project_id)

    def _tool_set_execution_preferences(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        preferred_lane = _require_string(args, "preferred_lane")
        if preferred_lane not in {"auto", "synth_hosted", "user_connected"}:
            raise ValueError("'preferred_lane' must be one of: auto, synth_hosted, user_connected")
        allow_fallback_to_synth = args.get("allow_fallback_to_synth")
        if allow_fallback_to_synth is not None and not isinstance(allow_fallback_to_synth, bool):
            raise ValueError("'allow_fallback_to_synth' must be a boolean when provided")
        free_tier_eligible = args.get("free_tier_eligible")
        if free_tier_eligible is not None and not isinstance(free_tier_eligible, bool):
            raise ValueError("'free_tier_eligible' must be a boolean when provided")
        monthly_soft_limit_tokens = args.get("monthly_soft_limit_tokens")
        if monthly_soft_limit_tokens is not None and not isinstance(monthly_soft_limit_tokens, int):
            raise ValueError("'monthly_soft_limit_tokens' must be an integer when provided")
        with self._client_from_args(args) as client:
            return client.set_execution_preferences(
                project_id,
                preferred_lane=preferred_lane,  # type: ignore[arg-type]
                allow_fallback_to_synth=allow_fallback_to_synth,
                free_tier_eligible=free_tier_eligible,
                monthly_soft_limit_tokens=monthly_soft_limit_tokens,
            )

    def _tool_get_capacity_lane_preview(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_capacity_lane_preview(project_id)

    # Project lifecycle mutations ---------------------------------------

    def _tool_create_project(self, args: JSONDict) -> Any:
        name = _require_string(args, "name")
        config = args.get("config") or {}
        if not isinstance(config, dict):
            raise ValueError("'config' must be a JSON object when provided")
        payload: JSONDict = {"name": name, **config}
        with self._client_from_args(args) as client:
            return client.create_project(payload)

    def _tool_get_project_repos(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_repos(project_id)

    def _tool_link_org_github(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.link_org_github(project_id)

    def _tool_add_project_repo(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        repo = _require_string(args, "repo")
        pr_write_enabled = _optional_bool(args, "pr_write_enabled", default=False)
        with self._client_from_args(args) as client:
            return client.add_project_repo(
                project_id,
                repo=repo,
                pr_write_enabled=pr_write_enabled,
            )

    def _tool_remove_project_repo(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        repo = _require_string(args, "repo")
        with self._client_from_args(args) as client:
            return client.remove_project_repo(project_id, repo=repo)

    def _tool_pause_project(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.pause_project(project_id)

    def _tool_resume_project(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.resume_project(project_id)

    def _tool_archive_project(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.archive_project(project_id)

    def _tool_unarchive_project(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.unarchive_project(project_id)

    # Logs --------------------------------------------------------------

    def _tool_get_run_logs(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        run_id = _require_string(args, "run_id")
        task_key = _optional_string(args, "task_key")
        component = _optional_string(args, "component")
        limit_raw = _optional_int(args, "limit")
        limit = limit_raw if limit_raw is not None else 200
        start = _optional_string(args, "start")
        end = _optional_string(args, "end")
        with self._client_from_args(args) as client:
            return client.get_run_logs(
                project_id,
                run_id,
                task_key=task_key,
                component=component,
                limit=limit,
                start=start,
                end=end,
            )

    def _tool_search_project_logs(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        q = _optional_string(args, "q")
        run_id = _optional_string(args, "run_id")
        service = _optional_string(args, "service")
        limit_raw = _optional_int(args, "limit")
        limit = limit_raw if limit_raw is not None else 200
        start = _optional_string(args, "start")
        end = _optional_string(args, "end")
        with self._client_from_args(args) as client:
            return client.search_victoria_logs(
                project_id,
                q=q,
                run_id=run_id,
                service=service,
                limit=limit,
                start=start,
                end=end,
            )

    # Artifacts + results -----------------------------------------------

    def _tool_list_run_artifacts(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        project_id = _optional_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.list_run_artifacts(run_id, project_id=project_id)

    def _tool_get_artifact(self, args: JSONDict) -> Any:
        artifact_id = _require_string(args, "artifact_id")
        with self._client_from_args(args) as client:
            return client.get_artifact(artifact_id)

    def _tool_get_artifact_content(self, args: JSONDict) -> Any:
        artifact_id = _require_string(args, "artifact_id")
        disposition = _optional_string(args, "disposition") or "inline"
        if disposition not in {"inline", "attachment"}:
            raise ValueError("'disposition' must be 'inline' or 'attachment'")
        max_bytes_raw = _optional_int(args, "max_bytes")
        max_bytes = max_bytes_raw if max_bytes_raw is not None else 200_000
        if max_bytes <= 0:
            raise ValueError("'max_bytes' must be a positive integer")

        with self._client_from_args(args) as client:
            artifact = client.get_artifact(artifact_id)
            response = client.get_artifact_content_response(
                artifact_id,
                disposition=disposition,
                follow_redirects=True,
            )
            content_bytes = response.content or b""

        preview = preview_binary_payload(content_bytes, max_bytes=max_bytes)

        return {
            "artifact_id": artifact_id,
            "artifact_type": artifact.get("artifact_type"),
            "title": artifact.get("title"),
            "uri": artifact.get("uri"),
            "content_type": response.headers.get("content-type"),
            "encoding": preview.encoding,
            "content": preview.content,
            "content_bytes_returned": preview.content_bytes_returned,
            "content_bytes_total": preview.content_bytes_total,
            "truncated": preview.truncated,
            "max_bytes": max_bytes,
        }

    def _tool_list_run_pull_requests(self, args: JSONDict) -> Any:
        run_id = _require_string(args, "run_id")
        project_id = _optional_string(args, "project_id")
        limit_raw = _optional_int(args, "limit")
        limit = limit_raw if limit_raw is not None else 100
        if limit <= 0:
            raise ValueError("'limit' must be a positive integer")
        with self._client_from_args(args) as client:
            return client.list_run_pull_requests(
                run_id,
                project_id=project_id,
                limit=limit,
            )

    def _tool_get_run_results(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        run_id = _require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.get_run_results(project_id, run_id)

    def _tool_get_project_git_status(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        with self._client_from_args(args) as client:
            return client.get_project_git_status(project_id)

    def _tool_get_orchestrator_status(self, args: JSONDict) -> Any:
        project_id = _require_string(args, "project_id")
        run_id = _require_string(args, "run_id")
        with self._client_from_args(args) as client:
            return client.get_run_orchestrator_status(project_id, run_id)

    def _tool_health_check(self, args: JSONDict) -> Any:
        project_id = _optional_string(args, "project_id")
        backend_base = _optional_string(args, "backend_base")
        api_key_override = _optional_string(args, "api_key")
        resolved_backend_base = (
            backend_base
            or os.environ.get("SYNTH_BACKEND_URL", "").strip()
            or "https://api.usesynth.ai"
        )
        try:
            resolved_api_key = api_key_override or get_api_key("SYNTH_API_KEY", required=False)
        except Exception:
            resolved_api_key = api_key_override or os.environ.get("SYNTH_API_KEY", "").strip()
        api_key_present = bool(resolved_api_key)
        tools = self.available_tool_names()
        checks: JSONDict = {
            "api_key": {
                "status": "pass" if api_key_present else "fail",
                "message": (
                    "Synth API key available."
                    if api_key_present
                    else "No Synth API key was resolved from args, environment, or Synth config."
                ),
                "hint": (
                    None
                    if api_key_present
                    else "Export SYNTH_API_KEY before launching your MCP client."
                ),
            },
            "mcp_server": {
                "status": "pass",
                "server_name": SERVER_NAME,
                "server_version": __version__,
                "protocol_version": DEFAULT_PROTOCOL_VERSION,
                "supported_protocol_versions": list(SUPPORTED_PROTOCOL_VERSIONS),
                "tool_count": len(tools),
            },
        }
        ok = api_key_present

        try:
            with self._client_from_args(args) as client:
                capabilities = client.get_capabilities()
                backend_check: JSONDict = {
                    "status": "pass",
                    "backend_url": resolved_backend_base,
                    "capability_keys": sorted(capabilities.keys())
                    if isinstance(capabilities, dict)
                    else [],
                }
                if isinstance(capabilities, dict):
                    for key in ("version", "backend_version", "api_version", "build_sha"):
                        value = capabilities.get(key)
                        if isinstance(value, str) and value.strip():
                            backend_check["backend_version"] = value.strip()
                            break
                checks["backend_ping"] = backend_check

                projects = client.list_projects(limit=1)
                checks["project_access"] = {
                    "status": "pass",
                    "project_count_sampled": len(projects),
                }

                if project_id:
                    project_status = client.get_project_status(project_id)
                    checks["project_status"] = {
                        "status": "pass",
                        "project_id": project_id,
                        "project_status_keys": sorted(project_status.keys())
                        if isinstance(project_status, dict)
                        else [],
                    }
        except Exception as exc:
            checks["backend_ping"] = {
                "status": "fail",
                "backend_url": resolved_backend_base,
                "message": f"{type(exc).__name__}: {exc}",
                "hint": "Verify SYNTH_API_KEY, SYNTH_BACKEND_URL, and backend availability.",
            }
            checks.setdefault(
                "project_access",
                {
                    "status": "fail",
                    "message": "Project access check skipped after backend failure.",
                },
            )
            ok = False
        else:
            ok = ok and True

        return {
            "ok": ok
            and all(
                isinstance(check, dict) and check.get("status") == "pass"
                for check in checks.values()
            ),
            "backend_url": resolved_backend_base,
            "project_id": project_id,
            "checks": checks,
            "tooling": {
                "mcp_server": SERVER_NAME,
                "mcp_server_version": __version__,
            },
            "recommended_next_steps": [
                "Register `managed-research-mcp` with your MCP client.",
                "Export SYNTH_API_KEY before launching the MCP server.",
            ],
        }

    # Protocol ----------------------------------------------------------

    def list_tools(self) -> list[JSONDict]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in self._tools.values()
        ]

    def _handle_initialize(self, params: JSONDict | None) -> JSONDict:
        requested_version = None
        if isinstance(params, dict):
            requested_version = params.get("protocolVersion")

        protocol_version = DEFAULT_PROTOCOL_VERSION
        if isinstance(requested_version, str) and requested_version in SUPPORTED_PROTOCOL_VERSIONS:
            protocol_version = requested_version

        return {
            "protocolVersion": protocol_version,
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {},
                "prompts": {},
            },
            "serverInfo": {
                "name": SERVER_NAME,
                "version": __version__,
            },
            "instructions": (
                "Use tools to control managed research projects and runs. "
                "All tool outputs are JSON-encoded in text content blocks."
            ),
        }

    def _handle_tools_call(self, params: JSONDict | None) -> JSONDict:
        if not isinstance(params, dict):
            return self._tool_error("Invalid params for tools/call")

        name = params.get("name")
        if not isinstance(name, str) or not name.strip():
            return self._tool_error("Tool call is missing a valid 'name'")

        tool = self._tools.get(name)
        if tool is None:
            return self._tool_error(f"Unknown tool: {name}")

        arguments = params.get("arguments", {})
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return self._tool_error("Tool 'arguments' must be a JSON object")

        try:
            result = tool.handler(arguments)
        except Exception as exc:
            return self._tool_error(f"{type(exc).__name__}: {exc}")

        text = json.dumps(result, indent=2, default=str)
        return {"content": [{"type": "text", "text": text}]}

    def _tool_error(self, message: str) -> JSONDict:
        return {
            "content": [{"type": "text", "text": message}],
            "isError": True,
        }

    def dispatch(self, method: str, params: JSONDict | None) -> JSONDict:
        if method == "initialize":
            return self._handle_initialize(params)
        if method == "ping":
            return {}
        if method == "tools/list":
            return {"tools": self.list_tools()}
        if method == "tools/call":
            return self._handle_tools_call(params)
        if method == "resources/list":
            return {"resources": []}
        if method == "prompts/list":
            return {"prompts": []}
        raise RpcError(-32601, f"Method not found: {method}")

    def handle_notification(self, method: str, _params: JSONDict | None) -> None:
        # No-op, but keep known notifications explicit.
        if method == "notifications/initialized":
            return

    def handle_request(self, message: JSONDict) -> JSONDict:
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params")

        if not isinstance(method, str):
            return _jsonrpc_error(request_id, -32600, "Invalid request: missing method")

        try:
            result = self.dispatch(method, params if isinstance(params, dict) else None)
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except RpcError as exc:
            return _jsonrpc_error(request_id, exc.code, exc.message, data=exc.data)
        except Exception as exc:
            return _jsonrpc_error(request_id, -32603, f"Internal error: {exc}")


def _jsonrpc_error(
    request_id: Any, code: int, message: str, *, data: Any | None = None
) -> JSONDict:
    error: JSONDict = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def _read_message(stdin: Any) -> tuple[JSONDict | None, str | None]:
    headers: dict[str, str] = {}

    while True:
        line = stdin.readline()
        if line == b"":
            return None, None
        stripped = line.strip()
        if not stripped:
            if headers:
                break
            continue
        # Codex CLI sends newline-delimited JSON-RPC requests on stdio during MCP startup.
        # Accept that form in addition to Content-Length framed messages.
        if not headers and stripped[:1] in (b"{", b"["):
            try:
                message = json.loads(stripped.decode("utf-8"))
            except Exception as exc:
                raise ValueError(f"Invalid JSON payload: {exc}") from exc
            if not isinstance(message, dict):
                raise ValueError("JSON-RPC message must be a JSON object")
            return message, "jsonl"
        if line in (b"\r\n", b"\n"):
            break

        try:
            text = line.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Invalid header encoding: {exc}") from exc

        if ":" not in text:
            continue
        key, value = text.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    raw_length = headers.get("content-length")
    if raw_length is None:
        raise ValueError("Missing Content-Length header")

    try:
        content_length = int(raw_length)
    except ValueError as exc:
        raise ValueError(f"Invalid Content-Length: {raw_length}") from exc

    if content_length < 0:
        raise ValueError("Content-Length must be non-negative")

    payload = stdin.read(content_length)
    if len(payload) != content_length:
        raise ValueError("Unexpected EOF while reading message body")

    try:
        message = json.loads(payload.decode("utf-8"))
    except Exception as exc:
        raise ValueError(f"Invalid JSON payload: {exc}") from exc

    if not isinstance(message, dict):
        raise ValueError("JSON-RPC message must be a JSON object")
    return message, "content-length"


def _write_message(stdout: Any, message: JSONDict, mode: str = "content-length") -> None:
    payload = json.dumps(message, separators=(",", ":"), default=str).encode("utf-8")
    if mode == "jsonl":
        stdout.write(payload + b"\n")
    else:
        header = f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii")
        stdout.write(header)
        stdout.write(payload)
    stdout.flush()


def run_stdio_server() -> None:
    """Run the MCP server using stdio transport."""
    server = ManagedResearchMcpServer()
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    response_mode = "content-length"

    while True:
        try:
            message, message_mode = _read_message(stdin)
            if message_mode is not None:
                response_mode = message_mode
        except Exception as exc:
            _write_message(
                stdout, _jsonrpc_error(None, -32700, f"Parse error: {exc}"), response_mode
            )
            continue

        if message is None:
            break

        method = message.get("method")
        request_id = message.get("id")

        if isinstance(method, str) and request_id is None:
            server.handle_notification(
                method, message.get("params") if isinstance(message.get("params"), dict) else None
            )
            continue

        if isinstance(method, str):
            _write_message(stdout, server.handle_request(message), response_mode)
            continue

        _write_message(
            stdout,
            _jsonrpc_error(message.get("id"), -32600, "Invalid request"),
            response_mode,
        )


def main() -> None:
    """CLI entrypoint for the Managed Research MCP server."""
    run_stdio_server()


__all__ = ["ManagedResearchMcpServer", "main", "run_stdio_server"]


if __name__ == "__main__":
    main()
