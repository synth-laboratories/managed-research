"""Usage MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_usage_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_get_billing_entitlements",
            description="Fetch the canonical org-level entitlement snapshot.",
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_get_billing_entitlements,
        ),
        ToolDefinition(
            name="smr_get_run_usage",
            description="Fetch canonical nominal, billed, internal, token, and breakdown usage for a run.",
            input_schema=tool_schema(
                {
                    "run_id": {
                        "type": "string",
                        "description": "Run id.",
                    },
                },
                required=["run_id"],
            ),
            handler=server._tool_get_run_usage,
        ),
        ToolDefinition(
            name="smr_get_project_usage",
            description="Fetch canonical project usage rollups and budgets.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Project id.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_project_usage,
        ),
        ToolDefinition(
            name="smr_get_project_economics",
            description="Fetch canonical project economics: usage, entitlements, and overlay posture.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Project id.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_project_economics,
        ),
    ]


__all__ = ["build_usage_tools"]
