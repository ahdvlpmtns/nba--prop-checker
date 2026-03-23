import os
import re
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple

from groq import Groq
import pandas as pd
import streamlit as st

from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, scoreboardv2

# ─────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────

if "logs" not in st.session_state:
    st.session_state.logs = None
if "ai_analysis" not in st.session_state:
    st.session_state.ai_analysis = None
if "ai_error" not in st.session_state:
    st.session_state.ai_error = None

# ─────────────────────────────────────────────
# Helpers
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
    hits = (pts > line).sum() if side == "Over" else (pts < line).sum()
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
def get_todays_matchup_for_player(player_team_abbr: str) -> dict:
    today_str = datetime.today().strftime("%m/%d/%Y")
    sb = scoreboardv2.ScoreboardV2(game_date=today_str, league_id="00", day_offset=0, timeout=120)
    games = sb.get_data_frames()[0]

    if games.empty:
        return {"has_game_today": False, "opponent": None, "matchup": None, "home_away": None}

    row = games[
        (games["HOME_TEAM_ABBREVIATION"] == player_team_abbr) |
        (games["VISITOR_TEAM_ABBREVIATION"] == player_team_abbr)
    ]

    if row.empty:
        return {"has_game_today": False, "opponent": None, "matchup": None, "home_away": None}

    row = row.iloc[0]
    home = row["HOME_TEAM_ABBREVIATION"]
    away = row["VISITOR_TEAM_ABBREVIATION"]

    if player_team_abbr == home:
        return {"has_game_today": True, "opponent": away, "matchup": f"{home} vs. {away}", "home_away": "Home"}
    else:
        return {"has_game_today": True, "opponent": home, "matchup": f"{player_team_abbr} @ {home}", "home_away": "Away"}


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


# ─────────────────────────────────────────────
# AI Analysis (Groq)
# ─────────────────────────────────────────────

def get_api_key() -> str:
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


def build_analysis_prompt(
    full_name, line, side, n_games, logs,
    baseline, adjusted, confidence_tier,
    avg_pts, avg_min, avg_fga,
    min_flag, fga_flag, pts_flag,
    minutes_sel, role_sel, shots_sel, matchup_sel, script_sel,
) -> str:
    game_rows = []
    for _, row in logs.iterrows():
        date = str(row["GAME_DATE"])[:10] if row["GAME_DATE"] is not None else "N/A"
        matchup = row["MATCHUP"] or "N/A"
        pts = row["PTS"]
        mins = row["MIN"]
        fga = row["FGA"]
        hit = "✓" if pd.notna(pts) and float(pts) > line else "✗"
        game_rows.append(f"  {date} | {matchup} | {pts} pts | {mins} min | {fga} FGA | {hit}")

    game_log_str = "\n".join(game_rows)

    return f"""You are a sharp NBA prop analyst. Write a clear, confident, data-driven breakdown of this points prop.

Player: {full_name}
Prop Line: {line} points ({side})
Sample: Last {n_games} games

=== GAME LOG ===
{game_log_str}

=== KEY STATS ===
- Avg PTS: {avg_pts:.1f}
- Avg MIN: {avg_min:.1f}
- Avg FGA: {avg_fga:.1f}
- Baseline hit rate vs {line}: {baseline:.0%}
- Adjusted hit rate: {adjusted:.0%}

=== TRENDS ===
- Minutes trend: {min_flag}
- FGA trend: {fga_flag}
- Points trend: {pts_flag}

=== CONTEXT ===
- Minutes outlook: {minutes_sel}
- Role/usage: {role_sel}
- Shot volume: {shots_sel}
- Matchup/pace: {matchup_sel}
- Game script: {script_sel}
- Confidence tier: {confidence_tier}

Write a 3-4 paragraph prop breakdown:
1. Lead with the prop and your lean.
2. What the recent game log shows — patterns, streaks, outliers.
3. How context factors affect this prop tonight.
4. Closing verdict with confidence level.

Be direct. Use real numbers. Write like a sharp bettor, not a TV analyst."""


def generate_ai_analysis(prompt: str) -> str:
    api_key = get_api_key()
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return chat_completion.choices[0].message.content


# ─────────────────────────────────────────────
# Slate Scanner
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

st.set_page_config(page_title="NBA Points Prop Checker", layout="wide")
st.title("NBA Points Prop Checker")
st.caption("Version 2.0 — AI-powered prop analysis")

st.markdown("## Inputs")

player_query = st.text_input("Search player", value="Fox")
line = st.number_input("Points line", min_value=0.0, value=24.5, step=0.5)
side = st.selectbox("Higher / Lower", ["Over", "Under"])
n_games = st.selectbox("Sample size", [5, 10, 15], index=1)
season = st.text_input("Season", value="2025-26")
fetch = st.button("Fetch logs")

with st.sidebar:
    st.markdown("## Advanced Tools")
    manual_mode = st.checkbox("Use manual last 10 input if fetch fails")
    scan_slate = st.checkbox("Enable slate scanner")
    st.markdown("---")
    st.markdown("## AI Analysis")
    enable_ai = st.checkbox("Enable AI-powered breakdown", value=True)

st.divider()

candidate_players = search_candidates(player_query)

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

if not fetch and st.session_state.logs is None and not scan_slate:
    st.info("Enter inputs, then click **Fetch logs**.")

# ── FETCH LOGS ───────────────────────────────
if fetch:
    st.session_state.ai_analysis = None  # clear old analysis on new fetch
    st.session_state.ai_error = None

    try:
        with st.spinner("Fetching player game logs..."):
            st.session_state.logs = fetch_with_retries(
                lambda: get_last_n_games(player_id=player_id, season=season, n=n_games)
            )
    except Exception as e:
        if not manual_mode:
            st.error(f"Fetch failed: {repr(e)}")
            st.exception(e)
            st.stop()
        else:
            st.warning("Live fetch failed. Enter last 10 points manually below.")
            st.session_state.logs = None

    if st.session_state.logs is None and manual_mode:
        manual_points = []
        st.markdown("### Manual Last 10 Points Entry")
        cols = st.columns(5)
        for i in range(10):
            col = cols[i % 5]
            val = col.number_input(f"Game {i+1}", min_value=0.0, step=1.0, key=f"manual_pts_{i}")
            manual_points.append(val)
        st.session_state.logs = pd.DataFrame({
            "GAME_DATE": [None] * 10,
            "MATCHUP": [None] * 10,
            "MIN": [None] * 10,
            "PTS": manual_points,
            "FGA": [None] * 10,
            "FTA": [None] * 10,
            "FG3A": [None] * 10,
        })

# ── RENDER ANALYSIS (persists across reruns) ─
if st.session_state.logs is not None:
    logs = st.session_state.logs

    baseline = hit_rate(logs, line=line, side=side)

    avg_min = pd.to_numeric(logs["MIN"], errors="coerce").dropna().mean()
    avg_fga = pd.to_numeric(logs["FGA"], errors="coerce").dropna().mean()
    avg_fta = pd.to_numeric(logs["FTA"], errors="coerce").dropna().mean()

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
    with col2:
        st.markdown("### Key Metrics")
        st.metric("Baseline hit rate", f"{baseline:.0%}")
        st.caption(f"Baseline = hits vs the line using the selected last {n_games} games.")
        st.markdown("### Quick Flags")
        st.write(f"Minutes trend: **{min_flag}**")
        st.write(f"Shot volume (FGA) trend: **{fga_flag}**")
        st.write(f"Points trend: **{pts_flag}**")

    st.divider()
    st.markdown("## Context Adjuster")

    adj_map_minutes = {"Strong": 0.05, "Okay": 0.00, "Risk": -0.07}
    adj_map_role    = {"Strong": 0.04, "Okay": 0.00, "Risk": -0.05}
    adj_map_shots   = {"High": 0.03, "Medium": 0.00, "Low": -0.05}
    adj_map_matchup = {"Good": 0.03, "Neutral": 0.00, "Bad": -0.04}
    adj_map_script  = {"Competitive": 0.02, "Neutral": 0.00, "Blowout risk": -0.04}

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        minutes_sel = st.selectbox("Minutes", ["Okay", "Strong", "Risk"],
                                   index=["Okay", "Strong", "Risk"].index(minutes_suggest))
    with c2:
        role_sel = st.selectbox("Role", ["Okay", "Strong", "Risk"],
                                index=["Okay", "Strong", "Risk"].index(role_suggest))
    with c3:
        shots_sel = st.selectbox("Shots", ["Medium", "High", "Low"],
                                 index=["Medium", "High", "Low"].index(shots_suggest))
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
    model_lean = "OVER" if sample_avg_pts > line else ("UNDER" if sample_avg_pts < line else "EVEN")

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

    badge_map = {
        "Strong Over":  "🟢 Strong Over",
        "Lean Over":    "🟡 Lean Over",
        "Lean Under":   "🟠 Lean Under",
        "Strong Under": "🔴 Strong Under",
        "Pass":         "⚪ Pass",
    }
    confidence_badge = badge_map[confidence_tier]

    # ── AI ANALYSIS ──────────────────────────────────────────────────────────
    if enable_ai:
        st.divider()
        st.markdown("## 🤖 AI-Powered Breakdown")

        api_key = get_api_key()

        if not api_key:
            st.error("❌ No GROQ_API_KEY found. Add it to your Streamlit secrets.")
        else:
            if st.button("Generate AI Analysis"):
                with st.spinner("Analyzing this prop..."):
                    try:
                        prompt = build_analysis_prompt(
                            full_name=full_name,
                            line=line,
                            side=side,
                            n_games=n_games,
                            logs=logs,
                            baseline=baseline,
                            adjusted=adjusted,
                            confidence_tier=confidence_tier,
                            avg_pts=sample_avg_pts,
                            avg_min=avg_min,
                            avg_fga=avg_fga,
                            min_flag=min_flag,
                            fga_flag=fga_flag,
                            pts_flag=pts_flag,
                            minutes_sel=minutes_sel,
                            role_sel=role_sel,
                            shots_sel=shots_sel,
                            matchup_sel=matchup_sel,
                            script_sel=script_sel,
                        )
                        st.session_state.ai_analysis = generate_ai_analysis(prompt)
                        st.session_state.ai_error = None
                    except Exception as e:
                        st.session_state.ai_error = repr(e)
                        st.session_state.ai_analysis = None

            # Always render stored analysis if available
            if st.session_state.ai_analysis:
                st.markdown(st.session_state.ai_analysis)
            elif st.session_state.ai_error:
                st.error(f"AI analysis failed: {st.session_state.ai_error}")

    # ── FINAL VERDICT ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("## Final Verdict")
    st.markdown(f"### {full_name} — Points Prop\n## {confidence_badge}")

    v1, v2, v3 = st.columns(3)
    with v1:
        st.metric("Line", f"{line:.1f}")
    with v2:
        st.metric(f"Recent Avg (Last {n_games})", f"{sample_avg_pts:.1f}")
    with v3:
        st.metric("Hit Rate", f"{baseline:.0%}")

    with st.expander("Show detailed analysis"):
        d1, d2, d3 = st.columns(3)
        with d1:
            st.metric("Model Lean", model_lean)
        with d2:
            st.metric("Confidence Tier", confidence_tier)
        with d3:
            st.metric("Edge vs Line", f"{line_diff:+.1f}")

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
    st.download_button("Download report CSV", data=csv, file_name="prop_report.csv", mime="text/csv")

# ─────────────────────────────────────────────
# Slate Scanner
# ─────────────────────────────────────────────

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
            st.warning("No players returned. API may have timed out.")
        else:
            st.dataframe(df_team_scan, use_container_width=True)

st.markdown("---")
st.caption(
    "This tool provides statistical analysis for educational purposes only. "
    "It does not guarantee outcomes and should not be considered financial or betting advice."
)
