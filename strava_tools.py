import os
from stravalib.client import Client
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import Field

import mcp.types as types
from mcp_utils import mcp

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
    pass 


    return 'stats'