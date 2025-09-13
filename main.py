"""
MCP Server Template
"""

from mcp_utils import mcp
from strava_tools import get_athletes_stats, get_last_runs
from weather_tools import get_weather_prediction


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
