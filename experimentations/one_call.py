import os
from stravalib.client import Client
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('STRAVA_ACCESS_TOKEN')

if not token:
    print("Error: STRAVA_ACCESS_TOKEN not found in .env file")
    exit(1)

client = Client(access_token=token)

try:
    for i, activity in enumerate(client.get_activities(limit=10), 1):
        distance_km = float(activity.distance) / 1000 if activity.distance else 0
        print(f"{i}. {activity.name} - {distance_km:.1f}km - {activity.type}")
except Exception as e:
    print(f"Error: {e}")
    print("Check your token at: https://www.strava.com/settings/api")

