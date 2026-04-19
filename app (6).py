import os
import time
from datetime import date
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "OPTIONS"])

BALLDONTLIE_BASE = "https://api.balldontlie.io/v1"
API_KEY = os.environ.get("BALLDONTLIE_API_KEY", "621e639d-76ee-41b9-8724-c96392e46a2e")

def bdl_get(path, params=None):
    if params is None:
        params = {}
    headers = {"Authorization": API_KEY}
    for attempt in range(3):
        try:
            r = requests.get(f"{BALLDONTLIE_BASE}{path}", headers=headers, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "key_prefix": API_KEY[:8] if API_KEY else "none"})


@app.route("/api/teams")
def all_teams():
    data = bdl_get("/teams", {"per_page": 30})
    return jsonify(data.get("data", []))


@app.route("/api/scoreboard")
def scoreboard():
    try:
        today = date.today().strftime("%Y-%m-%d")
        data = bdl_get("/games", {"dates[]": today, "per_page": 15})
        return jsonify(data.get("data", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/roster")
def team_roster(team_id):
    try:
        # Fetch players for this team, all pages
        all_players = []
        cursor = None
        while True:
            params = {"team_ids[]": team_id, "per_page": 100}
            if cursor:
                params["cursor"] = cursor
            data = bdl_get("/players", params)
            all_players.extend(data.get("data", []))
            next_cursor = data.get("meta", {}).get("next_cursor")
            if not next_cursor:
                break
            cursor = next_cursor

        # Filter to players who have stats in the 2024 season
        # Check season averages for a batch of player IDs
        player_ids = [str(p["id"]) for p in all_players]
        if not player_ids:
            return jsonify([])

        # Get season averages to filter active players
        avg_data = bdl_get("/season_averages", {
            "season": 2025,
            "player_ids[]": player_ids,
        })
        active_ids = {str(a["player_id"]) for a in avg_data.get("data", [])}

        # Return only players with 2024 season averages
        active_players = [p for p in all_players if str(p["id"]) in active_ids]

        # If filtering removed everyone, return all (fallback)
        return jsonify(active_players if active_players else all_players)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/gamelog")
def player_gamelog(player_id):
    try:
        last_n = request.args.get("last_n", 15, type=int)
        data = bdl_get("/stats", {
            "player_ids[]": player_id,
            "seasons[]": 2025,
            "per_page": last_n,
        })
        return jsonify(data.get("data", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/averages")
def player_averages(player_id):
    try:
        data = bdl_get("/season_averages", {
            "season": 2025,
            "player_ids[]": player_id,
        })
        results = data.get("data", [])
        return jsonify(results[0] if results else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/players/search")
def search_players():
    try:
        q = request.args.get("q", "")
        if len(q) < 2:
            return jsonify([])
        data = bdl_get("/players", {"search": q, "per_page": 20})
        return jsonify(data.get("data", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
