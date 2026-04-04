"""Project-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_project_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_list_projects",
            description="List managed research projects.",
            input_schema=tool_schema(
                {
                    "include_archived": {
                        "type": "boolean",
                        "description": "Include archived projects in results.",
                    }
                },
                required=[],
            ),
            handler=server._tool_list_projects,
        ),
        ToolDefinition(
            name="smr_get_project",
            description="Fetch a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_get_project,
        ),
        ToolDefinition(
            name="smr_get_project_status",
            description="Fetch status for a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_get_project_status,
        ),
        ToolDefinition(
            name="smr_get_binding",
            description="Fetch the active project binding (pool lineage and runtime/environment resolution).",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Optional expected published_by_run_id for handoff verification.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_binding,
        ),
        ToolDefinition(
            name="smr_promote_binding",
            description="Promote/update active binding with expected-revision CAS semantics.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "pool_id": {
                        "type": "string",
                        "description": "Target pool id to bind.",
                    },
                    "dataset_revision": {
                        "type": "string",
                        "description": "Dataset revision id to bind.",
                    },
                    "expected_revision": {
                        "type": "integer",
                        "description": "Current binding revision expected by caller (CAS).",
                    },
                    "runtime_kind": {
                        "type": "string",
                        "description": "Optional runtime kind override.",
                    },
                    "environment_kind": {
                        "type": "string",
                        "description": "Optional environment kind override.",
                    },
                    "published_by_run_id": {
                        "type": "string",
                        "description": "Optional run id publishing this binding.",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for audit trail.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Optional idempotency key.",
                    },
                },
                required=["project_id", "pool_id", "dataset_revision", "expected_revision"],
            ),
            handler=server._tool_promote_binding,
        ),
        ToolDefinition(
            name="smr_get_pool_context",
            description=(
                "Fetch project/run pool context for worker coordination: active binding, "
                "run-level pool ledger summary, recommended target (if any), and fallback policy."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Optional run id used to read run-scoped pool metadata.",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Optional task id for task-level assignment lookup.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_get_pool_context,
        ),
        ToolDefinition(
            name="smr_get_starting_data_upload_urls",
            description="Request presigned upload URLs for starting-data files.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "dataset_ref": {
                        "type": "string",
                        "description": "Optional dataset ref override (for example starting-data/banking77).",
                    },
                    "files": {
                        "type": "array",
                        "description": "File metadata entries to upload.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content_type": {"type": "string"},
                            },
                            "required": ["path"],
                            "additionalProperties": False,
                        },
                        "minItems": 1,
                    },
                    "idempotency_key_upload": {
                        "type": "string",
                        "description": "Canonical idempotency key for upload retries.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Deprecated alias for idempotency_key_upload.",
                    },
                },
                required=["project_id", "files"],
            ),
            handler=server._tool_get_starting_data_upload_urls,
        ),
        ToolDefinition(
            name="smr_upload_starting_data",
            description="Upload starting-data file contents (text) via presigned URLs.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "dataset_ref": {
                        "type": "string",
                        "description": "Optional dataset ref override (for example starting-data/banking77).",
                    },
                    "files": {
                        "type": "array",
                        "description": "Files to upload (UTF-8 text content).",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"},
                                "content_type": {"type": "string"},
                            },
                            "required": ["path", "content"],
                            "additionalProperties": False,
                        },
                        "minItems": 1,
                    },
                    "idempotency_key_upload": {
                        "type": "string",
                        "description": "Canonical idempotency key for upload retries.",
                    },
                    "idempotency_key": {
                        "type": "string",
                        "description": "Deprecated alias for idempotency_key_upload.",
                    },
                },
                required=["project_id", "files"],
            ),
            handler=server._tool_upload_starting_data,
        ),
        ToolDefinition(
            name="smr_set_agent_config",
            description=(
                "Set the default agent model and/or kind for all future runs of a project. "
                "Writes into project.execution.agent_model / agent_kind. "
                "Use smr_trigger_run agent_model/agent_kind params for one-off overrides."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "model": {
                        "type": "string",
                        "description": (
                            "Model string, e.g. 'claude-opus-4-5', 'gpt-4o', "
                            "'claude-haiku-4-5-20251001'."
                        ),
                    },
                    "agent_kind": {
                        "type": "string",
                        "enum": ["codex", "claude", "opencode"],
                        "description": "Agent runtime: 'codex' (default), 'claude', or 'opencode'.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_set_agent_config,
        ),
        ToolDefinition(
            name="smr_create_project",
            description="Create a new managed research project.",
            input_schema=tool_schema(
                {
                    "name": {
                        "type": "string",
                        "description": "Human-readable project name.",
                    },
                    "config": {
                        "type": "object",
                        "description": "Project configuration payload.",
                    },
                },
                required=["name"],
            ),
            handler=server._tool_create_project,
        ),
        ToolDefinition(
            name="smr_get_project_repos",
            description="List project-scoped GitHub repos configured in integrations.github.repos.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_get_project_repos,
        ),
        ToolDefinition(
            name="smr_link_org_github",
            description="Link a project to the org-level GitHub credential.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_link_org_github,
        ),
        ToolDefinition(
            name="smr_add_project_repo",
            description="Add a GitHub repo to a project with optional PR write enablement.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repo in owner/name format.",
                    },
                    "pr_write_enabled": {
                        "type": "boolean",
                        "description": "Whether PR creation should be enabled for this repo.",
                    },
                },
                required=["project_id", "repo"],
            ),
            handler=server._tool_add_project_repo,
        ),
        ToolDefinition(
            name="smr_remove_project_repo",
            description="Remove a GitHub repo from a project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repo in owner/name format.",
                    },
                },
                required=["project_id", "repo"],
            ),
            handler=server._tool_remove_project_repo,
        ),
        ToolDefinition(
            name="smr_pause_project",
            description="Pause a managed research project (prevents new runs from starting).",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_pause_project,
        ),
        ToolDefinition(
            name="smr_resume_project",
            description="Resume a paused managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_resume_project,
        ),
        ToolDefinition(
            name="smr_archive_project",
            description="Archive a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_archive_project,
        ),
        ToolDefinition(
            name="smr_unarchive_project",
            description="Unarchive a managed research project.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_unarchive_project,
        ),
    ]


__all__ = ["build_project_tools"]
