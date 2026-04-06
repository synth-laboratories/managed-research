"""Project-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_project_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_health_check",
            description="Return a connectivity and setup report for the managed-research MCP server.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Optional project id to verify access.",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=[],
            ),
            handler=server._tool_health_check,
        ),
        ToolDefinition(
            name="smr_create_project",
            description="Create a managed research project.",
            input_schema=tool_schema(
                {
                    "name": {"type": "string", "description": "Human-readable project name."},
                    "config": {
                        "type": "object",
                        "description": "Additional project configuration payload.",
                    },
                },
                required=[],
            ),
            handler=server._tool_create_project,
        ),
        ToolDefinition(
            name="smr_list_projects",
            description="List managed research projects.",
            input_schema=tool_schema(
                {
                    "include_archived": {
                        "type": "boolean",
                        "description": "Include archived projects.",
                    },
                    "limit": {"type": "integer", "description": "Maximum projects to return."},
                },
                required=[],
            ),
            handler=server._tool_list_projects,
        ),
        ToolDefinition(
            name="smr_get_project",
            description="Fetch a managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project,
        ),
        ToolDefinition(
            name="smr_patch_project",
            description="Patch a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "config": {
                        "type": "object",
                        "description": "Partial project fields to update.",
                    },
                },
                required=["project_id", "config"],
            ),
            handler=server._tool_patch_project,
        ),
        ToolDefinition(
            name="smr_get_project_status",
            description="Fetch a polling-friendly status snapshot for a project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project_status,
        ),
        ToolDefinition(
            name="smr_get_project_entitlement",
            description="Fetch the managed-research entitlement status for a project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project_entitlement,
        ),
        ToolDefinition(
            name="smr_get_project_notes",
            description="Fetch the durable notebook text for a managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project_notes,
        ),
        ToolDefinition(
            name="smr_set_project_notes",
            description="Replace the durable notebook text for a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "notes": {"type": "string", "description": "Notebook text to store."},
                },
                required=["project_id", "notes"],
            ),
            handler=server._tool_set_project_notes,
        ),
        ToolDefinition(
            name="smr_append_project_notes",
            description="Append text to the durable notebook for a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "notes": {"type": "string", "description": "Notebook text to append."},
                },
                required=["project_id", "notes"],
            ),
            handler=server._tool_append_project_notes,
        ),
        ToolDefinition(
            name="smr_pause_project",
            description="Pause a managed research project so new runs cannot start.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_pause_project,
        ),
        ToolDefinition(
            name="smr_resume_project",
            description="Resume a paused managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_resume_project,
        ),
        ToolDefinition(
            name="smr_archive_project",
            description="Archive a managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_archive_project,
        ),
        ToolDefinition(
            name="smr_unarchive_project",
            description="Unarchive a managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_unarchive_project,
        ),
        ToolDefinition(
            name="smr_get_capabilities",
            description=(
                "Fetch server capabilities for parity-safe client behavior. "
                "Run trigger maps backend ``error_code`` payloads (limits, routing, "
                "credits, project budget, managed inference) to structured MCP results."
            ),
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_get_capabilities,
        ),
        ToolDefinition(
            name="smr_get_limits",
            description="Fetch resource limits for the authenticated org's plan. This is informative only; trigger and blockers remain authoritative.",
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_get_limits,
        ),
        ToolDefinition(
            name="smr_get_capacity_lane_preview",
            description=(
                "Preview the preferred/resolved capacity lane before launch. "
                "Call this before smr_get_run_start_blockers or smr_trigger_run when you need a user-facing launch check."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_capacity_lane_preview,
        ),
        ToolDefinition(
            name="smr_get_run_start_blockers",
            description=(
                "Return ordered launch blockers for the same payload shape used by smr_trigger_run. "
                "Use this before trigger when you want a clear 'can I launch?' answer."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "host_kind": {
                        "type": "string",
                        "description": "Execution substrate for this run: local, docker, or daytona.",
                    },
                    "work_mode": {
                        "type": "string",
                        "enum": ["open_ended_discovery", "directed_effort"],
                        "description": "Run work mode.",
                    },
                    "worker_pool_id": {
                        "type": "string",
                        "description": "Optional worker pool override.",
                    },
                    "timebox_seconds": {"type": "integer", "description": "Optional run timebox."},
                    "agent_profile": {
                        "type": "string",
                        "description": "Optional agent profile override.",
                    },
                    "agent_model": {
                        "type": "string",
                        "description": "Optional run-level agent model override.",
                    },
                    "agent_kind": {
                        "type": "string",
                        "description": "Optional run-level agent kind override.",
                    },
                    "agent_model_params": {
                        "type": "object",
                        "description": "Optional agent model params override (for example reasoning_effort).",
                    },
                    "initial_runtime_messages": {
                        "type": "array",
                        "description": "Optional kickoff runtime messages to enqueue durably before the run starts. Use this instead of the removed prompt field.",
                        "items": {"type": "object"},
                    },
                    "workflow": {"type": "object", "description": "Optional workflow override."},
                    "sandbox_override": {
                        "type": "object",
                        "description": "Optional sandbox override.",
                    },
                    "idempotency_key_run_create": {
                        "type": "string",
                        "description": "Optional idempotency key for the launch request.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Deprecated compatibility alias for idempotency_key_run_create.",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id", "host_kind", "work_mode"],
            ),
            handler=server._tool_get_run_start_blockers,
        ),
        ToolDefinition(
            name="smr_get_workspace_download_url",
            description=(
                "Return a short-lived presigned URL to download the project workspace as a tarball "
                "(git snapshot archived by the backend). Use smr_download_workspace_archive to save "
                "the file locally in one step, or fetch download_url with curl yourself."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_workspace_download_url,
        ),
        ToolDefinition(
            name="smr_get_project_git",
            description=(
                "Read-only git metadata for the project workspace (commit, branch, remote-related fields). "
                "Pair with smr_get_workspace_download_url or smr_download_workspace_archive to retrieve files."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_project_git,
        ),
        ToolDefinition(
            name="smr_download_workspace_archive",
            description=(
                "Download the project workspace tarball to a path on the machine running this MCP server "
                "(presigned URL under the hood). Parent directories are created. Large repos may take minutes; "
                "raise timeout_seconds if needed (default 600)."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "output_path": {
                        "type": "string",
                        "description": "Absolute or home-relative path for the .tar.gz file (e.g. ~/smr-workspace.tar.gz).",
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "HTTP timeout for the presigned download in seconds (default 600).",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id", "output_path"],
            ),
            handler=server._tool_download_workspace_archive,
        ),
    ]


__all__ = ["build_project_tools"]
