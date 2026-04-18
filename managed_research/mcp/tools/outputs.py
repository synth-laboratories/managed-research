"""Results-stage output tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_output_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_results_outputs_list",
            description="List project outputs and deliverables.",
            input_schema=tool_schema(
                {"project_id": {"type": "string"}},
                required=["project_id"],
            ),
            handler=server._tool_results_outputs_list,
        )
    ]


__all__ = ["build_output_tools"]
