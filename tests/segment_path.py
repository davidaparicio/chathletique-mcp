from dotenv import load_dotenv

import os
import stravalib
import openrouteservice
import polyline
import openrouteservice
from urllib.parse import quote_plus, urlencode
import requests
import math
import random


load_dotenv()


strava_api_key = os.getenv("STRAVA_ACCESS_TOKEN")
ors_api_key = os.getenv("ORS_KEY")
google_api_key = os.getenv("GOOGLE_MAP_API_KEY")

client_strava = stravalib.Client(access_token=strava_api_key)
client_ors = openrouteservice.Client(key=ors_api_key)

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


bounds = [48.84, 2.23, 48.88, 2.27]


def compute_route(origin, destination, waypoints=None, mode="WALK", api_key=google_api_key) -> dict:
    """
    origin, destination, waypoints: (lat, lon)
    mode: "WALK" | "DRIVE" | "BICYCLE" | "TWO_WHEELER"
    Retourne dict avec distance (m), durée ISO, et polyline encodée.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline",
    }
    def ll(pt):  # (lat, lon) -> payload Routes API
        return {"location": {"latLng": {"latitude": float(pt[0]), "longitude": float(pt[1])}}}

    body = {
        "origin": ll(origin),
        "destination": ll(destination),
        "travelMode": mode.upper(),
    }
    if waypoints:
        body["intermediates"] = [ll(w) for w in waypoints]

    r = requests.post(ROUTES_URL, headers=headers, json=body, timeout=20)
    if r.status_code != 200:
        # Affiche la vraie raison du 400/403/etc.
        raise RuntimeError(f"Routes API {r.status_code}: {r.text}")

    route = r.json()["routes"][0]

    return {
        "distance_m": route["distanceMeters"],
        "duration_iso": route["duration"],
        "encoded_polyline": route["polyline"]["encodedPolyline"],
    }



def get_segments(bounds):

    segments=client_strava.explore_segments(bounds=bounds, activity_type='running')

    list_segment=[]

    for seg in segments:
        desc = {
            "id": int(seg.id),
            "name": seg.name,
            "distance_m": float(seg.distance),
            "points": polyline.decode(seg.points),
            "start_latlng": seg.start_latlng,
            "end_latlng": seg.end_latlng,
        }
        list_segment.append(desc)

    return list_segment

def get_path_segment(segment : dict) -> list[tuple[float, float]]:
    """Get a running path from start to end, passing through segment_path."""

    length_segment=len(segment["points"])
    middle_coord_index1=length_segment//4
    middle_coord_index2=3*length_segment//4
    quarter_coord=segment["points"][middle_coord_index1]  
    three_quarter_coord=segment["points"][middle_coord_index2]
    start_coord=(segment["start_latlng"].root[0], segment["start_latlng"].root[1])
    end_coord=(segment["end_latlng"].root[0], segment["end_latlng"].root[1])

    return [start_coord, quarter_coord, three_quarter_coord, end_coord]


def _get_gmaps_directions_link(
        origin_coords: tuple[float, float],
        waypoints_coords_list: list[tuple[float, float]] | None = None,
    ) -> str:
        """Build a Google Maps directions URL.

        Inputs are (lon, lat) tuples (GeoJSON-style). Output uses "lat,lon" order.
        If waypoints are provided, creates a loop: origin -> waypoints... -> origin.
        If no waypoints, returns a link to navigate to the origin (from 'Your location').
        """
        lat0, lon0 = origin_coords
        origin = f"{lat0},{lon0}"

        if waypoints_coords_list:
            wps = [
                f"{lat},{lon}"
                for lat, lon in waypoints_coords_list
                if f"{lat},{lon}" != origin
            ]
            params = {
                "api": 1,
                "origin": origin,
                "destination": origin,
                "waypoints": "|".join(wps),
            }
            return "https://www.google.com/maps/dir/?" + urlencode(
                params, quote_via=quote_plus
            )

        # No waypoints: just point to the origin as destination
        params = {"api": 1, "destination": origin}
        return "https://www.google.com/maps/dir/?" + urlencode(
            params, quote_via=quote_plus
        )



def create_path(listsegment, distance, start_coords):
    new_list_segment=[]

    for list_seg in listsegment:
        for seg in list_seg:
            coord_seg=get_path_segment(seg)
            print("longueur segment depuis le depart: ",compute_route(start_coords,coord_seg[0],coord_seg[1:-1], mode="WALK", api_key=google_api_key)["distance_m"],"Distance segment + nom",seg["distance_m"],seg["name"])
            if distance/3<compute_route(start_coords,coord_seg[0],coord_seg[1:-1], mode="WALK", api_key=google_api_key)["distance_m"]<(distance)/2:
                    print("OK")
                    new_list_segment.append(seg)
        
    print("Nb segments retenus :", len(new_list_segment))

    segs = new_list_segment[:]        
    random.shuffle(segs) # on choisit un ordre aléatoire pour eviter de donner le meme segment au client à chaque fois
            
    for seg in segs:

        pas=0.1
        path_segment=get_path_segment(seg)
        new_waypoint=(path_segment[-1][0]+pas, path_segment[-1][1]+pas)
        path_segment.append(new_waypoint)
        pas=pas/2

        for _ in range(10):

            actual_distance=compute_route(start_coords, start_coords, path_segment, mode="WALK",api_key=google_api_key)["distance_m"]

            if distance-100<actual_distance<distance+100:
                print("Nom du segment:",seg["name"], "Distance segment :",seg["distance_m"])
                return start_coords, path_segment

            if actual_distance>distance:
                new_waypoint=(new_waypoint[0]- pas, new_waypoint[1]-pas)
                
                
            elif actual_distance<distance:
                new_waypoint=(new_waypoint[0]+pas, new_waypoint[1]+pas)

            path_segment[-1]=new_waypoint
            pas=pas/2

            print("Distance Actuel, point et pas !", actual_distance, new_waypoint, pas)

    return "No segment found"

import math

def bounds_for_run(center_lat, center_lon, distance_m):
    """
    Retourne 4 bounds (SW, SE, NW, NE), chacun au format
    [min_lat, min_lon, max_lat, max_lon].
    Le bounds global est centré sur (center_lat, center_lon) et
    peut contenir un cercle de rayon = distance_m/2.
    """
    half = distance_m / 2.0  # demi-côté du carré
    dlat = half / 111_320.0
    dlon = half / (111_320.0 * math.cos(math.radians(center_lat)))

    min_lat, max_lat = center_lat - dlat, center_lat + dlat
    min_lon, max_lon = center_lon - dlon, center_lon + dlon
    mid_lat = (min_lat + max_lat) / 2.0
    mid_lon = (min_lon + max_lon) / 2.0

    # Quadrillage en 4 tuiles : SW, SE, NW, NE
    bounds = [
        [min_lat, min_lon, mid_lat, mid_lon],  # SW
        [min_lat, mid_lon, mid_lat, max_lon],  # SE
        [mid_lat,  min_lon, max_lat, mid_lon], # NW
        [mid_lat,  mid_lon, max_lat, max_lon], # NE
    ]
    return bounds

DOBROPOL_16 = (48.8833, 2.2857)  # approx lat, lon


bounds = bounds_for_run(48.8833, 2.285, 10_000)
list_segment=[]
for bound in bounds:
    list_segment.append(get_segments(bound))
Path=create_path(list_segment, 10000, DOBROPOL_16)
print(Path)
maps=_get_gmaps_directions_link(Path[0], Path[1])
print(maps)






