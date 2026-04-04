"""Run-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_run_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_trigger_run",
            description="Trigger a managed research run.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "work_mode": {
                        "type": "string",
                        "enum": ["open_ended_discovery", "directed_effort"],
                        "description": "Run work mode.",
                    },
                    "timebox_seconds": {"type": "integer", "description": "Optional run timebox."},
                    "agent_model": {"type": "string", "description": "Optional run-level agent model override."},
                    "agent_kind": {"type": "string", "description": "Optional run-level agent kind override."},
                    "prompt": {"type": "string", "description": "Optional bootstrap prompt override."},
                    "workflow": {"type": "object", "description": "Optional workflow override."},
                    "sandbox_override": {"type": "object", "description": "Optional sandbox override."},
                },
                required=["project_id", "work_mode"],
            ),
            handler=server._tool_trigger_run,
        ),
        ToolDefinition(
            name="smr_list_runs",
            description="List runs for a project.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "active_only": {"type": "boolean", "description": "Only return active runs."},
                    "state": {"type": "string", "description": "Optional run-state filter."},
                    "limit": {"type": "integer", "description": "Maximum runs to return."},
                },
                required=["project_id"],
            ),
            handler=server._tool_list_runs,
        ),
        ToolDefinition(
            name="smr_get_run",
            description="Fetch a run by id.",
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "Run id."},
                    "project_id": {"type": "string", "description": "Optional project-scoped route enforcement."},
                },
                required=["run_id"],
            ),
            handler=server._tool_get_run,
        ),
        ToolDefinition(
            name="smr_list_active_runs",
            description="List active runs for a project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_list_active_runs,
        ),
        ToolDefinition(
            name="smr_list_run_questions",
            description="List pending or historical questions for a run.",
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "Run id."},
                    "project_id": {"type": "string", "description": "Optional project-scoped route enforcement."},
                    "status_filter": {"type": "string", "description": "Optional question status filter."},
                    "limit": {"type": "integer", "description": "Maximum questions to return."},
                },
                required=["run_id"],
            ),
            handler=server._tool_list_run_questions,
        ),
        ToolDefinition(
            name="smr_create_run_checkpoint",
            description="Request a run checkpoint.",
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "Run id."},
                    "project_id": {"type": "string", "description": "Optional project-scoped route enforcement."},
                    "checkpoint_id": {"type": "string", "description": "Optional checkpoint id override."},
                    "reason": {"type": "string", "description": "Optional checkpoint reason."},
                },
                required=["run_id"],
            ),
            handler=server._tool_create_run_checkpoint,
        ),
        ToolDefinition(
            name="smr_list_run_checkpoints",
            description="List checkpoints for a run.",
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "Run id."},
                    "project_id": {"type": "string", "description": "Optional project-scoped route enforcement."},
                },
                required=["run_id"],
            ),
            handler=server._tool_list_run_checkpoints,
        ),
        ToolDefinition(
            name="smr_restore_run_checkpoint",
            description="Restore a run to a checkpoint.",
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "Run id."},
                    "project_id": {"type": "string", "description": "Optional project-scoped route enforcement."},
                    "checkpoint_id": {"type": "string", "description": "Optional checkpoint id override."},
                    "reason": {"type": "string", "description": "Optional restore reason."},
                },
                required=["run_id"],
            ),
            handler=server._tool_restore_run_checkpoint,
        ),
    ]


__all__ = ["build_run_tools"]
