# Strava API Client Guide

This guide covers the main methods available in the `stravalib` Python client for interacting with the Strava API.

## Setup

```python
import os
from stravalib.client import Client
from dotenv import load_dotenv

load_dotenv()
client = Client(access_token=os.getenv('STRAVA_ACCESS_TOKEN'))
```

## 🏃‍♂️ Activities

### Get Activities
```python
# Get recent activities (most common)
activities = client.get_activities(limit=10)

# Get activities with date filters
from datetime import datetime, timedelta
after_date = datetime.now() - timedelta(days=30)
activities = client.get_activities(after=after_date, limit=50)

# Get activities before a specific date
before_date = datetime.now() - timedelta(days=7)
activities = client.get_activities(before=before_date, limit=20)
```

### Get Single Activity
```python
# Get detailed activity by ID
activity = client.get_activity(activity_id=12345)

# Get activity with all segment efforts
activity = client.get_activity(activity_id=12345, include_all_efforts=True)
```

### Create & Update Activities
```python
# Create manual activity
from datetime import datetime
activity = client.create_activity(
    name="Morning Run",
    activity_type="Run",
    start_date_local=datetime.now(),
    elapsed_time=1800,  # 30 minutes in seconds
    description="Great morning run!",
    distance=5000  # 5km in meters
)

# Update existing activity
client.update_activity(
    activity_id=12345,
    name="Updated Activity Name",
    description="New description",
    private=False
)
```

### Upload Activity File
```python
# Upload GPX/TCX file
with open('activity.gpx', 'rb') as f:
    upload = client.upload_activity(
        activity_file=f,
        data_type='gpx',
        name="Uploaded Run",
        description="Uploaded from GPS watch"
    )
```

## 👤 Athlete Info

### Get Athlete Details
```python
# Get your own profile
athlete = client.get_athlete()
print(f"Name: {athlete.firstname} {athlete.lastname}")
print(f"Location: {athlete.city}, {athlete.state}")

# Get athlete statistics
stats = client.get_athlete_stats()
print(f"Total runs: {stats.recent_run_totals.count}")
print(f"Total distance: {stats.all_run_totals.distance / 1000:.1f} km")
```

### Update Athlete Profile
```python
# Update your profile
client.update_athlete(
    city="New City",
    state="New State", 
    weight=70.5  # kg
)
```

## 🏘️ Clubs

### Get Club Info
```python
# Get your clubs
clubs = client.get_athlete_clubs()

# Get specific club details
club = client.get_club(club_id=12345)
print(f"Club: {club.name}, Members: {club.member_count}")

# Get club members
members = client.get_club_members(club_id=12345, limit=50)

# Get club activities
club_activities = client.get_club_activities(club_id=12345, limit=20)
```

### Join/Leave Clubs
```python
# Join a club
client.join_club(club_id=12345)

# Leave a club
client.leave_club(club_id=12345)
```

## 🛣️ Segments

### Explore Segments
```python
# Find segments in an area (bounding box)
segments = client.explore_segments(
    bounds=[37.7749, -122.4194, 37.7849, -122.4094],  # San Francisco area
    activity_type="running"
)

# Get specific segment
segment = client.get_segment(segment_id=12345)
print(f"Segment: {segment.name}, Distance: {segment.distance}m")

# Get your starred segments
starred = client.get_starred_segments(limit=20)
```

### Segment Efforts
```python
# Get specific segment effort
effort = client.get_segment_effort(effort_id=12345)
print(f"Time: {effort.elapsed_time}, Rank: {effort.pr_rank}")
```

## 🗺️ Routes

### Get Routes
```python
# Get your routes
routes = client.get_routes(limit=20)

# Get specific route
route = client.get_route(route_id=12345)
print(f"Route: {route.name}, Distance: {route.distance}m")
```

## 📊 Streams (Detailed Activity Data)

### Activity Streams
```python
# Get activity streams (GPS, heart rate, power, etc.)
streams = client.get_activity_streams(
    activity_id=12345,
    types=['time', 'distance', 'latlng', 'altitude', 'heartrate'],
    resolution='medium'
)

# Access stream data
if 'latlng' in streams:
    gps_points = streams['latlng'].data
    print(f"GPS points: {len(gps_points)}")

if 'heartrate' in streams:
    hr_data = streams['heartrate'].data
    print(f"Avg HR: {sum(hr_data)/len(hr_data):.0f}")
```

### Segment & Route Streams
```python
# Get segment streams
segment_streams = client.get_segment_streams(
    segment_id=12345,
    types=['distance', 'altitude']
)

# Get route streams  
route_streams = client.get_route_streams(route_id=12345)
```

## 🔧 Common Patterns

### Basic Activity Loop
```python
for activity in client.get_activities(limit=20):
    distance_km = float(activity.distance) / 1000 if activity.distance else 0
    print(f"{activity.name} - {distance_km:.1f}km - {activity.type}")
    print(f"Date: {activity.start_date_local.strftime('%Y-%m-%d')}")
```

### Filter by Activity Type
```python
runs = [a for a in client.get_activities(limit=50) if a.type == 'Run']
rides = [a for a in client.get_activities(limit=50) if a.type == 'Ride']
```

### Get Recent Running Stats
```python
from datetime import datetime, timedelta

recent_runs = []
for activity in client.get_activities(limit=100):
    if activity.type == 'Run':
        recent_runs.append(activity)
    if len(recent_runs) >= 10:  # Get last 10 runs
        break

total_distance = sum(float(run.distance or 0) for run in recent_runs) / 1000
print(f"Last 10 runs: {total_distance:.1f} km")
```

## 🔑 Authentication & Error Handling

### Basic Error Handling
```python
try:
    activities = client.get_activities(limit=10)
    for activity in activities:
        print(activity.name)
except Exception as e:
    print(f"Error: {e}")
    print("Check your token at: https://www.strava.com/settings/api")
```

### Token Setup
1. Go to https://www.strava.com/settings/api
2. Create an access token with required scopes (e.g., `activity:read`)
3. Add to your `.env` file: `STRAVA_ACCESS_TOKEN=your_token_here`

## 📝 Activity Types
Common activity types you'll see:
- `Run`, `Ride`, `Swim`, `Hike`, `Walk`
- `WeightTraining`, `Crossfit`, `Yoga`
- `AlpineSki`, `BackcountrySki`, `NordicSki`
- `Kayaking`, `Canoeing`, `Rowing`
- And many more...

## 🔗 Useful Resources
- [Strava API Documentation](https://developers.strava.com/docs/reference/)
- [Stravalib Documentation](https://stravalib.readthedocs.io/)
- [Strava Developer Portal](https://www.strava.com/settings/api)
