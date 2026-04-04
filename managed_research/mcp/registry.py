"""Small MCP registry helpers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

JSONDict = dict[str, Any]
ToolHandler = Callable[[JSONDict], Any]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: JSONDict
    handler: ToolHandler


def tool_schema(properties: JSONDict, *, required: list[str]) -> JSONDict:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


__all__ = ["JSONDict", "ToolDefinition", "tool_schema"]
