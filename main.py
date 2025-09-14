"""
MCP Server Template
"""

from strava_tools import get_user_stats, get_last_runs, create_itinerary
from weather_tools import get_weather_prediction

from mcp_utils import mcp



if __name__ == "__main__":
    mcp.run(transport="streamable-http")
