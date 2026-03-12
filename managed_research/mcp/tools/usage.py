"""Usage-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_usage_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_get_run_usage",
            description="Fetch run-level usage with charged-spend totals and ledger entries.",
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "Run id."},
                    "project_id": {
                        "type": "string",
                        "description": "Optional project id for project-scoped strict route.",
                    },
                },
                required=["run_id"],
            ),
            handler=server._tool_get_run_usage,
        ),
        ToolDefinition(
            name="smr_get_usage",
            description="Fetch project usage metrics.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_get_usage,
        ),
        ToolDefinition(
            name="smr_get_ops_status",
            description="Fetch ops/task status for a project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "include_done_tasks": {
                        "type": "boolean",
                        "description": "Include completed tasks in response.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_ops_status,
        ),
        ToolDefinition(
            name="smr_set_execution_preferences",
            description="Set execution lane preferences for a project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "preferred_lane": {
                        "type": "string",
                        "enum": ["auto", "synth_hosted", "user_connected"],
                        "description": "Preferred execution lane.",
                    },
                    "allow_fallback_to_synth": {
                        "type": "boolean",
                        "description": "Allow fallback to synth-hosted lane.",
                    },
                    "free_tier_eligible": {
                        "type": "boolean",
                        "description": "Mark project eligible for free-tier synth hosted lane.",
                    },
                    "monthly_soft_limit_tokens": {
                        "type": "integer",
                        "description": "Optional monthly soft token limit.",
                    },
                },
                required=["project_id", "preferred_lane"],
            ),
            handler=server._tool_set_execution_preferences,
        ),
        ToolDefinition(
            name="smr_get_capacity_lane_preview",
            description="Preview resolved execution lane for a project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_get_capacity_lane_preview,
        ),
    ]


__all__ = ["build_usage_tools"]
