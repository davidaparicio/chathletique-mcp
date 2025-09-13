import os
import json


from stravalib.client import Client

from mcp_utils import mcp

from dotenv import load_dotenv



# -------------------------------- Globals --------------------------------
load_dotenv()
token = os.getenv('STRAVA_ACCESS_TOKEN')
if not token:
    print("Error: STRAVA_ACCESS_TOKEN not found in .env file")
    exit(1)

client = Client(access_token=token)



# -------------------------------- Tools --------------------------------


@mcp.tool(
    title="Get Authenticated user Strava Stats",
    description="Return the Strava stats of the user as a JSON File ",
)
def get_athletes_stats() -> str :
    '''
    Output : A JSON Containing all the stats of the current user
    '''
    athlete_id = client.get_athlete().id # APi call
    ahtlete_stats = client.get_athlete_stats(athlete_id)
    dict = {"recent_run_totals" : ahtlete_stats.recent_run_totals.model_dump_json(), "ytd_run_totals" : ahtlete_stats.ytd_run_totals.model_dump_json(), "all_run_totals" : ahtlete_stats.all_run_totals.model_dump_json()}
    
    return str(dict)




@mcp.tool(
    title="Get Last Runs",
    description="Get the last runs from the user's Strava account and return them in a list for activity analysis",
)
def get_last_runs() -> str:
    """
    Get the last runs from the user's Strava account and return them in a list for activity analysis
    This function will use the Strava API to get the last runs from the user's Strava account and return them in a list for activity analysis
    The function will return a list of runs with the following information:
    name, distance, type, start_date_local, moving_time, average_speed, max_speed, max_heartrate, average_heartrate, total_elevation_gain, average_speed
    
    """

    text_result : str = ''
    runs_position : list = []

    # Get the last 10 runs
    activities = client.get_activities(limit=2)

    # Extract the data from the activities
    for activity in activities:
        if activity.type != 'Run':
            continue

        activity_data = {
            'name' : str(activity.name),
            'distance' : str(activity.distance),
            'type' : str(activity.type),
            'start_date_local' : str(activity.start_date_local),
            'moving_time' : str(activity.moving_time),
            'average_speed' : str(activity.average_speed),
            'max_speed' : str(activity.max_speed),
            'max_heartrate' : str(activity.max_heartrate),
            'average_heartrate' : str(activity.average_heartrate),
            'total_elevation_gain' : str(activity.total_elevation_gain),
            'average_speed' : str(activity.average_speed)
        }

        runs_position.append(activity.start_latlng)

        text_result += json.dumps(activity_data) + '\n'

    # Save runs_position to a text file
        with open("run_positions.txt", "w") as f:
            for pos in runs_position:
                f.write(str(pos) + "\n")

    return text_result
