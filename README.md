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
cd chathletique-mcp
```

2. **Install Python dependencies with uv:**
```bash
# Install uv if you don't have it (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync

# Install development dependencies (for contributing)
uv sync --extra dev
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
uv run pre-commit install

# Optional: Run pre-commit on all files to check everything
uv run pre-commit run --all-files
```

## Usage

### Starting the Server

```bash
# Using uv (recommended)
uv run python -m src.strava_mcp.main

# Or activate the environment and run directly
source .venv/bin/activate  # On Unix/macOS
python -m src.strava_mcp.main
```

The server will start on port 3000 and be accessible at `http://localhost:3000/mcp`.

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

### Contributing Guidelines

1. **Install development dependencies:**
   ```bash
   uv sync --extra dev
   uv run pre-commit install
   ```

2. **Run tests:**
   ```bash
   uv run pytest
   ```

3. **Run quality checks manually:**
   ```bash
   # Run all pre-commit hooks
   uv run pre-commit run --all-files

   # Run specific tools
   uv run ruff check src/
   uv run mypy src/
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Your commit message"
   # Pre-commit hooks run automatically
   ```

All code is automatically checked for:
- **Security vulnerabilities** (Bandit-style checks)
- **Code style** (PEP 8 compliance)
- **Import organization** (isort-style)
- **Type annotations** (MyPy checking)
- **Documentation quality** (Google docstring format)
- **Common Python mistakes** (Bugbear checks)

### 🇫🇷 Installation et Pre-commit (French)

**Installation rapide avec uv :**
```bash
# 1. Cloner le projet
git clone <votre-repo-url>
cd chathletique-mcp

# 2. Installer uv (gestionnaire de paquets Python ultra-rapide)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Installer les dépendances
uv sync --extra dev

# 4. Configurer les hooks pre-commit
uv run pre-commit install
```

**Comment fonctionne pre-commit :**

Pre-commit est un système qui exécute automatiquement des vérifications de qualité de code **avant chaque commit**.

**Avantages :**
- ✅ **Code toujours propre** : Impossible de commiter du code mal formaté
- ✅ **Sécurité automatique** : Détection des vulnérabilités courantes
- ✅ **Style cohérent** : Formatage automatique selon les standards Google
- ✅ **Documentation forcée** : Docstrings obligatoires et bien formatées
- ✅ **Imports organisés** : Tri automatique des imports

**Que se passe-t-il lors d'un commit :**
1. Vous faites `git commit -m "mon message"`
2. Pre-commit lance automatiquement tous les outils de qualité
3. Si des problèmes sont détectés, le commit est **bloqué**
4. Les outils corrigent automatiquement ce qu'ils peuvent
5. Vous revérifiez les modifications et recommitez

**Outils inclus :**
- **Ruff** : Linter ultra-rapide (remplace flake8, isort, black)
- **MyPy** : Vérification des types Python
- **Codespell** : Correction des fautes de frappe
- **Security checks** : Détection de failles de sécurité

## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Use Cases

- **AI Running Coach**: Integrate with Le Chat or other AI assistants for personalized running advice
- **Training Analysis**: Analyze performance trends and provide insights
- **Route Discovery**: Generate new running routes based on preferences and weather
- **Weather-aware Planning**: Plan runs based on upcoming weather conditions
