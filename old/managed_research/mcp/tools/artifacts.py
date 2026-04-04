"""Artifact-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_artifact_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_list_run_artifacts",
            description="List artifacts produced by a run.",
            input_schema=tool_schema(
                {
                    "run_id": {
                        "type": "string",
                        "description": "Run id.",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Optional project id for project-scoped lookup.",
                    },
                },
                required=["run_id"],
            ),
            handler=server._tool_list_run_artifacts,
        ),
        ToolDefinition(
            name="smr_get_artifact",
            description="Fetch artifact metadata (title, uri, type) by artifact id.",
            input_schema=tool_schema(
                {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact id.",
                    }
                },
                required=["artifact_id"],
            ),
            handler=server._tool_get_artifact,
        ),
        ToolDefinition(
            name="smr_get_artifact_content",
            description=(
                "Download artifact content by artifact id. Returns UTF-8 text when possible, "
                "otherwise base64-encoded bytes."
            ),
            input_schema=tool_schema(
                {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact id.",
                    },
                    "disposition": {
                        "type": "string",
                        "description": "Either 'inline' or 'attachment'.",
                    },
                    "max_bytes": {
                        "type": "integer",
                        "description": "Maximum bytes to return in the response (default 200000).",
                    },
                },
                required=["artifact_id"],
            ),
            handler=server._tool_get_artifact_content,
        ),
        ToolDefinition(
            name="smr_list_run_pull_requests",
            description="List pull requests created for a run via github_pr artifacts.",
            input_schema=tool_schema(
                {
                    "run_id": {
                        "type": "string",
                        "description": "Run id.",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Optional project id for project-scoped lookup.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum PR artifacts to inspect (default 100).",
                    },
                },
                required=["run_id"],
            ),
            handler=server._tool_list_run_pull_requests,
        ),
        ToolDefinition(
            name="smr_get_run_results",
            description=(
                "Get a run result summary: outcome, artifacts grouped by type, "
                "and a pre-built log query hint for debugging."
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
                },
                required=["project_id", "run_id"],
            ),
            handler=server._tool_get_run_results,
        ),
        ToolDefinition(
            name="smr_get_project_git_status",
            description=(
                "Get read-only workspace git status for a project: "
                "commit SHA, last push timestamp, default branch, and optional "
                "remote repo metadata. Does not expose storage internals or allow download."
            ),
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_get_project_git_status,
        ),
        ToolDefinition(
            name="smr_get_orchestrator_status",
            description=(
                "Get orchestrator status for a run: current phase, heartbeat, "
                "turn count, turn history (phase + outcome + timing for each turn), "
                "and a log query hint scoped to the orchestrator component."
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
                },
                required=["project_id", "run_id"],
            ),
            handler=server._tool_get_orchestrator_status,
        ),
    ]


__all__ = ["build_artifact_tools"]
