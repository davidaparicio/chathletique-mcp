"""
MCP Server Template
"""

from strava_tools import get_athletes_stats, get_last_runs, create_itinerary
from weather_tools import get_weather_prediction

from mcp.server.fastmcp import FastMCP
from mcp_utils import mcp

mcp = FastMCP("Echo Server", port=3000, stateless_http=True, debug=True)



if __name__ == "__main__":
    mcp.run(transport="streamable-http")
