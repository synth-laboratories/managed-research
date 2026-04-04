"""Progress-oriented MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_progress_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_get_project_readiness",
            description="Fetch a project readiness projection with blockers and recommended next actions.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project_readiness,
        ),
        ToolDefinition(
            name="smr_get_run_progress",
            description="Fetch a run progress projection with blockers and recommended next actions.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "run_id": {"type": "string", "description": "Run id."},
                },
                required=["project_id", "run_id"],
            ),
            handler=server._tool_get_run_progress,
        ),
    ]


__all__ = ["build_progress_tools"]
