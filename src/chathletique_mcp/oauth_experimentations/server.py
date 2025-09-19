import json
import os

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.auth import AccessToken, TokenVerifier
from fastmcp.server.dependencies import get_access_token

load_dotenv()

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
BASE_URL = os.getenv("BASE_URL")


# --- Strava token verifier (opaque tokens) ---
class StravaTokenVerifier(TokenVerifier):
    """
    Minimal verifier for Strava OAuth access tokens.
    Validates by calling GET https://www.strava.com/api/v3/athlete.
    If 200 OK, the token is accepted.
    """

    def __init__(self, required_scopes: list[str] | None = None):
        self.required_scopes = required_scopes or ["activity:read_all"]

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            resp = requests.get(
                "https://www.strava.com/api/v3/athlete",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if resp.status_code != 200:
                return None

            athlete = resp.json() or {}
            athlete_id = str(athlete.get("id", "")) or "strava-user"
            # Build an AccessToken; claims can be read later via get_access_token()
            return AccessToken(
                token=token,
                client_id=athlete_id,
                scopes=self.required_scopes,
            )
        except Exception:
            return None


# --- OAuth Proxy bridging MCP <-> Strava OAuth ---
auth = OAuthProxy(
    # Strava OAuth endpoints (from Strava docs)
    upstream_authorization_endpoint="https://www.strava.com/oauth/authorize",
    upstream_token_endpoint="https://www.strava.com/oauth/token",  # noqa
    # Your Strava app credentials (env recommended)
    upstream_client_id=STRAVA_CLIENT_ID,
    upstream_client_secret=STRAVA_CLIENT_SECRET,
    # Validate tokens with our custom verifier
    token_verifier=StravaTokenVerifier(required_scopes=["activity:read_all"]),
    # Public base URL of this FastMCP server (e.g., your ngrok https URL)
    base_url=os.getenv("BASE_URL", "http://localhost:8000"),
    # Strava expects client_id/client_secret in POST body for token exchange
    token_endpoint_auth_method="client_secret_post",  # noqa
)

mcp = FastMCP(name="Strava MCP", auth=auth)


@mcp.tool
def get_last_run_statistics() -> str:
    """
    Return stats from the most recent Strava activity with type == 'Run'.
    """
    text_result: str = ""

    token = get_access_token()
    if token is None or not getattr(token, "token", ""):
        raise RuntimeError("Not authenticated. Complete OAuth first.")

    # Pull recent activities and find the first Run
    # (Strava: GET /athlete/activities, requires activity:read)
    activities = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        params={"per_page": 10},
        headers={"Authorization": f"Bearer {token.token}"},
        timeout=15,
    )
    if activities.status_code != 200:
        raise RuntimeError(
            f"Strava API error: {activities.status_code} {activities.text}"
        )

    for activity in activities.json() or []:
        if activity.get("type") != "Run":
            continue

        avg_speed = activity.get("average_speed") or 0
        average_pace_min_per_km = (1000.0 / avg_speed / 60.0) if avg_speed else None

        activity_data = {
            "name": str(activity.get("name")),
            "distance": str(activity.get("distance")),  # meters
            "type": str(activity.get("type")),
            "start_date_local": str(activity.get("start_date_local")),
            "moving_time": str(activity.get("moving_time")),  # seconds
            "average_speed (m/s)": str(activity.get("average_speed")),
            "max_speed (m/s)": str(activity.get("max_speed")),
            "max_heartrate": str(activity.get("max_heartrate")),
            "average_heartrate": str(activity.get("average_heartrate")),
            "total_elevation_gain": str(activity.get("total_elevation_gain")),
            "average_pace (min/km)": str(average_pace_min_per_km)
            if average_pace_min_per_km is not None
            else "",
        }
        text_result += json.dumps(activity_data) + "\n"
        break  # only the most recent Run

    return text_result
