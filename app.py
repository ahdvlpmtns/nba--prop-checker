import re
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple

import pandas as pd
import streamlit as st

from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, scoreboardv2

def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def find_player_id(player_name: str) -> Tuple[Optional[int], Optional[str]]:
    name = normalize_name(player_name)
    all_players = players.get_players()

    # Exact match first
    for p in all_players:
        if normalize_name(p["full_name"]) == name:
            return p["id"], p["full_name"]

    # Contains match fallback
    candidates = [p for p in all_players if name in normalize_name(p["full_name"])]
    if len(candidates) == 1:
        return candidates[0]["id"], candidates[0]["full_name"]

    if len(candidates) > 1:
        return None, None

    return None, None


def search_candidates(player_name: str):
    name = normalize_name(player_name)
    all_players = players.get_players()
    return [p for p in all_players if name in normalize_name(p["full_name"])]

@st.cache_data(ttl=600)  # cache for 10 minutes
@st.cache_data(ttl=600)
def get_last_n_games(player_id: int, season: str, n: int = 10) -> pd.DataFrame:
    df = playergamelog.PlayerGameLog(
        player_id=player_id,
        season=season,
        timeout=15,
    ).get_data_frames()[0]

    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df = df.sort_values("GAME_DATE", ascending=False).head(n).copy()

    for c in ["MATCHUP", "MIN", "PTS", "FGA", "FTA", "FG3A"]:
        if c not in df.columns:
            df[c] = None

    return df[["GAME_DATE", "MATCHUP", "MIN", "PTS", "FGA", "FTA", "FG3A"]]


def hit_rate(df: pd.DataFrame, line: float, side: str) -> float:
    pts = pd.to_numeric(df["PTS"], errors="coerce").dropna()
    if len(pts) == 0:
        return 0.0
    if side == "Over":
        hits = (pts > line).sum()
    else:
        hits = (pts < line).sum()
    return hits / len(pts)


def trend_flag(series: pd.Series, lookback: int = 3) -> str:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < lookback + 2:
        return "Not enough data"
    recent = s.iloc[:lookback].mean()
    prior = s.iloc[lookback:].mean()
    diff = recent - prior
    if diff >= 2:
        return "Up"
    if diff <= -2:
        return "Down"
    return "Flat"

def suggest_bucket(value: float, strong_cut: float, risk_cut: float) -> str:
    """
    Returns "Strong", "Okay", or "Risk" based on thresholds.
    strong_cut: value at/above this is Strong
    risk_cut: value below this is Risk
    """
    if value >= strong_cut:
        return "Strong"
    if value < risk_cut:
        return "Risk"
    return "Okay"

def fetch_with_retries(fn, retries=3, wait=2):
    last_err = None
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            time.sleep(wait * (i + 1))
    raise last_err

@st.cache_data(ttl=600)
def get_todays_teams() -> list:
    today_str = datetime.today().strftime("%m/%d/%Y")

    sb = scoreboardv2.ScoreboardV2(
        game_date=today_str,
        league_id="00",
        day_offset=0,
        timeout=20,
    )

    games = sb.get_data_frames()[0]

    if games.empty:
        return []

    teams = sorted(
        set(games["HOME_TEAM_ABBREVIATION"].tolist()) |
        set(games["VISITOR_TEAM_ABBREVIATION"].tolist())
    )
    return teams


@st.cache_data(ttl=600)
def get_todays_matchup_for_player(player_team_abbr: str) -> dict:
    today_str = datetime.today().strftime("%m/%d/%Y")

    sb = scoreboardv2.ScoreboardV2(
        game_date=today_str,
        league_id="00",
        day_offset=0,
        timeout=120,
    )

    games = sb.get_data_frames()[0]  # GameHeader table

    if games.empty:
        return {
            "has_game_today": False,
            "opponent": None,
            "matchup": None,
            "home_away": None,
        }

    row = games[
        (games["HOME_TEAM_ABBREVIATION"] == player_team_abbr) |
        (games["VISITOR_TEAM_ABBREVIATION"] == player_team_abbr)
    ]

    if row.empty:
        return {
            "has_game_today": False,
            "opponent": None,
            "matchup": None,
            "home_away": None,
        }

    row = row.iloc[0]

    home = row["HOME_TEAM_ABBREVIATION"]
    away = row["VISITOR_TEAM_ABBREVIATION"]

    if player_team_abbr == home:
        opponent = away
        home_away = "Home"
        matchup = f"{home} vs. {away}"
    else:
        opponent = home
        home_away = "Away"
        matchup = f"{player_team_abbr} @ {opponent}"

    return {
        "has_game_today": True,
        "opponent": opponent,
        "matchup": matchup,
        "home_away": home_away,
    }

    row = row.iloc[0]
    matchup = row["MATCHUP"]

    if "vs." in matchup:
        opp = matchup.split("vs.")[-1].strip()
        home_away = "Home"
    elif "@" in matchup:
        opp = matchup.split("@")[-1].strip()
        home_away = "Away"
    else:
        opp = None
        home_away = None

    return {
        "has_game_today": True,
        "opponent": opp,
        "matchup": matchup,
        "home_away": home_away,
    }

@dataclass
class Adjustments:
    minutes: float = 0.0
    role: float = 0.0
    shots: float = 0.0
    matchup: float = 0.0
    script: float = 0.0

    @property
    def total(self) -> float:
        return self.minutes + self.role + self.shots + self.matchup + self.script


def label_from_prob(p: float) -> str:
    if p >= 0.65:
        return "GREEN"
    if p >= 0.58:
        return "YELLOW"
    return "RED"


st.set_page_config(page_title="NBA Points Prop Checker", layout="wide")
st.title("NBA Points Prop Checker (Conservative Method)")
st.caption("Version 1.0 — Player prop analysis tool")
st.caption("Analyze NBA points props using recent game logs, hit rate, and context adjustments.")

NBA_TEAMS = [
    "ATL","BOS","BKN","CHA","CHI","CLE","DAL","DEN","DET","GSW",
    "HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NOP","NYK",
    "OKC","ORL","PHI","PHX","POR","SAC","SAS","TOR","UTA","WAS"
]

TEAM_ROSTERS = {
    "NYK": ["Jalen Brunson", "Josh Hart", "Miles McBride"],
    "SAC": ["De'Aaron Fox", "Domantas Sabonis", "Keegan Murray"],
    "HOU": ["Jalen Green", "Alperen Sengun", "Fred VanVleet"],
    "SAS": ["Victor Wembanyama", "Devin Vassell", "Keldon Johnson"],
    "LAL": ["LeBron James", "Anthony Davis", "Austin Reaves"],
    "BOS": ["Jayson Tatum", "Jaylen Brown", "Derrick White"],
    "PHX": ["Kevin Durant", "Devin Booker", "Bradley Beal"],
    "DAL": ["Luka Doncic", "Kyrie Irving", "PJ Washington"],
    "DEN": ["Nikola Jokic", "Jamal Murray", "Michael Porter Jr."],
    "MIL": ["Giannis Antetokounmpo", "Damian Lillard", "Khris Middleton"],
}

@st.cache_data(ttl=300)
def scan_team_players(team_abbr: str, season: str) -> pd.DataFrame:
    roster = TEAM_ROSTERS.get(team_abbr, [])
    results = []

    for player_name in roster[:3]:
        try:
            player_id, full_name = find_player_id(player_name)
            if not player_id:
                continue

            # no retries here on purpose
            logs = get_last_n_games(player_id=player_id, season=season, n=10)
        except Exception:
            continue

        if logs is None or logs.empty:
            continue

        avg_pts = pd.to_numeric(logs["PTS"], errors="coerce").dropna().mean()
        avg_min = pd.to_numeric(logs["MIN"], errors="coerce").dropna().mean()
        avg_fga = pd.to_numeric(logs["FGA"], errors="coerce").dropna().mean()

        results.append({
            "Player": full_name,
            "Team": team_abbr,
            "Avg PTS (L10)": round(avg_pts, 1) if pd.notna(avg_pts) else None,
            "Avg MIN (L10)": round(avg_min, 1) if pd.notna(avg_min) else None,
            "Avg FGA (L10)": round(avg_fga, 1) if pd.notna(avg_fga) else None,
        })

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(results).sort_values(
        by=["Avg PTS (L10)", "Avg MIN (L10)", "Avg FGA (L10)"],
        ascending=False
    ).reset_index(drop=True)

with st.sidebar:
    st.header("Inputs")
    player_query = st.text_input("Search player", value="Fox")
    player_name = player_query
    season = st.text_input("Season (format: 2025-26)", value="2025-26")

    line = st.number_input("Points line", min_value=0.0, value=24.5, step=0.5)
    side = st.selectbox("Over/Under", ["Over", "Under"])

    n_games = st.selectbox("Sample size", [5, 10, 15], index=1)

    fetch = st.button("Fetch logs")

    manual_mode = st.checkbox("Use manual last 10 input if fetch fails")

    st.markdown("---")
    st.subheader("Slate Scanner")

    scan_slate = st.checkbox("Enable slate scanner")

st.divider()

candidate_players = search_candidates(player_name)

if len(candidate_players) == 0:
    st.error("No player found. Try a different spelling.")
    st.stop()

player_options = [p["full_name"] for p in candidate_players]
selected_player = st.selectbox("Select player", player_options)

player_id, full_name = find_player_id(selected_player)

if player_id is None:
    st.error("Could not resolve the selected player.")
    st.stop()

st.markdown("## Player Analysis")
st.subheader(f"Player: {full_name}")

if not fetch and not scan_slate:
    st.info("Enter inputs, then click **Fetch logs** or use **Scan today's slate**.")

if fetch:
    logs = None

    try:
        with st.spinner("Fetching player game logs..."):
            logs = fetch_with_retries(
                lambda: get_last_n_games(player_id=player_id, season=season, n=n_games)
            )
      
    except Exception as e:
        if not manual_mode:
            st.error(f"Fetch failed: {repr(e)}")
            st.exception(e)
            st.stop()

        else:
            st.warning("Live fetch failed. Enter last 10 points manually below.")

    if logs is None:
        manual_points = []
        st.markdown("### Manual Last 10 Points Entry")

        cols = st.columns(5)

        for i in range(10):
            col = cols[i % 5]
            val = col.number_input(
                f"Game {i+1}",
                min_value=0.0,
                step=1.0,
                key=f"manual_pts_{i}"
            )
            manual_points.append(val)

        logs = pd.DataFrame({
            "GAME_DATE": [None] * 10,
            "MATCHUP": [None] * 10,
            "MIN": [None] * 10,
            "PTS": manual_points,
            "FGA": [None] * 10,
            "FTA": [None] * 10,
            "FG3A": [None] * 10,
        })

if fetch:
    baseline = hit_rate(logs, line=line, side=side)

    # Simple averages (last N games) for auto-suggestions
    avg_min = pd.to_numeric(logs["MIN"], errors="coerce").dropna().mean()
    avg_fga = pd.to_numeric(logs["FGA"], errors="coerce").dropna().mean()
    avg_fta = pd.to_numeric(logs["FTA"], errors="coerce").dropna().mean()

    # Auto-suggest buckets
    minutes_suggest = suggest_bucket(avg_min, strong_cut=32, risk_cut=26)
    shots_suggest = "High" if avg_fga >= 15 else ("Low" if avg_fga < 10 else "Medium")

    role_proxy = avg_fga + (0.5 * avg_fta)
    role_suggest = suggest_bucket(role_proxy, strong_cut=18, risk_cut=12)

    min_flag = trend_flag(logs["MIN"])
    fga_flag = trend_flag(logs["FGA"])
    pts_flag = trend_flag(logs["PTS"])

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown(f"### Game Log (Last {n_games})")
        st.dataframe(logs.reset_index(drop=True), use_container_width=True)

        st.markdown("### Baseline")
    with col2:
        st.markdown("### Key Metrics")
        st.metric("Baseline hit rate", f"{baseline:.0%}")
        st.caption(f"Baseline = hits vs the line using the selected last {n_games} games.")

        st.markdown("### Quick Flags")
        st.write(f"Minutes trend: **{min_flag}**")
        st.write(f"Shot volume (FGA) trend: **{fga_flag}**")
        st.write(f"Points trend: **{pts_flag}**")

    st.divider()

    st.markdown("## Context Adjuster (simple + / −)")
    st.caption("You still choose context, but the app calculates adjusted %.")

    adj_map_minutes = {"Strong": 0.05, "Okay": 0.00, "Risk": -0.07}
    adj_map_role = {"Strong": 0.04, "Okay": 0.00, "Risk": -0.05}
    adj_map_shots = {"High": 0.03, "Medium": 0.00, "Low": -0.05}
    adj_map_matchup = {"Good": 0.03, "Neutral": 0.00, "Bad": -0.04}
    adj_map_script = {"Competitive": 0.02, "Neutral": 0.00, "Blowout risk": -0.04}

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        minutes_sel = st.selectbox(
            "Minutes",
            ["Okay", "Strong", "Risk"],
            index=["Okay", "Strong", "Risk"].index(minutes_suggest)
        )

    with c2:
        role_sel = st.selectbox(
            "Role",
            ["Okay", "Strong", "Risk"],
            index=["Okay", "Strong", "Risk"].index(role_suggest)
        )

    with c3:
        shots_sel = st.selectbox(
            "Shots",
            ["Medium", "High", "Low"],
            index=["Medium", "High", "Low"].index(shots_suggest)
        )

    with c4:
        matchup_sel = st.selectbox("Matchup/Pace", ["Neutral", "Good", "Bad"])

    with c5:
        script_sel = st.selectbox("Game script", ["Neutral", "Competitive", "Blowout risk"])

    adjs = Adjustments(
        minutes=adj_map_minutes[minutes_sel],
        role=adj_map_role[role_sel],
        shots=adj_map_shots[shots_sel],
        matchup=adj_map_matchup[matchup_sel],
        script=adj_map_script[script_sel],
    )

    adjusted = max(0.0, min(1.0, baseline + adjs.total))
    label = label_from_prob(adjusted)

    sample_avg_pts = pd.to_numeric(logs["PTS"], errors="coerce").dropna().mean()
    line_diff = sample_avg_pts - line

    if sample_avg_pts > line:
        model_lean = "OVER"
    elif sample_avg_pts < line:
        model_lean = "UNDER"
    else:
        model_lean = "EVEN"

    if adjusted >= 0.65 and line_diff >= 2:
        confidence_tier = "Strong Over"
    elif adjusted >= 0.58 and line_diff > 0:
        confidence_tier = "Lean Over"
    elif adjusted <= 0.42 and line_diff <= -2:
        confidence_tier = "Strong Under"
    elif adjusted <= 0.48 and line_diff < 0:
        confidence_tier = "Lean Under"
    else:
        confidence_tier = "Pass"

    if confidence_tier == "Strong Over":
        confidence_badge = "🟢 Strong Over"
    elif confidence_tier == "Lean Over":
        confidence_badge = "🟡 Lean Over"
    elif confidence_tier == "Lean Under":
        confidence_badge = "🟠 Lean Under"
    elif confidence_tier == "Strong Under":
        confidence_badge = "🔴 Strong Under"
    else:
        confidence_badge = "⚪ Pass"

    cA, cB, cC = st.columns(3)
    with cA:
        st.metric("Baseline %", f"{baseline:.0%}")
    with cB:
        st.metric("Adjusted %", f"{adjusted:.0%}")
    with cC:
        st.metric("Traffic light", label)

    st.markdown("## Final Verdict")
    st.markdown(
        f"""
### {full_name} — Points Prop
## {confidence_badge}
**Model Lean:** {model_lean}  
**Edge vs Line:** {line_diff:+.1f}  
**Hit Rate:** {baseline:.0%}
"""
    )
    
    st.markdown("## Quick Verdict")

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric("Player", full_name)
        st.metric("Line", f"{line:.1f}")

    with s2:
        st.metric(f"Avg (Last {n_games})", f"{sample_avg_pts:.1f}")
        st.metric("Hit Rate", f"{baseline:.0%}")

    with s3:
        st.metric("Model Lean", model_lean)
        st.metric("Confidence Tier", confidence_tier)
        st.markdown(f"### {confidence_badge}")
        st.metric("Avg - Line", f"{line_diff:+.1f}")

    out = logs.copy()
    out.insert(0, "PLAYER", full_name)
    out.insert(1, "LINE", line)
    out.insert(2, "SIDE", side)
    out.insert(3, "BASELINE_HIT_RATE", baseline)
    out.insert(4, "ADJUSTED_HIT_RATE", adjusted)
    out.insert(5, "LABEL", label)

    st.divider()
    st.markdown("### Export")

    csv = out.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download report CSV",
        data=csv,
        file_name="prop_report.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("## Advanced Tools")
st.subheader("Slate Scanner")

if scan_slate:
    selected_team = st.selectbox("Choose a team to scan", NBA_TEAMS)
    st.write(f"Selected team: **{selected_team}**")

    run_team_scan = st.button("Run team scan")

    if run_team_scan:
        st.write(f"Running scan for **{selected_team}**...")
        df_team_scan = scan_team_players(selected_team, season)

        if df_team_scan.empty:
            st.warning("No players returned. This usually means the API timed out for all scanned players.")
        else:
            st.dataframe(df_team_scan, use_container_width=True)

st.markdown("---")
st.caption(
    "This tool provides statistical analysis for educational purposes only. "
    "It does not guarantee outcomes and should not be considered financial or betting advice."
)
