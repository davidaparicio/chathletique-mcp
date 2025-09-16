"""MCP Server Template"""

from .mcp_utils import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
