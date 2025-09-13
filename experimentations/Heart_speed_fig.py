import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from stravalib.client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('STRAVA_ACCESS_TOKEN')
if not token:
    print("Error: STRAVA_ACCESS_TOKEN not found in .env file")
    exit(1)

client = Client(access_token=token)

def figures_speed_hr_by_activity(client, number_of_activity: int,
                                 resolution: str = "high",
                                 series_type: str = "time"):
    """
    Retourne une liste de tuples: [(activity_name, fig_hr, fig_speed), ...]
    - fig_hr : courbe FC (rouge) en fonction du temps (s)
    - fig_speed : courbe vitesse (bleue) en fonction du temps (s)
    Crée une figure séparée par métrique (pas de subplots).
    """
    out = []
    activities = client.get_activities(limit=number_of_activity)

    for act in activities:
        try:
            streams = client.get_activity_streams(
                act.id,
                types=["time", "distance", "velocity_smooth", "heartrate"],
                resolution=resolution,
                series_type=series_type
            )
        except Exception as e:
            continue

        t = np.array(streams["time"].data) if streams and "time" in streams else None
        dist = np.array(streams["distance"].data) if streams and "distance" in streams else None
        vel = np.array(streams["velocity_smooth"].data) if streams and "velocity_smooth" in streams else None
        hr  = np.array(streams["heartrate"].data) if streams and "heartrate" in streams else None

        if vel is None and (t is not None) and (dist is not None) and len(t) == len(dist) and len(t) > 1:
            try:
                vel = np.gradient(dist, t)
            except Exception:
                vel = None

        speed_kmh = vel * 3.6 if vel is not None else None

        # Figure 1: Heart rate (rouge)
        fig_hr = plt.figure()
        if (t is not None) and (hr is not None) and len(t) == len(hr) and len(hr) > 0:
            plt.plot(t, hr, color="red")
            plt.xlabel("Time (s)")
            plt.ylabel("Heart rate (bpm)")
            plt.title(f"{getattr(act, 'name', 'Activity')} – Heart rate")
        else:
            plt.title(f"{getattr(act, 'name', 'Activity')} – Heart rate")
            plt.text(0.5, 0.5, "No heart rate stream", ha="center", va="center", transform=plt.gca().transAxes)

        # Figure 2: Speed (bleu)
        fig_speed = plt.figure()
        if (t is not None) and (speed_kmh is not None) and len(t) == len(speed_kmh) and len(speed_kmh) > 0:
            plt.plot(t, speed_kmh, color="blue")
            plt.xlabel("Time (s)")
            plt.ylabel("Speed (km/h)")
            plt.title(f"{getattr(act, 'name', 'Activity')} – Speed")
        else:
            plt.title(f"{getattr(act, 'name', 'Activity')} – Speed")
            plt.text(0.5, 0.5, "No speed stream", ha="center", va="center", transform=plt.gca().transAxes)

        out.append((getattr(act, "name", "Activity"), fig_hr, fig_speed))

    return out
