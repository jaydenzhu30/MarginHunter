import os
import time
from datetime import date
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Keep CORS open to allow your frontend to talk to this backend
CORS(app, resources={r"/api/*": {"origins": "*"}})

BALLDONTLIE_BASE = "https://api.balldontlie.io/v1"
# Priority: Environment Variable -> Hardcoded Key
API_KEY = os.environ.get("BALLDONTLIE_API_KEY", "621e639d-76ee-41b9-8724-c96392e46a2e")

def bdl_get(path, params=None):
    if params is None:
        params = {}
    headers = {"Authorization": API_KEY}
    
    # Increased retry logic to handle "Service Unavailable" blips
    for attempt in range(3):
        try:
            r = requests.get(
                f"{BALLDONTLIE_BASE}{path}",
                headers=headers,
                params=params,
                timeout=10 # Slightly shorter timeout for better responsiveness
            )
            # If we hit a rate limit or service error, don't crash, just retry
            if r.status_code in [429, 503]:
                time.sleep(2)
                continue
                
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == 2:
                print(f"BDL API Error: {e}")
                return None
            time.sleep(1)
    return None


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "key_prefix": API_KEY[:8] if API_KEY else "none"})


@app.route("/api/teams")
def all_teams():
    data = bdl_get("/teams", {"per_page": 30})
    if data:
        return jsonify(data.get("data", []))
    return jsonify([])


@app.route("/api/scoreboard")
def scoreboard():
    try:
        today = date.today().strftime("%Y-%m-%d")
        # BallDontLie uses 'dates[]' (plural) for the query parameter
        data = bdl_get("/games", {"dates[]": today, "per_page": 15})
        if data:
            return jsonify(data.get("data", []))
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/roster")
def team_roster(team_id):
    # Try active players first
    data = bdl_get("/players/active", {"team_ids[]": team_id, "per_page": 50})
    if not data:
        # Fallback to general players
        data = bdl_get("/players", {"team_ids[]": team_id, "per_page": 50})
    
    return jsonify(data.get("data", []) if data else [])


@app.route("/api/player/<int:player_id>/gamelog")
def player_gamelog(player_id):
    last_n = request.args.get("last_n", 15, type=int)
    data = bdl_get("/stats", {
        "player_ids[]": player_id,
        "seasons[]": 2024, # Ensure this matches current season
        "per_page": last_n,
    })
    return jsonify(data.get("data", []) if data else [])


@app.route("/api/player/<int:player_id>/averages")
def player_averages(player_id):
    data = bdl_get("/season_averages", {
        "season": 2024,
        "player_ids[]": player_id,
    })
    if data and data.get("data"):
        return jsonify(data["data"][0])
    return jsonify({})


@app.route("/api/players/search")
def search_players():
    q = request.args.get("q", "")
    if len(q) < 2:
        return jsonify([])
    data = bdl_get("/players", {"search": q, "per_page": 20})
    return jsonify(data.get("data", []) if data else [])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)