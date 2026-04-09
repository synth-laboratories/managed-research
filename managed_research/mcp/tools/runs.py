"""Run-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema
from managed_research.models.smr_agent_models import SMR_AGENT_MODEL_VALUES
from managed_research.models.smr_actor_models import (
    SMR_ACTOR_SUBTYPE_VALUES,
    SMR_ACTOR_TYPE_VALUES,
)
from managed_research.models.smr_host_kinds import SMR_HOST_KIND_VALUES


def _actor_model_assignment_schema(*, field_label: str) -> dict[str, Any]:
    return {
        "type": "array",
        "description": field_label,
        "items": {
            "type": "object",
            "properties": {
                "actor_type": {
                    "type": "string",
                    "enum": list(SMR_ACTOR_TYPE_VALUES),
                },
                "actor_subtype": {
                    "type": "string",
                    "enum": list(SMR_ACTOR_SUBTYPE_VALUES),
                },
                "agent_model": {
                    "type": "string",
                    "enum": list(SMR_AGENT_MODEL_VALUES),
                },
                "agent_model_params": {
                    "type": "object",
                },
            },
            "required": ["actor_type", "actor_subtype", "agent_model"],
        },
    }


def build_run_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_trigger_run",
            description=(
                "Trigger a managed research run. Call smr_get_capacity_lane_preview and "
                "smr_get_run_start_blockers first when you want a user-facing launch check, "
                "and always branch on result.error in MCP clients."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "host_kind": {
                        "type": "string",
                        "enum": list(SMR_HOST_KIND_VALUES),
                        "description": "Execution substrate for this run: local, docker, or daytona.",
                    },
                    "work_mode": {
                        "type": "string",
                        "enum": ["open_ended_discovery", "directed_effort"],
                        "description": "Run work mode.",
                    },
                    "worker_pool_id": {
                        "type": "string",
                        "description": "Optional worker pool override.",
                    },
                    "timebox_seconds": {"type": "integer", "description": "Optional run timebox."},
                    "agent_profile": {
                        "type": "string",
                        "description": "Optional agent profile override. Prefer this when you want an exact backend-managed preset.",
                    },
                    "agent_model": {
                        "type": "string",
                        "enum": list(SMR_AGENT_MODEL_VALUES),
                        "description": "Optional run-level agent model override using a public model id such as gpt-5.4, gpt-5.4-nano, or gpt-oss-120b.",
                    },
                    "agent_kind": {
                        "type": "string",
                        "description": "Optional run-level agent kind override.",
                    },
                    "agent_model_params": {
                        "type": "object",
                        "description": "Optional agent model params override (for example reasoning_effort).",
                    },
                    "actor_model_overrides": _actor_model_assignment_schema(
                        field_label=(
                            "Optional actor-scoped model overrides keyed by actor_type "
                            "and actor_subtype."
                        )
                    ),
                    "initial_runtime_messages": {
                        "type": "array",
                        "description": "Optional kickoff runtime messages to enqueue durably before the run starts. Use this instead of the removed prompt field.",
                        "items": {"type": "object"},
                    },
                    "workflow": {"type": "object", "description": "Optional workflow override."},
                    "sandbox_override": {
                        "type": "object",
                        "description": "Optional sandbox override.",
                    },
                    "idempotency_key_run_create": {
                        "type": "string",
                        "description": "Optional idempotency key for the launch request.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Deprecated compatibility alias for idempotency_key_run_create.",
                    },
                },
                required=["project_id", "host_kind", "work_mode"],
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
                    "project_id": {
                        "type": "string",
                        "description": "Optional project-scoped route enforcement.",
                    },
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
                    "project_id": {
                        "type": "string",
                        "description": "Optional project-scoped route enforcement.",
                    },
                    "status_filter": {
                        "type": "string",
                        "description": "Optional question status filter.",
                    },
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
                    "project_id": {
                        "type": "string",
                        "description": "Optional project-scoped route enforcement.",
                    },
                    "checkpoint_id": {
                        "type": "string",
                        "description": "Optional checkpoint id override.",
                    },
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
                    "project_id": {
                        "type": "string",
                        "description": "Optional project-scoped route enforcement.",
                    },
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
                    "project_id": {
                        "type": "string",
                        "description": "Optional project-scoped route enforcement.",
                    },
                    "checkpoint_id": {
                        "type": "string",
                        "description": "Optional checkpoint id override.",
                    },
                    "reason": {"type": "string", "description": "Optional restore reason."},
                },
                required=["run_id"],
            ),
            handler=server._tool_restore_run_checkpoint,
        ),
    ]


__all__ = ["build_run_tools"]
