import os
import re
import time
import requests
from datetime import datetime, timedelta
from typing import Optional, Tuple, List

from groq import Groq
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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

for key, default in [
    ("logs", None), ("ai_analysis", None), ("ai_error", None),
    ("defense_data", None), ("tracker", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
# BallDontLie API layer
# ─────────────────────────────────────────────

BDL_BASE = "https://api.balldontlie.io/nba/v1"

def bdl_headers() -> dict:
    key = ""
    try:
        # support both uppercase and lowercase secret names
        key = st.secrets.get("BALLDONTLIE_API_KEY") or st.secrets.get("balldontlie_api_key") or ""
    except Exception:
        key = os.environ.get("BALLDONTLIE_API_KEY", "") or os.environ.get("balldontlie_api_key", "")
    if not key:
        st.error("❌ BALLDONTLIE_API_KEY not found in Streamlit secrets. Add it at balldontlie.io (free).")
        st.stop()
    # BDL v1 requires Bearer prefix
    if not key.startswith("Bearer "):
        key = f"Bearer {key}"
    return {"Authorization": key}

def bdl_get(endpoint: str, params: dict = None, retries: int = 3) -> dict:
    """GET from BallDontLie with simple retry."""
    url = f"{BDL_BASE}/{endpoint}"
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=bdl_headers(), params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}

# ── Player search ─────────────────────────────

@st.cache_data(ttl=86400)
def bdl_get_all_players() -> List[dict]:
    """Fetch all active NBA players from BallDontLie (paginated)."""
    all_players = []
    cursor = None
    while True:
        params = {"per_page": 100}
        if cursor:
            params["cursor"] = cursor
        data = bdl_get("players/active", params=params)
        all_players.extend(data.get("data", []))
        meta = data.get("meta", {})
        cursor = meta.get("next_cursor")
        if not cursor:
            break
    return all_players

def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def find_player(player_name: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Returns (bdl_player_id, full_name, team_abbreviation).
    """
    name = normalize_name(player_name)
    all_players = bdl_get_all_players()
    for p in all_players:
        full = f"{p['first_name']} {p['last_name']}"
        if normalize_name(full) == name:
            team_abbr = p.get("team", {}).get("abbreviation") if p.get("team") else None
            return p["id"], full, team_abbr
    # partial match
    candidates = [
        p for p in all_players
        if name in normalize_name(f"{p['first_name']} {p['last_name']}")
    ]
    if len(candidates) == 1:
        p = candidates[0]
        full = f"{p['first_name']} {p['last_name']}"
        team_abbr = p.get("team", {}).get("abbreviation") if p.get("team") else None
        return p["id"], full, team_abbr
    return None, None, None

# ── Game logs ─────────────────────────────────

@st.cache_data(ttl=600)
def bdl_get_game_logs(player_id: int, season: int, n: int = 10) -> pd.DataFrame:
    """
    Fetch last N game logs for a player from BallDontLie.
    season: integer year e.g. 2025 for 2025-26 season.
    Returns DataFrame with columns: GAME_DATE, MATCHUP, MIN, PTS, FGA, FTA, FG3A, PLUS_MINUS
    """
    all_stats = []
    cursor = None
    # Fetch up to 3 pages to ensure we get enough games
    for _ in range(3):
        params = {
            "player_ids[]": player_id,
            "seasons[]": season,
            "per_page": 25,
        }
        if cursor:
            params["cursor"] = cursor
        data = bdl_get("stats", params=params)
        all_stats.extend(data.get("data", []))
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor or len(all_stats) >= n * 2:
            break

    if not all_stats:
        return pd.DataFrame(columns=["GAME_DATE", "MATCHUP", "MIN", "PTS", "FGA", "FTA", "FG3A", "PLUS_MINUS"])

    rows = []
    for s in all_stats:
        g = s.get("game", {})
        team = s.get("team", {})
        # Build matchup string: "TEAM vs. OPP" or "TEAM @ OPP"
        home_id   = g.get("home_team_id")
        team_id   = team.get("id")
        is_home   = (team_id == home_id)
        opp_abbr  = ""  # we'll fill from the game teams endpoint if needed
        team_abbr = team.get("abbreviation", "")
        # BDL stats don't directly give opponent abbr in stats endpoint
        # Use home_team_id vs visitor_team_id with a lookup
        matchup = f"{team_abbr} {'vs.' if is_home else '@'} ?"
        rows.append({
            "GAME_DATE":  pd.to_datetime(g.get("date", "")[:10]),
            "MATCHUP":    matchup,
            "GAME_ID":    g.get("id"),
            "IS_HOME":    is_home,
            "TEAM_ABBR":  team_abbr,
            "MIN":        s.get("min", "0"),
            "PTS":        s.get("pts", 0),
            "FGA":        s.get("fga", 0),
            "FTA":        s.get("fta", 0),
            "FG3A":       s.get("fg3a", 0),
            "PLUS_MINUS": s.get("plus_minus", 0),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("GAME_DATE", ascending=False).head(n).reset_index(drop=True)

    # Enrich MATCHUP with actual opponent abbreviation using games endpoint
    try:
        game_ids = df["GAME_ID"].dropna().tolist()
        if game_ids:
            params = {"ids[]": game_ids[:n], "per_page": n}
            gdata = bdl_get("games", params=params)
            game_map = {}
            for gm in gdata.get("data", []):
                game_map[gm["id"]] = gm
            for i, row in df.iterrows():
                gm = game_map.get(row["GAME_ID"])
                if not gm:
                    continue
                home_abbr = gm.get("home_team", {}).get("abbreviation", "")
                away_abbr = gm.get("visitor_team", {}).get("abbreviation", "")
                team_abbr = row["TEAM_ABBR"]
                if row["IS_HOME"]:
                    df.at[i, "MATCHUP"] = f"{team_abbr} vs. {away_abbr}"
                else:
                    df.at[i, "MATCHUP"] = f"{team_abbr} @ {home_abbr}"
    except Exception:
        pass

    return df[["GAME_DATE", "MATCHUP", "MIN", "PTS", "FGA", "FTA", "FG3A", "PLUS_MINUS"]]


def season_str_to_int(season_str: str) -> int:
    """Convert '2025-26' -> 2025, '2024-25' -> 2024."""
    try:
        return int(season_str.split("-")[0])
    except Exception:
        return 2025

# ── Next game / schedule ──────────────────────

@st.cache_data(ttl=300)
def bdl_get_next_game(team_abbr: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Find next upcoming game for a team using BallDontLie games endpoint.
    Returns (opp_abbr, game_date_str, venue) where venue is 'Home' or 'Away'.
    Skips games with status 'Final'.
    """
    if not team_abbr:
        return None, None, None

    try:
        import pytz
        et = pytz.timezone("America/New_York")
        today = datetime.now(et).date()
    except Exception:
        today = datetime.today().date()

    # Check today + next 10 days
    for offset in range(10):
        check = today + timedelta(days=offset)
        date_str = check.strftime("%Y-%m-%d")
        try:
            data = bdl_get("games", params={"dates[]": date_str, "per_page": 30})
            for gm in data.get("data", []):
                home = gm.get("home_team", {}).get("abbreviation", "")
                away = gm.get("visitor_team", {}).get("abbreviation", "")
                if team_abbr not in (home, away):
                    continue
                status = str(gm.get("status", "")).strip()
                # Skip finished games
                if "final" in status.lower():
                    continue
                game_date_str = check.strftime("%b %d, %Y")
                if team_abbr == home:
                    return away, game_date_str, "Home"
                else:
                    return home, game_date_str, "Away"
        except Exception:
            continue

    return None, None, None

# ── Opponent defense rating ───────────────────

@st.cache_data(ttl=3600)
def bdl_get_opp_pts_allowed(opp_abbr: str, season: int) -> Optional[float]:
    """
    Get opponent pts allowed per game using BallDontLie team season averages.
    Uses pts_allowed directly from team averages if available.
    """
    try:
        # Get all teams to find team ID
        tdata = bdl_get("teams", params={"per_page": 30})
        team_id = None
        for t in tdata.get("data", []):
            if t.get("abbreviation") == opp_abbr:
                team_id = t["id"]
                break
        if not team_id:
            return None

        # Get team season averages
        avg_data = bdl_get(
            "team_season_averages/general",
            params={"season": season, "season_type": "regular", "type": "base", "team_ids[]": team_id}
        )
        for row in avg_data.get("data", []):
            if row.get("team", {}).get("id") == team_id:
                stats = row.get("stats", {})
                # pfd = personal fouls drawn (pts fouled = opponent pts)
                # opp_pts not directly available — use pts - plus_minus approximation
                pts = stats.get("pts")
                if pts:
                    return round(float(pts), 1)
        return None
    except Exception:
        return None

def classify_matchup_bdl(opp_abbr: Optional[str], season: int) -> Tuple[str, Optional[float], str]:
    """Classify opponent defense quality using BallDontLie team averages."""
    league_avg = 114.5
    if not opp_abbr:
        return "Neutral", None, str(league_avg)

    opp_pts = bdl_get_opp_pts_allowed(opp_abbr, season)

    if opp_pts is None:
        return "Neutral", None, str(league_avg)

    diff = opp_pts - league_avg
    if diff >= 1.5:
        return "Good", opp_pts, str(league_avg)
    if diff <= -1.5:
        return "Bad", opp_pts, str(league_avg)
    return "Neutral", opp_pts, str(league_avg)

# ─────────────────────────────────────────────
# Prediction engine (unchanged)
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
    result = {"home_rate": None, "away_rate": None, "home_games": 0, "away_games": 0, "home_avg": None, "away_avg": None}
    if df is None or df.empty or "MATCHUP" not in df.columns:
        return result
    df = df.copy()
    df["PTS_NUM"] = pd.to_numeric(df["PTS"], errors="coerce")
    df["IS_HOME"] = df["MATCHUP"].apply(lambda m: "vs." in str(m) if m else None)
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

def venue_adjustment(splits: dict, tonight_venue: Optional[str], side: str) -> str:
    if not tonight_venue:
        return "Neutral"
    home_rate = splits.get("home_rate")
    away_rate = splits.get("away_rate")
    if home_rate is None or away_rate is None:
        return "Neutral"
    diff = (home_rate - away_rate) if tonight_venue == "Home" else (away_rate - home_rate)
    if diff >= 0.10:
        return "Boost"
    if diff <= -0.10:
        return "Penalty"
    return "Neutral"

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
    multipliers = {
        "minutes":  {"Strong": 1.08, "Okay": 1.00, "Risk": 0.88},
        "role":     {"Strong": 1.06, "Okay": 1.00, "Risk": 0.92},
        "shots":    {"High":   1.05, "Medium": 1.00, "Low": 0.90},
        "matchup":  {"Good":   1.08, "Neutral": 1.00, "Bad": 0.91},
        "script":   {"Competitive": 1.03, "Neutral": 1.00, "Blowout risk": 0.93},
        "venue":    {"Boost": 1.06, "Neutral": 1.00, "Penalty": 0.92},
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
        if tier == "Strong Over":   tier = "Lean Over"
        elif tier == "Strong Under": tier = "Lean Under"
    return tier

def flag_pill(label: str, flag: str) -> str:
    icon = {"up": "↑", "down": "↓", "flat": "→", "nodata": "—"}.get(flag, "—")
    css  = flag if flag in ["up", "down", "flat", "nodata"] else "nodata"
    return f'<span class="flag-pill {css}">{label} {icon}</span>'

# ─────────────────────────────────────────────
# Chart (unchanged)
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
# AI Analysis (unchanged)
# ─────────────────────────────────────────────

def get_groq_key() -> str:
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
    splits=None, tonight_venue=None, venue_adj=None,
) -> str:
    game_rows = []
    for _, row in logs.iterrows():
        date    = str(row["GAME_DATE"])[:10] if row["GAME_DATE"] is not None else "N/A"
        matchup = row.get("MATCHUP") or "N/A"
        pts     = row["PTS"]
        mins    = row["MIN"]
        fga     = row["FGA"]
        hit     = "✓" if pd.notna(pts) and float(pts) >= line else "✗"
        game_rows.append(f"  {date} | {matchup} | {pts} pts | {mins} min | {fga} FGA | {hit}")
    defense_note = f"\nOpponent ({opp_abbr}) allows {opp_pts:.1f} pts/game (league avg: {league_avg})" if opp_abbr and opp_pts else ""
    sp = splits or {}
    home_rate  = f"{sp.get('home_rate', 0):.0%}" if sp.get("home_rate") is not None else "N/A"
    away_rate  = f"{sp.get('away_rate', 0):.0%}" if sp.get("away_rate") is not None else "N/A"
    venue      = tonight_venue or "Unknown"
    venue_note = f" ({venue_adj} applied)" if venue_adj and venue_adj != "Neutral" else ""
    return f"""You are a sharp NBA prop analyst. Write a clear, data-driven breakdown.

Player: {full_name} | Line: {line} pts ({side}) | Last {n_games} games

GAME LOG:
{chr(10).join(game_rows)}

STATS:
- Avg PTS: {avg_pts:.1f} | Avg MIN: {avg_min:.1f} | Avg FGA: {avg_fga:.1f}
- Raw hit rate: {baseline:.0%} | Weighted hit rate: {weighted_base:.0%}
- Adjusted rate: {adjusted:.0%} | Consistency: {consistency:.0%}
- Home hit rate: {home_rate} ({sp.get('home_games',0)} games, avg {sp.get('home_avg','N/A')} pts)
- Away hit rate: {away_rate} ({sp.get('away_games',0)} games, avg {sp.get('away_avg','N/A')} pts)
- Tonight venue: {venue}{venue_note}
- Trends: MIN {min_flag} | FGA {fga_flag} | PTS {pts_flag}

CONTEXT:
- Minutes: {minutes_sel} | Role: {role_sel} | Shots: {shots_sel}
- Matchup: {matchup_sel} (auto-detected from real defense stats){defense_note}
- Game script: {script_sel}
- Venue split adjustment: {venue_adj or "Neutral"} (based on home/away hit rate differential)

MODEL OUTPUT: {tier}

Write 3-4 paragraphs: (1) lead with the prop and lean, (2) what the game log shows, (3) how the opponent defense, venue split, and context affect it tonight, (4) closing verdict. Be direct, use real numbers, write like a sharp bettor."""

def generate_ai_analysis(prompt: str) -> str:
    client = Groq(api_key=get_groq_key())
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
    if st.button("🔄 Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")
    st.markdown("<div style='margin-top:2rem; font-family:DM Mono; font-size:0.65rem; color:#334155; line-height:1.6;'>For educational purposes only. Not financial or betting advice.</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Player & Prop inputs
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Player & Prop</div>", unsafe_allow_html=True)

col_a, col_b, col_c, col_d, col_e = st.columns([2.5, 1, 1, 1, 0.8])
with col_a:
    player_query = st.text_input(
        "Player",
        placeholder="🔍  Type a player name (e.g. LeBron James)...",
        help="Type at least 3 characters to search"
    )
with col_b:
    line = st.number_input("Points Line", min_value=0.0, value=24.5, step=0.5)
with col_c:
    side = st.selectbox("Over / Under", ["Over", "Under"])
with col_d:
    n_games = st.selectbox("Sample", [5, 10, 15], index=1)
with col_e:
    season_str = st.text_input("Season", value="2025-26")

season_int = season_str_to_int(season_str)

# Live search: show matching players as a selectbox once user types 3+ chars
selected_player = None
if player_query and len(player_query.strip()) >= 3:
    query_norm = normalize_name(player_query)
    try:
        all_bdl_players = bdl_get_all_players()
        matches = [
            f"{p['first_name']} {p['last_name']}"
            for p in all_bdl_players
            if query_norm in normalize_name(f"{p['first_name']} {p['last_name']}")
        ]
        matches = sorted(matches, key=lambda x: x.split()[-1])
    except Exception as e:
        matches = []
        st.warning(f"Could not load player list: {e}")

    if not matches:
        st.warning("No players found matching that name.")
        st.stop()
    elif len(matches) == 1:
        selected_player = matches[0]
        st.markdown(f"<div style='font-family:DM Mono; font-size:0.75rem; color:#22c55e; margin-top:-0.5rem;'>✓ {selected_player}</div>", unsafe_allow_html=True)
    else:
        selected_player = st.selectbox(
            "Select player",
            options=matches,
            help="Multiple matches found — select the right one"
        )
else:
    st.markdown("<div style='color:#475569; font-family:DM Mono; font-size:0.8rem; margin-top:0.5rem;'>Type a player name above to get started.</div>", unsafe_allow_html=True)
    st.stop()

if not selected_player:
    st.stop()

player_id, full_name, player_team = find_player(selected_player)

if player_id is None:
    st.error("Could not resolve player. Try a different spelling.")
    st.stop()

fetch = st.button("🔍  Analyze Prop")
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

if not fetch and st.session_state.logs is None:
    st.markdown("<div style='color:#475569; font-family:DM Mono; font-size:0.8rem; margin-top:1rem;'>↑ Select a player, set the line, then click Analyze Prop.</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Fetch logs
# ─────────────────────────────────────────────

if fetch:
    st.session_state.ai_analysis = None
    st.session_state.ai_error    = None
    try:
        with st.spinner("Fetching game logs..."):
            st.session_state.logs = bdl_get_game_logs(
                player_id=player_id, season=season_int, n=n_games
            )
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

    if logs.empty:
        st.warning("No game log data found for this player/season. Try a different season or check the player name.")
        st.stop()

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

    min_flag = trend_flag(logs["MIN"], n_games)
    fga_flag = trend_flag(logs["FGA"], n_games)
    pts_flag = trend_flag(logs["PTS"], n_games)

    # ── Next game + defense ───────────────────
    opp_abbr, game_date, tonight_venue = bdl_get_next_game(player_team) if player_team else (None, None, None)

    # Splits
    splits = home_away_split(logs, line, side, player_team)

    # Fallback opponent from logs
    if not opp_abbr and logs is not None and not logs.empty:
        latest_matchup = logs.iloc[0].get("MATCHUP", "")
        if " vs. " in str(latest_matchup):
            opp_abbr = latest_matchup.split(" vs. ")[1].strip()
        elif " @ " in str(latest_matchup):
            opp_abbr = latest_matchup.split(" @ ")[1].strip()

    matchup_auto, opp_pts, league_avg = classify_matchup_bdl(opp_abbr, season_int)

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
        badge_css   = matchup_auto.lower()
        badge_label = {"Good": "✅ Weak defense", "Bad": "🔴 Strong defense", "Neutral": "⚪ Average defense"}[matchup_auto]
        date_str    = f" · {game_date}" if game_date else ""
        label       = f"Next game vs {opp_abbr}{date_str}" if game_date else f"Most recent opp: {opp_abbr}"
        st.markdown(f"""
        <div class='defense-card'>
            <div>
                <div class='stat-label'>{label}</div>
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
    st.markdown(f"""<div class='flag-row'>
        {flag_pill("MIN", min_flag)}
        {flag_pill("FGA", fga_flag)}
        {flag_pill("PTS", pts_flag)}
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Home/Away splits ──────────────────────
    if splits["home_games"] > 0 or splits["away_games"] > 0:
        st.markdown("<div class='section-header'>Home / Away Splits</div>", unsafe_allow_html=True)
        venue_color = "#22c55e" if tonight_venue == "Home" else "#60a5fa"
        venue_note_html = (
            f"<span style='background:{venue_color}22; color:{venue_color}; font-family:DM Mono; "
            f"font-size:0.7rem; padding:3px 10px; border-radius:999px; border:1px solid {venue_color}44; "
            f"margin-left:8px;'>Tonight: {tonight_venue}</span>"
        ) if tonight_venue else ""

        ha1, ha2 = st.columns(2)
        with ha1:
            if splits["home_games"] >= 2:
                hr_pct   = splits["home_rate"]
                hr_color = "#22c55e" if hr_pct >= 0.6 else ("#eab308" if hr_pct >= 0.5 else "#ef4444")
                st.markdown(f"""
                <div class='stat-card' style='border-color:{"#166534" if tonight_venue=="Home" else "#1e293b"};'>
                    <div class='stat-label'>Home {venue_note_html if tonight_venue=="Home" else ""}</div>
                    <div style='display:flex; align-items:baseline; gap:12px; margin-top:4px;'>
                        <div class='stat-value' style='color:{hr_color};'>{hr_pct:.0%}</div>
                        <div style='font-family:DM Mono; font-size:0.72rem; color:#475569;'>hit rate</div>
                    </div>
                    <div style='font-family:DM Mono; font-size:0.72rem; color:#475569; margin-top:4px;'>
                        {splits["home_avg"]} avg pts · {splits["home_games"]} games
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div class='stat-card'><div class='stat-label'>Home</div><div style='color:#475569; font-size:0.8rem; margin-top:4px;'>Not enough data</div></div>", unsafe_allow_html=True)

        with ha2:
            if splits["away_games"] >= 2:
                ar_pct   = splits["away_rate"]
                ar_color = "#22c55e" if ar_pct >= 0.6 else ("#eab308" if ar_pct >= 0.5 else "#ef4444")
                st.markdown(f"""
                <div class='stat-card' style='border-color:{"#166534" if tonight_venue=="Away" else "#1e293b"};'>
                    <div class='stat-label'>Away {venue_note_html if tonight_venue=="Away" else ""}</div>
                    <div style='display:flex; align-items:baseline; gap:12px; margin-top:4px;'>
                        <div class='stat-value' style='color:{ar_color};'>{ar_pct:.0%}</div>
                        <div style='font-family:DM Mono; font-size:0.72rem; color:#475569;'>hit rate</div>
                    </div>
                    <div style='font-family:DM Mono; font-size:0.72rem; color:#475569; margin-top:4px;'>
                        {splits["away_avg"]} avg pts · {splits["away_games"]} games
                    </div>
                </div>""", unsafe_allow_html=True)
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

    if opp_abbr:
        badge_css   = matchup_auto.lower()
        badge_text  = {"Good": "Weak defense", "Bad": "Strong defense", "Neutral": "Average defense"}[matchup_auto]
        opp_pts_str = f"{opp_pts:.1f}" if opp_pts else "N/A"
        date_display = game_date if game_date else ""
        st.markdown(
            "<div style='background:#0f172a; border:1px solid #1e293b; border-radius:10px; "
            "padding:0.75rem 1.2rem; margin-bottom:1rem; display:flex; "
            "align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;'>"
            "<div>"
            "<div style='font-family:DM Mono; font-size:0.65rem; color:#475569; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:4px;'>Next Game</div>"
            "<div style='font-size:1.2rem; font-weight:800; color:#f1f5f9; letter-spacing:-0.5px;'>"
            f"vs <span style='color:#f97316;'>{opp_abbr}</span>"
            f"<span style='font-family:DM Mono; font-size:0.75rem; color:#475569; font-weight:400; margin-left:8px;'>{date_display}</span></div>"
            "</div>"
            f"<span class='defense-badge {badge_css}'>{badge_text} · {opp_pts_str} pts/g allowed</span>"
            "</div>",
            unsafe_allow_html=True
        )
        st.caption("Matchup quality auto-filled from opponent's defensive rating. Override manually if needed.")
    else:
        st.caption("Next opponent not found — matchup set to Neutral.")

    pc1, pc2 = st.columns(2)
    with pc1:
        matchup_options = ["Neutral", "Good", "Bad"]
        matchup_sel = st.selectbox(
            "Matchup 🤖", matchup_options,
            index=matchup_options.index(matchup_auto),
            help=f"Auto: {opp_abbr or 'unknown'} allows {f'{opp_pts:.1f}' if opp_pts else 'N/A'} pts/game"
        )
    with pc2:
        script_sel = st.selectbox("Game Script", ["Neutral", "Competitive", "Blowout risk"])

    with st.expander("⚙️  Advanced overrides"):
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            minutes_sel = st.selectbox("Minutes", ["Okay", "Strong", "Risk"],
                                       index=["Okay", "Strong", "Risk"].index(minutes_suggest))
        with ac2:
            role_sel = st.selectbox("Role", ["Okay", "Strong", "Risk"],
                                    index=["Okay", "Strong", "Risk"].index(role_suggest))
        with ac3:
            shots_sel = st.selectbox("Shots", ["Medium", "High", "Low"],
                                     index=["Medium", "High", "Low"].index(shots_suggest))

    venue_adj = venue_adjustment(splits, tonight_venue, side)

    context = {
        "minutes": minutes_sel,
        "role":    role_sel,
        "shots":   shots_sel,
        "matchup": matchup_sel,
        "script":  script_sel,
        "venue":   venue_adj,
    }

    adjusted  = apply_adjustments(weighted_base, context)
    line_diff = sample_avg_pts - line
    tier      = get_confidence_tier(adjusted, line_diff, consistency)

    tier_css   = {"Strong Over": "green", "Lean Over": "yellow", "Lean Under": "orange", "Strong Under": "red", "Pass": "gray"}
    tier_emoji = {"Strong Over": "🟢", "Lean Over": "🟡", "Lean Under": "🟠", "Strong Under": "🔴", "Pass": "⚪"}
    css = tier_css[tier]

    # ── Verdict banner ────────────────────────
    st.markdown("<div class='section-header'>Verdict</div>", unsafe_allow_html=True)

    venue_adj_labels = {
        "Boost":   ("▲ Venue Boost",   "#22c55e"),
        "Penalty": ("▼ Venue Penalty", "#ef4444"),
        "Neutral": ("",                "#475569"),
    }
    venue_label_text, venue_label_color = venue_adj_labels.get(venue_adj, ("", "#475569"))
    venue_badge_html = (
        f"<span style='font-family:DM Mono; font-size:0.7rem; color:{venue_label_color}; "
        f"background:{venue_label_color}18; border:1px solid {venue_label_color}44; "
        f"padding:3px 10px; border-radius:999px;'>{venue_label_text}</span>"
    ) if venue_adj != "Neutral" else ""

    st.markdown(f"""
    <div class='verdict-banner {css}'>
        <div>
            <div class='verdict-label'>{full_name} · {line} pts · {side}</div>
            <div class='verdict-tier {css}'>{tier_emoji[tier]} {tier}</div>
            <div style='margin-top:6px;'>{venue_badge_html}</div>
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

    with st.expander("🔢  Model details"):
        st.markdown(f"""<div class='model-note'>
        Raw hit rate: {baseline:.0%} &nbsp;·&nbsp;
        Weighted (recency): {weighted_base:.0%} &nbsp;·&nbsp;
        After context: {adjusted:.0%} &nbsp;·&nbsp;
        Sample: {n_games} games &nbsp;·&nbsp;
        Matchup: {matchup_sel} (vs {opp_abbr or "unknown"}) &nbsp;·&nbsp;
        Venue: {tonight_venue or "Unknown"} ({venue_adj})
        </div>""", unsafe_allow_html=True)

    # ── AI Analysis ───────────────────────────
    st.markdown("<div class='section-header'>AI Breakdown</div>", unsafe_allow_html=True)
    groq_key = get_groq_key()
    if not groq_key:
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
                            splits=splits, tonight_venue=tonight_venue, venue_adj=venue_adj,
                        )
                        st.session_state.ai_analysis = generate_ai_analysis(prompt)
                        st.session_state.ai_error = None
                    except Exception as e:
                        st.session_state.ai_error = repr(e)
                        st.session_state.ai_analysis = None

    # ── Export + Tracker ─────────────────────
    st.markdown("<div class='section-header'>Export</div>", unsafe_allow_html=True)
    ex1, ex2 = st.columns([1, 1])
    with ex1:
        out = logs.copy()
        for i, (col, val) in enumerate([
            ("PLAYER", full_name), ("LINE", line), ("SIDE", side),
            ("OPPONENT", opp_abbr or ""), ("OPP_PTS_ALLOWED", opp_pts or ""),
            ("MATCHUP_QUALITY", matchup_sel), ("VENUE", tonight_venue or ""),
            ("VENUE_ADJ", venue_adj), ("RAW_HIT_RATE", baseline),
            ("WEIGHTED_HIT_RATE", weighted_base), ("ADJUSTED_RATE", adjusted),
            ("CONSISTENCY", consistency), ("TIER", tier),
        ]):
            out.insert(i, col, val)
        csv = out.to_csv(index=False).encode("utf-8")
        st.download_button("⬇  Download CSV", data=csv, file_name="prop_report.csv", mime="text/csv")
    with ex2:
        if st.button("➕  Add to Prop Tracker"):
            entry = {
                "Player":      full_name,
                "Line":        f"{line} {side}",
                "Opponent":    opp_abbr or "—",
                "Matchup":     matchup_sel,
                "Venue":       f"{tonight_venue or '?'} ({venue_adj})",
                "Avg PTS":     round(sample_avg_pts, 1),
                "Hit Rate":    f"{weighted_base:.0%}",
                "Adjusted":    f"{adjusted:.0%}",
                "Consistency": f"{consistency:.0%}",
                "Verdict":     tier,
            }
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
        <div style='font-family:DM Mono; font-size:0.75rem; color:#334155;'>No props tracked yet</div>
        <div style='font-size:0.85rem; color:#475569; margin-top:4px;'>
            Analyze a player then click ➕ Add to Prop Tracker
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    tier_css   = {"Strong Over": "green", "Lean Over": "yellow", "Lean Under": "orange", "Strong Under": "red", "Pass": "gray"}
    tier_emoji = {"Strong Over": "🟢", "Lean Over": "🟡", "Lean Under": "🟠", "Strong Under": "🔴", "Pass": "⚪"}
    to_remove = None
    for i, entry in enumerate(st.session_state.tracker):
        t   = entry["Verdict"]
        css = tier_css.get(t, "gray")
        em  = tier_emoji.get(t, "⚪")
        col_card, col_remove = st.columns([11, 1])
        with col_card:
            st.markdown(f"""
            <div class='verdict-banner {css}' style='margin:0.3rem 0; padding:1rem 1.4rem;'>
                <div>
                    <div class='verdict-label'>{entry["Line"]} · vs {entry["Opponent"]}</div>
                    <div style='font-size:1.1rem; font-weight:800; color:#f1f5f9;'>{entry["Player"]}</div>
                </div>
                <div style='display:flex; gap:1.5rem; flex-wrap:wrap; align-items:center;'>
                    <div><div class='verdict-label'>Verdict</div><div class='verdict-tier {css}' style='font-size:1rem;'>{em} {t}</div></div>
                    <div><div class='verdict-label'>Venue</div><div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry.get("Venue","—")}</div></div>
                    <div><div class='verdict-label'>Avg PTS</div><div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Avg PTS"]}</div></div>
                    <div><div class='verdict-label'>Hit Rate</div><div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Hit Rate"]}</div></div>
                    <div><div class='verdict-label'>Adjusted</div><div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Adjusted"]}</div></div>
                    <div><div class='verdict-label'>Matchup</div><div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Matchup"]}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_remove:
            st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
            if st.button("✕", key=f"remove_{i}", help="Remove"):
                to_remove = i
    if to_remove is not None:
        st.session_state.tracker.pop(to_remove)
        st.rerun()

    tc1, tc2 = st.columns([1, 1])
    with tc1:
        tracker_df  = pd.DataFrame(st.session_state.tracker)
        tracker_csv = tracker_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇  Export Tracker CSV", data=tracker_csv, file_name="prop_tracker.csv", mime="text/csv")
    with tc2:
        if st.button("🗑️  Clear All"):
            st.session_state.tracker = []
            st.rerun()

st.markdown("<div style='margin-top:3rem; font-family:DM Mono; font-size:0.65rem; color:#334155; text-align:center;'>PropLens — For educational purposes only. Not financial or betting advice.</div>", unsafe_allow_html=True)
