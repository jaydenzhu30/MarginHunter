import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CURRENT_SEASON = "2024-25"


def safe_call(fn, *args, **kwargs):
    for attempt in range(3):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2)


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
        from nba_api.stats.endpoints import scoreboardv2
        sb = safe_call(scoreboardv2.ScoreboardV2)
        return jsonify({
            "games": sb.game_header.get_dict(),
            "line_score": sb.line_score.get_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/roster")
def team_roster(team_id):
    try:
        from nba_api.stats.endpoints import commonteamroster
        roster = safe_call(commonteamroster.CommonTeamRoster,
                           team_id=team_id, season=CURRENT_SEASON)
        return jsonify(roster.common_team_roster.get_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/gamelog")
def player_gamelog(player_id):
    try:
        from nba_api.stats.endpoints import playergamelog
        last_n = request.args.get("last_n", 15, type=int)
        logs = safe_call(
            playergamelog.PlayerGameLog,
            player_id=player_id,
            season=CURRENT_SEASON,
            season_type_all_star="Regular Season",
        )
        data = logs.player_game_log.get_dict()
        data["rowSet"] = data["rowSet"][:last_n]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/dvp")
def team_dvp(team_id):
    try:
        from nba_api.stats.endpoints import leaguedashptteamdefend
        positions = ["Guard", "Forward", "Center"]
        result = {}
        for pos in positions:
            dvp = safe_call(
                leaguedashptteamdefend.LeagueDashPtTeamDefend,
                season=CURRENT_SEASON,
                defense_category=pos,
            )
            data = dvp.league_dash_pt_team_defend.get_dict()
            headers = data["headers"]
            team_id_idx = headers.index("TEAM_ID")
            row = next((r for r in data["rowSet"] if r[team_id_idx] == team_id), None)
            result[pos.lower()] = dict(zip(headers, row)) if row else {}
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/team/<int:team_id>/shotdefence")
def team_shot_defence(team_id):
    try:
        from nba_api.stats.endpoints import leaguedashteamstats
        shots = safe_call(
            leaguedashteamstats.LeagueDashTeamStats,
            season=CURRENT_SEASON,
            measure_type_detailed_defense="Opponent",
        )
        data = shots.league_dash_team_stats.get_dict()
        headers = data["headers"]
        team_id_idx = headers.index("TEAM_ID")
        row = next((r for r in data["rowSet"] if r[team_id_idx] == team_id), None)
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
