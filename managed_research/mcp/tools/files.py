"""Work-stage file tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema
from managed_research.mcp.tools.resources import _FILE_ITEM_SCHEMA


def build_file_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_work_files_list",
            description="List project files for the work stage.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string"},
                    "visibility": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                required=["project_id"],
            ),
            handler=server._tool_list_project_files,
        ),
        ToolDefinition(
            name="smr_work_files_upload",
            description="Upload project files for the work stage.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string"},
                    "files": {
                        "type": "array",
                        "minItems": 1,
                        "items": _FILE_ITEM_SCHEMA,
                    },
                },
                required=["project_id", "files"],
            ),
            handler=server._tool_create_project_files,
        ),
    ]


__all__ = ["build_file_tools"]
