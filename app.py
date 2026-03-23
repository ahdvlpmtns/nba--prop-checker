import os
import re
import time
import math
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple

from groq import Groq
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import (
    playergamelog, scoreboardv2, commonteamroster,
    leaguedashteamstats, commonplayerinfo,
)

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="PropLens — NBA Prop Checker",
    page_icon="🏀",
    layout="wide",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #080c14;
    color: #e2e8f0;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }

.proplens-header { display: flex; align-items: center; gap: 14px; margin-bottom: 0.25rem; }
.proplens-logo {
    font-size: 2.6rem; font-weight: 800; letter-spacing: -2px;
    background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fdba74 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1;
}
.proplens-sub {
    font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #64748b;
    letter-spacing: 0.15em; text-transform: uppercase; margin-top: 2px;
}

.stat-card {
    background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
    border: 1px solid #1e293b; border-radius: 14px;
    padding: 1.1rem 1.3rem; margin-bottom: 0.75rem;
}
.stat-label {
    font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #475569;
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 4px;
}
.stat-value { font-size: 1.8rem; font-weight: 800; color: #f1f5f9; letter-spacing: -1px; line-height: 1.1; }
.stat-value.orange { color: #f97316; }
.stat-value.green  { color: #22c55e; }
.stat-value.red    { color: #ef4444; }
.stat-value.yellow { color: #eab308; }

.defense-card {
    background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
    border: 1px solid #1e293b; border-radius: 14px;
    padding: 1rem 1.3rem; margin-bottom: 0.75rem;
    display: flex; align-items: center; justify-content: space-between;
}
.defense-badge {
    font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 500;
    padding: 4px 12px; border-radius: 999px; letter-spacing: 0.05em;
}
.defense-badge.good    { background: #052e16; color: #22c55e; border: 1px solid #166534; }
.defense-badge.neutral { background: #0f172a; color: #94a3b8; border: 1px solid #1e293b; }
.defense-badge.bad     { background: #1c0505; color: #ef4444; border: 1px solid #991b1b; }

.verdict-banner {
    border-radius: 16px; padding: 1.5rem 2rem; margin: 1.5rem 0;
    border: 1px solid #1e293b; display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 1rem;
}
.verdict-banner.green  { background: linear-gradient(135deg, #052e16 0%, #0f2a1a 100%); border-color: #166534; }
.verdict-banner.yellow { background: linear-gradient(135deg, #1c1a05 0%, #2a260f 100%); border-color: #854d0e; }
.verdict-banner.orange { background: linear-gradient(135deg, #1c1005 0%, #2a1a0f 100%); border-color: #9a3412; }
.verdict-banner.red    { background: linear-gradient(135deg, #1c0505 0%, #2a0f0f 100%); border-color: #991b1b; }
.verdict-banner.gray   { background: linear-gradient(135deg, #0f172a 0%, #111827 100%); border-color: #1e293b; }

.verdict-label { font-size: 0.65rem; font-family: 'DM Mono', monospace; letter-spacing: 0.15em; text-transform: uppercase; color: #64748b; margin-bottom: 4px; }
.verdict-tier { font-size: 2rem; font-weight: 800; letter-spacing: -1px; }
.verdict-tier.green  { color: #22c55e; }
.verdict-tier.yellow { color: #eab308; }
.verdict-tier.orange { color: #f97316; }
.verdict-tier.red    { color: #ef4444; }
.verdict-tier.gray   { color: #64748b; }

.section-header {
    font-size: 0.65rem; font-family: 'DM Mono', monospace; letter-spacing: 0.2em;
    text-transform: uppercase; color: #f97316; margin: 1.75rem 0 0.75rem 0;
    padding-bottom: 6px; border-bottom: 1px solid #1e293b;
}

.ai-box {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1525 100%);
    border: 1px solid #1e3a5f; border-radius: 14px; padding: 1.5rem;
    margin-top: 1rem; font-size: 0.95rem; line-height: 1.75; color: #cbd5e1;
}

.model-note {
    background: #0f172a; border: 1px solid #1e293b; border-radius: 10px;
    padding: 0.75rem 1rem; margin-top: 0.5rem;
    font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #475569; line-height: 1.6;
}

.flag-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 0.5rem; }
.flag-pill { font-family: 'DM Mono', monospace; font-size: 0.7rem; padding: 4px 10px; border-radius: 999px; letter-spacing: 0.05em; }
.flag-pill.up     { background: #052e16; color: #22c55e; border: 1px solid #166534; }
.flag-pill.down   { background: #1c0505; color: #ef4444; border: 1px solid #991b1b; }
.flag-pill.flat   { background: #0f172a; color: #94a3b8; border: 1px solid #1e293b; }
.flag-pill.nodata { background: #0f172a; color: #475569; border: 1px solid #1e293b; }

.stButton > button {
    background: linear-gradient(135deg, #ea580c, #f97316) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    letter-spacing: 0.03em !important; padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
hr { border-color: #1e293b !important; }
section[data-testid="stSidebar"] { background: #0a0f1e !important; border-right: 1px solid #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────

if "logs" not in st.session_state:
    st.session_state.logs = None
if "ai_analysis" not in st.session_state:
    st.session_state.ai_analysis = None
if "ai_error" not in st.session_state:
    st.session_state.ai_error = None
if "defense_data" not in st.session_state:
    st.session_state.defense_data = None
if "tracker" not in st.session_state:
    st.session_state.tracker = []  # list of prop result dicts

# ─────────────────────────────────────────────
# NBA API helpers
# ─────────────────────────────────────────────

def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def find_player_id(player_name: str) -> Tuple[Optional[int], Optional[str]]:
    name = normalize_name(player_name)
    all_players = players.get_players()
    for p in all_players:
        if normalize_name(p["full_name"]) == name:
            return p["id"], p["full_name"]
    candidates = [p for p in all_players if name in normalize_name(p["full_name"])]
    if len(candidates) == 1:
        return candidates[0]["id"], candidates[0]["full_name"]
    return None, None

def search_candidates(player_name: str):
    name = normalize_name(player_name)
    all_players = players.get_players()
    return [p for p in all_players if name in normalize_name(p["full_name"])]

@st.cache_data(ttl=600)
def get_last_n_games(player_id: int, season: str, n: int = 10) -> pd.DataFrame:
    df = playergamelog.PlayerGameLog(
        player_id=player_id, season=season, timeout=15,
    ).get_data_frames()[0]
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df = df.sort_values("GAME_DATE", ascending=False).head(n).copy()
    for c in ["MATCHUP", "MIN", "PTS", "FGA", "FTA", "FG3A"]:
        if c not in df.columns:
            df[c] = None
    return df[["GAME_DATE", "MATCHUP", "MIN", "PTS", "FGA", "FTA", "FG3A"]]

@st.cache_data(ttl=3600)
def get_team_id(abbr: str) -> Optional[int]:
    for t in teams.get_teams():
        if t["abbreviation"] == abbr:
            return t["id"]
    return None

@st.cache_data(ttl=3600)
def get_live_roster(team_abbr: str, season: str) -> list:
    team_id = get_team_id(team_abbr)
    if not team_id:
        return []
    try:
        df = commonteamroster.CommonTeamRoster(
            team_id=team_id, season=season, timeout=20,
        ).get_data_frames()[0]
        return df["PLAYER"].tolist()
    except Exception:
        return []

@st.cache_data(ttl=600)
def get_player_team(player_id: int) -> Optional[str]:
    """Get the current team abbreviation for a player."""
    try:
        info = commonplayerinfo.CommonPlayerInfo(
            player_id=player_id, timeout=15,
        ).get_data_frames()[0]
        return info["TEAM_ABBREVIATION"].iloc[0] if not info.empty else None
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_opponent_pts_allowed(opp_abbr: str, season: str) -> Optional[float]:
    """
    Calculate points allowed per game for a team using their roster player logs.
    Each player game log has PTS (player pts) and PLUS_MINUS.
    Team pts scored = sum of all player pts... but easier:
    
    Pull one player from the opponent team. Their game log has:
    - PTS: player points (not useful directly)
    - PLUS_MINUS: team_pts_scored - opp_pts_scored for that game
    
    We also need team pts scored per game. The teamgamelog endpoint
    columns vary — so instead we use a player game log which has
    MIN, PTS, PLUS_MINUS reliably. We grab a high-minute player
    and use their team-level PLUS_MINUS alongside a known team PTS
    by pulling teamgamelog and inspecting all available columns.
    """
    from nba_api.stats.endpoints import teamgamelog

    try:
        team_id = get_team_id(opp_abbr)
        if not team_id:
            return None

        tgl = teamgamelog.TeamGameLog(
            team_id=team_id,
            season=season,
            season_type_all_star="Regular Season",
            timeout=20,
        ).get_data_frames()[0]

        if tgl.empty:
            return None

        # Log available columns to debug
        cols = tgl.columns.tolist()

        # Try direct columns first
        if "OPP_PTS" in cols:
            return float(pd.to_numeric(tgl["OPP_PTS"], errors="coerce").dropna().mean())

        # PTS - PLUS_MINUS = opponent pts scored against this team
        if "PTS" in cols and "PLUS_MINUS" in cols:
            pts = pd.to_numeric(tgl["PTS"], errors="coerce")
            pm  = pd.to_numeric(tgl["PLUS_MINUS"], errors="coerce")
            opp_pts_series = pts - pm
            return float(opp_pts_series.dropna().mean())

        # Try W_PCTG, PTS_QTR columns etc — return None if nothing works
        return None

    except Exception:
        return None


@st.cache_data(ttl=3600)
def get_opponent_pts_allowed_from_player_logs(opp_abbr: str, season: str) -> Optional[float]:
    """
    Estimate pts allowed by opponent using PLUS_MINUS from player game logs.
    Tries all roster players until it finds one with a valid game log.
    PLUS_MINUS = team_pts - opp_pts per game (team level stat in player logs).
    pts_allowed ≈ league_avg - avg_plus_minus
    """
    try:
        roster = get_live_roster(opp_abbr, season)
        if not roster:
            return None

        all_plus_minus = []

        # Try ALL roster players — keep going until we have enough data
        for player_name in roster:
            try:
                pid, _ = find_player_id(player_name)
                if not pid:
                    continue
                log = playergamelog.PlayerGameLog(
                    player_id=pid,
                    season=season,
                    timeout=15,
                ).get_data_frames()[0]
                if log.empty or "PLUS_MINUS" not in log.columns:
                    continue
                pm = pd.to_numeric(log["PLUS_MINUS"], errors="coerce").dropna()
                if len(pm) < 5:
                    continue
                all_plus_minus.extend(pm.tolist())
                # Once we have 20+ game entries, that's enough
                if len(all_plus_minus) >= 20:
                    break
            except Exception:
                continue

        if not all_plus_minus:
            return None

        avg_pm = sum(all_plus_minus) / len(all_plus_minus)
        # pts_allowed = league_avg - avg_PLUS_MINUS
        pts_allowed = 114.5 - avg_pm
        return round(pts_allowed, 1)

    except Exception:
        return None


def get_league_avg_pts_allowed(season: str) -> float:
    """
    League average points allowed — hardcoded as a reasonable baseline
    since the league-wide endpoint is unreliable on Streamlit Cloud.
    Updated per season. 2024-25 and 2025-26 avg is ~114-115 pts/game.
    """
    return 114.5

@st.cache_data(ttl=300)
def get_next_opponent(player_team: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Look up the next scheduled game for a team using scoreboardv2.
    Checks today first, then tomorrow (day_offset=1) as a fallback.
    Returns (opponent_abbreviation, game_date_string).
    """
    if not player_team:
        return None, None

    from datetime import timedelta
    base_date = datetime.today()

    for day_offset in [0, 1, 2]:
        try:
            check_date = base_date + timedelta(days=day_offset)
            check_date_str = check_date.strftime("%m/%d/%Y")
            sb = scoreboardv2.ScoreboardV2(
                game_date=check_date_str,
                league_id="00",
                day_offset=0,
                timeout=20,
            )
            games = sb.get_data_frames()[0]
            if games.empty:
                continue

            row = games[
                (games["HOME_TEAM_ABBREVIATION"] == player_team) |
                (games["VISITOR_TEAM_ABBREVIATION"] == player_team)
            ]
            if row.empty:
                continue

            row = row.iloc[0]
            home = row["HOME_TEAM_ABBREVIATION"]
            away = row["VISITOR_TEAM_ABBREVIATION"]

            # Try multiple possible date column names
            game_date = None
            for col in ["GAME_DATE_EST", "GAME_DATE", "GAME_STATUS_TEXT"]:
                if col in row.index and row[col]:
                    val = str(row[col])[:10]
                    if val and val != "nan":
                        game_date = check_date.strftime("%b %d, %Y")
                        break
            if not game_date:
                game_date = check_date.strftime("%b %d, %Y")

            if player_team == home:
                return away, game_date
            else:
                return home, game_date
        except Exception:
            continue

    return None, None


def get_opponent_from_logs(logs: pd.DataFrame, player_team: Optional[str]) -> Optional[str]:
    """
    Fallback: extract most recent opponent from game log if schedule lookup fails.
    MATCHUP format is either 'TEM vs. OPP' or 'TEM @ OPP'.
    """
    if logs is None or logs.empty:
        return None
    latest = logs.iloc[0]["MATCHUP"]
    if not latest:
        return None
    if " vs. " in latest:
        parts = latest.split(" vs. ")
        return parts[1].strip() if player_team and parts[0].strip() == player_team else parts[0].strip()
    if " @ " in latest:
        parts = latest.split(" @ ")
        return parts[1].strip()
    return None

def classify_matchup(opp_abbr: Optional[str], season: str) -> Tuple[str, Optional[float], str]:
    """
    Estimate pts allowed by opponent using PLUS_MINUS from their player game logs.
    pts_allowed = 114.5 - avg_PLUS_MINUS (inlined to avoid caching issues).
    """
    if not opp_abbr:
        return "Neutral", None, "N/A"

    avg_pts = 114.5
    avg_str = f"{avg_pts:.1f}"
    opp_pts = None

    # Try all roster players until we accumulate enough PLUS_MINUS data
    try:
        roster = get_live_roster(opp_abbr, season)
        all_pm = []
        for player_name in roster:
            try:
                pid, _ = find_player_id(player_name)
                if not pid:
                    continue
                log = playergamelog.PlayerGameLog(
                    player_id=pid, season=season, timeout=15,
                ).get_data_frames()[0]
                if log.empty or "PLUS_MINUS" not in log.columns:
                    continue
                pm = pd.to_numeric(log["PLUS_MINUS"], errors="coerce").dropna()
                if len(pm) < 5:
                    continue
                all_pm.extend(pm.tolist())
                if len(all_pm) >= 20:
                    break
            except Exception:
                continue
        if all_pm:
            avg_pm = sum(all_pm) / len(all_pm)
            opp_pts = round(avg_pts - avg_pm, 1)
    except Exception:
        pass

    if opp_pts is None:
        return "Neutral", None, avg_str

    diff = opp_pts - avg_pts
    if diff >= 1.5:
        return "Good", opp_pts, avg_str
    if diff <= -1.5:
        return "Bad", opp_pts, avg_str
    return "Neutral", opp_pts, avg_str

def fetch_with_retries(fn, retries=3, wait=2):
    last_err = None
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            time.sleep(wait * (i + 1))
    raise last_err

# ─────────────────────────────────────────────
# Prediction engine
# ─────────────────────────────────────────────

def hit_rate(df: pd.DataFrame, line: float, side: str) -> float:
    pts = pd.to_numeric(df["PTS"], errors="coerce").dropna()
    if len(pts) == 0:
        return 0.0
    hits = (pts >= line).sum() if side == "Over" else (pts <= line).sum()
    return float(hits / len(pts))

def weighted_hit_rate(df: pd.DataFrame, line: float, side: str) -> float:
    pts = pd.to_numeric(df["PTS"], errors="coerce").dropna().reset_index(drop=True)
    n = len(pts)
    if n == 0:
        return 0.0
    weights = [n - i for i in range(n)]
    total_weight = sum(weights)
    if side == "Over":
        weighted_hits = sum(w for p, w in zip(pts, weights) if p >= line)
    else:
        weighted_hits = sum(w for p, w in zip(pts, weights) if p <= line)
    return weighted_hits / total_weight

def consistency_score(df: pd.DataFrame, line: float) -> float:
    pts = pd.to_numeric(df["PTS"], errors="coerce").dropna()
    if len(pts) == 0:
        return 0.5
    within_3 = (abs(pts - line) <= 3).sum()
    return float(within_3 / len(pts))

def home_away_split(df: pd.DataFrame, line: float, side: str, player_team: Optional[str]) -> dict:
    """
    Split hit rate into home vs away games using MATCHUP column.
    MATCHUP format: 'TEM vs. OPP' = home, 'TEM @ OPP' = away.
    Returns dict with home_rate, away_rate, home_games, away_games, home_avg, away_avg.
    """
    result = {
        "home_rate": None, "away_rate": None,
        "home_games": 0, "away_games": 0,
        "home_avg": None, "away_avg": None,
    }
    if df is None or df.empty or "MATCHUP" not in df.columns:
        return result

    df = df.copy()
    df["PTS_NUM"] = pd.to_numeric(df["PTS"], errors="coerce")

    def is_home(matchup):
        if not matchup:
            return None
        return "vs." in str(matchup)

    df["IS_HOME"] = df["MATCHUP"].apply(is_home)

    home_df = df[df["IS_HOME"] == True].dropna(subset=["PTS_NUM"])
    away_df = df[df["IS_HOME"] == False].dropna(subset=["PTS_NUM"])

    if len(home_df) >= 2:
        home_hits = (home_df["PTS_NUM"] >= line).sum() if side == "Over" else (home_df["PTS_NUM"] <= line).sum()
        result["home_rate"]  = round(float(home_hits / len(home_df)), 2)
        result["home_games"] = len(home_df)
        result["home_avg"]   = round(float(home_df["PTS_NUM"].mean()), 1)

    if len(away_df) >= 2:
        away_hits = (away_df["PTS_NUM"] >= line).sum() if side == "Over" else (away_df["PTS_NUM"] <= line).sum()
        result["away_rate"]  = round(float(away_hits / len(away_df)), 2)
        result["away_games"] = len(away_df)
        result["away_avg"]   = round(float(away_df["PTS_NUM"].mean()), 1)

    return result


def trend_flag(series: pd.Series, n: int) -> str:
    s = pd.to_numeric(series, errors="coerce").dropna()
    lookback = max(2, n // 3)
    if len(s) < lookback + 2:
        return "nodata"
    recent = s.iloc[:lookback].mean()
    prior  = s.iloc[lookback:].mean()
    diff   = recent - prior
    threshold = 3.0 if n <= 5 else 2.0
    if diff >= threshold:
        return "up"
    if diff <= -threshold:
        return "down"
    return "flat"

def suggest_bucket(value: float, strong_cut: float, risk_cut: float) -> str:
    if value >= strong_cut:
        return "Strong"
    if value < risk_cut:
        return "Risk"
    return "Okay"

def apply_adjustments(weighted: float, context: dict) -> float:
    """
    Multiplicative adjustments on the margin from 50%.
    Respects bounded [0,1] nature of probabilities.
    """
    multipliers = {
        "minutes":  {"Strong": 1.08, "Okay": 1.00, "Risk": 0.88},
        "role":     {"Strong": 1.06, "Okay": 1.00, "Risk": 0.92},
        "shots":    {"High":   1.05, "Medium": 1.00, "Low": 0.90},
        "matchup":  {"Good":   1.08, "Neutral": 1.00, "Bad": 0.91},
        "script":   {"Competitive": 1.03, "Neutral": 1.00, "Blowout risk": 0.93},
    }
    margin = weighted - 0.5
    for key, val in context.items():
        margin *= multipliers[key][val]
    return max(0.0, min(1.0, 0.5 + margin))

def get_confidence_tier(adjusted: float, line_diff: float, consistency: float) -> str:
    low_consistency = consistency < 0.35
    if adjusted >= 0.64 and line_diff >= 1.5:
        tier = "Strong Over"
    elif adjusted >= 0.55 and line_diff > 0:
        tier = "Lean Over"
    elif adjusted <= 0.36 and line_diff <= -1.5:
        tier = "Strong Under"
    elif adjusted <= 0.45 and line_diff < 0:
        tier = "Lean Under"
    else:
        tier = "Pass"
    if low_consistency:
        if tier == "Strong Over":
            tier = "Lean Over"
        elif tier == "Strong Under":
            tier = "Lean Under"
    return tier

def flag_pill(label: str, flag: str) -> str:
    icon = {"up": "↑", "down": "↓", "flat": "→", "nodata": "—"}.get(flag, "—")
    css  = flag if flag in ["up", "down", "flat", "nodata"] else "nodata"
    return f'<span class="flag-pill {css}">{label} {icon}</span>'

# ─────────────────────────────────────────────
# Chart
# ─────────────────────────────────────────────

def build_points_chart(logs: pd.DataFrame, full_name: str, line: float, avg_pts: float) -> go.Figure:
    df = logs.copy()
    df["PTS"] = pd.to_numeric(df["PTS"], errors="coerce")
    df = df.dropna(subset=["PTS"]).sort_values("GAME_DATE", ascending=True)
    labels = df["MATCHUP"].fillna(df["GAME_DATE"].astype(str).str[:10])
    pts    = df["PTS"].tolist()
    colors = ["#22c55e" if p >= line else "#ef4444" for p in pts]

    fig = go.Figure()
    fig.add_hrect(y0=line, y1=max(pts) + 5, fillcolor="rgba(34,197,94,0.04)", line_width=0)
    fig.add_hrect(y0=0,    y1=line,         fillcolor="rgba(239,68,68,0.04)",  line_width=0)
    fig.add_trace(go.Scatter(
        x=list(range(len(pts))), y=pts, mode="lines+markers", name="Points",
        line=dict(color="#60a5fa", width=2.5),
        marker=dict(color=colors, size=11, line=dict(color="#080c14", width=2)),
        hovertemplate=[
            f"<b>{labels.iloc[i]}</b><br>Points: <b>{pts[i]}</b><br>{'✅ Over' if pts[i] >= line else '❌ Under'}<extra></extra>"
            for i in range(len(pts))
        ],
    ))
    fig.add_hline(y=line, line_dash="dash", line_color="#f97316", line_width=2,
                  annotation_text=f"  Line {line}", annotation_position="top left",
                  annotation_font=dict(color="#f97316", size=11))
    fig.add_hline(y=avg_pts, line_dash="dot", line_color="#a78bfa", line_width=1.5,
                  annotation_text=f"  Avg {avg_pts:.1f}", annotation_position="bottom left",
                  annotation_font=dict(color="#a78bfa", size=11))
    fig.update_layout(
        xaxis=dict(tickmode="array", tickvals=list(range(len(pts))),
                   ticktext=[labels.iloc[i] for i in range(len(pts))],
                   tickangle=-30, showgrid=False,
                   tickfont=dict(size=10, color="#475569"), linecolor="#1e293b"),
        yaxis=dict(title="PTS", showgrid=True, gridcolor="rgba(30,41,59,0.8)",
                   tickfont=dict(size=10, color="#475569")),
        plot_bgcolor="#080c14", paper_bgcolor="#080c14",
        font=dict(color="#e2e8f0"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0f172a", bordercolor="#1e293b"),
        margin=dict(l=50, r=30, t=20, b=80), height=340, showlegend=False,
    )
    return fig

# ─────────────────────────────────────────────
# AI Analysis
# ─────────────────────────────────────────────

def get_api_key() -> str:
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")

def build_analysis_prompt(
    full_name, line, side, n_games, logs,
    baseline, weighted_base, adjusted, tier,
    avg_pts, avg_min, avg_fga, consistency,
    min_flag, fga_flag, pts_flag,
    minutes_sel, role_sel, shots_sel, matchup_sel, script_sel,
    opp_abbr, opp_pts, league_avg,
    splits=None, tonight_venue=None,
) -> str:
    game_rows = []
    for _, row in logs.iterrows():
        date    = str(row["GAME_DATE"])[:10] if row["GAME_DATE"] is not None else "N/A"
        matchup = row["MATCHUP"] or "N/A"
        pts     = row["PTS"]
        mins    = row["MIN"]
        fga     = row["FGA"]
        hit     = "✓" if pd.notna(pts) and float(pts) >= line else "✗"
        game_rows.append(f"  {date} | {matchup} | {pts} pts | {mins} min | {fga} FGA | {hit}")

    defense_note = ""
    if opp_abbr and opp_pts:
        defense_note = f"\nOpponent ({opp_abbr}) allows {opp_pts:.1f} pts/game (league avg: {league_avg})"

    sp = splits or {}
    home_rate  = f"{sp.get('home_rate', 0):.0%}" if sp.get("home_rate") is not None else "N/A"
    away_rate  = f"{sp.get('away_rate', 0):.0%}" if sp.get("away_rate") is not None else "N/A"
    home_games = sp.get("home_games", 0)
    away_games = sp.get("away_games", 0)
    home_avg   = sp.get("home_avg", "N/A")
    away_avg   = sp.get("away_avg", "N/A")
    venue      = tonight_venue or "Unknown"

    return f"""You are a sharp NBA prop analyst. Write a clear, data-driven breakdown.

Player: {full_name} | Line: {line} pts ({side}) | Last {n_games} games

GAME LOG:
{chr(10).join(game_rows)}

STATS:
- Avg PTS: {avg_pts:.1f} | Avg MIN: {avg_min:.1f} | Avg FGA: {avg_fga:.1f}
- Raw hit rate: {baseline:.0%} | Weighted hit rate: {weighted_base:.0%}
- Adjusted rate: {adjusted:.0%} | Consistency: {consistency:.0%}
- Home hit rate: {home_rate} ({home_games} games, avg {home_avg} pts)
- Away hit rate: {away_rate} ({away_games} games, avg {away_avg} pts)
- Tonight venue: {venue}
- Trends: MIN {min_flag} | FGA {fga_flag} | PTS {pts_flag}

CONTEXT:
- Minutes: {minutes_sel} | Role: {role_sel} | Shots: {shots_sel}
- Matchup: {matchup_sel} (auto-detected from real defense stats){defense_note}
- Game script: {script_sel}

MODEL OUTPUT: {tier}

Write 3-4 paragraphs: (1) lead with the prop and lean, (2) what the game log shows, (3) how the opponent defense and context affect it tonight, (4) closing verdict. Be direct, use real numbers, write like a sharp bettor."""

def generate_ai_analysis(prompt: str) -> str:
    client = Groq(api_key=get_api_key())
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content



# ─────────────────────────────────────────────
# UI — Header
# ─────────────────────────────────────────────

st.markdown("""
<div class="proplens-header">
    <div>
        <div class="proplens-logo">PropLens</div>
        <div class="proplens-sub">NBA Points Prop Analyzer</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("<div class='section-header'>Settings</div>", unsafe_allow_html=True)
    manual_mode = st.checkbox("Manual input fallback")
    st.markdown("<div style='margin-top:2rem; font-family:DM Mono; font-size:0.65rem; color:#334155; line-height:1.6;'>For educational purposes only. Not financial or betting advice.</div>", unsafe_allow_html=True)

enable_ai = True
scan_slate = False

# ─────────────────────────────────────────────
# Player & Prop inputs
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Player & Prop</div>", unsafe_allow_html=True)

# Build full player list once for the searchable dropdown
@st.cache_data(ttl=86400)
def get_all_player_names():
    all_players = players.get_players()
    active = sorted(
        [p["full_name"] for p in all_players if p.get("is_active", True)],
        key=lambda x: x.split()[-1]
    )
    return active

all_player_names = get_all_player_names()

col_a, col_b, col_c, col_d, col_e = st.columns([2.5, 1, 1, 1, 0.8])
with col_a:
    selected_player = st.selectbox(
        "Player",
        options=[None] + all_player_names,
        index=0,
        format_func=lambda x: "🔍  Type to search for a player..." if x is None else x,
        help="Start typing a player's name to filter the list"
    )
with col_b:
    line = st.number_input("Points Line", min_value=0.0, value=24.5, step=0.5)
with col_c:
    side = st.selectbox("Over / Under", ["Over", "Under"])
with col_d:
    n_games = st.selectbox("Sample", [5, 10, 15], index=1)
with col_e:
    season = st.text_input("Season", value="2025-26")

if not selected_player:
    st.markdown("<div style='color:#475569; font-family:DM Mono; font-size:0.8rem; margin-top:1rem;'>Search for a player above to get started.</div>", unsafe_allow_html=True)
    st.stop()

player_id, full_name = find_player_id(selected_player)

if player_id is None:
    st.error("Could not resolve player. Try a different spelling.")
    st.stop()

fetch = st.button("🔍  Analyze Prop")
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

if not fetch and st.session_state.logs is None and not scan_slate:
    st.markdown("<div style='color:#475569; font-family:DM Mono; font-size:0.8rem; margin-top:1rem;'>↑ Select a player, set the line, then click Analyze Prop.</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Fetch logs + defense data
# ─────────────────────────────────────────────

if fetch:
    st.session_state.ai_analysis = None
    st.session_state.ai_error    = None

    try:
        with st.spinner("Fetching game logs..."):
            st.session_state.logs = fetch_with_retries(
                lambda: get_last_n_games(player_id=player_id, season=season, n=n_games)
            )
            st.session_state.defense_data = None  # will be fetched after opponent is known
    except Exception as e:
        if not manual_mode:
            st.error(f"Fetch failed: {repr(e)}")
            st.stop()
        else:
            st.warning("Live fetch failed. Enter points manually.")
            st.session_state.logs = None

    if st.session_state.logs is None and manual_mode:
        manual_points = []
        st.markdown("<div class='section-header'>Manual Entry</div>", unsafe_allow_html=True)
        cols = st.columns(5)
        for i in range(10):
            val = cols[i % 5].number_input(f"G{i+1}", min_value=0.0, step=1.0, key=f"mp_{i}")
            manual_points.append(val)
        st.session_state.logs = pd.DataFrame({
            "GAME_DATE": [None]*10, "MATCHUP": [None]*10, "MIN": [None]*10,
            "PTS": manual_points, "FGA": [None]*10, "FTA": [None]*10, "FG3A": [None]*10,
        })

# ─────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────

if st.session_state.logs is not None:
    logs = st.session_state.logs

    # ── Core stats ────────────────────────────
    baseline       = hit_rate(logs, line, side)
    weighted_base  = weighted_hit_rate(logs, line, side)
    consistency    = consistency_score(logs, line)
    avg_min        = pd.to_numeric(logs["MIN"],  errors="coerce").dropna().mean()
    avg_fga        = pd.to_numeric(logs["FGA"],  errors="coerce").dropna().mean()
    avg_fta        = pd.to_numeric(logs["FTA"],  errors="coerce").dropna().mean()
    sample_avg_pts = pd.to_numeric(logs["PTS"],  errors="coerce").dropna().mean()

    minutes_suggest = suggest_bucket(avg_min, 32, 26)
    shots_suggest   = "High" if avg_fga >= 15 else ("Low" if avg_fga < 10 else "Medium")
    role_suggest    = suggest_bucket(avg_fga + 0.5 * avg_fta, 18, 12)

    tonight_venue = None  # set after player_team is resolved

    min_flag = trend_flag(logs["MIN"], n_games)
    fga_flag = trend_flag(logs["FGA"], n_games)
    pts_flag = trend_flag(logs["PTS"], n_games)

    # ── Auto-detect NEXT opponent + defense rating ─
    player_team         = get_player_team(player_id)
    opp_abbr, game_date = get_next_opponent(player_team)

    # Home/away splits — needs player_team to detect home vs away from MATCHUP
    splits = home_away_split(logs, line, side, player_team)

    # Fall back to most recent game log opponent if no upcoming game found
    if not opp_abbr:
        opp_abbr  = get_opponent_from_logs(logs, player_team)
        game_date = None

    matchup_auto, opp_pts, league_avg = classify_matchup(opp_abbr, season)

    # ── Stat cards ────────────────────────────
    st.markdown(f"<div class='section-header'>{full_name}</div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Avg PTS (L{n_games})</div>
            <div class='stat-value orange'>{sample_avg_pts:.1f}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        hr_color = "green" if weighted_base >= 0.6 else ("yellow" if weighted_base >= 0.5 else "red")
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Weighted Hit Rate</div>
            <div class='stat-value {hr_color}'>{weighted_base:.0%}</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        cons_color = "green" if consistency >= 0.5 else ("yellow" if consistency >= 0.35 else "red")
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Consistency Score</div>
            <div class='stat-value {cons_color}'>{consistency:.0%}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Avg MIN (L{n_games})</div>
            <div class='stat-value'>{avg_min:.1f}</div>
        </div>""", unsafe_allow_html=True)

    # ── Defense card ──────────────────────────
    if opp_abbr and opp_pts:
        badge_css = matchup_auto.lower()
        badge_label = {"Good": "✅ Weak defense", "Bad": "🔴 Strong defense", "Neutral": "⚪ Average defense"}[matchup_auto]
        date_str = f" · {game_date}" if game_date else ""
        schedule_label = f"Next game vs {opp_abbr}{date_str}" if game_date is not None else f"Most recent opp: {opp_abbr}"
        st.markdown(f"""
        <div class='defense-card'>
            <div>
                <div class='stat-label'>{schedule_label}</div>
                <div style='font-size:1.1rem; font-weight:700; color:#f1f5f9; margin-top:4px;'>
                    {opp_pts:.1f} pts allowed/game
                    <span style='font-family:DM Mono; font-size:0.72rem; color:#475569; margin-left:8px;'>
                        league avg {league_avg}
                    </span>
                </div>
            </div>
            <span class='defense-badge {badge_css}'>{badge_label}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        matchup_auto = "Neutral"

    # Trend flags
    flags_html = f"""<div class='flag-row'>
        {flag_pill("MIN", min_flag)}
        {flag_pill("FGA", fga_flag)}
        {flag_pill("PTS", pts_flag)}
    </div>"""
    st.markdown(flags_html, unsafe_allow_html=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Home/Away splits ──────────────────────
    if splits["home_games"] > 0 or splits["away_games"] > 0:
        # Detect if tonight is home or away
        tonight_venue = None
        if player_team and opp_abbr:
            tonight_venue = "Home" if splits.get("home_games", 0) > 0 else None
            # Re-derive from next game: if player_team is home team they play at home
            try:
                from datetime import timedelta
                for day_offset in [0, 1, 2]:
                    check_date = (datetime.today() + timedelta(days=day_offset)).strftime("%m/%d/%Y")
                    sb_check = scoreboardv2.ScoreboardV2(game_date=check_date, league_id="00", day_offset=0, timeout=10)
                    g = sb_check.get_data_frames()[0]
                    if not g.empty:
                        r = g[(g["HOME_TEAM_ABBREVIATION"] == player_team) | (g["VISITOR_TEAM_ABBREVIATION"] == player_team)]
                        if not r.empty:
                            tonight_venue = "Home" if r.iloc[0]["HOME_TEAM_ABBREVIATION"] == player_team else "Away"
                            break
            except Exception:
                pass

        st.markdown("<div class='section-header'>Home / Away Splits</div>", unsafe_allow_html=True)

        venue_note = ""
        if tonight_venue:
            venue_color = "#22c55e" if tonight_venue == "Home" else "#60a5fa"
            venue_note = f"<span style='background:{venue_color}22; color:{venue_color}; font-family:DM Mono; font-size:0.7rem; padding:3px 10px; border-radius:999px; border:1px solid {venue_color}44; margin-left:8px;'>Tonight: {tonight_venue}</span>"

        ha1, ha2 = st.columns(2)
        with ha1:
            if splits["home_games"] >= 2:
                hr_pct = splits["home_rate"]
                hr_color = "#22c55e" if hr_pct >= 0.6 else ("#eab308" if hr_pct >= 0.5 else "#ef4444")
                st.markdown(f"""
                <div class='stat-card' style='border-color: {"#166534" if tonight_venue == "Home" else "#1e293b"};'>
                    <div class='stat-label'>Home {venue_note if tonight_venue == "Home" else ""}</div>
                    <div style='display:flex; align-items:baseline; gap:12px; margin-top:4px;'>
                        <div class='stat-value' style='color:{hr_color};'>{hr_pct:.0%}</div>
                        <div style='font-family:DM Mono; font-size:0.72rem; color:#475569;'>hit rate</div>
                    </div>
                    <div style='font-family:DM Mono; font-size:0.72rem; color:#475569; margin-top:4px;'>
                        {splits["home_avg"]} avg pts · {splits["home_games"]} games
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='stat-card'><div class='stat-label'>Home</div><div style='color:#475569; font-size:0.8rem; margin-top:4px;'>Not enough data</div></div>", unsafe_allow_html=True)

        with ha2:
            if splits["away_games"] >= 2:
                ar_pct = splits["away_rate"]
                ar_color = "#22c55e" if ar_pct >= 0.6 else ("#eab308" if ar_pct >= 0.5 else "#ef4444")
                st.markdown(f"""
                <div class='stat-card' style='border-color: {"#166534" if tonight_venue == "Away" else "#1e293b"};'>
                    <div class='stat-label'>Away {venue_note if tonight_venue == "Away" else ""}</div>
                    <div style='display:flex; align-items:baseline; gap:12px; margin-top:4px;'>
                        <div class='stat-value' style='color:{ar_color};'>{ar_pct:.0%}</div>
                        <div style='font-family:DM Mono; font-size:0.72rem; color:#475569;'>hit rate</div>
                    </div>
                    <div style='font-family:DM Mono; font-size:0.72rem; color:#475569; margin-top:4px;'>
                        {splits["away_avg"]} avg pts · {splits["away_games"]} games
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='stat-card'><div class='stat-label'>Away</div><div style='color:#475569; font-size:0.8rem; margin-top:4px;'>Not enough data</div></div>", unsafe_allow_html=True)

    # ── Chart ─────────────────────────────────
    st.markdown("<div class='section-header'>Points Chart</div>", unsafe_allow_html=True)
    fig = build_points_chart(logs, full_name, line, sample_avg_pts)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋  Game Log"):
        st.dataframe(logs.reset_index(drop=True), use_container_width=True)

    # ── Context ───────────────────────────────
    st.markdown("<div class='section-header'>Context</div>", unsafe_allow_html=True)

    # Show next opponent clearly
    if opp_abbr:
        date_display = game_date if game_date else ""
        badge_css = matchup_auto.lower()
        badge_text = {"Good": "Weak defense", "Bad": "Strong defense", "Neutral": "Average defense"}[matchup_auto]
        opp_pts_str = f"{opp_pts:.1f}" if opp_pts else "N/A"
        next_game_html = (
            "<div style='background:#0f172a; border:1px solid #1e293b; border-radius:10px; "
            "padding:0.75rem 1.2rem; margin-bottom:1rem; display:flex; "
            "align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;'>"
            "<div>"
            "<div style='font-family:DM Mono; font-size:0.65rem; color:#475569; "
            "letter-spacing:0.12em; text-transform:uppercase; margin-bottom:4px;'>Next Game</div>"
            "<div style='font-size:1.2rem; font-weight:800; color:#f1f5f9; letter-spacing:-0.5px;'>"
            "vs <span style='color:#f97316;'>" + opp_abbr + "</span>"
            "<span style='font-family:DM Mono; font-size:0.75rem; color:#475569; font-weight:400; margin-left:8px;'>"
            + date_display + "</span></div>"
            "</div>"
            "<span class='defense-badge " + badge_css + "'>" + badge_text + " · " + opp_pts_str + " pts/g allowed</span>"
            "</div>"
        )
        st.markdown(next_game_html, unsafe_allow_html=True)
        st.caption("Matchup quality is auto-filled based on the next opponent's defensive rating. You can override it manually.")
    else:
        st.caption("Next opponent not found — matchup set to Neutral.")

    # Primary controls — always visible
    pc1, pc2 = st.columns(2)
    with pc1:
        matchup_options = ["Neutral","Good","Bad"]
        matchup_sel = st.selectbox(
            "Matchup 🤖",
            matchup_options,
            index=matchup_options.index(matchup_auto),
            help=f"Auto-detected: {opp_abbr or 'unknown'} allows {f'{opp_pts:.1f}' if opp_pts else 'N/A'} pts/game"
        )
    with pc2:
        script_sel = st.selectbox("Game Script", ["Neutral","Competitive","Blowout risk"])

    # Advanced overrides — collapsed by default
    with st.expander("⚙️  Advanced overrides"):
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            minutes_sel = st.selectbox("Minutes", ["Okay","Strong","Risk"],
                                       index=["Okay","Strong","Risk"].index(minutes_suggest))
        with ac2:
            role_sel = st.selectbox("Role", ["Okay","Strong","Risk"],
                                    index=["Okay","Strong","Risk"].index(role_suggest))
        with ac3:
            shots_sel = st.selectbox("Shots", ["Medium","High","Low"],
                                     index=["Medium","High","Low"].index(shots_suggest))

    context = {
        "minutes": minutes_sel,
        "role":    role_sel,
        "shots":   shots_sel,
        "matchup": matchup_sel,
        "script":  script_sel,
    }

    adjusted   = apply_adjustments(weighted_base, context)
    line_diff  = sample_avg_pts - line
    model_lean = "OVER" if sample_avg_pts > line else ("UNDER" if sample_avg_pts < line else "EVEN")
    tier = get_confidence_tier(adjusted, line_diff, consistency)

    tier_css   = {"Strong Over":"green","Lean Over":"yellow","Lean Under":"orange","Strong Under":"red","Pass":"gray"}
    tier_emoji = {"Strong Over":"🟢","Lean Over":"🟡","Lean Under":"🟠","Strong Under":"🔴","Pass":"⚪"}
    css = tier_css[tier]

    # ── Verdict banner ────────────────────────
    st.markdown("<div class='section-header'>Verdict</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='verdict-banner {css}'>
        <div>
            <div class='verdict-label'>{full_name} · {line} pts · {side}</div>
            <div class='verdict-tier {css}'>{tier_emoji[tier]} {tier}</div>
        </div>
        <div style='display:flex; gap:2rem; flex-wrap:wrap;'>
            <div>
                <div class='verdict-label'>Adjusted Hit Rate</div>
                <div style='font-size:1.4rem; font-weight:800; color:#f1f5f9;'>{adjusted:.0%}</div>
            </div>
            <div>
                <div class='verdict-label'>Edge vs Line</div>
                <div style='font-size:1.4rem; font-weight:800; color:{"#22c55e" if line_diff > 0 else "#ef4444"};'>{line_diff:+.1f}</div>
            </div>
            <div>
                <div class='verdict-label'>Consistency</div>
                <div style='font-size:1.4rem; font-weight:800; color:#f1f5f9;'>{consistency:.0%}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""<div class='model-note'>
    Raw hit rate: {baseline:.0%} &nbsp;·&nbsp;
    Weighted (recency): {weighted_base:.0%} &nbsp;·&nbsp;
    After context: {adjusted:.0%} &nbsp;·&nbsp;
    Sample: {n_games} games &nbsp;·&nbsp;
    Matchup: {matchup_sel} (vs {opp_abbr or "unknown"})
    </div>""", unsafe_allow_html=True)

    # ── AI Analysis ───────────────────────────
    st.markdown("<div class='section-header'>AI Breakdown</div>", unsafe_allow_html=True)
    api_key = get_api_key()
    if not api_key:
        st.error("❌ No GROQ_API_KEY found in Streamlit secrets.")
    else:
        if st.session_state.ai_analysis:
            st.markdown(f"<div class='ai-box'>{st.session_state.ai_analysis}</div>", unsafe_allow_html=True)
            if st.button("⚡  Regenerate"):
                st.session_state.ai_analysis = None
                st.session_state.ai_error = None
                st.rerun()
        elif st.session_state.ai_error:
            st.error(f"AI analysis failed: {st.session_state.ai_error}")
            if st.button("⚡  Retry"):
                st.session_state.ai_analysis = None
                st.session_state.ai_error = None
                st.rerun()
        else:
            if st.button("⚡  Generate AI Analysis"):
                with st.spinner("Analyzing..."):
                    try:
                        prompt = build_analysis_prompt(
                            full_name=full_name, line=line, side=side, n_games=n_games,
                            logs=logs, baseline=baseline, weighted_base=weighted_base,
                            adjusted=adjusted, tier=tier, avg_pts=sample_avg_pts,
                            avg_min=avg_min, avg_fga=avg_fga, consistency=consistency,
                            min_flag=min_flag, fga_flag=fga_flag, pts_flag=pts_flag,
                            minutes_sel=minutes_sel, role_sel=role_sel, shots_sel=shots_sel,
                            matchup_sel=matchup_sel, script_sel=script_sel,
                            opp_abbr=opp_abbr, opp_pts=opp_pts, league_avg=league_avg,
                            splits=splits, tonight_venue=tonight_venue,
                        )
                        st.session_state.ai_analysis = generate_ai_analysis(prompt)
                        st.session_state.ai_error = None
                    except Exception as e:
                        st.session_state.ai_error = repr(e)
                        st.session_state.ai_analysis = None

    # ── Export + Add to Tracker ──────────────
    st.markdown("<div class='section-header'>Export</div>", unsafe_allow_html=True)
    ex1, ex2 = st.columns([1, 1])
    with ex1:
        out = logs.copy()
        out.insert(0, "PLAYER",            full_name)
        out.insert(1, "LINE",              line)
        out.insert(2, "SIDE",              side)
        out.insert(3, "OPPONENT",          opp_abbr or "")
        out.insert(4, "OPP_PTS_ALLOWED",   opp_pts or "")
        out.insert(5, "MATCHUP_QUALITY",   matchup_sel)
        out.insert(6, "RAW_HIT_RATE",      baseline)
        out.insert(7, "WEIGHTED_HIT_RATE", weighted_base)
        out.insert(8, "ADJUSTED_RATE",     adjusted)
        out.insert(9, "CONSISTENCY",       consistency)
        out.insert(10,"TIER",              tier)
        csv = out.to_csv(index=False).encode("utf-8")
        st.download_button("⬇  Download CSV", data=csv, file_name="prop_report.csv", mime="text/csv")
    with ex2:
        if st.button("➕  Add to Prop Tracker"):
            entry = {
                "Player":      full_name,
                "Line":        f"{line} {side}",
                "Opponent":    opp_abbr or "—",
                "Matchup":     matchup_sel,
                "Avg PTS":     round(sample_avg_pts, 1),
                "Hit Rate":    f"{weighted_base:.0%}",
                "Adjusted":    f"{adjusted:.0%}",
                "Consistency": f"{consistency:.0%}",
                "Verdict":     tier,
            }
            # Avoid duplicates — replace if same player+line already tracked
            existing = [i for i, e in enumerate(st.session_state.tracker)
                        if e["Player"] == full_name and e["Line"] == f"{line} {side}"]
            if existing:
                st.session_state.tracker[existing[0]] = entry
                st.success(f"Updated {full_name} in tracker.")
            else:
                st.session_state.tracker.append(entry)
                st.success(f"Added {full_name} to tracker!")

# ─────────────────────────────────────────────
# Prop Tracker
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Prop Tracker</div>", unsafe_allow_html=True)

if not st.session_state.tracker:
    st.markdown("""
    <div style='background:#0f172a; border:1px dashed #1e293b; border-radius:12px;
                padding:1.5rem; text-align:center;'>
        <div style='font-family:DM Mono; font-size:0.75rem; color:#334155;'>
            No props tracked yet
        </div>
        <div style='font-size:0.85rem; color:#475569; margin-top:4px;'>
            Analyze a player then click ➕ Add to Prop Tracker
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Render each tracked prop as a styled card with remove button
    tier_css   = {"Strong Over":"green","Lean Over":"yellow","Lean Under":"orange","Strong Under":"red","Pass":"gray"}
    tier_emoji = {"Strong Over":"🟢","Lean Over":"🟡","Lean Under":"🟠","Strong Under":"🔴","Pass":"⚪"}

    to_remove = None
    for i, entry in enumerate(st.session_state.tracker):
        t = entry["Verdict"]
        css = tier_css.get(t, "gray")
        emoji = tier_emoji.get(t, "⚪")

        col_card, col_remove = st.columns([11, 1])
        with col_card:
            st.markdown(f"""
            <div class='verdict-banner {css}' style='margin:0.3rem 0; padding:1rem 1.4rem;'>
                <div>
                    <div class='verdict-label'>{entry["Line"]} · vs {entry["Opponent"]}</div>
                    <div style='font-size:1.1rem; font-weight:800; color:#f1f5f9; letter-spacing:-0.5px;'>
                        {entry["Player"]}
                    </div>
                </div>
                <div style='display:flex; gap:1.5rem; flex-wrap:wrap; align-items:center;'>
                    <div>
                        <div class='verdict-label'>Verdict</div>
                        <div class='verdict-tier {css}' style='font-size:1rem;'>{emoji} {t}</div>
                    </div>
                    <div>
                        <div class='verdict-label'>Avg PTS</div>
                        <div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Avg PTS"]}</div>
                    </div>
                    <div>
                        <div class='verdict-label'>Hit Rate</div>
                        <div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Hit Rate"]}</div>
                    </div>
                    <div>
                        <div class='verdict-label'>Adjusted</div>
                        <div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Adjusted"]}</div>
                    </div>
                    <div>
                        <div class='verdict-label'>Matchup</div>
                        <div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Matchup"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_remove:
            st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
            if st.button("✕", key=f"remove_{i}", help="Remove from tracker"):
                to_remove = i

    if to_remove is not None:
        st.session_state.tracker.pop(to_remove)
        st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    tc1, tc2 = st.columns([1, 1])
    with tc1:
        tracker_df = pd.DataFrame(st.session_state.tracker)
        tracker_csv = tracker_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇  Export Tracker CSV", data=tracker_csv,
                           file_name="prop_tracker.csv", mime="text/csv")
    with tc2:
        if st.button("🗑️  Clear All"):
            st.session_state.tracker = []
            st.rerun()

st.markdown("<div style='margin-top:3rem; font-family:DM Mono; font-size:0.65rem; color:#334155; text-align:center;'>PropLens — For educational purposes only. Not financial or betting advice.</div>", unsafe_allow_html=True)
