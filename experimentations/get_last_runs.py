from mcp.server.fastmcp import FastMCP
from pydantic import Field
from stravalib.client import Client
from dotenv import load_dotenv
import os

import mcp.types as types

load_dotenv()
token = os.getenv('STRAVA_ACCESS_TOKEN')

if not token:
    print("Error: STRAVA_ACCESS_TOKEN not found in .env file")
    exit(1)

client = Client(access_token=token)











mcp = FastMCP("Echo Server", port=3000, stateless_http=True, debug=True)


@mcp.tool(
    title="Get Last Runs",
    description="Get the last runs from the user's Strava account and return them in a list for activity analysis",
)
def get_last_runs() -> str:
    runs = []
    for i, activity in enumerate(client.get_activities(limit=10), 1):
        distance_km = float(activity.distance) / 1000 if activity.distance else 0
        runs.append(f"{i}. {activity.name} - {distance_km:.1f}km - {activity.type}")

    return '\n'.join(runs)
