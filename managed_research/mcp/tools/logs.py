"""Log-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_log_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_get_run_logs",
            description=(
                "Query VictoriaLogs for a specific run. "
                "Returns structured log records with optional task/component filters."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Run id.",
                    },
                    "task_key": {
                        "type": "string",
                        "description": "Optional filter by task key.",
                    },
                    "component": {
                        "type": "string",
                        "description": "Optional filter by component (e.g. 'orchestrator', 'worker').",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of log records to return (default 200, max 1000).",
                    },
                    "start": {
                        "type": "string",
                        "description": "Optional RFC3339 start time filter.",
                    },
                    "end": {
                        "type": "string",
                        "description": "Optional RFC3339 end time filter.",
                    },
                },
                required=["project_id", "run_id"],
            ),
            handler=server._tool_get_run_logs,
        ),
        ToolDefinition(
            name="smr_search_project_logs",
            description=(
                "Free-text LogSQL search across VictoriaLogs for a project. "
                "Use smr_get_run_logs for structured run-scoped queries."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "q": {
                        "type": "string",
                        "description": "Optional free-text LogSQL query string.",
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Optional filter by run id.",
                    },
                    "service": {
                        "type": "string",
                        "description": "Optional filter by service name.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records (default 200).",
                    },
                    "start": {
                        "type": "string",
                        "description": "Optional RFC3339 start time filter.",
                    },
                    "end": {
                        "type": "string",
                        "description": "Optional RFC3339 end time filter.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_search_project_logs,
        ),
    ]


__all__ = ["build_log_tools"]
