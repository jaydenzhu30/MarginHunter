import os
import time
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "OPTIONS"])

CURRENT_SEASON = "2024-25"

NBA_HEADERS = {
    "Host": "stats.nba.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/",
    "Connection": "keep-alive",
}


def nba_get(url, params={}):
    """Direct HTTP call to stats.nba.com with browser headers."""
    for attempt in range(3):
        try:
            r = requests.get(url, headers=NBA_HEADERS, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2)


def parse_response(data):
    """Convert NBA API resultSets format to {headers, rowSet}."""
    rs = data.get("resultSets", data.get("resultSet", []))
    if isinstance(rs, list) and rs:
        return {"headers": rs[0]["headers"], "rowSet": rs[0]["rowSet"]}
    return {"headers": [], "rowSet": []}


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "season": CURRENT_SEASON})


@app.route("/api/teams")
def all_teams():
    from nba_api.stats.static import teams
    return jsonify(teams.get_teams())


@app.route("/api/scoreboard")
def scoreboard():
    try:
        data = nba_get("https://stats.nba.com/stats/scoreboardv2", {
            "DayOffset": "0",
            "LeagueID": "00",
            "gameDate": "",
        })
        rs = data.get("resultSets", [])
        game_header = next((x for x in rs if x["name"] == "GameHeader"), {"headers": [], "rowSet": []})
        line_score = next((x for x in rs if x["name"] == "LineScore"), {"headers": [], "rowSet": []})
        return jsonify({"games": game_header, "line_score": line_score})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/roster")
def team_roster(team_id):
    try:
        data = nba_get("https://stats.nba.com/stats/commonteamroster", {
            "TeamID": team_id,
            "Season": CURRENT_SEASON,
        })
        rs = data.get("resultSets", [])
        roster = next((x for x in rs if x["name"] == "CommonTeamRoster"), {"headers": [], "rowSet": []})
        return jsonify(roster)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/gamelog")
def player_gamelog(player_id):
    try:
        last_n = request.args.get("last_n", 15, type=int)
        data = nba_get("https://stats.nba.com/stats/playergamelog", {
            "PlayerID": player_id,
            "Season": CURRENT_SEASON,
            "SeasonType": "Regular Season",
        })
        rs = data.get("resultSets", [])
        logs = next((x for x in rs if x["name"] == "PlayerGameLog"), {"headers": [], "rowSet": []})
        logs["rowSet"] = logs["rowSet"][:last_n]
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/dvp")
def team_dvp(team_id):
    try:
        result = {}
        for pos in ["Guard", "Forward", "Center"]:
            data = nba_get("https://stats.nba.com/stats/leaguedashptteamdefend", {
                "Season": CURRENT_SEASON,
                "SeasonType": "Regular Season",
                "DefenseCategory": pos,
                "PerMode": "PerGame",
                "LeagueID": "00",
            })
            rs = data.get("resultSets", [])
            table = next((x for x in rs), {"headers": [], "rowSet": []})
            headers = table["headers"]
            team_id_idx = headers.index("TEAM_ID") if "TEAM_ID" in headers else -1
            row = next((r for r in table["rowSet"] if team_id_idx >= 0 and r[team_id_idx] == team_id), None)
            result[pos.lower()] = dict(zip(headers, row)) if row else {}
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/shotdefence")
def team_shot_defence(team_id):
    try:
        data = nba_get("https://stats.nba.com/stats/leaguedashteamstats", {
            "Season": CURRENT_SEASON,
            "SeasonType": "Regular Season",
            "MeasureType": "Opponent",
            "PerMode": "PerGame",
            "LeagueID": "00",
        })
        rs = data.get("resultSets", [])
        table = next((x for x in rs), {"headers": [], "rowSet": []})
        headers = table["headers"]
        team_id_idx = headers.index("TEAM_ID") if "TEAM_ID" in headers else -1
        row = next((r for r in table["rowSet"] if team_id_idx >= 0 and r[team_id_idx] == team_id), None)
        return jsonify(dict(zip(headers, row)) if row else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/players/search")
def search_players():
    from nba_api.stats.static import players
    q = request.args.get("q", "").lower()
    if len(q) < 2:
        return jsonify([])
    results = [p for p in players.get_players() if q in p["full_name"].lower()][:20]
    return jsonify(results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
