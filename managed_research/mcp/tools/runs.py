"""Run-related MCP tool definitions."""

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


def build_run_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_trigger_run",
            description=(
                "Trigger a managed research run. Follow the canonical setup -> "
                "launch-preflight -> trigger flow, and always branch on "
                "result.error in MCP clients."
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
                        "enum": list(SMR_WORK_MODE_VALUES),
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
                        "enum": list(SMR_AGENT_KIND_VALUES),
                        "description": (
                            "Optional run-level agent kind override. "
                            "Public managed-research currently supports only codex."
                        ),
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
                        "description": "Optional staged-run kickoff contract. This becomes the authoritative staged contract persisted on the run.",
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
            name="smr_get_run_logical_timeline",
            description=(
                "Read the operator-facing logical timeline for a run. "
                "Use this for actors, checkpoints, branch provenance, and queue "
                "chronology instead of the low-level runtime timeline."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "run_id": {"type": "string", "description": "Run id."},
                },
                required=["project_id", "run_id"],
            ),
            handler=server._tool_get_run_logical_timeline,
        ),
        ToolDefinition(
            name="smr_get_run_traces",
            description=(
                "Read persisted run traces for a run. "
                "Use this to inspect or download session-backed Codex traces and other persisted operator-facing trace artifacts."
            ),
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
            handler=server._tool_get_run_traces,
        ),
        ToolDefinition(
            name="smr_get_run_actor_usage",
            description=(
                "Read actor-centric usage for a run. "
                "Use this for truthful per-actor spend, provider, and model activity rather than guessing from worker config."
            ),
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
            handler=server._tool_get_run_actor_usage,
        ),
        ToolDefinition(
            name="smr_get_run_primary_parent",
            description="Fetch the bound primary parent objective for a run.",
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "Run id."},
                },
                required=["run_id"],
            ),
            handler=server._tool_get_run_primary_parent,
        ),
        ToolDefinition(
            name="smr_stop_run",
            description=(
                "Stop a queued or running run. Response includes "
                "`control_intent_id` and `control_intent_ack_at` so a replay "
                "of the same control correlates with the original intent."
            ),
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
            handler=server._tool_stop_run,
        ),
        ToolDefinition(
            name="smr_pause_run",
            description=(
                "Pause a live run without stopping it. Response includes "
                "`control_intent_id` and `control_intent_ack_at` for "
                "idempotent replay correlation."
            ),
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
            handler=server._tool_pause_run,
        ),
        ToolDefinition(
            name="smr_resume_run",
            description=(
                "Resume a paused run. Response includes `control_intent_id` "
                "and `control_intent_ack_at` for idempotent replay correlation."
            ),
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
            handler=server._tool_resume_run,
        ),
        ToolDefinition(
            name="smr_branch_run_from_checkpoint",
            description=(
                "Create a child run from a checkpoint. "
                "Use mode=exact for a pure branch and mode=with_message to seed the child with one bootstrap message."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Optional project-scoped route enforcement. Requires run_id when present.",
                    },
                    "run_id": {"type": "string", "description": "Optional run id scope."},
                    "checkpoint_id": {
                        "type": "string",
                        "description": "Checkpoint id reference.",
                    },
                    "checkpoint_record_id": {
                        "type": "string",
                        "description": "Checkpoint record id reference.",
                    },
                    "checkpoint_uri": {
                        "type": "string",
                        "description": "Checkpoint URI reference.",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["exact", "with_message"],
                        "description": "Whether to create an exact branch or bootstrap the child with a new message.",
                    },
                    "message": {
                        "type": "string",
                        "description": "Required when mode=with_message.",
                    },
                    "reason": {"type": "string", "description": "Optional operator reason."},
                    "title": {"type": "string", "description": "Optional branch label."},
                    "source_node_id": {
                        "type": "string",
                        "description": "Optional logical timeline node provenance.",
                    },
                },
                required=[],
            ),
            handler=server._tool_branch_run_from_checkpoint,
        ),
        ToolDefinition(
            name="smr_runtime_message_queue",
            description=(
                "List or enqueue durable runtime messages for a run. "
                "Use operation=list for inspection and operation=enqueue for live operator steering. "
                "Do not use this tool to branch from checkpoints."
            ),
            input_schema=tool_schema(
                {
                    "operation": {
                        "type": "string",
                        "enum": ["list", "enqueue"],
                        "description": "List the queue or enqueue a new runtime message.",
                    },
                    "run_id": {"type": "string", "description": "Run id."},
                    "status": {
                        "type": "string",
                        "description": "Optional message status filter when listing.",
                    },
                    "viewer_role": {
                        "type": "string",
                        "description": "Optional viewer role filter when listing.",
                    },
                    "viewer_target": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ],
                        "description": "Optional viewer target filter when listing.",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "description": "Maximum messages to return when listing.",
                    },
                    "topic": {"type": "string", "description": "Optional runtime topic."},
                    "causation_id": {
                        "type": "string",
                        "description": "Optional causation id for correlation.",
                    },
                    "mode": {"type": "string", "description": "Optional message mode."},
                    "spawn_policy": {
                        "type": "string",
                        "enum": ["live_only", "request_template"],
                        "description": "Optional spawn policy when enqueueing.",
                    },
                    "sender": {"type": "string", "description": "Optional sender identity."},
                    "target": {
                        "type": "string",
                        "description": "Optional runtime target when enqueueing.",
                    },
                    "participant_session_id": {
                        "type": "string",
                        "description": "Optional participant session target when enqueueing.",
                    },
                    "action": {"type": "string", "description": "Optional action label."},
                    "body": {"type": "string", "description": "Optional message body text."},
                    "payload": {
                        "type": "object",
                        "description": "Optional JSON payload when enqueueing.",
                    },
                },
                required=["operation", "run_id"],
            ),
            handler=server._tool_runtime_message_queue,
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
            description=(
                "List checkpoints for a run, including restorable/branchable flags "
                "and any recoverable checkpoint quota failure details."
            ),
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
            description=(
                "Restore a run to a restorable checkpoint. "
                "Use smr_branch_run_from_checkpoint for child-run branching; "
                "checkpoint quota failures return a structured error with operator_action."
            ),
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
                    "checkpoint_record_id": {
                        "type": "string",
                        "description": "Optional checkpoint record id reference.",
                    },
                    "checkpoint_uri": {
                        "type": "string",
                        "description": "Optional checkpoint URI reference.",
                    },
                    "reason": {"type": "string", "description": "Optional restore reason."},
                    "mode": {
                        "type": "string",
                        "enum": ["in_place", "branch"],
                        "description": (
                            "Restore mode. Prefer in_place; branch is a compatibility alias."
                        ),
                    },
                },
                required=["run_id"],
            ),
            handler=server._tool_restore_run_checkpoint,
        ),
    ]


__all__ = ["build_run_tools"]
