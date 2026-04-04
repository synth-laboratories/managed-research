"""Usage MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_usage_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_get_usage_analytics",
            description="Fetch gross usage vs billed amount analytics for an org or managed account.",
            input_schema=tool_schema(
                {
                    "subject_kind": {
                        "type": "string",
                        "enum": ["org", "managed_account"],
                        "description": "Analytics subject kind.",
                    },
                    "org_id": {"type": "string", "description": "Org id when querying org-scoped usage."},
                    "managed_account_id": {
                        "type": "string",
                        "description": "Managed pooled-account id when querying managed-account usage.",
                    },
                    "start_at": {"type": "string", "description": "Inclusive ISO datetime window start."},
                    "end_at": {"type": "string", "description": "Exclusive ISO datetime window end."},
                    "bucket": {
                        "type": "string",
                        "enum": ["AUTO", "HOUR", "DAY", "WEEK"],
                        "description": "Chart bucket size.",
                    },
                    "first": {"type": "integer", "description": "Maximum drilldown rows to return."},
                    "after": {"type": "string", "description": "Opaque pagination cursor from a previous response."},
                },
                required=["subject_kind", "start_at", "end_at", "bucket", "first"],
            ),
            handler=server._tool_get_usage_analytics,
        )
    ]


__all__ = ["build_usage_tools"]
