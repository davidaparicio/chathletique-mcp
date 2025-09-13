import requests


#@mcp.tool(description="Given a latitude and longitude, this function returns a string describing the weather forecast at the specified location.")
def get_weather_prediction(positions:list)->str:
    """
        Args:
        lat (float): Latitude of the Location.
        lon (float): Longitude of the location.
        api_key (str): Your OpenWieatherMap API key.

        Returns:
        str: A string describing the weather forecast at the specified location.
    """
    base_url = "http://api.openweathermap.org/data/2.5/forecast"

    average_location = get_user_localisation(positions)
    params = {
    "lat": average_location[0],
    "lon": average_location[1],
    "appid" : "a515a7dc9326035e665789c9cad88573", #hardcoded for now, should be in env variable
    "exclude" : "current,minutely",

    }

    response = requests.get(base_url, params=params)
    response = filter_weather_data(response.json())
    return response



# Look at the coordinates of the 20 last runs to create an average latitude and longitude which will be used to get the weather
def get_user_localisation(positions:list)->tuple:
    if not positions:
        return (0, 0)
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


    simplified = [{"sunrise": sunrise_utc, "sunset": sunset_utc, "timezone": timezone_offset}]

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