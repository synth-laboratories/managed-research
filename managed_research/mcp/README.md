# MCP

This package owns the stdio MCP surface for `managed-research`.

What belongs here:
- JSON-RPC/MCP transport handling
- tool registration and input schemas
- MCP-specific request parsing at the boundary
- translation from MCP tool calls into SDK client calls

What does not belong here:
- general SDK request construction
- broad public response-model ownership
- backend contract decisions

Primary entrypoints:
- `server.py`: stdio server and tool dispatch
- `tools/`: tool definitions and input schemas
- `request_models.py`: typed MCP request parsing helpers
- `registry.py`: shared MCP tool registration primitives

Boundary rule:
- parse untyped JSON-RPC payloads once near the transport boundary
- pass normalized typed values or request objects into handlers
- do not carry ad hoc `.get()` / `isinstance()` branching deep into tool logic

Stability rule:
- keep MCP tool names and wire payload shapes stable unless a deliberate migration is planned
- fail loudly on malformed input instead of silently defaulting to success-shaped values
