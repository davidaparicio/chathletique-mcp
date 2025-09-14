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
import numpy as np
import json

def figures_speed_hr_by_activity(client, number_of_activity: int,
                                 resolution: str = "high",
                                 series_type: str = "time", slice_step: int = 10) -> str:
    """
    Retourne un JSON contenant les données de fréquence cardiaque et vitesse
    pour les dernières activités.
    Format :
    [
      {
        "name": "...",
        "time_s": [...],
        "heartrate_bpm": [...],
        "speed_kmh": [...]
      },
      ...
    ]
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
        except Exception:
            continue

        t = np.array(streams["time"].data) if streams and "time" in streams else None
        dist = np.array(streams["distance"].data) if streams and "distance" in streams else None
        vel = np.array(streams["velocity_smooth"].data) if streams and "velocity_smooth" in streams else None
        hr  = np.array(streams["heartrate"].data) if streams and "heartrate" in streams else None

        # Si pas de vitesse, calcul à partir de la distance
        if vel is None and (t is not None) and (dist is not None) and len(t) == len(dist) and len(t) > 1:
            try:
                vel = np.gradient(dist, t)
            except Exception:
                vel = None

        speed_kmh = vel * 3.6 if vel is not None else None

        if t is not None:
            t = t[::slice_step]
        if hr is not None:
            hr = hr[::slice_step]
        if speed_kmh is not None:
            speed_kmh = speed_kmh[::slice_step]

        # Conversion en listes pour JSON
        activity_data = {
            "name": getattr(act, "name", "Activity"),
            "time_s": t.tolist() if t is not None else [],
            "heartrate_bpm": hr.tolist() if hr is not None else [],
            "speed_kmh": speed_kmh.tolist() if speed_kmh is not None else []
        }

        out.append(activity_data)

    # Retour JSON (string)
    return json.dumps(out, indent=2)

activities_data = figures_speed_hr_by_activity(client, number_of_activity=1)

# Sauvegarde en JSON
output_file = "activities.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(activities_data, f, indent=2, ensure_ascii=False)

print(f"✅ Données sauvegardées dans {output_file}")