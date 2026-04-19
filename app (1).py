import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Simplest CORS possible to rule out header issues
CORS(app)

# Use your key or the environment variable
API_KEY = os.environ.get("BALLDONTLIE_API_KEY", "621e639d-76ee-41b9-8724-c96392e46a2e")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "message": "App is running"})

@app.route("/api/scoreboard")
def scoreboard():
    url = "https://api.balldontlie.io/v1/games"
    headers = {"Authorization": API_KEY}
    try:
        # per_page=5 to keep it small and fast
        r = requests.get(url, headers=headers, params={"per_page": 5}, timeout=5)
        r.raise_for_status()
        return jsonify(r.json().get("data", []))
    except Exception as e:
        # EMERGENCY FALLBACK: Return fake data so the app doesn't show 500/503
        print(f"API Failed: {e}")
        return jsonify([{"id": 0, "home_team": {"full_name": "API Error"}, "visitor_team": {"full_name": "Check Logs"}}])

if __name__ == "__main__":
    # CRITICAL: Railway must have the port set this way
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)