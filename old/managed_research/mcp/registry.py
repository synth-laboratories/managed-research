"""Shared MCP registry types and schema helpers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

JSONDict = dict[str, Any]
ToolHandler = Callable[[JSONDict], Any]


@dataclass(frozen=True)
class ToolDefinition:
    """MCP tool metadata and handler."""

    name: str
    description: str
    input_schema: JSONDict
    handler: ToolHandler


_CONNECTION_PROPERTIES: JSONDict = {
    "api_key": {
        "type": "string",
        "description": "Optional API key override (defaults to SYNTH_API_KEY).",
    },
    "backend_base": {
        "type": "string",
        "description": "Optional backend URL override (defaults to SYNTH_BACKEND_URL).",
    },
}


def tool_schema(properties: JSONDict, required: list[str]) -> JSONDict:
    """Attach shared connection properties to a tool schema."""
    merged: JSONDict = dict(properties)
    merged.update(_CONNECTION_PROPERTIES)
    return {
        "type": "object",
        "properties": merged,
        "required": required,
        "additionalProperties": False,
    }


__all__ = ["JSONDict", "ToolDefinition", "ToolHandler", "tool_schema"]
