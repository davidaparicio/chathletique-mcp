"""
MCP Server Template
"""

from mcp_utils import mcp, echo, get_greeting, greet_user





if __name__ == "__main__":
    mcp.run(transport="streamable-http")
