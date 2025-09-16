# Tests

Simple test suite for the Strava Coach MCP Server.

## Running Tests

```bash
# Install development dependencies
uv add --dev pytest pytest-mock

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_weather_tools.py -v
```

## Test Coverage

### `test_weather_tools.py`
- Tests weather data filtering functionality
- Validates weather API response processing
- Tests edge cases (missing data, empty responses)

### `test_strava_tools.py`
- Tests route planning utility functions
- Validates Google Maps link generation
- Tests distance validation and conversion logic

### `test_mcp_utils.py`
- Tests MCP server configuration and imports
- Basic module loading validation

## Test Structure

Tests focus on:
- **Pure functions** that don't require API calls
- **Data processing logic** for weather and route planning
- **URL generation** for Google Maps integration
- **Validation logic** for distance parameters

API-dependent functions are not directly tested to avoid requiring API keys and external service dependencies during testing.
