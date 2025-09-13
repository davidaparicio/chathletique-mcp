import os
import math
from dotenv import load_dotenv
from urllib.parse import urlencode, quote_plus

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp_utils import mcp
import openrouteservice

# -------------------------------- Globals --------------------------------

mcp = FastMCP("Echo Server", port=3000, stateless_http=True, debug=True)

load_dotenv()
api_key = os.getenv('ORS_KEY')

if not api_key:
    print("Error: ORS_KEY not found in .env file")
    exit(1)

client = openrouteservice.Client(key=api_key)

# -------------------------------- Tools --------------------------------

@mcp.tool(
    title="Create Itinerary",
    description="Create an itinerary for the user",
)
def create_itinerary(start : tuple[float, float], 
                    distance_km : int = 10
                    ) -> str :
    """
    Output : link for the itinerary
    """
    seed = 0

    def _get_route(distance_km : int, start : tuple[float, float], seed = 0):
        route = client.directions(
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



if __name__ == "__main__":
    distance_km = 20
    start = [2.3522, 48.8566]
    gmaps_directions_link = create_itinerary(distance_km = distance_km, start = start)
    print(gmaps_directions_link)

    
