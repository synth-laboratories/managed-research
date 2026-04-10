"""Allow ``managed-research-mcp`` or ``python -m managed_research.mcp`` to start MCP."""

from managed_research.mcp.server import main

if __name__ == "__main__":
    main()
