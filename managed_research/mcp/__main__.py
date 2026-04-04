"""CLI entrypoint for the stdio MCP server."""

from managed_research.mcp.server import ManagedResearchMcpServer


def main() -> None:
    ManagedResearchMcpServer().serve_stdio()


if __name__ == "__main__":
    main()
