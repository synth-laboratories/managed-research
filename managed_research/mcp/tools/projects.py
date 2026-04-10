"""Project-related MCP tool definitions."""

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
from managed_research.models.smr_credential_providers import (
    SMR_CREDENTIAL_PROVIDER_VALUES,
)
from managed_research.models.smr_environment_kinds import (
    SMR_ENVIRONMENT_KIND_VALUES,
)
from managed_research.models.smr_funding_sources import SMR_FUNDING_SOURCE_VALUES
from managed_research.models.smr_host_kinds import SMR_HOST_KIND_VALUES
from managed_research.models.smr_runtime_kinds import SMR_RUNTIME_KIND_VALUES
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


def build_project_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_health_check",
            description="Return a connectivity and setup report for the managed-research MCP server.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Optional project id to verify access.",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=[],
            ),
            handler=server._tool_health_check,
        ),
        ToolDefinition(
            name="smr_create_runnable_project",
            description=(
                "Create a managed research project with the full runnable launch "
                "contract required for SDK, MCP, and eval flows."
            ),
            input_schema=tool_schema(
                {
                    "name": {"type": "string", "description": "Human-readable project name."},
                    "timezone": {
                        "type": "string",
                        "description": "Project timezone. Defaults to UTC when omitted.",
                    },
                    "pool_id": {
                        "type": "string",
                        "description": "Required execution pool id.",
                    },
                    "runtime_kind": {
                        "type": "string",
                        "enum": list(SMR_RUNTIME_KIND_VALUES),
                        "description": "Required project runtime kind.",
                    },
                    "environment_kind": {
                        "type": "string",
                        "enum": list(SMR_ENVIRONMENT_KIND_VALUES),
                        "description": "Required project environment kind.",
                    },
                    "orchestrator_profile_id": {
                        "type": "string",
                        "description": "Required shared orchestrator profile id.",
                    },
                    "default_worker_profile_id": {
                        "type": "string",
                        "description": "Required default worker profile id.",
                    },
                    "worker_profile_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional shared worker profile bindings.",
                    },
                    "actor_model_assignments": _actor_model_assignment_schema(
                        field_label=(
                            "Optional actor-scoped worker model overrides. "
                            "Use this instead of shared top-level model selection."
                        )
                    ),
                    "budgets": {
                        "type": "object",
                        "description": "Optional project budgets payload.",
                    },
                    "key_policy": {
                        "type": "object",
                        "description": "Optional project key-policy payload.",
                    },
                    "execution_policy": {
                        "type": "object",
                        "description": "Optional execution-policy payload.",
                    },
                    "scenario": {
                        "type": "string",
                        "description": "Optional project research scenario.",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional project notes / launch context.",
                    },
                    "metered_infra": {
                        "type": "object",
                        "description": "Optional metered-infra metadata payload.",
                    },
                    "schedule": {
                        "type": "object",
                        "description": "Optional project schedule payload.",
                    },
                    "integrations": {
                        "type": "object",
                        "description": "Optional project integrations payload.",
                    },
                    "synth_ai": {
                        "type": "object",
                        "description": "Optional project synth_ai payload.",
                    },
                    "policy": {
                        "type": "object",
                        "description": "Optional project policy payload.",
                    },
                    "trial_matrix": {
                        "type": "object",
                        "description": "Optional project trial-matrix payload.",
                    },
                },
                required=[
                    "name",
                    "pool_id",
                    "runtime_kind",
                    "environment_kind",
                    "orchestrator_profile_id",
                    "default_worker_profile_id",
                ],
            ),
            handler=server._tool_create_runnable_project,
        ),
        ToolDefinition(
            name="smr_create_project",
            description="Create a managed research project.",
            input_schema=tool_schema(
                {
                    "name": {"type": "string", "description": "Human-readable project name."},
                    "config": {
                        "type": "object",
                        "description": "Additional project configuration payload.",
                    },
                    "actor_model_assignments": _actor_model_assignment_schema(
                        field_label=(
                            "Optional durable actor-scoped model assignments stored under "
                            "execution.actor_model_assignments."
                        )
                    ),
                },
                required=[],
            ),
            handler=server._tool_create_project,
        ),
        ToolDefinition(
            name="smr_list_projects",
            description="List managed research projects.",
            input_schema=tool_schema(
                {
                    "include_archived": {
                        "type": "boolean",
                        "description": "Include archived projects.",
                    },
                    "limit": {"type": "integer", "description": "Maximum projects to return."},
                },
                required=[],
            ),
            handler=server._tool_list_projects,
        ),
        ToolDefinition(
            name="smr_get_project",
            description="Fetch a managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project,
        ),
        ToolDefinition(
            name="smr_patch_project",
            description="Patch a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "config": {
                        "type": "object",
                        "description": "Partial project fields to update.",
                    },
                    "actor_model_assignments": _actor_model_assignment_schema(
                        field_label=(
                            "Optional durable actor-scoped model assignments stored under "
                            "execution.actor_model_assignments."
                        )
                    ),
                },
                required=["project_id", "config"],
            ),
            handler=server._tool_patch_project,
        ),
        ToolDefinition(
            name="smr_get_project_status",
            description="Fetch a polling-friendly status snapshot for a project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project_status,
        ),
        ToolDefinition(
            name="smr_get_project_entitlement",
            description="Fetch the managed-research entitlement status for a project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project_entitlement,
        ),
        ToolDefinition(
            name="smr_get_project_notes",
            description="Fetch the durable notebook text for a managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project_notes,
        ),
        ToolDefinition(
            name="smr_set_project_notes",
            description="Replace the durable notebook text for a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "notes": {"type": "string", "description": "Notebook text to store."},
                },
                required=["project_id", "notes"],
            ),
            handler=server._tool_set_project_notes,
        ),
        ToolDefinition(
            name="smr_append_project_notes",
            description="Append text to the durable notebook for a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "notes": {"type": "string", "description": "Notebook text to append."},
                },
                required=["project_id", "notes"],
            ),
            handler=server._tool_append_project_notes,
        ),
        ToolDefinition(
            name="smr_get_org_knowledge",
            description="Fetch curated org-wide knowledge for the authenticated organization. This is distinct from project notes.",
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_get_org_knowledge,
        ),
        ToolDefinition(
            name="smr_set_org_knowledge",
            description="Replace curated org-wide knowledge for the authenticated organization. This is distinct from project notes.",
            input_schema=tool_schema(
                {
                    "content": {
                        "type": "string",
                        "description": "Curated org-wide knowledge content to store.",
                    },
                },
                required=["content"],
            ),
            handler=server._tool_set_org_knowledge,
        ),
        ToolDefinition(
            name="smr_get_project_knowledge",
            description="Fetch curated knowledge for a managed research project. This is distinct from the project notebook notes surface.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_get_project_knowledge,
        ),
        ToolDefinition(
            name="smr_set_project_knowledge",
            description="Replace curated knowledge for a managed research project. This is distinct from the project notebook notes surface.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "content": {
                        "type": "string",
                        "description": "Curated project knowledge content to store.",
                    },
                },
                required=["project_id", "content"],
            ),
            handler=server._tool_set_project_knowledge,
        ),
        ToolDefinition(
            name="smr_curated_knowledge",
            description=(
                "Get or set curated knowledge for the authenticated org or for one project. "
                "Use scope=org|project, and provide content when operation=set."
            ),
            input_schema=tool_schema(
                {
                    "operation": {
                        "type": "string",
                        "enum": ["get", "set"],
                        "description": "Get the current durable knowledge blob or replace it.",
                    },
                    "scope": {
                        "type": "string",
                        "enum": ["org", "project"],
                        "description": "Whether the knowledge is org-wide or project-scoped.",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id when scope is project.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Replacement knowledge content when operation is set.",
                    },
                },
                required=["operation", "scope"],
            ),
            handler=server._tool_curated_knowledge,
        ),
        ToolDefinition(
            name="smr_pause_project",
            description="Pause a managed research project so new runs cannot start.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_pause_project,
        ),
        ToolDefinition(
            name="smr_resume_project",
            description="Resume a paused managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_resume_project,
        ),
        ToolDefinition(
            name="smr_archive_project",
            description="Archive a managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_archive_project,
        ),
        ToolDefinition(
            name="smr_unarchive_project",
            description="Unarchive a managed research project.",
            input_schema=tool_schema(
                {"project_id": {"type": "string", "description": "Managed research project id."}},
                required=["project_id"],
            ),
            handler=server._tool_unarchive_project,
        ),
        ToolDefinition(
            name="smr_get_capabilities",
            description=(
                "Fetch server capabilities for parity-safe client behavior. "
                "Run trigger maps backend ``error_code`` payloads (limits, routing, "
                "credits, project budget, managed inference) to structured MCP results."
            ),
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_get_capabilities,
        ),
        ToolDefinition(
            name="smr_get_limits",
            description="Fetch resource limits for the authenticated org's plan. This is informative only; trigger and blockers remain authoritative.",
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_get_limits,
        ),
        ToolDefinition(
            name="smr_get_capacity_lane_preview",
            description=(
                "Preview the preferred/resolved capacity lane before launch. "
                "Call this before smr_get_run_start_blockers or smr_trigger_run when you need a user-facing launch check."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_capacity_lane_preview,
        ),
        ToolDefinition(
            name="smr_get_run_start_blockers",
            description=(
                "Return ordered launch blockers for the same payload shape used by smr_trigger_run. "
                "Use this before trigger when you want a clear 'can I launch?' answer."
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
                    "run_policy": run_policy_input_schema(),
                    "idempotency_key_run_create": {
                        "type": "string",
                        "description": "Optional idempotency key for the launch request.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Deprecated compatibility alias for idempotency_key_run_create.",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id", "host_kind", "work_mode"],
            ),
            handler=server._tool_get_run_start_blockers,
        ),
        ToolDefinition(
            name="smr_set_provider_key",
            description="Store or rotate a project-scoped provider key for a supported credential provider.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "provider": {
                        "type": "string",
                        "enum": list(SMR_CREDENTIAL_PROVIDER_VALUES),
                        "description": "Credential provider to configure.",
                    },
                    "funding_source": {
                        "type": "string",
                        "enum": list(SMR_FUNDING_SOURCE_VALUES),
                        "description": "Funding source bucket for the credential. Usually customer_byok.",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Plaintext provider API key.",
                    },
                    "encrypted_key_b64": {
                        "type": "string",
                        "description": "Optional encrypted provider API key payload.",
                    },
                },
                required=["project_id", "provider", "funding_source"],
            ),
            handler=server._tool_set_provider_key,
        ),
        ToolDefinition(
            name="smr_get_provider_key_status",
            description="Check whether a project-scoped provider key is configured.",
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "provider": {
                        "type": "string",
                        "enum": list(SMR_CREDENTIAL_PROVIDER_VALUES),
                        "description": "Credential provider to inspect.",
                    },
                    "funding_source": {
                        "type": "string",
                        "enum": list(SMR_FUNDING_SOURCE_VALUES),
                        "description": "Funding source bucket for the credential. Usually customer_byok.",
                    },
                },
                required=["project_id", "provider", "funding_source"],
            ),
            handler=server._tool_get_provider_key_status,
        ),
        ToolDefinition(
            name="smr_get_workspace_download_url",
            description=(
                "Return a short-lived presigned URL to download the project workspace as a tarball "
                "(git snapshot archived by the backend). Use smr_download_workspace_archive to save "
                "the file locally in one step, or fetch download_url with curl yourself."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_workspace_download_url,
        ),
        ToolDefinition(
            name="smr_get_project_git",
            description=(
                "Read-only git metadata for the project workspace (commit, branch, remote-related fields). "
                "Pair with smr_get_workspace_download_url or smr_download_workspace_archive to retrieve files."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_project_git,
        ),
        ToolDefinition(
            name="smr_download_workspace_archive",
            description=(
                "Download the project workspace tarball to a path on the machine running this MCP server "
                "(presigned URL under the hood). Parent directories are created. Large repos may take minutes; "
                "raise timeout_seconds if needed (default 600)."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {"type": "string", "description": "Managed research project id."},
                    "output_path": {
                        "type": "string",
                        "description": "Absolute or home-relative path for the .tar.gz file (e.g. ~/smr-workspace.tar.gz).",
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "HTTP timeout for the presigned download in seconds (default 600).",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Optional Synth API key override.",
                    },
                    "backend_base": {
                        "type": "string",
                        "description": "Optional backend base override.",
                    },
                },
                required=["project_id", "output_path"],
            ),
            handler=server._tool_download_workspace_archive,
        ),
    ]


__all__ = ["build_project_tools"]
