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

:root {
    --bg:       #07090f;
    --bg2:      #0c1018;
    --bg3:      #111827;
    --border:   #1a2333;
    --border2:  #243044;
    --orange:   #f97316;
    --orange2:  #fb923c;
    --green:    #22c55e;
    --red:      #ef4444;
    --yellow:   #eab308;
    --blue:     #60a5fa;
    --muted:    #475569;
    --muted2:   #64748b;
    --text:     #e2e8f0;
    --text2:    #94a3b8;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 4rem; max-width: 1180px; }

/* ── Logo ── */
.pl-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.2rem 1.8rem; margin-bottom: 1.5rem;
    background: linear-gradient(135deg, #0c1018 0%, #0f1623 100%);
    border: 1px solid var(--border2); border-radius: 18px;
    box-shadow: 0 4px 24px rgba(249,115,22,0.06);
}
.pl-logo-wrap { display: flex; align-items: center; gap: 14px; }
.pl-icon {
    width: 44px; height: 44px; border-radius: 12px;
    background: linear-gradient(135deg, #ea580c, #f97316);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; box-shadow: 0 2px 12px rgba(249,115,22,0.35);
    flex-shrink: 0;
}
.pl-logo {
    font-size: 2rem; font-weight: 800; letter-spacing: -1.5px;
    background: linear-gradient(135deg, #f97316 0%, #fb923c 60%, #fdba74 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1;
}
.pl-sub {
    font-family: 'DM Mono', monospace; font-size: 0.65rem; color: var(--muted2);
    letter-spacing: 0.18em; text-transform: uppercase; margin-top: 3px;
}
.pl-badge {
    font-family: 'DM Mono', monospace; font-size: 0.65rem;
    background: rgba(249,115,22,0.12); color: var(--orange);
    border: 1px solid rgba(249,115,22,0.25); padding: 4px 12px;
    border-radius: 999px; letter-spacing: 0.08em;
}

/* ── Cards ── */
.stat-card {
    background: linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 1.1rem 1.3rem; margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.stat-card:hover { border-color: var(--border2); }

.stat-label {
    font-family: 'DM Mono', monospace; font-size: 0.63rem; color: var(--muted);
    letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 4px;
    display: flex; align-items: center; gap: 5px;
}
.stat-label .tip {
    display: inline-flex; align-items: center; justify-content: center;
    width: 13px; height: 13px; border-radius: 50%;
    background: var(--border2); color: var(--muted2);
    font-size: 0.55rem; font-weight: 700; cursor: default;
    flex-shrink: 0;
}
.stat-value { font-size: 1.8rem; font-weight: 800; color: var(--text); letter-spacing: -1px; line-height: 1.1; }
.stat-value.orange { color: var(--orange); }
.stat-value.green  { color: var(--green); }
.stat-value.red    { color: var(--red); }
.stat-value.yellow { color: var(--yellow); }
.stat-hint { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: var(--muted); margin-top: 5px; line-height: 1.5; }

/* ── Defense card ── */
.defense-card {
    background: linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%);
    border: 1px solid var(--border); border-radius: 14px;
    padding: 1rem 1.3rem; margin-bottom: 0.75rem;
    display: flex; align-items: center; justify-content: space-between;
}
.defense-badge {
    font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 500;
    padding: 4px 12px; border-radius: 999px; letter-spacing: 0.05em;
}
.defense-badge.good    { background: #052e16; color: var(--green);  border: 1px solid #166534; }
.defense-badge.neutral { background: var(--bg2); color: var(--text2); border: 1px solid var(--border); }
.defense-badge.bad     { background: #1c0505; color: var(--red);    border: 1px solid #991b1b; }

/* ── Verdict ── */
.verdict-banner {
    border-radius: 18px; padding: 1.6rem 2rem; margin: 1.5rem 0;
    border: 1px solid var(--border); display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 1rem;
    box-shadow: 0 4px 32px rgba(0,0,0,0.3);
}
.verdict-banner.green  { background: linear-gradient(135deg, #041f10 0%, #0a2018 100%); border-color: #166534; box-shadow: 0 4px 32px rgba(34,197,94,0.08); }
.verdict-banner.yellow { background: linear-gradient(135deg, #151200 0%, #1f1a00 100%); border-color: #854d0e; box-shadow: 0 4px 32px rgba(234,179,8,0.08); }
.verdict-banner.orange { background: linear-gradient(135deg, #160800 0%, #1f1000 100%); border-color: #9a3412; box-shadow: 0 4px 32px rgba(249,115,22,0.08); }
.verdict-banner.red    { background: linear-gradient(135deg, #140000 0%, #1f0505 100%); border-color: #991b1b; box-shadow: 0 4px 32px rgba(239,68,68,0.08); }
.verdict-banner.gray   { background: linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%); border-color: var(--border); }

.verdict-label { font-size: 0.63rem; font-family: 'DM Mono', monospace; letter-spacing: 0.15em; text-transform: uppercase; color: var(--muted); margin-bottom: 4px; }
.verdict-tier  { font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; }
.verdict-tier.green  { color: var(--green); }
.verdict-tier.yellow { color: var(--yellow); }
.verdict-tier.orange { color: var(--orange); }
.verdict-tier.red    { color: var(--red); }
.verdict-tier.gray   { color: var(--muted); }

/* ── Section headers ── */
.section-header {
    font-size: 0.62rem; font-family: 'DM Mono', monospace; letter-spacing: 0.22em;
    text-transform: uppercase; color: var(--orange); margin: 2rem 0 0.8rem 0;
    padding-bottom: 7px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 8px;
}
.section-header::before {
    content: ''; display: inline-block; width: 3px; height: 12px;
    background: var(--orange); border-radius: 2px;
}

/* ── AI box ── */
.ai-box {
    background: linear-gradient(135deg, #080e1c 0%, #0b1220 100%);
    border: 1px solid #1a3050; border-radius: 14px; padding: 1.6rem;
    margin-top: 1rem; font-size: 0.95rem; line-height: 1.8; color: #c8d5e8;
}

/* ── Model note ── */
.model-note {
    background: var(--bg2); border: 1px solid var(--border); border-radius: 10px;
    padding: 0.8rem 1.1rem; margin-top: 0.5rem;
    font-family: 'DM Mono', monospace; font-size: 0.68rem; color: var(--muted); line-height: 1.7;
}

/* ── Pills ── */
.flag-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 0.6rem; }
.flag-pill {
    font-family: 'DM Mono', monospace; font-size: 0.68rem;
    padding: 4px 11px; border-radius: 999px; letter-spacing: 0.05em;
}
.flag-pill.up     { background: #052e16; color: var(--green);  border: 1px solid #166534; }
.flag-pill.down   { background: #1c0505; color: var(--red);    border: 1px solid #991b1b; }
.flag-pill.flat   { background: var(--bg2); color: var(--text2); border: 1px solid var(--border); }
.flag-pill.nodata { background: var(--bg2); color: var(--muted); border: 1px solid var(--border); }

/* ── Explainer box ── */
.explainer {
    background: linear-gradient(135deg, #0c1018 0%, #0f1420 100%);
    border: 1px solid var(--border); border-left: 3px solid var(--orange);
    border-radius: 0 10px 10px 0; padding: 0.75rem 1rem;
    margin-bottom: 1rem; font-size: 0.82rem; color: var(--text2); line-height: 1.6;
}
.explainer strong { color: var(--text); }

/* ── How it works panel ── */
.how-it-works {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 14px; padding: 1.2rem 1.4rem; margin-bottom: 1.5rem;
}
.how-step {
    display: flex; gap: 12px; align-items: flex-start; margin-bottom: 0.9rem;
}
.how-step:last-child { margin-bottom: 0; }
.how-num {
    min-width: 24px; height: 24px; border-radius: 50%;
    background: linear-gradient(135deg, #ea580c, #f97316);
    color: white; font-size: 0.7rem; font-weight: 800;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.how-text { font-size: 0.82rem; color: var(--text2); line-height: 1.5; }
.how-text strong { color: var(--text); }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #ea580c, #f97316) !important;
    color: white !important; border: none !important; border-radius: 9px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    letter-spacing: 0.03em !important; padding: 0.55rem 1.6rem !important;
    transition: all 0.2s !important; box-shadow: 0 2px 12px rgba(249,115,22,0.25) !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(249,115,22,0.35) !important; }

hr { border-color: var(--border) !important; }

/* ── Player search suggestion buttons ── */
button[data-testid="baseButton-secondary"] {
    background: #0c1018 !important;
    color: #94a3b8 !important;
    border: 1px solid #1a2333 !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    text-align: left !important;
    padding: 0.4rem 0.8rem !important;
    box-shadow: none !important;
    transition: background 0.15s !important;
    margin-bottom: 2px !important;
}
button[data-testid="baseButton-secondary"]:hover {
    background: #1a2333 !important;
    color: #f1f5f9 !important;
    border-color: #243044 !important;
    transform: none !important;
    box-shadow: none !important;
}
/* ── Clear ✕ button — small and red on hover ── */
button[key="clear_player_x"],
button[data-testid="baseButton-secondary"][title="Clear player"] {
    background: transparent !important;
    color: #475569 !important;
    border: 1px solid #1a2333 !important;
    border-radius: 6px !important;
    padding: 0.2rem 0.5rem !important;
    font-size: 0.75rem !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] {
    background: #080d15 !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Streamlit overrides ── */
.stSelectbox label, .stTextInput label, .stNumberInput label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important; color: var(--muted) !important;
    text-transform: uppercase; letter-spacing: 0.1em;
}
div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important; background: var(--bg2) !important;
}
div[data-testid="stExpander"] p,
div[data-testid="stExpander"] li,
div[data-testid="stExpander"] span,
div[data-testid="stExpander"] label,
div[data-testid="stExpander"] div {
    color: #94a3b8 !important;
}
div[data-testid="stExpander"] summary {
    color: #94a3b8 !important;
}
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
# ─────────────────────────────────────────────
# Data layer — ESPN (schedule) + nba_api (game logs)
# ESPN for schedule: fast, reliable, no key needed
# nba_api for game logs: direct player stats, well-structured
# ─────────────────────────────────────────────

from nba_api.stats.static import players as nba_players
from nba_api.stats.endpoints import playergamelog, commonplayerinfo

ESPN_SITE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"

ESPN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def espn_get(url: str, params: dict = None, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=ESPN_HEADERS, params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}

def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

# ── Player search — load all rosters from ESPN teams ──────────────

# All 30 NBA team IDs on ESPN (stable, never changes)
NBA_TEAM_IDS = [
    1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
    16,17,18,19,20,21,22,23,24,25,26,27,28,29,30
]

@st.cache_data(ttl=3600)
def espn_get_all_players() -> List[dict]:
    """
    Load all active NBA players by fetching each team roster from ESPN.
    Returns list of {id, full_name, team_abbr}.
    ESPN team roster endpoint is fast and always works.
    """
    all_players = []
    for team_id in NBA_TEAM_IDS:
        try:
            url  = f"{ESPN_SITE}/teams/{team_id}/roster"
            data = espn_get(url)
            team_abbr = data.get("team", {}).get("abbreviation", "")
            for athlete in data.get("athletes", []):
                for item in (athlete.get("items") or [athlete]):
                    pid  = str(item.get("id", ""))
                    name = item.get("displayName") or item.get("fullName") or ""
                    if pid and name:
                        all_players.append({
                            "id":         pid,
                            "full_name":  name,
                            "team_abbr":  team_abbr,
                        })
        except Exception:
            continue
    return all_players

def espn_search_players(query: str) -> List[dict]:
    """Search loaded player list by name query."""
    query_norm = normalize_name(query)
    all_players = espn_get_all_players()
    matches = [
        p for p in all_players
        if query_norm in normalize_name(p["full_name"])
    ]
    return sorted(matches, key=lambda x: x["full_name"].split()[-1])

def find_player(player_name: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Returns (espn_player_id, full_name, team_abbreviation)."""
    name_norm = normalize_name(player_name)
    all_players = espn_get_all_players()
    # exact match first
    for p in all_players:
        if normalize_name(p["full_name"]) == name_norm:
            return p["id"], p["full_name"], p["team_abbr"]
    # partial match
    candidates = [p for p in all_players if name_norm in normalize_name(p["full_name"])]
    if len(candidates) == 1:
        return candidates[0]["id"], candidates[0]["full_name"], candidates[0]["team_abbr"]
    if candidates:
        return candidates[0]["id"], candidates[0]["full_name"], candidates[0]["team_abbr"]
    return None, None, None

# ── nba_api: player lookup + game logs ───────────────────────────

def normalize_name(s: str) -> str:
    import unicodedata
    # Strip accents so "Doncic" matches "Dončić", "Jokic" matches "Jokić" etc.
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s.strip().lower())

@st.cache_data(ttl=86400)
def nba_find_player(player_name: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Find player ID from nba_api static list.
    Tries multiple matching strategies to handle:
    - Accented chars: Doncic -> Dončić
    - Name order variants
    - Partial last name matches
    """
    name = normalize_name(player_name)
    all_p = nba_players.get_players()

    # 1. Exact normalized match
    for p in all_p:
        if normalize_name(p["full_name"]) == name:
            return p["id"], p["full_name"]

    # 2. Partial match — query contained in full name
    candidates = [p for p in all_p if name in normalize_name(p["full_name"])]
    if len(candidates) == 1:
        return candidates[0]["id"], candidates[0]["full_name"]
    if candidates:
        # prefer active players
        active = [p for p in candidates if p.get("is_active", True)]
        if active:
            return active[0]["id"], active[0]["full_name"]
        return candidates[0]["id"], candidates[0]["full_name"]

    # 3. Last name only match (e.g. "doncic" in "luka doncic")
    parts = name.split()
    if len(parts) >= 2:
        last = parts[-1]
        first = parts[0]
        last_matches = [
            p for p in all_p
            if last in normalize_name(p["full_name"])
            and first in normalize_name(p["full_name"])
        ]
        if last_matches:
            active = [p for p in last_matches if p.get("is_active", True)]
            best = active if active else last_matches
            return best[0]["id"], best[0]["full_name"]

    # 4. Last name only (single strong signal)
    if len(parts) >= 1:
        last = parts[-1]
        if len(last) >= 5:  # avoid short names matching too broadly
            last_only = [p for p in all_p if normalize_name(p["full_name"]).endswith(last)]
            if len(last_only) == 1:
                return last_only[0]["id"], last_only[0]["full_name"]

    return None, None

@st.cache_data(ttl=600)
def nba_get_game_logs(player_id: int, season: str, n: int = 10) -> pd.DataFrame:
    """
    Fetch last N game logs using nba_api playergamelog.
    Uses browser-like headers to avoid timeouts on Streamlit Cloud.
    season: e.g. "2025-26"
    """
    empty = pd.DataFrame(columns=["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A"])
    try:
        from nba_api.library.http import NBAStatsHTTP
        NBAStatsHTTP.nba_response.headers = {
            "Host": "stats.nba.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "x-nba-stats-origin": "stats",
            "x-nba-stats-token": "true",
            "Referer": "https://www.nba.com/",
            "Origin": "https://www.nba.com",
            "Connection": "keep-alive",
        }
    except Exception:
        pass

    for attempt in range(4):
        try:
            df = playergamelog.PlayerGameLog(
                player_id=player_id, season=season, timeout=45,
            ).get_data_frames()[0]
            df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
            df = df.sort_values("GAME_DATE", ascending=False).head(n).copy()
            for c in ["MATCHUP","MIN","PTS","FGA","FTA","FG3A"]:
                if c not in df.columns:
                    df[c] = None
            return df[["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A"]]
        except Exception as e:
            if attempt < 3:
                time.sleep(3 * (attempt + 1))
            else:
                raise
    return empty

@st.cache_data(ttl=600)
def nba_get_player_team(player_id: int) -> Optional[str]:
    """Get player current team abbreviation."""
    try:
        from nba_api.library.http import NBAStatsHTTP
        NBAStatsHTTP.nba_response.headers = {
            "Host": "stats.nba.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "x-nba-stats-origin": "stats",
            "x-nba-stats-token": "true",
            "Referer": "https://www.nba.com/",
            "Origin": "https://www.nba.com",
        }
    except Exception:
        pass
    try:
        info = commonplayerinfo.CommonPlayerInfo(player_id=player_id, timeout=45).get_data_frames()[0]
        return info["TEAM_ABBREVIATION"].iloc[0] if not info.empty else None
    except Exception:
        return None

def season_str_to_season(season_str: str) -> str:
    """Return season string as-is for nba_api e.g. '2025-26'."""
    return season_str.strip()

# ── H2H vs opponent ───────────────────────────

@st.cache_data(ttl=3600)
def get_h2h_logs(player_id: int, opp_abbr: str, season: str) -> pd.DataFrame:
    """
    Fetch full season logs and filter for games vs opp_abbr.
    Returns DataFrame with same columns as nba_get_game_logs.
    Looks at current + prior season for enough sample.
    """
    empty = pd.DataFrame(columns=["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A"])
    if not opp_abbr:
        return empty

    try:
        from nba_api.library.http import NBAStatsHTTP
        NBAStatsHTTP.nba_response.headers = {
            "Host": "stats.nba.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "x-nba-stats-origin": "stats",
            "x-nba-stats-token": "true",
            "Referer": "https://www.nba.com/",
            "Origin": "https://www.nba.com",
            "Connection": "keep-alive",
        }
    except Exception:
        pass

    all_rows = []
    # Check current + 2 prior seasons for enough H2H games
    try:
        start_year = int(season.split("-")[0])
    except Exception:
        start_year = 2025

    for yr in [start_year, start_year - 1, start_year - 2]:
        try:
            season_str = f"{yr}-{str(yr+1)[-2:]}"
            df = playergamelog.PlayerGameLog(
                player_id=player_id, season=season_str, timeout=45,
            ).get_data_frames()[0]
            df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
            for c in ["MATCHUP","MIN","PTS","FGA","FTA","FG3A"]:
                if c not in df.columns:
                    df[c] = None
            # Filter to games vs this opponent
            mask = df["MATCHUP"].astype(str).str.contains(opp_abbr, na=False)
            all_rows.append(df[mask][["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A"]])
        except Exception:
            time.sleep(2)
            continue

    if not all_rows:
        return empty

    combined = pd.concat(all_rows).sort_values("GAME_DATE", ascending=False).reset_index(drop=True)
    return combined


def h2h_signal(h2h_df: pd.DataFrame, line: float, side: str) -> Tuple[str, Optional[float], int]:
    """
    Returns (signal, avg_pts, games_count).
    signal: 'Strong', 'Okay', or 'Risk'
    """
    if h2h_df is None or h2h_df.empty:
        return "Neutral", None, 0

    pts = pd.to_numeric(h2h_df["PTS"], errors="coerce").dropna()
    if len(pts) < 2:
        return "Neutral", None, len(pts)

    avg = float(pts.mean())
    hit = float((pts >= line).sum() / len(pts)) if side == "Over" else float((pts <= line).sum() / len(pts))

    if hit >= 0.65 and avg > line:
        return "Strong", avg, len(pts)
    if hit <= 0.35 or avg < line - 3:
        return "Risk", avg, len(pts)
    return "Neutral", avg, len(pts)


# ── Back-to-back detection ────────────────────

def detect_b2b(logs: pd.DataFrame, game_date: Optional[str]) -> str:
    """
    Returns 'B2B' if tonight's game is the day after a logged game, else 'Normal'.
    Uses game_date (next game date string) + logs to check.
    """
    if game_date is None or logs is None or logs.empty:
        return "Normal"

    try:
        tonight = pd.to_datetime(game_date)
        log_dates = pd.to_datetime(logs["GAME_DATE"], errors="coerce").dropna()
        # Check if any logged game was yesterday
        yesterday = tonight - pd.Timedelta(days=1)
        if any(abs((d - yesterday).days) == 0 for d in log_dates):
            return "B2B"
        return "Normal"
    except Exception:
        return "Normal"

def season_str_to_int(season_str: str) -> int:
    """Convert '2025-26' -> 2025 for ESPN year param."""
    try:
        return int(season_str.split("-")[0])
    except Exception:
        return 2025

# ── Season average fetch + divergence signal ─────────────────────

@st.cache_data(ttl=3600)
def nba_get_season_avg(player_id: int, season: str) -> Optional[float]:
    """
    Fetch full season game log and return season avg pts.
    Different from the L5/L10 sample — this is the full-season baseline.
    """
    try:
        from nba_api.library.http import NBAStatsHTTP
        NBAStatsHTTP.nba_response.headers = {
            "Host": "stats.nba.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "x-nba-stats-origin": "stats",
            "x-nba-stats-token": "true",
            "Referer": "https://www.nba.com/",
            "Origin": "https://www.nba.com",
            "Connection": "keep-alive",
        }
    except Exception:
        pass
    for attempt in range(3):
        try:
            df = playergamelog.PlayerGameLog(
                player_id=player_id, season=season, timeout=45,
            ).get_data_frames()[0]
            pts = pd.to_numeric(df["PTS"], errors="coerce").dropna()
            return round(float(pts.mean()), 1) if len(pts) >= 5 else None
        except Exception:
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
    return None


def form_divergence_signal(
    recent_avg: float,
    season_avg: Optional[float],
    line: float,
    side: str,
) -> Tuple[str, Optional[float]]:
    """
    Compare L5/L10 average to season average.
    Returns (signal, divergence_pts) where:
      'Hot'    — recent avg is 3+ pts above season avg (riding a hot streak)
      'Cold'   — recent avg is 3+ pts below season avg (in a slump)
      'Neutral' — within 3 pts either way
    The signal then interacts with the line direction:
      Hot + Over  = boost | Hot + Under = slight penalty
      Cold + Under = boost | Cold + Over = penalty
    We encode this as a single verdict-ready key.
    """
    if season_avg is None or season_avg == 0:
        return "Neutral", None

    diff = recent_avg - season_avg  # positive = running hot, negative = running cold

    if diff >= 3.0:
        streak = "Hot"
    elif diff <= -3.0:
        streak = "Cold"
    else:
        return "Neutral", round(diff, 1)

    # Align streak direction with bet side for final signal
    if streak == "Hot" and side == "Over":
        return "Boost", round(diff, 1)
    if streak == "Hot" and side == "Under":
        return "Penalty", round(diff, 1)
    if streak == "Cold" and side == "Under":
        return "Boost", round(diff, 1)
    if streak == "Cold" and side == "Over":
        return "Penalty", round(diff, 1)
    return "Neutral", round(diff, 1)


# ── Next game / schedule ──────────────────────

@st.cache_data(ttl=300)
def espn_get_next_game(team_abbr: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Find next upcoming game for a team using ESPN scoreboard.
    Returns (opp_abbr, game_date_str, venue).
    Skips completed games.
    """
    if not team_abbr:
        return None, None, None

    try:
        import pytz
        et    = pytz.timezone("America/New_York")
        today = datetime.now(et).date()
    except Exception:
        today = datetime.today().date()

    for offset in range(10):
        check    = today + timedelta(days=offset)
        date_str = check.strftime("%Y%m%d")
        try:
            data   = espn_get(f"{ESPN_SITE}/scoreboard", params={"dates": date_str})
            events = data.get("events", [])
            for ev in events:
                comps = ev.get("competitions", [{}])[0]
                competitors = comps.get("competitors", [])
                teams_in_game = {c.get("team", {}).get("abbreviation", ""): c for c in competitors}

                if team_abbr not in teams_in_game:
                    continue

                # Skip if final
                status = ev.get("status", {}).get("type", {}).get("name", "")
                if "final" in status.lower() or "complete" in status.lower():
                    continue

                # Find opponent
                opp = next((c for abbr, c in teams_in_game.items() if abbr != team_abbr), None)
                if not opp:
                    continue
                opp_abbr_found = opp.get("team", {}).get("abbreviation", "")

                # Home or away
                my_side   = teams_in_game[team_abbr]
                home_away = "Home" if my_side.get("homeAway", "") == "home" else "Away"
                game_date_str = check.strftime("%b %d, %Y")

                return opp_abbr_found, game_date_str, home_away
        except Exception:
            continue

    return None, None, None

# ── Opponent defense rating ───────────────────

@st.cache_data(ttl=3600)
def espn_get_opp_pts_allowed(opp_abbr: str) -> Optional[float]:
    """
    Calculate pts allowed per game by averaging opponent scores
    from the team's last 15 completed games via ESPN scoreboard.
    ESPN's team stats endpoint doesn't include pts allowed directly.
    """
    try:
        import pytz
        et    = pytz.timezone("America/New_York")
        today = datetime.now(et).date()
    except Exception:
        today = datetime.today().date()

    try:
        pts_allowed_list = []
        # Look back up to 30 days to find 15 completed games
        for offset in range(1, 35):
            if len(pts_allowed_list) >= 15:
                break
            check    = today - timedelta(days=offset)
            date_str = check.strftime("%Y%m%d")
            try:
                data   = espn_get(f"{ESPN_SITE}/scoreboard", params={"dates": date_str})
                events = data.get("events", [])
                for ev in events:
                    comp        = ev.get("competitions", [{}])[0]
                    competitors = comp.get("competitors", [])
                    # Find this team
                    team_comp = next(
                        (c for c in competitors
                         if c.get("team", {}).get("abbreviation", "") == opp_abbr),
                        None
                    )
                    if not team_comp:
                        continue
                    # Only completed games
                    status = ev.get("status", {}).get("type", {}).get("name", "")
                    if "final" not in status.lower() and "complete" not in status.lower():
                        continue
                    # Opponent score = the other team's score
                    opp_comp = next(
                        (c for c in competitors
                         if c.get("team", {}).get("abbreviation", "") != opp_abbr),
                        None
                    )
                    if opp_comp:
                        score = opp_comp.get("score", "")
                        try:
                            pts_allowed_list.append(float(score))
                        except Exception:
                            continue
            except Exception:
                continue

        if len(pts_allowed_list) >= 5:
            return round(sum(pts_allowed_list) / len(pts_allowed_list), 1)
        return None
    except Exception:
        return None

def classify_matchup_espn(opp_abbr: Optional[str]) -> Tuple[str, Optional[float], str]:
    """Classify opponent defense quality using ESPN team stats."""
    league_avg = 114.5
    if not opp_abbr:
        return "Neutral", None, str(league_avg)

    opp_pts = espn_get_opp_pts_allowed(opp_abbr)

    if opp_pts is None:
        return "Neutral", None, str(league_avg)

    diff = opp_pts - league_avg
    if diff >= 1.5:
        return "Good", opp_pts, str(league_avg)
    if diff <= -1.5:
        return "Bad", opp_pts, str(league_avg)
    return "Neutral", opp_pts, str(league_avg)

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
    """
    % of games where pts landed within 3 of the line.
    NOTE: this measures clustering around the line, not reliability.
    A player averaging 38 on a 24.5 line will score near 0% here
    not because they're volatile, but because they always blow past it.
    Use line_diff alongside this to interpret correctly.
    """
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
    """
    Apply context multipliers as additive boosts/penalties in percentage points.

    Using additive adjustments (not multiplicative on the margin) ensures that
    positive signals always push probability UP and negative signals always push
    DOWN — regardless of whether the starting probability is above or below 50%.

    Each multiplier value is converted to a pp adjustment:
      1.08 → +8pp boost toward the bet side  (always helps)
      0.91 → -9pp penalty away from bet side  (always hurts)
      1.00 → no change
    """
    # Convert multipliers to flat pp adjustments
    # Positive = helps the bet (pushes probability toward the over/under hitting)
    # Negative = hurts the bet
    adj_map = {
        "minutes":  {"Strong": +0.05, "Okay": 0.00, "Risk": -0.07},
        "role":     {"Strong": +0.04, "Okay": 0.00, "Risk": -0.05},
        "shots":    {"High":   +0.03, "Medium": 0.00, "Low": -0.06},
        "matchup":  {"Good":   +0.06, "Neutral": 0.00, "Bad": -0.06},
        "script":   {"Competitive": +0.02, "Neutral": 0.00, "Blowout risk": -0.04},
        "venue":    {"Boost": +0.04, "Neutral": 0.00, "Penalty": -0.05},
        "h2h":      {"Strong": +0.05, "Neutral": 0.00, "Risk": -0.06},
        "b2b":      {"Normal": 0.00, "B2B": -0.06},
        "form":     {"Boost": +0.05, "Neutral": 0.00, "Penalty": -0.05},
    }
    adjusted = weighted
    for key, val in context.items():
        adjusted += adj_map[key].get(val, 0.0)
    adjusted = max(0.0, min(1.0, adjusted))

    # Hard cap: context cannot override what the raw data says.
    # Rule: context can move probability by at most 12pp in total.
    # This prevents a player with 52% hit rate from reaching 67% just from signals.
    max_shift = 0.12
    if adjusted > weighted + max_shift:
        adjusted = weighted + max_shift
    if adjusted < weighted - max_shift:
        adjusted = weighted - max_shift

    return max(0.0, min(1.0, adjusted))

def get_confidence_tier(adjusted: float, line_diff: float, consistency: float) -> str:
    """
    Assign confidence tier based on adjusted hit rate + edge vs line.

    Consistency override logic:
    - Only fires when edge is SMALL (abs < 5 pts).
    - When edge is large (e.g. +14 pts), low consistency just means the player
      consistently scores FAR above the line — which is a positive signal, not
      a risk. So we skip the downgrade in those cases.
    """
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

    # Only apply consistency downgrade when edge is tight (within 5 pts of line)
    # Large edges with low consistency = player consistently blows past the line
    edge_is_tight = abs(line_diff) < 5.0
    low_consistency = consistency < 0.35 and edge_is_tight

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
- H2H vs {opp_abbr}: {h2h_sig} signal — {h2h_count} games, avg {f"{h2h_avg:.1f}" if h2h_avg else "N/A"} pts
- Schedule: {b2b_status}{"  — FATIGUE RISK, second night of back-to-back" if b2b_status == "B2B" else ""}
- Form: recent avg {sample_avg_pts:.1f} vs season avg {f"{season_avg:.1f}" if season_avg else "N/A"} ({f"{form_diff:+.1f} pts divergence" if form_diff else "N/A"}) — {form_sig} signal for {side}

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
<div class="pl-header">
    <div class="pl-logo-wrap">
        <div class="pl-icon">🏀</div>
        <div>
            <div class="pl-logo">PropLens</div>
            <div class="pl-sub">NBA Points Prop Analyzer</div>
        </div>
    </div>
    <div style="display:flex; align-items:center; gap:10px;">
        <span class="pl-badge">v2.0 · 2025-26</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1rem 0;'>
        <div style='font-size:1.1rem; font-weight:800; color:#f97316; letter-spacing:-0.5px; margin-bottom:2px;'>🏀 PropLens</div>
        <div style='font-family:DM Mono; font-size:0.62rem; color:#475569; letter-spacing:0.15em; text-transform:uppercase;'>NBA Prop Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>How It Works</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='how-it-works'>
        <div class='how-step'>
            <div class='how-num'>1</div>
            <div class='how-text'><strong>Game Logs</strong> — fetches your last 5–15 games from NBA.com</div>
        </div>
        <div class='how-step'>
            <div class='how-num'>2</div>
            <div class='how-text'><strong>Hit Rate</strong> — calculates raw + recency-weighted % over/under the line</div>
        </div>
        <div class='how-step'>
            <div class='how-num'>3</div>
            <div class='how-text'><strong>Signals</strong> — applies 8 context multipliers: matchup, venue, H2H, rest, form, role, minutes, shots</div>
        </div>
        <div class='how-step'>
            <div class='how-num'>4</div>
            <div class='how-text'><strong>Verdict</strong> — outputs a confidence tier from Strong Over to Strong Under</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Verdict Guide</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:DM Mono; font-size:0.72rem; line-height:2; color:#94a3b8;'>
        🟢 <span style='color:#22c55e;'>Strong Over/Under</span> — High confidence<br>
        🟡 <span style='color:#eab308;'>Lean Over</span> — Moderate edge<br>
        🟠 <span style='color:#f97316;'>Lean Under</span> — Moderate edge<br>
        🔴 <span style='color:#ef4444;'>Strong Under</span> — High confidence<br>
        ⚪ <span style='color:#64748b;'>Pass</span> — No clear edge
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Settings</div>", unsafe_allow_html=True)
    manual_mode = st.checkbox("Manual input fallback", help="Enter points manually if NBA API is unavailable")
    if st.button("🔄 Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")

    st.markdown("""
    <div style='margin-top:2rem; padding:0.75rem; background:#0c1018; border:1px solid #1a2333;
                border-radius:8px; font-family:DM Mono; font-size:0.62rem; color:#334155; line-height:1.7;'>
        ⚠️ For educational purposes only.<br>Not financial or betting advice.<br>
        Always bet responsibly.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Mode selector
# ─────────────────────────────────────────────

for _k in ["scanner_results", "scanner_error"]:
    if _k not in st.session_state:
        st.session_state[_k] = None

_mode = st.radio(
    "mode", ["🏀  Player Prop", "🎯  Slate Scanner"],
    horizontal=True, label_visibility="collapsed", key="app_mode"
)
st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Slate Scanner
# ─────────────────────────────────────────────

if _mode == "🎯  Slate Scanner":
    st.markdown("<div class='section-header'>PrizePicks NBA — Today's Slate</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='explainer'>
        Fetches today's NBA points props from PrizePicks and runs every player through the PropLens model.
        Surfaces <strong>Strong Over</strong> and <strong>Strong Under</strong> results ranked by confidence.
        Takes 2–4 minutes. Results are cached for 5 minutes.
    </div>
    """, unsafe_allow_html=True)

    _sc1, _sc2, _sc3, _sc4 = st.columns([1, 1, 1, 1])
    with _sc1:
        _run = st.button("🔍  Scan Slate", key="run_scanner")
    with _sc2:
        _day_sel = st.selectbox(
            "Day", ["Today", "Tomorrow"],
            key="scanner_day", label_visibility="collapsed"
        )
    with _sc3:
        _batch = st.selectbox(
            "Players", [20, 40, "All"],
            key="scanner_batch", label_visibility="collapsed",
            help="How many props to analyze. Fewer = faster."
        )
    with _sc4:
        _filter = st.selectbox(
            "Show", ["Strong Only", "Strong + Lean", "All results"],
            key="scanner_filter", label_visibility="collapsed"
        )

    if _run:
        st.session_state.scanner_results = None
        st.session_state.scanner_error   = None
        with st.spinner(f"Fetching PrizePicks slate for {_day_sel}..."):
            try:
                import pytz as _pytz
                _et      = _pytz.timezone("America/New_York")
                _today   = datetime.now(_et).date()
                _tgt     = _today + timedelta(days=1) if _day_sel == "Tomorrow" else _today
                _tgt_str = _tgt.strftime("%Y-%m-%d")
                _r = requests.get(
                    "https://api.prizepicks.com/projections",
                    params={"league_id": 7, "per_page": 250, "single_stat": "true",
                            "game_date": _tgt_str},
                    headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json",
                             "Referer": "https://prizepicks.com/"},
                    timeout=15
                )
                _data = _r.json()
                _pmap = {}
                for _item in _data.get("included", []):
                    if _item.get("type") == "new_player":
                        _a = _item.get("attributes", {})
                        _pmap[_item["id"]] = {
                            "name": _a.get("display_name", _a.get("name", "")),
                            "team": _a.get("team_abbreviation", ""),
                        }
                _slate = []
                for _proj in _data.get("data", []):
                    _a = _proj.get("attributes", {})
                    if _a.get("stat_type", "").lower() not in ("points", "pts"):
                        continue
                    _ln = _a.get("line_score")
                    if not _ln:
                        continue
                    _pid  = _proj.get("relationships", {}).get("new_player", {}).get("data", {}).get("id")
                    _pi   = _pmap.get(_pid, {})
                    if _pi.get("name"):
                        _slate.append({"player_name": _pi["name"], "line": float(_ln), "team": _pi.get("team", "")})
            except Exception as _e:
                _slate = []
                st.session_state.scanner_error = f"Could not fetch PrizePicks slate: {_e}"

        if _slate and not st.session_state.scanner_error:
            # Apply batch limit
            _limit = len(_slate) if _batch == "All" else int(_batch)
            _slate = _slate[:_limit]
            st.info(f"Analyzing {len(_slate)} props for {_day_sel}...")
            _results  = []
            _progress = st.progress(0)
            _status   = st.empty()
            _season   = "2025-26"

            def _analyze_prop(_prop, _season):
                """Analyze a single prop. Returns result dict or None."""
                try:
                    _nid, _fn = nba_find_player(_prop["player_name"])
                    if not _nid:
                        return None
                    _logs = nba_get_game_logs(_nid, _season, n=10)
                    if _logs.empty:
                        return None
                    _ln   = _prop["line"]
                    _wb   = weighted_hit_rate(_logs, _ln, "Over")
                    _avgp = pd.to_numeric(_logs["PTS"], errors="coerce").dropna().mean()
                    _ld   = _avgp - _ln

                    # ── Early exit: skip players with no clear edge ──
                    # If weighted hit rate is 44-56% AND edge is within 1pt,
                    # this prop will almost certainly be Pass — skip expensive calls
                    if 0.44 <= _wb <= 0.56 and abs(_ld) < 1.0:
                        return None

                    _cons = consistency_score(_logs, _ln)
                    _avgm = pd.to_numeric(_logs["MIN"], errors="coerce").dropna().mean()
                    _avgf = pd.to_numeric(_logs["FGA"], errors="coerce").dropna().mean()
                    _avgt = pd.to_numeric(_logs["FTA"], errors="coerce").dropna().mean()
                    _ep   = next((p for p in espn_get_all_players()
                                  if normalize_name(p["full_name"]) == normalize_name(_fn)), None)
                    _team = _ep["team_abbr"] if _ep else None
                    _opp, _gd, _ven = espn_get_next_game(_team) if _team else (None, None, None)
                    _mq, _, _  = classify_matchup_espn(_opp)
                    _sp        = home_away_split(_logs, _ln, "Over", _team)
                    _vadj      = venue_adjustment(_sp, _ven, "Over")
                    _b2b       = detect_b2b(_logs, _gd)
                    _h2hdf     = get_h2h_logs(_nid, _opp, _season) if _opp else pd.DataFrame()
                    _hsig, _, _= h2h_signal(_h2hdf, _ln, "Over")
                    _savg      = nba_get_season_avg(_nid, _season)
                    _fsig, _   = form_divergence_signal(_avgp, _savg, _ln, "Over")
                    _ctx = {
                        "minutes": suggest_bucket(_avgm, 32, 26),
                        "role":    suggest_bucket(_avgf + 0.5 * _avgt, 18, 12),
                        "shots":   "High" if _avgf >= 15 else ("Low" if _avgf < 10 else "Medium"),
                        "matchup": _mq, "script": "Neutral", "venue": _vadj,
                        "h2h": _hsig, "b2b": _b2b, "form": _fsig,
                    }
                    _adj  = apply_adjustments(_wb, _ctx)
                    _tier = get_confidence_tier(_adj, _ld, _cons)
                    return {
                        "Player": _fn, "Line": _ln, "Avg PTS": round(_avgp, 1),
                        "Edge": round(_ld, 1), "Weighted HR": f"{_wb:.0%}",
                        "Adjusted": f"{_adj:.0%}", "Matchup": _mq,
                        "B2B": _b2b, "Form": _fsig, "Venue": _ven or "?",
                        "Tier": _tier, "_adj_raw": _adj,
                    }
                except Exception:
                    return None

            # Run in parallel batches of 5
            from concurrent.futures import ThreadPoolExecutor, as_completed
            _WORKERS = 5
            _futures = {}
            with ThreadPoolExecutor(max_workers=_WORKERS) as _ex:
                for _prop in _slate:
                    _f = _ex.submit(_analyze_prop, _prop, _season)
                    _futures[_f] = _prop["player_name"]

                _done = 0
                for _f in as_completed(_futures):
                    _done += 1
                    _progress.progress(_done / len(_slate))
                    _status.text(f"Analyzed {_done}/{len(_slate)} · {len(_results)} results so far...")
                    _res = _f.result()
                    if _res:
                        _results.append(_res)

            _progress.empty()
            _status.empty()
            st.session_state.scanner_results = sorted(
                _results,
                key=lambda x: -x["_adj_raw"] if "Over" in x["Tier"] else x["_adj_raw"]
            )
            st.session_state["scanner_day_label"] = _day_sel

    if st.session_state.scanner_error:
        st.error(st.session_state.scanner_error)

    if st.session_state.scanner_results is not None:
        _res = st.session_state.scanner_results
        if _filter == "Strong Only":
            _show = [r for r in _res if r["Tier"] in ("Strong Over", "Strong Under")]
        elif _filter == "Strong + Lean":
            _show = [r for r in _res if "Strong" in r["Tier"] or "Lean" in r["Tier"]]
        else:
            _show = _res

        _tc = {"Strong Over":"green","Lean Over":"yellow","Lean Under":"orange","Strong Under":"red","Pass":"gray"}
        _te = {"Strong Over":"🟢","Lean Over":"🟡","Lean Under":"🟠","Strong Under":"🔴","Pass":"⚪"}

        if not _show:
            st.info("No results match the filter. Try 'Strong + Lean' or 'All results'.")
        else:
            _day_label = st.session_state.get("scanner_day_label", "Today")
            st.markdown(f"<div style='font-family:DM Mono;font-size:0.72rem;color:#475569;margin-bottom:1rem;'>Showing {len(_show)} results for {_day_label} · sorted by confidence</div>", unsafe_allow_html=True)
            for _r in _show:
                _t  = _r["Tier"]
                _cs = _tc.get(_t, "gray")
                _em = _te.get(_t, "⚪")
                _ec = "#22c55e" if _r["Edge"] > 0 else "#ef4444"
                st.markdown(f"""
                <div class='verdict-banner {_cs}' style='margin:0.4rem 0;padding:1rem 1.4rem;'>
                    <div>
                        <div class='verdict-label'>{_r["Line"]} pts Over · PrizePicks</div>
                        <div style='font-size:1.1rem;font-weight:800;color:#f1f5f9;'>{_r["Player"]}</div>
                        <div style='font-family:DM Mono;font-size:0.68rem;color:#475569;margin-top:4px;'>
                            {_r["Venue"]} · {_r["Matchup"]} defense · {_r["B2B"]} · Form: {_r["Form"]}
                        </div>
                    </div>
                    <div style='display:flex;gap:1.5rem;flex-wrap:wrap;align-items:center;'>
                        <div><div class='verdict-label'>Tier</div>
                             <div class='verdict-tier {_cs}' style='font-size:1rem;'>{_em} {_t}</div></div>
                        <div><div class='verdict-label'>Avg PTS</div>
                             <div style='font-size:1rem;font-weight:700;color:#f1f5f9;'>{_r["Avg PTS"]}</div></div>
                        <div><div class='verdict-label'>Edge</div>
                             <div style='font-size:1rem;font-weight:700;color:{_ec};'>{_r["Edge"]:+.1f}</div></div>
                        <div><div class='verdict-label'>Hit Rate</div>
                             <div style='font-size:1rem;font-weight:700;color:#f1f5f9;'>{_r["Weighted HR"]}</div></div>
                        <div><div class='verdict-label'>Adjusted</div>
                             <div style='font-size:1rem;font-weight:700;color:#f1f5f9;'>{_r["Adjusted"]}</div></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            _edf = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in _show])
            st.download_button("⬇  Export CSV", data=_edf.to_csv(index=False).encode(),
                               file_name="slate_scanner.csv", mime="text/csv")

    st.stop()  # prevents player prop section rendering in scanner mode

# ─────────────────────────────────────────────
# Player & Prop inputs
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Player & Prop</div>", unsafe_allow_html=True)

# Load player list
with st.spinner("Loading players..."):
    try:
        all_players_list = espn_get_all_players()
        player_names_list = sorted(
            [p["full_name"] for p in all_players_list],
            key=lambda x: x.split()[-1]
        )
    except Exception:
        player_names_list = []

# Session state for player clear
if "player_key" not in st.session_state:
    st.session_state.player_key = 0

col_a, col_b, col_c, col_d, col_e = st.columns([2.5, 1, 1, 1, 0.8])

with col_a:
    # st.selectbox has native instant filtering — fastest possible search
    # We use a unique key driven by player_key so clearing resets it to blank
    player_query = st.selectbox(
        "Player",
        options=[""] + player_names_list,
        index=0,
        format_func=lambda x: "— select a player —" if x == "" else x,
        key=f"player_sel_{st.session_state.player_key}",
    )

    # Show clear button only when a player is selected
    if player_query:
        _pc, _xc = st.columns([5, 1])
        with _pc:
            st.markdown(
                f"<div style='font-family:DM Mono;font-size:0.72rem;color:#22c55e;"
                f"background:#052e16;border:1px solid #166534;border-radius:8px;"
                f"padding:5px 12px;margin-top:-0.2rem;'>✓ {player_query}</div>",
                unsafe_allow_html=True
            )
        with _xc:
            if st.button("✕", key="clear_player_x", help="Clear"):
                st.session_state.player_key += 1
                st.session_state.logs = None
                st.session_state.ai_analysis = None
                st.rerun()

with col_b:
    line = st.number_input("Points Line", min_value=0.0, value=24.5, step=0.5)
with col_c:
    side = st.selectbox("Over / Under", ["Over", "Under"])
with col_d:
    n_games = st.selectbox("Sample", [5, 10, 15], index=1)
with col_e:
    season_str = st.text_input("Season", value="2025-26")

season_int = season_str_to_int(season_str)
season_str_clean = season_str_to_season(season_str)

selected_player = player_query if player_query else None
if not selected_player:
    st.markdown(
        "<div style='color:#475569;font-family:DM Mono;font-size:0.8rem;"
        "margin-top:0.5rem;'>Select a player above to get started.</div>",
        unsafe_allow_html=True
    )
    st.stop()

# Look up player: nba_api for ID/logs, ESPN roster for team
nba_id, full_name = nba_find_player(selected_player)
# ESPN player lookup for team abbr (already loaded in roster)
espn_player = next((p for p in espn_get_all_players() if normalize_name(p["full_name"]) == normalize_name(selected_player)), None)
player_team = espn_player["team_abbr"] if espn_player else None
player_id   = nba_id

if player_id is None:
    # Show what we tried vs what's available as a hint
    import unicodedata as _ud
    _norm = normalize_name(selected_player)
    from nba_api.stats.static import players as _nba_p
    _close = [p["full_name"] for p in _nba_p.get_players()
              if any(part in normalize_name(p["full_name"]) for part in _norm.split() if len(part) > 3)][:5]
    hint = f" Did you mean: {', '.join(_close)}?" if _close else ""
    st.error(f"Could not find '{selected_player}' in NBA database.{hint}")
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
            st.session_state.logs = nba_get_game_logs(
                player_id=player_id, season=season_str_clean, n=n_games
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
        with st.expander("🛠️ ESPN debug — raw response"):
            err = getattr(nba_get_game_logs, "_last_error", "unknown error")
            raw = {}
            st.write("Top-level keys:", list(raw.keys()) if raw else "empty")
            st.write("Error:", err or "none")
            if raw:
                st.json({k: v for k, v in list(raw.items())[:3]})
        st.warning("No game log data found. Expand debug above to diagnose.")
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
    opp_abbr, game_date, tonight_venue = espn_get_next_game(player_team) if player_team else (None, None, None)

    # Splits
    splits = home_away_split(logs, line, side, player_team)

    # Fallback opponent from logs
    if not opp_abbr and logs is not None and not logs.empty:
        latest_matchup = logs.iloc[0].get("MATCHUP", "")
        if " vs. " in str(latest_matchup):
            opp_abbr = latest_matchup.split(" vs. ")[1].strip()
        elif " @ " in str(latest_matchup):
            opp_abbr = latest_matchup.split(" @ ")[1].strip()

    matchup_auto, opp_pts, league_avg = classify_matchup_espn(opp_abbr)

    # ── H2H + B2B ────────────────────────────
    h2h_df     = get_h2h_logs(player_id, opp_abbr, season_str_clean) if opp_abbr else pd.DataFrame()
    h2h_sig, h2h_avg, h2h_count = h2h_signal(h2h_df, line, side)
    b2b_status  = detect_b2b(logs, game_date)
    season_avg  = nba_get_season_avg(player_id, season_str_clean)
    form_sig, form_diff = form_divergence_signal(sample_avg_pts, season_avg, line, side)

    # ── Stat cards ────────────────────────────
    st.markdown(f"<div class='section-header'>{full_name} &nbsp;·&nbsp; {line} pts {side}</div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Avg PTS (L{n_games})
                <span class='tip' title='Average points scored across the last {n_games} games'>?</span>
            </div>
            <div class='stat-value orange'>{sample_avg_pts:.1f}</div>
            <div class='stat-hint'>Line is {line} · edge {sample_avg_pts - line:+.1f}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        hr_color = "green" if weighted_base >= 0.6 else ("yellow" if weighted_base >= 0.5 else "red")
        hr_label = "Strong" if weighted_base >= 0.6 else ("Moderate" if weighted_base >= 0.5 else "Weak")
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Weighted Hit Rate
                <span class='tip' title='% of games hitting the line, with more weight on recent games'>?</span>
            </div>
            <div class='stat-value {hr_color}'>{weighted_base:.0%}</div>
            <div class='stat-hint'>{hr_label} signal · L{n_games} sample</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        cons_color = "green" if consistency >= 0.5 else ("yellow" if consistency >= 0.35 else "red")
        # If edge is large, low consistency just means player blows past line — not volatile
        if abs(sample_avg_pts - line) >= 5.0 and consistency < 0.35:
            cons_label = "Dominates line"
            cons_color = "green"
        else:
            cons_label = "Consistent" if consistency >= 0.5 else ("Variable" if consistency >= 0.35 else "Volatile")
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Consistency Score
                <span class='tip' title='% of games where points landed within 3 of the line — high = predictable'>?</span>
            </div>
            <div class='stat-value {cons_color}'>{consistency:.0%}</div>
            <div class='stat-hint'>{cons_label} scorer</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        min_color = "green" if avg_min >= 32 else ("yellow" if avg_min >= 26 else "red")
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Avg Minutes
                <span class='tip' title='Average minutes per game — more minutes = more scoring opportunities'>?</span>
            </div>
            <div class='stat-value {min_color}'>{avg_min:.1f}</div>
            <div class='stat-hint'>Avg FGA: {avg_fga:.1f} · FTA: {avg_fta:.1f}</div>
        </div>""", unsafe_allow_html=True)

    # ── Defense card ──────────────────────────
    if opp_abbr:
        badge_css   = matchup_auto.lower()
        badge_label = {"Good": "✅ Weak defense", "Bad": "🔴 Strong defense", "Neutral": "⚪ Average defense"}[matchup_auto]
        date_str    = f" · {game_date}" if game_date else ""
        label       = f"Next game vs {opp_abbr}{date_str}" if game_date else f"Most recent opp: {opp_abbr}"

        # Venue badge
        if tonight_venue:
            venue_color  = "#22c55e" if tonight_venue == "Home" else "#60a5fa"
            venue_badge  = (
                f"<span style='font-family:DM Mono; font-size:0.68rem; font-weight:600; "
                f"background:{venue_color}22; color:{venue_color}; border:1px solid {venue_color}55; "
                f"padding:2px 10px; border-radius:999px; margin-left:10px;'>"
                f"{'🏠 Home' if tonight_venue == 'Home' else '✈️ Away'}</span>"
            )
        else:
            venue_badge = ""

        pts_line = (
            f"{opp_pts:.1f} pts allowed/game"
            f"<span style='font-family:DM Mono; font-size:0.72rem; color:#475569; margin-left:8px;'>league avg {league_avg}</span>"
        ) if opp_pts else "<span style='font-family:DM Mono; font-size:0.8rem; color:#475569;'>Defense data unavailable</span>"

        st.markdown(f"""
        <div class='defense-card'>
            <div>
                <div class='stat-label'>{label}{venue_badge}</div>
                <div style='font-size:1.1rem; font-weight:700; color:#f1f5f9; margin-top:4px;'>
                    {pts_line}
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

    # ── H2H + B2B + Form cards ───────────────
    st.markdown("<div class='section-header'>H2H, Form & Schedule</div>", unsafe_allow_html=True)
    hb1, hb2, hb3 = st.columns(3)

    with hb1:
        if h2h_count >= 2:
            sig_color = {"Strong": "#22c55e", "Neutral": "#94a3b8", "Risk": "#ef4444"}.get(h2h_sig, "#94a3b8")
            sig_bg    = {"Strong": "#052e16", "Neutral": "#0f172a",  "Risk": "#1c0505"}.get(h2h_sig, "#0f172a")
            sig_border= {"Strong": "#166534", "Neutral": "#1e293b",  "Risk": "#991b1b"}.get(h2h_sig, "#1e293b")
            st.markdown(f"""
            <div class='stat-card' style='border-color:{sig_border}; background:linear-gradient(135deg,{sig_bg} 0%,#111827 100%);'>
                <div class='stat-label'>vs {opp_abbr} (L{h2h_count} H2H)</div>
                <div style='display:flex; align-items:baseline; gap:12px; margin-top:4px;'>
                    <div class='stat-value' style='color:{sig_color};'>{h2h_avg:.1f}</div>
                    <div style='font-family:DM Mono; font-size:0.72rem; color:#475569;'>avg pts</div>
                </div>
                <div style='font-family:DM Mono; font-size:0.72rem; color:{sig_color}; margin-top:4px;'>
                    {h2h_sig} H2H signal · line is {line}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-label'>vs {opp_abbr or "opponent"} H2H</div>
                <div style='color:#475569; font-size:0.85rem; margin-top:8px;'>
                    {"Not enough H2H data (need 2+ games)" if opp_abbr else "Opponent not detected"}
                </div>
            </div>""", unsafe_allow_html=True)

    with hb2:
        if b2b_status == "B2B":
            st.markdown(f"""
            <div class='stat-card' style='border-color:#991b1b; background:linear-gradient(135deg,#1c0505 0%,#111827 100%);'>
                <div class='stat-label'>Schedule</div>
                <div style='display:flex; align-items:center; gap:10px; margin-top:6px;'>
                    <div style='font-size:1.5rem;'>😴</div>
                    <div>
                        <div style='font-size:1rem; font-weight:800; color:#ef4444;'>Back-to-Back</div>
                        <div style='font-family:DM Mono; font-size:0.7rem; color:#ef4444; margin-top:2px;'>
                            Fatigue penalty applied to verdict
                        </div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='stat-card' style='border-color:#166534; background:linear-gradient(135deg,#052e16 0%,#111827 100%);'>
                <div class='stat-label'>Schedule</div>
                <div style='display:flex; align-items:center; gap:10px; margin-top:6px;'>
                    <div style='font-size:1.5rem;'>✅</div>
                    <div>
                        <div style='font-size:1rem; font-weight:800; color:#22c55e;'>Normal Rest</div>
                        <div style='font-family:DM Mono; font-size:0.7rem; color:#475569; margin-top:2px;'>
                            No fatigue adjustment
                        </div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    with hb3:
        if season_avg is not None and form_diff is not None:
            is_hot     = form_diff >= 3.0
            is_cold    = form_diff <= -3.0
            form_color = "#22c55e" if form_sig == "Boost" else ("#ef4444" if form_sig == "Penalty" else "#94a3b8")
            form_bg    = "#052e16" if form_sig == "Boost" else ("#1c0505" if form_sig == "Penalty" else "#0f172a")
            form_border= "#166534" if form_sig == "Boost" else ("#991b1b" if form_sig == "Penalty" else "#1e293b")
            streak_label = "🔥 Running Hot" if is_hot else ("🥶 Running Cold" if is_cold else "📊 On Pace")
            streak_sub   = (
                f"{form_diff:+.1f} pts vs season avg ({season_avg:.1f})"
                if form_diff else f"Season avg: {season_avg:.1f}"
            )
            form_verdict = {
                "Boost":   f"{'Favors Over' if side == 'Over' else 'Favors Under'} — applied",
                "Penalty": f"{'Hurts Over' if side == 'Over' else 'Hurts Under'} — applied",
                "Neutral": "No adjustment",
            }.get(form_sig, "No adjustment")
            st.markdown(f"""
            <div class='stat-card' style='border-color:{form_border}; background:linear-gradient(135deg,{form_bg} 0%,#111827 100%);'>
                <div class='stat-label'>Recent Form vs Season</div>
                <div style='font-size:1rem; font-weight:800; color:{form_color}; margin-top:6px;'>{streak_label}</div>
                <div style='font-family:DM Mono; font-size:0.7rem; color:#475569; margin-top:4px;'>{streak_sub}</div>
                <div style='font-family:DM Mono; font-size:0.68rem; color:{form_color}; margin-top:4px;'>{form_verdict}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='stat-card'>
                <div class='stat-label'>Recent Form vs Season</div>
                <div style='color:#475569; font-size:0.85rem; margin-top:8px;'>Season data loading...</div>
            </div>""", unsafe_allow_html=True)

    # ── Home/Away splits ──────────────────────
    if splits.get("home_games", 0) > 0 or splits.get("away_games", 0) > 0:
        st.markdown("<div class='section-header'>Home / Away Splits</div>", unsafe_allow_html=True)
        venue_color = "#22c55e" if tonight_venue == "Home" else "#60a5fa"
        venue_note_html = (
            f"<span style='background:{venue_color}22; color:{venue_color}; font-family:DM Mono; "
            f"font-size:0.7rem; padding:3px 10px; border-radius:999px; border:1px solid {venue_color}44; "
            f"margin-left:8px;'>Tonight: {tonight_venue}</span>"
        ) if tonight_venue else ""

        ha1, ha2 = st.columns(2)
        with ha1:
            if splits.get("home_games", 0) >= 2:
                hr_pct   = splits.get("home_rate", 0)
                hr_color = "#22c55e" if hr_pct >= 0.6 else ("#eab308" if hr_pct >= 0.5 else "#ef4444")
                st.markdown(f"""
                <div class='stat-card' style='border-color:{"#166534" if tonight_venue=="Home" else "#1e293b"};'>
                    <div class='stat-label'>Home {venue_note_html if tonight_venue=="Home" else ""}</div>
                    <div style='display:flex; align-items:baseline; gap:12px; margin-top:4px;'>
                        <div class='stat-value' style='color:{hr_color};'>{hr_pct:.0%}</div>
                        <div style='font-family:DM Mono; font-size:0.72rem; color:#475569;'>hit rate</div>
                    </div>
                    <div style='font-family:DM Mono; font-size:0.72rem; color:#475569; margin-top:4px;'>
                        {splits.get("home_avg", "N/A")} avg pts · {splits.get("home_games", 0)} games
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div class='stat-card'><div class='stat-label'>Home</div><div style='color:#475569; font-size:0.8rem; margin-top:4px;'>Not enough data</div></div>", unsafe_allow_html=True)

        with ha2:
            if splits.get("away_games", 0) >= 2:
                ar_pct   = splits.get("away_rate", 0)
                ar_color = "#22c55e" if ar_pct >= 0.6 else ("#eab308" if ar_pct >= 0.5 else "#ef4444")
                st.markdown(f"""
                <div class='stat-card' style='border-color:{"#166534" if tonight_venue=="Away" else "#1e293b"};'>
                    <div class='stat-label'>Away {venue_note_html if tonight_venue=="Away" else ""}</div>
                    <div style='display:flex; align-items:baseline; gap:12px; margin-top:4px;'>
                        <div class='stat-value' style='color:{ar_color};'>{ar_pct:.0%}</div>
                        <div style='font-family:DM Mono; font-size:0.72rem; color:#475569;'>hit rate</div>
                    </div>
                    <div style='font-family:DM Mono; font-size:0.72rem; color:#475569; margin-top:4px;'>
                        {splits.get("away_avg", "N/A")} avg pts · {splits.get("away_games", 0)} games
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
        badge_css    = matchup_auto.lower()
        badge_text   = {"Good": "Weak defense", "Bad": "Strong defense", "Neutral": "Average defense"}[matchup_auto]
        opp_pts_str  = f"{opp_pts:.1f}" if opp_pts else "N/A"
        date_display = game_date if game_date else ""

        # Venue pill
        if tonight_venue:
            vc = "#22c55e" if tonight_venue == "Home" else "#60a5fa"
            venue_pill = (
                f"<span style='font-family:DM Mono; font-size:0.68rem; font-weight:600; "
                f"background:{vc}22; color:{vc}; border:1px solid {vc}55; "
                f"padding:2px 10px; border-radius:999px; margin-left:10px;'>"
                f"{'🏠 Home' if tonight_venue == 'Home' else '✈️ Away'}</span>"
            )
        else:
            venue_pill = ""

        st.markdown(
            f"<div style='background:#0f172a; border:1px solid #1e293b; border-radius:10px; "
            f"padding:0.75rem 1.2rem; margin-bottom:1rem; display:flex; "
            f"align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;'>"
            f"<div>"
            f"<div style='font-family:DM Mono; font-size:0.65rem; color:#475569; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:4px;'>Next Game</div>"
            f"<div style='font-size:1.2rem; font-weight:800; color:#f1f5f9; letter-spacing:-0.5px;'>"
            f"vs <span style='color:#f97316;'>{opp_abbr}</span>"
            f"<span style='font-family:DM Mono; font-size:0.75rem; color:#475569; font-weight:400; margin-left:8px;'>{date_display}</span>"
            f"{venue_pill}</div>"
            f"</div>"
            f"<span class='defense-badge {badge_css}'>{badge_text} · {opp_pts_str} pts/g allowed</span>"
            f"</div>",
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
        "h2h":     h2h_sig,
        "b2b":     b2b_status,
        "form":    form_sig,
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

    with st.expander("🔬  Logic Debugger — step-by-step verdict breakdown"):
        # ── Step-by-step adjustment trace ────────────────────────────
        multipliers_map = {
            "minutes":  {"Strong": +0.05, "Okay": 0.00, "Risk": -0.07},
            "role":     {"Strong": +0.04, "Okay": 0.00, "Risk": -0.05},
            "shots":    {"High":   +0.03, "Medium": 0.00, "Low": -0.06},
            "matchup":  {"Good":   +0.06, "Neutral": 0.00, "Bad": -0.06},
            "script":   {"Competitive": +0.02, "Neutral": 0.00, "Blowout risk": -0.04},
            "venue":    {"Boost": +0.04, "Neutral": 0.00, "Penalty": -0.05},
            "h2h":      {"Strong": +0.05, "Neutral": 0.00, "Risk": -0.06},
            "b2b":      {"Normal": 0.00, "B2B": -0.06},
            "form":     {"Boost": +0.05, "Neutral": 0.00, "Penalty": -0.05},
        }
        signal_labels = {
            "minutes": "Minutes load",
            "role":    "Role/usage",
            "shots":   "Shot volume",
            "matchup": "Opponent defense",
            "script":  "Game script",
            "venue":   "Home/Away split",
            "h2h":     "H2H vs opponent",
            "b2b":     "Back-to-back rest",
            "form":    "Recent form vs season",
        }

        # Simulate the computation step by step (additive)
        running = weighted_base
        steps   = []
        for key, val in context.items():
            adj    = multipliers_map[key].get(val, 0.0)
            before = running
            running = max(0.0, min(1.0, running + adj))
            after  = running
            delta  = after - before
            steps.append((key, val, adj, before, after, delta))

        # Consistency override check
        edge_is_tight = abs(line_diff) < 5.0
        low_cons = consistency < 0.35 and edge_is_tight
        cons_override = low_cons and tier in ["Lean Over", "Lean Under"]

        # Render debug table
        st.markdown(f"""
        <div style='font-family:DM Mono; font-size:0.72rem; color:#94a3b8; line-height:1.8;'>

        <div style='color:#f97316; font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase;
                    border-bottom:1px solid #1a2333; padding-bottom:4px; margin-bottom:10px;'>
            INPUT
        </div>
        <table style='width:100%; border-collapse:collapse;'>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Player</td>
                <td style='color:#e2e8f0;'>{full_name}</td>
                <td style='padding:3px 8px; color:#475569;'>Line</td>
                <td style='color:#e2e8f0;'>{line} pts {side}</td>
            </tr>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Sample</td>
                <td style='color:#e2e8f0;'>L{n_games} · avg {sample_avg_pts:.1f} pts</td>
                <td style='padding:3px 8px; color:#475569;'>Edge vs line</td>
                <td style='color:{"#22c55e" if line_diff > 0 else "#ef4444"};'>{line_diff:+.1f} pts</td>
            </tr>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Raw hit rate</td>
                <td style='color:#e2e8f0;'>{baseline:.1%}</td>
                <td style='padding:3px 8px; color:#475569;'>Weighted hit rate</td>
                <td style='color:#e2e8f0;'>{weighted_base:.1%} ← starting point</td>
            </tr>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Consistency</td>
                <td style='color:{"#22c55e" if consistency>=0.5 else "#eab308" if consistency>=0.35 else "#ef4444"};'>
                    {consistency:.1%} {f"⚠️ low but edge {line_diff:+.1f} > 5pts — override skipped" if not edge_is_tight and consistency < 0.35 else ""}
                </td>
                <td style='padding:3px 8px; color:#475569;'>Season avg</td>
                <td style='color:#e2e8f0;'>{f"{season_avg:.1f} pts" if season_avg else "N/A"}</td>
            </tr>
        </table>

        <div style='color:#f97316; font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase;
                    border-bottom:1px solid #1a2333; padding-bottom:4px; margin:14px 0 10px 0;'>
            MULTIPLIER TRACE
        </div>
        <table style='width:100%; border-collapse:collapse;'>
            <tr style='color:#475569; font-size:0.63rem; border-bottom:1px solid #1a2333;'>
                <td style='padding:3px 0;'>SIGNAL</td>
                <td>VALUE</td>
                <td>ADJUSTMENT</td>
                <td>BEFORE</td>
                <td>AFTER</td>
                <td>IMPACT</td>
            </tr>
        """, unsafe_allow_html=True)

        rows_html = ""
        for key, val, adj, before, after, delta in steps:
            impact_color = "#22c55e" if delta > 0.005 else "#ef4444" if delta < -0.005 else "#475569"
            mult_display = (f"+{adj:.0%}" if adj > 0 else f"{adj:.0%}" if adj < 0 else "no change")
            mult_color   = "#22c55e" if adj > 0 else "#ef4444" if adj < 0 else "#475569"
            rows_html += f"""
            <tr style='border-bottom:1px solid #111827;'>
                <td style='padding:4px 0; color:#94a3b8;'>{signal_labels.get(key, key)}</td>
                <td style='color:#e2e8f0; font-weight:600;'>{val}</td>
                <td style='color:{mult_color};'>{mult_display}</td>
                <td style='color:#64748b;'>{before:.1%}</td>
                <td style='color:#e2e8f0;'>{after:.1%}</td>
                <td style='color:{impact_color};'>{delta:+.1%}</td>
            </tr>"""

        st.markdown(rows_html + "</table>", unsafe_allow_html=True)

        # Pre-compute values to avoid nested f-string quote issues in HTML
        _tier_color = ("#22c55e" if "Strong Over" in tier else
                       "#eab308" if "Lean Over" in tier else
                       "#f97316" if "Lean Under" in tier else
                       "#ef4444" if "Strong Under" in tier else "#64748b")
        _cons_note  = ("  ← consistency downgrade applied"
                       if low_cons and tier in ["Lean Over","Lean Under"] else "")

        # Final decision
        # Consistency override only matters when tier is Strong Over/Under
        override_relevant = tier in ["Strong Over", "Strong Under", "Lean Over", "Lean Under"]
        if consistency < 0.35 and edge_is_tight and override_relevant:
            edge_tight_note = f"Edge {line_diff:+.1f} {'< 5 → downgrade applied' if edge_is_tight else '≥ 5 → skipped'}"
            cons_note = f"Consistency {consistency:.0%} < 35% · {edge_tight_note}"
        elif not edge_is_tight and consistency < 0.35:
            cons_note = f"Consistency {consistency:.0%} < 35% but edge {line_diff:+.1f} ≥ 5 → override skipped (player dominates line)"
        else:
            cons_note = f"Consistency {consistency:.0%} · No override needed"

        st.markdown(f"""
        <div style='color:#f97316; font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase;
                    border-bottom:1px solid #1a2333; padding-bottom:4px; margin:14px 0 10px 0;'>
            FINAL DECISION
        </div>
        <table style='width:100%; border-collapse:collapse; font-family:DM Mono; font-size:0.72rem;'>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Adjusted probability</td>
                <td style='color:#e2e8f0; font-weight:700;'>{adjusted:.1%}</td>
                <td style='padding:3px 8px; color:#475569;'>Threshold for Strong Over</td>
                <td style='color:#94a3b8;'>≥ 64% AND edge ≥ +1.5</td>
            </tr>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Edge vs line</td>
                <td style='color:{"#22c55e" if line_diff>=1.5 else "#ef4444"};'>{line_diff:+.1f} pts {"✓" if abs(line_diff)>=1.5 else "✗ too small"}</td>
                <td style='padding:3px 8px; color:#475569;'>Threshold for Lean Over</td>
                <td style='color:#94a3b8;'>≥ 55% AND edge > 0</td>
            </tr>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Consistency check</td>
                <td colspan='3' style='color:{"#ef4444" if low_cons else "#475569"};'>{cons_note}</td>
            </tr>
            <tr style='border-top:1px solid #1a2333; margin-top:4px;'>
                <td style='padding:6px 8px 3px 0; color:#475569;'>Final tier</td>
                <td colspan='3' style='font-size:0.9rem; font-weight:800; color:{_tier_color};'>
                    {tier_emoji[tier]} {tier}{_cons_note}
                </td>
            </tr>
        </table>
        </div>
        """, unsafe_allow_html=True)

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
