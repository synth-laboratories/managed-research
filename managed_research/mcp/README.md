# MCP

This package owns the canonical MCP surface for `managed-research`.

What belongs here:
- tool registration, schemas, and scope metadata
- shared tool-list / call-tool primitives used by both stdio and hosted transport
- stdio JSON-RPC/MCP transport handling
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
- `registry.py`: shared MCP tool registration, metadata, and call primitives

Boundary rule:
- parse untyped JSON-RPC payloads once near the transport boundary
- pass normalized typed values or request objects into handlers
- do not carry ad hoc `.get()` / `isinstance()` branching deep into tool logic

Stability rule:
- keep MCP tool names and wire payload shapes stable unless a deliberate migration is planned
- fail loudly on malformed input instead of silently defaulting to success-shaped values
