import os
import re
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple

from groq import Groq
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, scoreboardv2, commonteamroster

# ─────────────────────────────────────────────
# Page config — must be first
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

/* Base */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #080c14;
    color: #e2e8f0;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }

/* Custom header */
.proplens-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 0.25rem;
}
.proplens-logo {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fdba74 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.proplens-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #64748b;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 2px;
}

/* Stat cards */
.stat-card {
    background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.75rem;
}
.stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #475569;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #f1f5f9;
    letter-spacing: -1px;
    line-height: 1.1;
}
.stat-value.orange { color: #f97316; }
.stat-value.green  { color: #22c55e; }
.stat-value.red    { color: #ef4444; }
.stat-value.yellow { color: #eab308; }

/* Verdict banner */
.verdict-banner {
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
    border: 1px solid #1e293b;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
}
.verdict-banner.green  { background: linear-gradient(135deg, #052e16 0%, #0f2a1a 100%); border-color: #166534; }
.verdict-banner.yellow { background: linear-gradient(135deg, #1c1a05 0%, #2a260f 100%); border-color: #854d0e; }
.verdict-banner.orange { background: linear-gradient(135deg, #1c1005 0%, #2a1a0f 100%); border-color: #9a3412; }
.verdict-banner.red    { background: linear-gradient(135deg, #1c0505 0%, #2a0f0f 100%); border-color: #991b1b; }
.verdict-banner.gray   { background: linear-gradient(135deg, #0f172a 0%, #111827 100%); border-color: #1e293b; }

.verdict-label {
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 4px;
}
.verdict-tier {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -1px;
}
.verdict-tier.green  { color: #22c55e; }
.verdict-tier.yellow { color: #eab308; }
.verdict-tier.orange { color: #f97316; }
.verdict-tier.red    { color: #ef4444; }
.verdict-tier.gray   { color: #64748b; }

/* Section headers */
.section-header {
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #f97316;
    margin: 1.75rem 0 0.75rem 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e293b;
}

/* AI analysis box */
.ai-box {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1525 100%);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 1.5rem;
    margin-top: 1rem;
    font-size: 0.95rem;
    line-height: 1.75;
    color: #cbd5e1;
}

/* Flag pills */
.flag-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 0.5rem; }
.flag-pill {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    padding: 4px 10px;
    border-radius: 999px;
    letter-spacing: 0.05em;
}
.flag-pill.up     { background: #052e16; color: #22c55e; border: 1px solid #166534; }
.flag-pill.down   { background: #1c0505; color: #ef4444; border: 1px solid #991b1b; }
.flag-pill.flat   { background: #0f172a; color: #94a3b8; border: 1px solid #1e293b; }
.flag-pill.nodata { background: #0f172a; color: #475569; border: 1px solid #1e293b; }

/* Input styling */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #ea580c, #f97316) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Divider */
hr { border-color: #1e293b !important; }

/* Dataframe */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0a0f1e !important;
    border-right: 1px solid #1e293b !important;
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
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
    all_teams = teams.get_teams()
    for t in all_teams:
        if t["abbreviation"] == abbr:
            return t["id"]
    return None


@st.cache_data(ttl=3600)
def get_live_roster(team_abbr: str, season: str) -> list:
    """Fetch live roster from NBA API for any team."""
    team_id = get_team_id(team_abbr)
    if not team_id:
        return []
    try:
        roster_df = commonteamroster.CommonTeamRoster(
            team_id=team_id,
            season=season,
            timeout=20,
        ).get_data_frames()[0]
        return roster_df["PLAYER"].tolist()
    except Exception:
        return []


def hit_rate(df: pd.DataFrame, line: float, side: str) -> float:
    pts = pd.to_numeric(df["PTS"], errors="coerce").dropna()
    if len(pts) == 0:
        return 0.0
    hits = (pts > line).sum() if side == "Over" else (pts < line).sum()
    return hits / len(pts)


def trend_flag(series: pd.Series, lookback: int = 3) -> str:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < lookback + 2:
        return "nodata"
    recent = s.iloc[:lookback].mean()
    prior = s.iloc[lookback:].mean()
    diff = recent - prior
    if diff >= 2:
        return "up"
    if diff <= -2:
        return "down"
    return "flat"


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


def flag_pill(label: str, flag: str) -> str:
    icon = {"up": "↑", "down": "↓", "flat": "→", "nodata": "—"}.get(flag, "—")
    css = {"up": "up", "down": "down", "flat": "flat", "nodata": "nodata"}.get(flag, "nodata")
    return f'<span class="flag-pill {css}">{label} {icon}</span>'


# ─────────────────────────────────────────────
# Chart
# ─────────────────────────────────────────────

def build_points_chart(logs: pd.DataFrame, full_name: str, line: float, avg_pts: float) -> go.Figure:
    df = logs.copy()
    df["PTS"] = pd.to_numeric(df["PTS"], errors="coerce")
    df = df.dropna(subset=["PTS"])
    df = df.sort_values("GAME_DATE", ascending=True)

    labels = df["MATCHUP"].fillna(df["GAME_DATE"].astype(str).str[:10])
    pts = df["PTS"].tolist()
    colors = ["#22c55e" if p > line else "#ef4444" for p in pts]

    fig = go.Figure()

    # Shaded over/under zones
    fig.add_hrect(y0=line, y1=max(pts) + 5, fillcolor="rgba(34,197,94,0.04)", line_width=0)
    fig.add_hrect(y0=0, y1=line, fillcolor="rgba(239,68,68,0.04)", line_width=0)

    # Points line
    fig.add_trace(go.Scatter(
        x=list(range(len(pts))),
        y=pts,
        mode="lines+markers",
        name="Points",
        line=dict(color="#60a5fa", width=2.5),
        marker=dict(color=colors, size=11, line=dict(color="#080c14", width=2)),
        hovertemplate=[
            f"<b>{labels.iloc[i]}</b><br>Points: <b>{pts[i]}</b><br>{'✅ Over' if pts[i] > line else '❌ Under'}<extra></extra>"
            for i in range(len(pts))
        ],
    ))

    # Prop line
    fig.add_hline(
        y=line, line_dash="dash", line_color="#f97316", line_width=2,
        annotation_text=f"  Line {line}", annotation_position="top left",
        annotation_font=dict(color="#f97316", size=11, family="DM Mono"),
    )

    # Average line
    fig.add_hline(
        y=avg_pts, line_dash="dot", line_color="#a78bfa", line_width=1.5,
        annotation_text=f"  Avg {avg_pts:.1f}", annotation_position="bottom left",
        annotation_font=dict(color="#a78bfa", size=11, family="DM Mono"),
    )

    fig.update_layout(
        title=None,
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(pts))),
            ticktext=[labels.iloc[i] for i in range(len(pts))],
            tickangle=-30,
            showgrid=False,
            tickfont=dict(family="DM Mono", size=10, color="#475569"),
            linecolor="#1e293b",
        ),
        yaxis=dict(
            title="PTS",
            showgrid=True,
            gridcolor="rgba(30,41,59,0.8)",
            tickfont=dict(family="DM Mono", size=10, color="#475569"),
            
        ),
        plot_bgcolor="#080c14",
        paper_bgcolor="#080c14",
        font=dict(color="#e2e8f0"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0f172a", bordercolor="#1e293b"),
        margin=dict(l=50, r=30, t=20, b=80),
        height=340,
        showlegend=False,
    )

    return fig


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

    return f"""You are a sharp NBA prop analyst. Write a clear, confident, data-driven breakdown.

Player: {full_name} | Line: {line} pts ({side}) | Last {n_games} games

GAME LOG:
{chr(10).join(game_rows)}

STATS: Avg PTS {avg_pts:.1f} | Avg MIN {avg_min:.1f} | Avg FGA {avg_fga:.1f}
Hit rate: {baseline:.0%} baseline → {adjusted:.0%} adjusted
Trends: MIN {min_flag} | FGA {fga_flag} | PTS {pts_flag}
Context: Minutes={minutes_sel} | Role={role_sel} | Shots={shots_sel} | Matchup={matchup_sel} | Script={script_sel}
Model output: {confidence_tier}

Write 3-4 paragraphs: (1) lead with prop and lean, (2) what the game log shows, (3) how context affects it tonight, (4) closing verdict. Be direct, use real numbers, write like a sharp bettor."""


def generate_ai_analysis(prompt: str) -> str:
    client = Groq(api_key=get_api_key())
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


@st.cache_data(ttl=300)
def scan_team_players(team_abbr: str, season: str) -> pd.DataFrame:
    roster = get_live_roster(team_abbr, season)
    if not roster:
        return pd.DataFrame()

    results = []
    for player_name in roster[:8]:  # scan top 8 players
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

    return pd.DataFrame(results).sort_values("Avg PTS (L10)", ascending=False).reset_index(drop=True)


# ─────────────────────────────────────────────
# Header
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

# Mobile sidebar hint
st.markdown("""
<div style='
    display:none;
    background:#0f172a;
    border:1px solid #1e293b;
    border-radius:10px;
    padding:0.6rem 1rem;
    margin-bottom:0.75rem;
    font-family:DM Mono;
    font-size:0.72rem;
    color:#94a3b8;
    align-items:center;
    gap:8px;
' class='mobile-hint'>
    ☰ st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)nbsp;Tap the <strong style='color:#f97316'>arrow</strong> in the top-left to access Settings, AI toggle, and Slate Scanner.
</div>
<style>
@media (max-width: 768px) {
    .mobile-hint { display:flex !important; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("<div class='section-header'>Settings</div>", unsafe_allow_html=True)
    manual_mode = st.checkbox("Manual input fallback")
    scan_slate = st.checkbox("Slate scanner")
    enable_ai = st.checkbox("AI breakdown", value=True)
    st.markdown("<div class='section-header'>Season</div>", unsafe_allow_html=True)
    season = st.text_input("", value="2025-26", label_visibility="collapsed")
    st.markdown("<div style='margin-top:2rem; font-family:DM Mono; font-size:0.65rem; color:#334155; line-height:1.6;'>For educational purposes only. Not financial or betting advice.</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Inputs
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Player & Prop</div>", unsafe_allow_html=True)

col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
with col_a:
    player_query = st.text_input("Player", value="Fox", placeholder="Search player...")
with col_b:
    line = st.number_input("Points Line", min_value=0.0, value=24.5, step=0.5)
with col_c:
    side = st.selectbox("Over / Under", ["Over", "Under"])
with col_d:
    n_games = st.selectbox("Sample", [5, 10, 15], index=1)

fetch = st.button("🔍  Analyze Prop", use_container_width=False)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Player selection
# ─────────────────────────────────────────────

candidate_players = search_candidates(player_query)

if len(candidate_players) == 0:
    st.error("No player found. Try a different spelling.")
    st.stop()

player_options = [p["full_name"] for p in candidate_players]
selected_player = st.selectbox("Select player", player_options, label_visibility="collapsed" if len(player_options) == 1 else "visible")
player_id, full_name = find_player_id(selected_player)

if player_id is None:
    st.error("Could not resolve player.")
    st.stop()

if not fetch and st.session_state.logs is None and not scan_slate:
    st.markdown("<div style='color:#475569; font-family:DM Mono; font-size:0.8rem; margin-top:1rem;'>↑ Enter a player and line, then click Analyze Prop.</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Fetch
# ─────────────────────────────────────────────

if fetch:
    st.session_state.ai_analysis = None
    st.session_state.ai_error = None

    try:
        with st.spinner("Fetching game logs..."):
            st.session_state.logs = fetch_with_retries(
                lambda: get_last_n_games(player_id=player_id, season=season, n=n_games)
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

    baseline = hit_rate(logs, line=line, side=side)
    avg_min  = pd.to_numeric(logs["MIN"], errors="coerce").dropna().mean()
    avg_fga  = pd.to_numeric(logs["FGA"], errors="coerce").dropna().mean()
    avg_fta  = pd.to_numeric(logs["FTA"], errors="coerce").dropna().mean()
    sample_avg_pts = pd.to_numeric(logs["PTS"], errors="coerce").dropna().mean()

    minutes_suggest = suggest_bucket(avg_min, 32, 26)
    shots_suggest   = "High" if avg_fga >= 15 else ("Low" if avg_fga < 10 else "Medium")
    role_suggest    = suggest_bucket(avg_fga + 0.5 * avg_fta, 18, 12)

    min_flag = trend_flag(logs["MIN"])
    fga_flag = trend_flag(logs["FGA"])
    pts_flag = trend_flag(logs["PTS"])

    # ── Player name + quick stats ─────────────
    st.markdown(f"<div class='section-header'>{full_name}</div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Avg PTS (L{n_games})</div>
            <div class='stat-value orange'>{sample_avg_pts:.1f}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Hit Rate</div>
            <div class='stat-value {"green" if baseline >= 0.6 else "red"}'>{baseline:.0%}</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Avg MIN (L{n_games})</div>
            <div class='stat-value'>{avg_min:.1f}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-label'>Avg FGA (L{n_games})</div>
            <div class='stat-value'>{avg_fga:.1f}</div>
        </div>""", unsafe_allow_html=True)

    # Trend flags
    flags_html = f"""<div class='flag-row'>
        {flag_pill("MIN", min_flag)}
        {flag_pill("FGA", fga_flag)}
        {flag_pill("PTS", pts_flag)}
    </div>"""
    st.markdown(flags_html, unsafe_allow_html=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Chart ─────────────────────────────────
    st.markdown("<div class='section-header'>Points Chart</div>", unsafe_allow_html=True)
    fig = build_points_chart(logs, full_name, line, sample_avg_pts)
    st.plotly_chart(fig, use_container_width=True)

    # ── Game log ──────────────────────────────
    with st.expander("📋  Game Log"):
        st.dataframe(logs.reset_index(drop=True), use_container_width=True)

    # ── Context adjuster ──────────────────────
    st.markdown("<div class='section-header'>Context</div>", unsafe_allow_html=True)

    adj_map_minutes = {"Strong": 0.05, "Okay": 0.00, "Risk": -0.07}
    adj_map_role    = {"Strong": 0.04, "Okay": 0.00, "Risk": -0.05}
    adj_map_shots   = {"High": 0.03, "Medium": 0.00, "Low": -0.05}
    adj_map_matchup = {"Good": 0.03, "Neutral": 0.00, "Bad": -0.04}
    adj_map_script  = {"Competitive": 0.02, "Neutral": 0.00, "Blowout risk": -0.04}

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        minutes_sel = st.selectbox("Minutes", ["Okay","Strong","Risk"],
                                   index=["Okay","Strong","Risk"].index(minutes_suggest))
    with c2:
        role_sel = st.selectbox("Role", ["Okay","Strong","Risk"],
                                index=["Okay","Strong","Risk"].index(role_suggest))
    with c3:
        shots_sel = st.selectbox("Shots", ["Medium","High","Low"],
                                 index=["Medium","High","Low"].index(shots_suggest))
    with c4:
        matchup_sel = st.selectbox("Matchup", ["Neutral","Good","Bad"])
    with c5:
        script_sel = st.selectbox("Script", ["Neutral","Competitive","Blowout risk"])

    adjs = Adjustments(
        minutes=adj_map_minutes[minutes_sel],
        role=adj_map_role[role_sel],
        shots=adj_map_shots[shots_sel],
        matchup=adj_map_matchup[matchup_sel],
        script=adj_map_script[script_sel],
    )

    adjusted  = max(0.0, min(1.0, baseline + adjs.total))
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

    tier_css = {
        "Strong Over": "green", "Lean Over": "yellow",
        "Lean Under": "orange", "Strong Under": "red", "Pass": "gray"
    }
    tier_emoji = {
        "Strong Over": "🟢", "Lean Over": "🟡",
        "Lean Under": "🟠", "Strong Under": "🔴", "Pass": "⚪"
    }
    css = tier_css[confidence_tier]

    # ── Verdict banner ────────────────────────
    st.markdown("<div class='section-header'>Verdict</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='verdict-banner {css}'>
        <div>
            <div class='verdict-label'>{full_name} · {line} pts · {side}</div>
            <div class='verdict-tier {css}'>{tier_emoji[confidence_tier]} {confidence_tier}</div>
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
                <div class='verdict-label'>Model Lean</div>
                <div style='font-size:1.4rem; font-weight:800; color:#f1f5f9;'>{model_lean}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI Analysis ───────────────────────────
    if enable_ai:
        st.markdown("<div class='section-header'>AI Breakdown</div>", unsafe_allow_html=True)

        api_key = get_api_key()
        if not api_key:
            st.error("❌ No GROQ_API_KEY found in Streamlit secrets.")
        else:
            if st.button("⚡  Generate AI Analysis"):
                with st.spinner("Analyzing..."):
                    try:
                        prompt = build_analysis_prompt(
                            full_name=full_name, line=line, side=side, n_games=n_games,
                            logs=logs, baseline=baseline, adjusted=adjusted,
                            confidence_tier=confidence_tier, avg_pts=sample_avg_pts,
                            avg_min=avg_min, avg_fga=avg_fga,
                            min_flag=min_flag, fga_flag=fga_flag, pts_flag=pts_flag,
                            minutes_sel=minutes_sel, role_sel=role_sel, shots_sel=shots_sel,
                            matchup_sel=matchup_sel, script_sel=script_sel,
                        )
                        st.session_state.ai_analysis = generate_ai_analysis(prompt)
                        st.session_state.ai_error = None
                    except Exception as e:
                        st.session_state.ai_error = repr(e)
                        st.session_state.ai_analysis = None

            if st.session_state.ai_analysis:
                st.markdown(f"<div class='ai-box'>{st.session_state.ai_analysis}</div>", unsafe_allow_html=True)
            elif st.session_state.ai_error:
                st.error(f"AI analysis failed: {st.session_state.ai_error}")

    # ── Export ────────────────────────────────
    st.markdown("<div class='section-header'>Export</div>", unsafe_allow_html=True)
    out = logs.copy()
    out.insert(0, "PLAYER", full_name)
    out.insert(1, "LINE", line)
    out.insert(2, "SIDE", side)
    out.insert(3, "BASELINE_HIT_RATE", baseline)
    out.insert(4, "ADJUSTED_HIT_RATE", adjusted)
    out.insert(5, "LABEL", label_from_prob(adjusted))
    csv = out.to_csv(index=False).encode("utf-8")
    st.download_button("⬇  Download CSV", data=csv, file_name="prop_report.csv", mime="text/csv")

# ─────────────────────────────────────────────
# Slate Scanner
# ─────────────────────────────────────────────

if scan_slate:
    st.markdown("<div class='section-header'>Slate Scanner</div>", unsafe_allow_html=True)
    selected_team = st.selectbox("Team", NBA_TEAMS)

    if st.button("🔎  Scan Roster"):
        with st.spinner(f"Loading {selected_team} roster and stats..."):
            df_scan = scan_team_players(selected_team, season)

        if df_scan.empty:
            st.warning("No data returned. Try again or check the season string.")
        else:
            st.dataframe(df_scan, use_container_width=True)
