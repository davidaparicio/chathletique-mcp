"""MCP Server Template"""

from .mcp_utils import mcp

from . import strava_tools
from . import weather_tools


def main():
        mcp.run(transport="streamable-http", port=3000, stateless_http=True)


if __name__ == "__main__":
    main()
