#  Strava Coach MCP Server

### 🏆 MISTRAL MCP HACKATHON WINNER 🏆

**@Loucienne** </n>
**@leotrois** </n>
**@frogens** </n>
**@Ulysse6307** </n>
**@colinfrisch** </n>

A Model Context Protocol (MCP) server that provides AI assistants with access to Strava running data, route planning, and weather information. This server enables intelligent running coaching by combining Strava activity analysis with real-time weather data and route generation capabilities.


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
cd chathletique-mcp
```

2. **Install Python dependencies:**
```bash
# Install project dependencies
pip install -e .

# Install development dependencies (for contributing)
pip install -e ".[dev]"
```

3. **Configure environment:**
```bash
# Create .env file with your API keys
cp .env.example .env
# Edit .env with your actual API keys
```

4. **Set up code quality tools (for contributors):**
```bash
# Install pre-commit hooks for automatic code quality checks
pre-commit install

# Optional: Run pre-commit on all files to check everything
pre-commit run --all-files
```


## Architecture

The server is built using:
- **FastMCP**: For MCP protocol implementation
- **Stravalib**: For Strava API integration
- **OpenRouteService**: For route generation
- **OpenWeatherMap API**: For weather data
- **Matplotlib**: For data visualization

### Project Structure
```
chathletique-mcp/
├── src/strava_mcp/
│   ├── __init__.py      # Package initialization
│   ├── main.py          # MCP server entry point
│   ├── strava_tools.py  # Strava API integration tools
│   ├── weather_tools.py # Weather prediction tools
│   └── mcp_utils.py     # MCP server configuration
├── tests/               # Test suite
├── .pre-commit-config.yaml  # Code quality configuration
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock             # Lock file for reproducible installs
└── README.md           # This file
```

## 🛠️ Development & Code Quality

This project uses modern Python development tools for maintaining high code quality:

### Code Quality Tools

- **Ruff**: Ultra-fast Python linter and formatter with comprehensive rules
- **MyPy**: Static type checking for better code reliability
- **Pre-commit**: Automatic code quality checks before each commit
- **Pytest**: Testing framework with coverage reporting
- **Black**: Code formatting (integrated with Ruff)

### Pre-commit Hooks

The project includes automatic quality checks that run before each commit:

1. **Code formatting**: Automatic code formatting with Ruff
2. **Import sorting**: Organize imports consistently
3. **Linting**: Check for bugs, security issues, and style problems
4. **Type checking**: Verify type annotations with MyPy
5. **Docstring validation**: Enforce Google-style docstrings
6. **Security scanning**: Detect potential security vulnerabilities
7. **Spell checking**: Catch typos in code and documentation


## Use Cases

- **AI Running Coach**: Integrate with Le Chat or other AI assistants for personalized running advice
- **Training Analysis**: Analyze performance trends and provide insights
- **Route Discovery**: Generate new running routes based on preferences and weather
- **Weather-aware Planning**: Plan runs based on upcoming weather conditions
