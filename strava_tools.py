import os
from stravalib.client import Client
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import Field

import mcp.types as types
from mcp_utils import mcp
import json
load_dotenv()
token = os.getenv('STRAVA_ACCESS_TOKEN')

if not token:
    print("Error: STRAVA_ACCESS_TOKEN not found in .env file")
    exit(1)

client = Client(access_token=token)




@mcp.tool(
    title="Get Authenticated user Strava Stats",
    description="Return the Strava stats of the user as a JSON File ",
)
def Get_Athletes_Stats() -> str :
    '''
    
    Output : A JSON Containing all the stats of the current user
    '''
    athlete_id = client.get_athlete().id # APi call
    ahtlete_stats = client.get_athlete_stats(athlete_id)
    dict = {"recent_run_totals" : ahtlete_stats.recent_run_totals.model_dump_json(), "ytd_run_totals" : ahtlete_stats.ytd_run_totals.model_dump_json(), "all_run_totals" : ahtlete_stats.all_run_totals.model_dump_json()}
    
    return dict

