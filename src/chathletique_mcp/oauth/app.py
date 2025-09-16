import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_key_123")  # pas important ici


STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = "https://gorilla-major-literally.ngrok-free.app/callback"


@app.route("/")
def home():
    """
    Redirect to Strava for authentication
    """

    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={STRAVA_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=activity:read_all"
        f"&approval_prompt=force"
    )
    print("Redirecting to Strava:", auth_url)  # Debug
    return redirect(auth_url)


@app.route("/callback")
def callback():
    """
    Callback from Strava after authentication => on récupère le code d'autorisation à partir de l'url de callback
    """
    print("Callback received! URL:", request.url)  # Debug
    print("Args:", request.args)  # Debug: Show all query parameters

    code = request.args.get("code")
    if not code:
        return "Error: No 'code' received. Check the Strava app settings.", 400

    print("Authorization code:", code)  # Debug: Print the code

    # Exchange code for token
    try:
        response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": STRAVA_CLIENT_ID,
                "client_secret": STRAVA_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        response.raise_for_status()
        token_data = response.json()
        print("Token data:", token_data)  # Debug: Print token data

        # Test the token by fetching athlete data
        athlete_response = requests.get(
            "https://www.strava.com/api/v3/athlete",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
            timeout=10,
        )
        athlete_data = athlete_response.json()
        return jsonify(
            {"status": "success", "token": token_data, "athlete": athlete_data}
        )
    except Exception as e:
        return f"Error: {e!s}", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)  # noqa
