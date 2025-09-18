"""MCP utilities for Strava coaching server."""

import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastmcp import FastMCP

mcp = FastMCP("Chathletique MCP Server", port=3000, stateless_http=True, debug=True)

load_dotenv()


# Strava OAuth config
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv(
    "REDIRECT_URI", "https://gorilla-major-literally.ngrok-free.app/callback"
)

# Store user tokens in memory (for demo; use a DB in production)
user_tokens = {}

auth = FastAPI()


@auth.get("/auth/strava")
async def auth_strava():
    """Redirect user to Strava for OAuth authorization."""
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={STRAVA_CLIENT_ID}&"
        f"response_type=code&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope=read,activity:read_all"
    )
    return {"url": auth_url}


@auth.get("/auth/callback")
async def callback(request: Request):
    """Handle Strava OAuth callback and store user token."""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": STRAVA_CLIENT_ID,
                "client_secret": STRAVA_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch access token")

        access_token = response.json()["access_token"]

        # TO MODIFY WITH ACTUAL USER DB IN PROD
        user_tokens[access_token] = True
        return {"status": "success", "access_token": access_token}
