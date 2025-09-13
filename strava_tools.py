import os
import math
import json
from dotenv import load_dotenv


import stravalib
from urllib.parse import urlencode, quote_plus
import mcp.types as types
import openrouteservice


from mcp_utils import mcp

from dotenv import load_dotenv



# -------------------------------- Globals --------------------------------
load_dotenv()
strava_api_key = os.getenv('STRAVA_ACCESS_TOKEN')
ors_api_key = os.getenv('ORS_KEY')
if not strava_api_key:
    print("Error: STRAVA_ACCESS_TOKEN not found in .env file")
    exit(1)

client_strava = stravalib.Client(access_token=strava_api_key)
client_ors = openrouteservice.Client(key=ors_api_key)

# -------------------------------- Tools --------------------------------


@mcp.tool(
    title="Get Authenticated user Strava Stats",
    description="Return the Strava stats of the user as a JSON File ",
)
def get_athletes_stats() -> str :
    '''
    Output : A JSON Containing all the stats of the current user
    '''
    athlete_id = client_strava.get_athlete().id # APi call
    ahtlete_stats = client_strava.get_athlete_stats(athlete_id)
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
    activities = client_strava.get_activities(limit=2)

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




@mcp.tool(
    title="Create Itinerary",
    description="Create an itinerary for the user",
)
def create_itinerary(start : tuple[float, float], 
                    distance_km : int = 10
                    ) -> str :
    """
    Produces an itinerary for the user

    Args :
    - start : tuple[float, float]
    - distance_km : int

    Returns :
    - gmaps_directions_link : str
    """
    seed = 0

    def _get_route(distance_km : int, start : tuple[float, float], seed = 0):
        route = client_ors.directions(
            coordinates=[start], # single coordinate for round_trip
            profile="foot-walking",
            format="geojson",
            options={
                "round_trip": {
                    "length": distance_m, # target length in meters
                    "points": math.ceil(distance_km/2), # more points -> more circular
                    "seed": seed # change to vary the route
                }
            }
        )
        
        return route


    def _get_mapping_coords(route: dict, distance_km: float) -> list[tuple[float, float]]:
        """
        ~2 points per km by evenly sampling indices (not true metric spacing).
        Includes start and end when possible.
        """
        coordinates = route["features"][0]["geometry"]["coordinates"]
        if not coordinates:
            return []
        if len(coordinates) == 1:
            lon, lat = coordinates[0]
            return [(float(lon), float(lat))]

        num_points = max(2, math.ceil(distance_km) + 1)  # include both endpoints
        last_index = len(coordinates) - 1
        sampled_coords = []
        for i in range(num_points):
            coord_index = round(i * last_index / (num_points - 1))
            lon, lat = coordinates[coord_index]
            sampled_coords.append((float(lon), float(lat)))
        return sampled_coords


    def _get_gmaps_directions_link(
            origin_coords: tuple[float, float],
            waypoints_coords_list: list[tuple[float, float]] | None = None,
        ) -> str:
            """
            Build a Google Maps directions URL.

            Inputs are (lon, lat) tuples (GeoJSON-style). Output uses "lat,lon" order.
            If waypoints are provided, creates a loop: origin -> waypoints... -> origin.
            If no waypoints, returns a link to navigate to the origin (from 'Your location').
            """
            lon0, lat0 = origin_coords
            origin = f"{lat0},{lon0}"

            if waypoints_coords_list:
                # Convert (lon, lat) -> "lat,lon" and drop duplicates of origin
                wps = [f"{lat},{lon}" for lon, lat in waypoints_coords_list if f"{lat},{lon}" != origin]
                params = {
                    "api": 1,
                    "origin": origin,
                    "destination": origin,
                    "waypoints": "|".join(wps),
                }
                return "https://www.google.com/maps/dir/?" + urlencode(params, quote_via=quote_plus)

            # No waypoints: just point to the origin as destination
            params = {"api": 1, "destination": origin}
            return "https://www.google.com/maps/dir/?" + urlencode(params, quote_via=quote_plus)


    if distance_km < 3:
        distance_km = 3

    distance_m = int(distance_km * 1300)

    route = _get_route(distance_km, start, seed = seed)
    route_distance = route["features"][0]["properties"]["summary"]["distance"]

    # Make sure that the route is the correct distance
    while route_distance < distance_m - 500 * distance_km / 10 or route_distance > distance_m + 500 * distance_km / 10:
        route = _get_route(distance_km, start, seed = seed + 1)
        route_distance = route["features"][0]["properties"]["summary"]["distance"]

        seed += 1
        if seed > 100:
            break
    
    # Give the mapping coords for the route (points evenly distributed - about 2 points per km)
    mapping_coords = _get_mapping_coords(route, distance_km)
    gmaps_directions_link = _get_gmaps_directions_link(start, mapping_coords)

    return gmaps_directions_link

