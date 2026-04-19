import os
import time
from datetime import date
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "OPTIONS"])

BALLDONTLIE_BASE = "https://api.balldontlie.io/v1"
API_KEY = os.environ.get("BALLDONTLIE_API_KEY", "")

def bdl_get(path, params={}):
    headers = {"Authorization": API_KEY} if API_KEY else {}
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
    return jsonify({"status": "ok"})


@app.route("/api/teams")
def all_teams():
    data = bdl_get("/teams", {"per_page": 30})
    return jsonify(data.get("data", []))


@app.route("/api/scoreboard")
def scoreboard():
    try:
        today = date.today().strftime("%Y-%m-%d")
        data = bdl_get("/games", {
            "dates[]": today,
            "per_page": 15,
        })
        return jsonify(data.get("data", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/roster")
def team_roster(team_id):
    try:
        data = bdl_get("/players", {
            "team_ids[]": team_id,
            "per_page": 30,
        })
        return jsonify(data.get("data", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/gamelog")
def player_gamelog(player_id):
    try:
        last_n = request.args.get("last_n", 15, type=int)
        current_season = 2024
        data = bdl_get("/stats", {
            "player_ids[]": player_id,
            "seasons[]": current_season,
            "per_page": last_n,
        })
        return jsonify(data.get("data", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/seasonaverages")
def team_season_averages(team_id):
    try:
        # Get all players on team then their season averages
        roster = bdl_get("/players", {"team_ids[]": team_id, "per_page": 30})
        player_ids = [str(p["id"]) for p in roster.get("data", [])]
        if not player_ids:
            return jsonify([])
        params = {"season": 2024}
        for pid in player_ids:
            params.setdefault("player_ids[]", []).append(pid)
        data = bdl_get("/season_averages", {"season": 2024, "player_ids[]": player_ids})
        return jsonify(data.get("data", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/averages")
def player_averages(player_id):
    try:
        data = bdl_get("/season_averages", {
            "season": 2024,
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
