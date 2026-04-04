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
                    "project_id": {"type": "string", "description": "Optional project id to verify access."},
                    "api_key": {"type": "string", "description": "Optional Synth API key override."},
                    "backend_base": {"type": "string", "description": "Optional backend base override."},
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
                    "config": {"type": "object", "description": "Additional project configuration payload."},
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
                    "include_archived": {"type": "boolean", "description": "Include archived projects."},
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
            name="smr_get_capabilities",
            description="Fetch server capabilities for parity-safe client behavior.",
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_get_capabilities,
        ),
        ToolDefinition(
            name="smr_get_limits",
            description="Fetch resource limits for the authenticated org's plan. Returns each resource with its cap, window, refresh cadence, and whether it is unlimited.",
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_get_limits,
        ),
    ]


__all__ = ["build_project_tools"]
