import requests

# Look at the coordinates of the 20 last runs to create an average latitude and longitude which will be used
# to get the weather
def get_user_localisation(positions:list)->tuple:
    if not positions:
        return (0, 0)
    x_sum = sum(t[0] for t in positions)
    y_sum = sum(t[1] for t in positions)
    n = len(positions)
    return (x_sum / n, y_sum / n)



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
    "exclude" : "minutely"

    }

    response = requests.get(base_url, params=params)

    return response.json()