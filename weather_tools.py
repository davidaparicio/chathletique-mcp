import requests
import os
from mcp_utils import mcp
import json
from dotenv import load_dotenv


# -------------------------------- Globals --------------------------------
load_dotenv()
token = os.getenv('WEATHER_API_KEY')
if not token:
    print("Error: WEATHER_API_KEY not found in .env file")
    exit(1)




# -------------------------------- Tools --------------------------------
@mcp.tool(
    title="Get Weather Predictions",
    description="Return some future weather informations for where the user leaves. the place where the user lives is found by looking at where previous runs is located ",
)
def get_weather_prediction()-> str:

    """
    Loads positions from run_positions.txt and returns weather forecast as a dict.
    """
    try:
        with open("run_positions.txt", "r") as f:
            positions = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: run_positions.txt not found. Please generate run positions first.")
        return None

    base_url = "http://api.openweathermap.org/data/2.5/forecast"

    average_location = get_user_localisation(positions)
    params = {
    "lat": round(average_location[0], 2),
    "lon": round(average_location[1], 2),
    "appid" : token,
    "exclude" : "current,minutely,alerts",

    }

    response = requests.get(base_url, params=params)
    response = filter_weather_data(response.json()) # filter out to keep relevant data
    return str(response)



# -------------------------------- Useful functions --------------------------------

# Look at the coordinates of the 20 last runs to create an average latitude and longitude which will be used to get the weather
def get_user_localisation(lines:list)->tuple:
    #preprocess positions from strings to tuples
    positions = []
    for line in lines:
        # Remove "root=" and brackets, then split by comma
        numbers = line.strip().replace("root=", "").strip("[]")
        lat, lon = map(float, numbers.split(","))
        positions.append([lat, lon])
    x_sum = sum(t[0] for t in positions)
    y_sum = sum(t[1] for t in positions)
    n = len(positions)
    return (x_sum / n, y_sum / n)



# Keep only the relevant fields from the weather data
def filter_weather_data(data):
    """
    Simplify OpenWeatherMap 5-day/3-hour forecast data, keeping:
    - temp
    - feels_like
    - humidity
    - weather (main + description)
    - wind (speed, deg, gust)
    - pop
    - rain (3h if available, else 0)
    - dt
    - sunrise and sunset (datetime in local time)
    """
    city_info = data.get("city", {})
    timezone_offset = city_info.get("timezone", 0)  # in seconds
    sunrise_utc = city_info.get("sunrise")
    sunset_utc = city_info.get("sunset")
    name = city_info.get("name")


    simplified = [{"sunrise": sunrise_utc, "sunset": sunset_utc, "timezone": timezone_offset, "name": name}]

    for entry in data.get("list", []):
        main = entry.get("main", {})
        weather = entry.get("weather", [{}])[0]  # usually one element
        wind = entry.get("wind", {})
        rain = entry.get("rain", {}).get("3h", 0)  # default to 0 if missing

        simplified.append({
            "temp": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "humidity": main.get("humidity"),
            "weather": {
                "main": weather.get("main"),
                "description": weather.get("description")
            },
            "wind": {
                "speed": wind.get("speed"),
                "deg": wind.get("deg"),
                "gust": wind.get("gust")
            },
            "pop": entry.get("pop"),
            "rain": rain,
            "dt": entry.get("dt")
        })

    return simplified
