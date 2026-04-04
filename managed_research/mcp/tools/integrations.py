"""Integration MCP tool definitions."""

from __future__ import annotations

from typing import Any

from managed_research.mcp.registry import ToolDefinition


def build_integration_tools(server: Any) -> list[ToolDefinition]:
    _ = server
    return []


__all__ = ["build_integration_tools"]
