"""Run-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_run_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_trigger_run",
            description="Trigger a run for a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "timebox_seconds": {
                        "type": "integer",
                        "description": "Optional run timebox in seconds.",
                    },
                    "agent_model": {
                        "type": "string",
                        "description": (
                            "Override agent model for this run only, "
                            "e.g. 'claude-opus-4-5' or 'gpt-4o'. "
                            "Does not affect the project's default model."
                        ),
                    },
                    "agent_kind": {
                        "type": "string",
                        "enum": ["codex", "claude", "opencode"],
                        "description": (
                            "Override agent runtime for this run only: "
                            "'codex' (default), 'claude' (Claude Code), or 'opencode'."
                        ),
                    },
                    "work_mode": {
                        "type": "string",
                        "enum": ["open_ended_discovery", "directed_effort"],
                        "description": (
                            "Required run work mode: 'open_ended_discovery' "
                            "for exploratory work or 'directed_effort' for scoped execution."
                        ),
                    },
                    "workflow": {
                        "type": "object",
                        "description": (
                            "Optional workflow payload for rails such as data_factory_v1. "
                            "When omitted, behavior is unchanged."
                        ),
                        "properties": {
                            "kind": {"type": "string"},
                            "profile": {"type": "string"},
                            "source_mode": {
                                "type": "string",
                                "enum": [
                                    "mcp_local",
                                    "oneshot_mcp_local",
                                    "synth_mcp_local",
                                    "frontend_interactive",
                                ],
                            },
                            "targets": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "harbor",
                                        "openenv",
                                        "archipelago",
                                        "custom_container",
                                        "synth_container",
                                    ],
                                },
                                "minItems": 1,
                            },
                            "preferred_target": {
                                "type": "string",
                                "enum": [
                                    "harbor",
                                    "openenv",
                                    "archipelago",
                                    "custom_container",
                                    "synth_container",
                                ],
                            },
                            "runtime_kind": {
                                "type": "string",
                                "enum": ["react_mcp", "react", "horizons", "sandbox_agent"],
                            },
                            "environment_kind": {
                                "type": "string",
                                "enum": [
                                    "harbor",
                                    "openenv",
                                    "archipelago",
                                    "custom_container",
                                    "synth_container",
                                ],
                            },
                            "template": {
                                "type": "string",
                                "enum": ["harbor_hardening_v1"],
                            },
                            "input": {
                                "type": "object",
                                "properties": {
                                    "dataset_ref": {"type": "string"},
                                    "bundle_manifest_path": {"type": "string"},
                                    "session_id": {"type": "string"},
                                    "session_state": {"type": "string"},
                                    "session_title": {"type": "string"},
                                    "session_notes": {"type": "string"},
                                },
                                "required": ["dataset_ref", "bundle_manifest_path"],
                                "additionalProperties": False,
                            },
                            "options": {
                                "type": "object",
                                "properties": {
                                    "strictness_mode": {
                                        "type": "string",
                                        "enum": ["warn", "strict"],
                                    }
                                },
                                "additionalProperties": False,
                            },
                        },
                        "required": ["kind", "source_mode", "targets", "input"],
                        "additionalProperties": False,
                    },
                    "idempotency_key_run_create": {
                        "type": "string",
                        "description": "Canonical idempotency key for run-create retries.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Deprecated alias for idempotency_key_run_create.",
                    },
                },
                required=["project_id", "work_mode"],
            ),
            handler=server._tool_trigger_run,
        ),
        ToolDefinition(
            name="smr_trigger_data_factory",
            description=(
                "Trigger a standardized Data Factory run "
                "(syntactic sugar over smr_trigger_run with workflow.kind=data_factory_v1)."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "dataset_ref": {
                        "type": "string",
                        "description": "S3-prefix style dataset ref containing capture bundle files.",
                    },
                    "bundle_manifest_path": {
                        "type": "string",
                        "description": "Path under dataset_ref to capture_bundle.json.",
                    },
                    "work_mode": {
                        "type": "string",
                        "enum": ["open_ended_discovery", "directed_effort"],
                        "description": (
                            "Required run work mode for the Data Factory launch: "
                            "'open_ended_discovery' or 'directed_effort'."
                        ),
                    },
                    "profile": {
                        "type": "string",
                        "enum": ["founder_default", "researcher_strict"],
                        "description": "Data Factory profile rail (default founder_default).",
                    },
                    "source_mode": {
                        "type": "string",
                        "enum": [
                            "mcp_local",
                            "oneshot_mcp_local",
                            "synth_mcp_local",
                            "frontend_interactive",
                        ],
                        "description": "Capture source mode (default synth_mcp_local).",
                    },
                    "template": {
                        "type": "string",
                        "enum": ["harbor_hardening_v1"],
                        "description": "Optional workflow template preset.",
                    },
                    "targets": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "harbor",
                                "openenv",
                                "archipelago",
                                "custom_container",
                                "synth_container",
                            ],
                        },
                        "minItems": 1,
                        "description": "Execution targets in priority set.",
                    },
                    "preferred_target": {
                        "type": "string",
                        "enum": [
                            "harbor",
                            "openenv",
                            "archipelago",
                            "custom_container",
                            "synth_container",
                        ],
                        "description": "Preferred target (default harbor).",
                    },
                    "runtime_kind": {
                        "type": "string",
                        "enum": ["react_mcp", "react", "horizons", "sandbox_agent"],
                        "description": "Optional runtime kind for compatibility gating.",
                    },
                    "environment_kind": {
                        "type": "string",
                        "enum": [
                            "harbor",
                            "openenv",
                            "archipelago",
                            "custom_container",
                            "synth_container",
                        ],
                        "description": "Optional environment kind for compatibility gating.",
                    },
                    "strictness_mode": {
                        "type": "string",
                        "enum": ["warn", "strict"],
                        "description": "Validation strictness mode (default warn).",
                    },
                    "timebox_seconds": {
                        "type": "integer",
                        "description": "Optional run timebox in seconds.",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Interactive session identifier when source_mode=frontend_interactive.",
                    },
                    "session_state": {
                        "type": "string",
                        "enum": [
                            "empty",
                            "active",
                            "completed",
                            "uploaded",
                            "finalizing",
                            "finalized",
                            "publish-ready",
                            "blocked",
                            "recoverable-fail",
                        ],
                        "description": "Interactive session lifecycle state.",
                    },
                    "session_title": {
                        "type": "string",
                        "description": "Optional interactive session title.",
                    },
                    "session_notes": {
                        "type": "string",
                        "description": "Optional interactive session notes/context.",
                    },
                    "idempotency_key_run_create": {
                        "type": "string",
                        "description": "Canonical idempotency key for run-create retries.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Deprecated alias for idempotency_key_run_create.",
                    },
                },
                required=["project_id", "dataset_ref", "bundle_manifest_path", "work_mode"],
            ),
            handler=server._tool_trigger_data_factory,
        ),
        ToolDefinition(
            name="smr_data_factory_finalize",
            description="Submit a Data Factory finalization run via the dedicated endpoint.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "dataset_ref": {
                        "type": "string",
                        "description": "Dataset ref containing capture bundle files.",
                    },
                    "bundle_manifest_path": {
                        "type": "string",
                        "description": "Path under dataset_ref to capture_bundle.json.",
                    },
                    "template": {
                        "type": "string",
                        "enum": ["harbor_hardening_v1"],
                        "description": "Optional workflow template preset.",
                    },
                    "target_formats": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "harbor",
                                "openenv",
                                "archipelago",
                                "custom_container",
                                "synth_container",
                            ],
                        },
                        "minItems": 1,
                        "description": "Execution target formats.",
                    },
                    "preferred_target": {
                        "type": "string",
                        "enum": [
                            "harbor",
                            "openenv",
                            "archipelago",
                            "custom_container",
                            "synth_container",
                        ],
                        "description": "Preferred target (default harbor).",
                    },
                    "finalizer_profile": {
                        "type": "string",
                        "enum": ["founder_default", "researcher_strict"],
                        "description": "Data Factory profile rail (default founder_default).",
                    },
                    "source_mode": {
                        "type": "string",
                        "enum": [
                            "mcp_local",
                            "oneshot_mcp_local",
                            "synth_mcp_local",
                            "frontend_interactive",
                        ],
                        "description": "Capture source mode (default synth_mcp_local).",
                    },
                    "runtime_kind": {
                        "type": "string",
                        "enum": ["react_mcp", "react", "horizons", "sandbox_agent"],
                        "description": "Optional runtime kind for compatibility gating.",
                    },
                    "environment_kind": {
                        "type": "string",
                        "enum": [
                            "harbor",
                            "openenv",
                            "archipelago",
                            "custom_container",
                            "synth_container",
                        ],
                        "description": "Optional environment kind for compatibility gating.",
                    },
                    "strictness_mode": {
                        "type": "string",
                        "enum": ["warn", "strict"],
                        "description": "Validation strictness mode (default warn).",
                    },
                    "timebox_seconds": {
                        "type": "integer",
                        "description": "Optional run timebox in seconds.",
                    },
                    "idempotency_key_run_create": {
                        "type": "string",
                        "description": "Canonical idempotency key for run-create retries.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Deprecated alias for idempotency_key_run_create.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_data_factory_finalize,
        ),
        ToolDefinition(
            name="smr_data_factory_finalize_status",
            description="Fetch Data Factory finalization status by job id.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "job_id": {
                        "type": "string",
                        "description": "Finalization job id (run id).",
                    },
                },
                required=["project_id", "job_id"],
            ),
            handler=server._tool_data_factory_finalize_status,
        ),
        ToolDefinition(
            name="smr_data_factory_publish",
            description="Publish finalized Data Factory artifacts.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "job_id": {
                        "type": "string",
                        "description": "Finalization job id (run id).",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Publish reason (default manual_publish).",
                    },
                    "idempotency_key_publish": {
                        "type": "string",
                        "description": "Canonical idempotency key for publish retries.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Deprecated alias for idempotency_key_publish.",
                    },
                },
                required=["project_id", "job_id"],
            ),
            handler=server._tool_data_factory_publish,
        ),
        ToolDefinition(
            name="smr_list_runs",
            description="List runs for a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "active_only": {
                        "type": "boolean",
                        "description": "Return only active runs.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_list_runs,
        ),
        ToolDefinition(
            name="smr_list_jobs",
            description="List org-level SMR jobs feed (runs), optionally filtered by project/state.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Optional managed research project id filter.",
                    },
                    "state": {
                        "type": "string",
                        "description": "Optional run state filter (single or comma-separated).",
                    },
                    "active_only": {
                        "type": "boolean",
                        "description": "Return only active runs.",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 200,
                        "description": "Maximum rows to return (default 50).",
                    },
                },
                required=[],
            ),
            handler=server._tool_list_jobs,
        ),
        ToolDefinition(
            name="smr_get_run",
            description="Fetch a run by id.",
            input_schema=tool_schema(
                {
                    "run_id": {"type": "string", "description": "Run id."},
                    "project_id": {
                        "type": "string",
                        "description": "Optional project id for project-scoped strict route.",
                    },
                },
                required=["run_id"],
            ),
            handler=server._tool_get_run,
        ),
        ToolDefinition(
            name="smr_get_actor_status",
            description="Fetch unified actor status (orchestrator + workers) for a project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Optional run id filter.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_actor_status,
        ),
        ToolDefinition(
            name="smr_control_actor",
            description="Pause or resume an orchestrator/worker actor within a run.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "run_id": {"type": "string", "description": "Run id."},
                    "actor_id": {
                        "type": "string",
                        "description": "Actor id (orchestrator or worker id).",
                    },
                    "action": {
                        "type": "string",
                        "enum": ["pause", "resume"],
                        "description": "Control action.",
                    },
                    "reason": {"type": "string", "description": "Optional operator reason."},
                    "idempotency_key": {
                        "type": "string",
                        "description": "Optional idempotency key for retries.",
                    },
                },
                required=["project_id", "run_id", "actor_id", "action"],
            ),
            handler=server._tool_control_actor,
        ),
        ToolDefinition(
            name="smr_pause_run",
            description="Pause a run.",
            input_schema=tool_schema(
                {"run_id": {"type": "string", "description": "Run id."}},
                required=["run_id"],
            ),
            handler=server._tool_pause_run,
        ),
        ToolDefinition(
            name="smr_resume_run",
            description="Resume a paused run.",
            input_schema=tool_schema(
                {"run_id": {"type": "string", "description": "Run id."}},
                required=["run_id"],
            ),
            handler=server._tool_resume_run,
        ),
        ToolDefinition(
            name="smr_stop_run",
            description="Stop a run.",
            input_schema=tool_schema(
                {"run_id": {"type": "string", "description": "Run id."}},
                required=["run_id"],
            ),
            handler=server._tool_stop_run,
        ),
    ]


__all__ = ["build_run_tools"]
