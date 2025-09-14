#  Strava Coach MCP Server

### 🏆 MISTRAL MCP HACKATHON WINNER 🏆

@Loucienne
@leotrois	
@frogens
@Ulysse6307	
@colinfrisch

A Model Context Protocol (MCP) server that provides AI assistants with access to Strava running data, route planning, and weather information. This server enables intelligent running coaching by combining Strava activity analysis with real-time weather data and route generation capabilities.

## Features

### Strava Integration
- **User Statistics**: Access comprehensive running stats (recent, year-to-date, and all-time totals)
- **Activity Analysis**: Retrieve detailed information about recent runs including pace, heart rate, and elevation
- **Performance Visualization**: Generate heart rate and speed charts for activity analysis

### Route Planning
- **Intelligent Itinerary Creation**: Generate running routes of specified distances from any starting location
- **Round-trip Route Generation**: Create circular routes that return to the starting point
- **Google Maps Integration**: Automatically generate Google Maps directions links for easy navigation

### Weather Intelligence
- **Location-based Forecasting**: Get weather predictions for your usual running areas
- **Activity-derived Location**: Automatically determine your location from previous run data
- **Detailed Weather Data**: Access temperature, humidity, precipitation, and wind information

## Setup

### Prerequisites
- Python 3.13+
- Active Strava account with API access
- OpenWeatherMap API key
- OpenRouteService API key

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
STRAVA_ACCESS_TOKEN=your_strava_access_token
WEATHER_API_KEY=your_openweathermap_api_key
ORS_KEY=your_openrouteservice_api_key
```

#### Getting API Keys (all for free)

**Strava API Token:**
1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Create an application if you haven't already
3. Use the "Create & View a Refresh Token" tool or follow Strava's OAuth flow
4. Copy the access token

**OpenWeatherMap API Key:**
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Subscribe to the 5 Day / 3 Hour Forecast API (free tier available)
3. Copy your API key

**OpenRouteService API Key:**
1. Register at [OpenRouteService](https://openrouteservice.org/)
2. Get your free API key from the dashboard

### Installation

1. **Clone and setup:**
```bash
git clone <your-repo-url>
cd MCP-hackathon
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Copy and edit the .env file with your API keys
cp .env.example .env
# Edit .env with your actual API keys
```

## Usage

### Starting the Server

```bash
python main.py
```

The server will start on port 3000 and be accessible at `http://localhost:3000/mcp`. Else you can deploy it directly on huggingface using https://huggingface.co/spaces/Jofthomas/MCP_Server_Template/blob/main/server.py

### Testing with MCP Inspector

1. **Install and run the MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector
```

2. **Configure connection:**
- Transport Type: `Streamable HTTP`
- URL: `http://127.0.0.1:3000/mcp`

## 📋 Available Tools

### `get_user_stats()`
Retrieves comprehensive Strava statistics for the authenticated user.

**Returns:** JSON containing recent, year-to-date, and all-time running totals

**Example response:**
```json
{
  "recent_run_totals": {"distance": 50000, "time": 12000, "count": 5},
  "ytd_run_totals": {"distance": 500000, "time": 120000, "count": 50},
  "all_run_totals": {"distance": 2000000, "time": 480000, "count": 200}
}
```

### `get_last_runs()`
Fetches detailed information about the user's most recent running activities.

**Returns:** Formatted text with activity details including distance, pace, heart rate, and elevation

**Data includes:**
- Activity name and date
- Distance and duration
- Average and maximum speed
- Heart rate metrics
- Elevation gain

### `create_itinerary(starting_place, distance_km)`
Generates a running route of specified distance starting from a given location.

**Parameters:**
- `starting_place` (str): Starting location (e.g., "Opéra, Paris")
- `distance_km` (int): Desired route distance in kilometers

**Returns:** Google Maps directions URL for the generated route

**Example:**
```python
# Generate a 10km route starting from central Paris
create_itinerary("Opéra, Paris", 10)
```

### `get_weather_prediction()`
Provides weather forecast for the user's typical running area based on previous activity locations.

**Returns:** Detailed weather forecast including temperature, humidity, precipitation probability, and wind conditions

**Note:** Requires running `get_last_runs()` first to establish location data.

### `figures_speed_hr_by_activity(number_of_activity, resolution, series_type)`
Generates heart rate and speed visualization charts for recent activities.

**Parameters:**
- `number_of_activity` (int): Number of recent activities to analyze
- `resolution` (str): Data resolution ("high", "medium", "low")
- `series_type` (str): Series type ("time" or "distance")

**Returns:** List of tuples containing activity names and matplotlib figures

## Architecture

The server is built using:
- **FastMCP**: For MCP protocol implementation
- **Stravalib**: For Strava API integration
- **OpenRouteService**: For route generation
- **OpenWeatherMap API**: For weather data
- **Matplotlib**: For data visualization

### Project Structure
```
hack/
├── main.py              # MCP server entry point
├── strava_tools.py      # Strava integration tools
├── weather_tools.py     # Weather prediction tools
├── mcp_utils.py         # MCP server configuration
├── experimentations/    # Development and testing scripts
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Use Cases

- **AI Running Coach**: Integrate with Le Chat or other AI assistants for personalized running advice
- **Training Analysis**: Analyze performance trends and provide insights
- **Route Discovery**: Generate new running routes based on preferences and weather
- **Weather-aware Planning**: Plan runs based on upcoming weather conditions
