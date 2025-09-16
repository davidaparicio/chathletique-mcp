"""
Simple tests for weather tools functionality
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from strava_mcp.weather_tools import filter_weather_data


def test_filter_weather_data_basic():
    """Test that filter_weather_data processes basic weather data correctly"""
    # Sample weather API response structure
    sample_data = {
        "city": {
            "name": "Paris",
            "timezone": 7200,
            "sunrise": 1234567890,
            "sunset": 1234567890,
        },
        "list": [
            {
                "main": {"temp": 20.5, "feels_like": 18.0, "humidity": 65},
                "weather": [{"main": "Clear", "description": "clear sky"}],
                "wind": {"speed": 5.2, "deg": 180, "gust": 7.1},
                "pop": 0.1,
                "rain": {"3h": 0.5},
                "dt": 1234567890,
            }
        ],
    }

    result = filter_weather_data(sample_data)

    # Check structure
    assert len(result) == 2  # Header + 1 weather entry

    # Check header
    header = result[0]
    assert header["name"] == "Paris"
    assert header["timezone"] == 7200
    assert "sunrise" in header
    assert "sunset" in header

    # Check weather entry
    weather_entry = result[1]
    assert weather_entry["temp"] == 20.5
    assert weather_entry["feels_like"] == 18.0
    assert weather_entry["humidity"] == 65
    assert weather_entry["weather"]["main"] == "Clear"
    assert weather_entry["weather"]["description"] == "clear sky"
    assert weather_entry["wind"]["speed"] == 5.2
    assert weather_entry["pop"] == 0.1
    assert weather_entry["rain"] == 0.5
    assert weather_entry["dt"] == 1234567890


def test_filter_weather_data_missing_rain():
    """Test that filter_weather_data handles missing rain data"""
    sample_data = {
        "city": {"name": "Test City", "timezone": 0},
        "list": [
            {
                "main": {"temp": 15.0, "feels_like": 14.0, "humidity": 80},
                "weather": [{"main": "Cloudy", "description": "overcast"}],
                "wind": {"speed": 3.0},
                "pop": 0.3,
                "dt": 1234567890,
                # No rain data
            }
        ],
    }

    result = filter_weather_data(sample_data)
    weather_entry = result[1]

    assert weather_entry["rain"] == 0  # Should default to 0


def test_filter_weather_data_empty_list():
    """Test that filter_weather_data handles empty weather list"""
    sample_data = {"city": {"name": "Empty", "timezone": 0}, "list": []}

    result = filter_weather_data(sample_data)

    assert len(result) == 1  # Only header, no weather entries
    assert result[0]["name"] == "Empty"
