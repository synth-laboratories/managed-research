"""Approval-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_approval_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_list_project_questions",
            description="List project-level pending questions.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "status_filter": {
                        "type": "string",
                        "description": "Question status filter.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_list_project_questions,
        ),
        ToolDefinition(
            name="smr_respond_question",
            description="Respond to a run question.",
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "Run id."},
                    "question_id": {"type": "string", "description": "Question id."},
                    "response_text": {"type": "string", "description": "Response text."},
                    "project_id": {
                        "type": "string",
                        "description": "Optional project id for project-scoped strict route.",
                    },
                },
                required=["run_id", "question_id", "response_text"],
            ),
            handler=server._tool_respond_question,
        ),
        ToolDefinition(
            name="smr_list_project_approvals",
            description="List project-level approvals.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "status_filter": {
                        "type": "string",
                        "description": "Approval status filter.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_list_project_approvals,
        ),
        ToolDefinition(
            name="smr_resolve_approval",
            description="Approve or deny an approval request.",
            input_schema=tool_schema(
                {
                    "decision": {
                        "type": "string",
                        "enum": ["approve", "deny"],
                        "description": "Decision to apply.",
                    },
                    "run_id": {"type": "string", "description": "Run id."},
                    "approval_id": {"type": "string", "description": "Approval id."},
                    "comment": {
                        "type": "string",
                        "description": "Optional decision comment.",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Optional project id for project-scoped strict route.",
                    },
                },
                required=["decision", "run_id", "approval_id"],
            ),
            handler=server._tool_resolve_approval,
        ),
    ]


__all__ = ["build_approval_tools"]
