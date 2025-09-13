"""
MCP Server Template
"""

#from mcp_utils import mcp, echo, get_greeting, greet_user
from strava_tools import mcp, get_athletes_stats, get_last_runs




if __name__ == "__main__":
    mcp.run(transport="streamable-http")
