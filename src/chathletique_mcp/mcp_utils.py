"""MCP utilities for Strava coaching server."""

from fastmcp import FastMCP

mcp = FastMCP("Chathletique MCP Server", port=3000, stateless_http=True, debug=True)
