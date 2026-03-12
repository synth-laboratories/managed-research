"""Integration-related MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition, tool_schema


def build_integration_tools(server: Any) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="smr_codex_subscription_status",
            description="Get global Codex subscription connection status.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Optional project id to read project-bound state.",
                    }
                },
                required=[],
            ),
            handler=server._tool_codex_subscription_status,
        ),
        ToolDefinition(
            name="smr_codex_subscription_connect_start",
            description="Start Codex subscription login (returns authorize_url and instructions).",
            input_schema=tool_schema(
                {
                    "sandbox_agent_url": {
                        "type": "string",
                        "description": "Optional connector URL override.",
                    },
                    "provider_id": {
                        "type": "string",
                        "description": (
                            "Optional connector provider id override (for example openai or codex)."
                        ),
                    },
                    "external_account_hint": {
                        "type": "string",
                        "description": "Optional account hint to store with the connection.",
                    },
                },
                required=[],
            ),
            handler=server._tool_codex_subscription_connect_start,
        ),
        ToolDefinition(
            name="smr_codex_subscription_connect_complete",
            description="Complete Codex subscription login after browser consent.",
            input_schema=tool_schema(
                {
                    "code": {
                        "type": "string",
                        "description": "Optional OAuth code for code-based flows.",
                    },
                    "sandbox_agent_url": {
                        "type": "string",
                        "description": "Optional connector URL override.",
                    },
                },
                required=[],
            ),
            handler=server._tool_codex_subscription_connect_complete,
        ),
        ToolDefinition(
            name="smr_codex_subscription_disconnect",
            description="Disconnect the global Codex subscription from SMR.",
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_codex_subscription_disconnect,
        ),
        ToolDefinition(
            name="smr_github_org_status",
            description="Get org-level GitHub integration status.",
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_github_org_status,
        ),
        ToolDefinition(
            name="smr_github_org_oauth_start",
            description="Start org-level GitHub OAuth flow.",
            input_schema=tool_schema(
                {
                    "redirect_uri": {
                        "type": "string",
                        "description": "Optional callback URL override.",
                    }
                },
                required=[],
            ),
            handler=server._tool_github_org_oauth_start,
        ),
        ToolDefinition(
            name="smr_github_org_oauth_callback",
            description="Complete org-level GitHub OAuth callback.",
            input_schema=tool_schema(
                {
                    "code": {
                        "type": "string",
                        "description": "OAuth callback code.",
                    },
                    "state": {
                        "type": "string",
                        "description": "Optional OAuth state value.",
                    },
                    "redirect_uri": {
                        "type": "string",
                        "description": "Optional callback URL override.",
                    },
                },
                required=["code"],
            ),
            handler=server._tool_github_org_oauth_callback,
        ),
        ToolDefinition(
            name="smr_github_org_disconnect",
            description="Disconnect org-level GitHub integration.",
            input_schema=tool_schema({}, required=[]),
            handler=server._tool_github_org_disconnect,
        ),
        ToolDefinition(
            name="smr_linear_status",
            description="Get project-level Linear integration status.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_linear_status,
        ),
        ToolDefinition(
            name="smr_linear_oauth_start",
            description="Start project-level Linear OAuth flow.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "redirect_uri": {
                        "type": "string",
                        "description": "Optional callback URL override.",
                    },
                },
                required=["project_id"],
            ),
            handler=server._tool_linear_oauth_start,
        ),
        ToolDefinition(
            name="smr_linear_oauth_callback",
            description="Complete project-level Linear OAuth callback.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    },
                    "code": {
                        "type": "string",
                        "description": "OAuth callback code.",
                    },
                    "state": {
                        "type": "string",
                        "description": "Optional OAuth state value.",
                    },
                    "redirect_uri": {
                        "type": "string",
                        "description": "Optional callback URL override.",
                    },
                },
                required=["project_id", "code"],
            ),
            handler=server._tool_linear_oauth_callback,
        ),
        ToolDefinition(
            name="smr_linear_disconnect",
            description="Disconnect project-level Linear integration.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_linear_disconnect,
        ),
        ToolDefinition(
            name="smr_linear_list_teams",
            description="List Linear teams available to the project integration.",
            input_schema=tool_schema(
                {
                    "project_id": {
                        "type": "string",
                        "description": "Managed research project id.",
                    }
                },
                required=["project_id"],
            ),
            handler=server._tool_linear_list_teams,
        ),
    ]


__all__ = ["build_integration_tools"]
