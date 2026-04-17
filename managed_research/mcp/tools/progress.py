"""Progress-oriented MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema
from managed_research.mcp.tools.smr_policy_schemas import run_policy_input_schema
from managed_research.models.smr_actor_models import (
    SMR_ACTOR_SUBTYPE_VALUES,
    SMR_ACTOR_TYPE_VALUES,
)
from managed_research.models.smr_agent_kinds import SMR_AGENT_KIND_VALUES
from managed_research.models.smr_agent_models import SMR_AGENT_MODEL_VALUES
from managed_research.models.smr_host_kinds import SMR_HOST_KIND_VALUES
from managed_research.models.smr_work_modes import SMR_WORK_MODE_VALUES


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


def build_progress_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_get_project_setup",
            description=(
                "Fetch the canonical project setup authority for a managed research "
                "project."
            ),
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project_setup,
        ),
        ToolDefinition(
            name="smr_prepare_project_setup",
            description=(
                "Run the explicit setup-authority preparation step before launch "
                "preflight and trigger."
            ),
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_prepare_project_setup,
        ),
        ToolDefinition(
            name="smr_get_launch_preflight",
            description=(
                "Fetch the canonical launch preflight for a concrete run request."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "host_kind": {
                        "type": "string",
                        "enum": list(SMR_HOST_KIND_VALUES),
                        "description": "Execution substrate for the launch.",
                    },
                    "work_mode": {
                        "type": "string",
                        "enum": list(SMR_WORK_MODE_VALUES),
                        "description": "Run work mode.",
                    },
                    "worker_pool_id": {"type": "string", "description": "Optional worker pool override."},
                    "timebox_seconds": {"type": "integer", "description": "Optional run timebox."},
                    "agent_profile": {"type": "string", "description": "Optional shared agent profile override."},
                    "agent_model": {
                        "type": "string",
                        "enum": list(SMR_AGENT_MODEL_VALUES),
                        "description": "Optional shared agent model override.",
                    },
                    "agent_kind": {
                        "type": "string",
                        "enum": list(SMR_AGENT_KIND_VALUES),
                        "description": "Optional agent kind override.",
                    },
                    "agent_model_params": {"type": "object", "description": "Optional model params override."},
                    "actor_model_overrides": _actor_model_assignment_schema(
                        field_label="Optional actor-scoped model overrides."
                    ),
                    "initial_runtime_messages": {"type": "array", "items": {"type": "object"}, "description": "Optional kickoff runtime messages."},
                    "workflow": {"type": "object", "description": "Optional workflow payload."},
                    "sandbox_override": {"type": "object", "description": "Optional sandbox override."},
                    "local_execution": {
                        "type": "object",
                        "description": "Explicit synth-dev local lane identity for slot-backed launches.",
                    },
                    "execution_profile": {
                        "type": "object",
                        "description": "Explicit product execution profile for local docker/daytona launches.",
                    },
                    "run_policy": run_policy_input_schema(),
                    "kickoff_contract": {
                        "type": "object",
                        "description": "Optional staged-run kickoff contract.",
                    },
                    "resource_bindings": {
                        "type": "object",
                        "description": "Optional Phase 3 run resource bindings for external repos and credential refs.",
                    },
                    "primary_parent_ref": {
                        "type": "object",
                        "description": "Optional existing project-scoped parent objective binding.",
                    },
                    "primary_parent": {
                        "type": "object",
                        "description": "Optional inline run-scoped parent objective creation payload.",
                    },
                    "idempotency_key_run_create": {"type": "string", "description": "Optional idempotency key."},
                    "idempotency_key": {"type": "string", "description": "Deprecated compatibility alias."},
                },
                required=["project_id", "host_kind", "work_mode"],
            ),
            handler=server._tool_get_launch_preflight,
        ),
    ]


__all__ = ["build_progress_tools"]
