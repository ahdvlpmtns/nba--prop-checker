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
    page_title="PropLens — Sports Intelligence",
    page_icon="🏀",
    layout="wide",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ══════════════════════════════════════════
   V5.0 — PropLens · Premium Sports Intelligence
   App Store Ready · Mobile-First · Elevated
══════════════════════════════════════════ */

:root {
    /* Core palette — deep navy blacks with warmth */
    --bg:       #080c14;
    --bg2:      #0d1520;
    --bg3:      #111e2e;
    --bg4:      #162033;
    --border:   rgba(255,255,255,0.06);
    --border2:  rgba(255,255,255,0.10);

    /* Electric blue — same but richer */
    --accent:   #3b82f6;
    --accent2:  #2563eb;
    --accent3:  #60a5fa;
    --accent-glow: rgba(59,130,246,0.25);

    /* Signal colors — more vivid */
    --green:    #10f590;
    --red:      #ff4560;
    --yellow:   #fbbf24;
    --orange:   #f97316;
    --purple:   #a78bfa;

    /* Typography */
    --text:     #f1f5f9;
    --text2:    #94a3b8;
    --text3:    #475569;

    /* Fonts */
    --font-display: 'Outfit', sans-serif;
    --font-body:    'Inter', sans-serif;
    --font-mono:    'JetBrains Mono', monospace;

    /* Radius system */
    --r-sm:  8px;
    --r-md:  12px;
    --r-lg:  16px;
    --r-xl:  20px;
    --r-full: 999px;

    /* Shadows */
    --shadow-sm:  0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md:  0 4px 16px rgba(0,0,0,0.5), 0 2px 6px rgba(0,0,0,0.3);
    --shadow-lg:  0 8px 32px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);
    --shadow-accent: 0 4px 24px rgba(59,130,246,0.3);
}

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    -webkit-tap-highlight-color: transparent;
    -webkit-font-smoothing: antialiased;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 4rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 900px !important;
}
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}
[data-testid="stAppViewBlockContainer"] {
    background: transparent !important;
}

/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideIn {
    from { opacity: 0; transform: translateX(-8px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pip-drop {
    0%   { transform: translateX(-50%) translateY(-6px) scale(0.5); opacity: 0; }
    70%  { transform: translateX(-50%) translateY(2px) scale(1.1); }
    100% { transform: translateX(-50%) translateY(0) scale(1); opacity: 1; }
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0; }
}
@keyframes scan {
    0%   { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
}

/* ── Header — V5.0 premium ── */
.pl-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 1.25rem 1rem 1.25rem;
    margin-bottom: 0;
    background: rgba(8,12,20,0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    animation: fadeUp 0.3s ease both;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 1px 0 var(--border), 0 4px 20px rgba(0,0,0,0.4);
}
.pl-header::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, var(--accent), transparent 60%);
}
.pl-logo-wrap { display: flex; align-items: center; gap: 14px; padding-left: 8px; }
.pl-icon {
    width: 52px; height: 44px;
    background: transparent;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
/* ── Logo animations ── */
@keyframes barGrow {
    0%   { transform: scaleY(0); }
    60%  { transform: scaleY(1.08); }
    100% { transform: scaleY(1); }
}
@keyframes ballBounce {
    0%   { transform: translateY(0px); }
    20%  { transform: translateY(-8px); }
    35%  { transform: translateY(0px); }
    50%  { transform: translateY(-4px); }
    65%  { transform: translateY(0px); }
    80%  { transform: translateY(-2px); }
    100% { transform: translateY(0px); }
}
@keyframes scanLogo {
    0%   { transform: translateX(-52px); opacity:0; }
    15%  { opacity:0.7; }
    85%  { opacity:0.7; }
    100% { transform: translateX(52px);  opacity:0; }
}
.pl-bar { transform-origin: bottom; animation: barGrow 0.5s cubic-bezier(0.34,1.56,0.64,1) both; }


.pl-bar-1 { animation-delay:0.05s; } .pl-bar-2 { animation-delay:0.10s; }
.pl-bar-3 { animation-delay:0.15s; } .pl-bar-4 { animation-delay:0.20s; }
.pl-bar-5 { animation-delay:0.25s; } .pl-bar-6 { animation-delay:0.30s; }
.pl-bar-7 { animation-delay:0.35s; }
.pl-bball { animation: ballBounce 1.0s cubic-bezier(0.36,0.07,0.19,0.97) 0.25s both; }
.pl-bbase { animation: ballBounce 1.0s cubic-bezier(0.36,0.07,0.19,0.97) 0.40s both; }
.pl-scan  { animation: scanLogo 1.6s ease-in-out 0.1s both; }

.pl-logo {
    font-family: var(--font-display) !important;
    font-size: 2rem; font-weight: 900; letter-spacing: -1px;
    color: var(--text) !important;
    line-height: 1;
    text-transform: uppercase;
    -webkit-text-fill-color: unset !important;
    background: none !important;
    -webkit-background-clip: unset !important;
}
.pl-logo span { color: var(--accent); letter-spacing: -1px; }
.pl-sub {
    font-family: var(--font-mono) !important;
    font-size: 0.52rem; color: var(--text3);
    letter-spacing: 0.2em; text-transform: uppercase; margin-top: 2px;
}
.pl-badge {
    font-family: var(--font-mono) !important;
    font-size: 0.58rem;
    background: rgba(59,130,246,0.1);
    color: var(--accent);
    font-weight: 700;
    padding: 3px 12px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: var(--r-full);
}

/* ── Ticker line below header — V5.0 ── */
.pl-ticker {
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    padding: 0.4rem 1.25rem;
    font-family: var(--font-mono);
    font-size: 0.58rem;
    color: var(--text3);
    letter-spacing: 0.12em;
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}
.pl-ticker-item { display: flex; gap: 6px; align-items: center; }
.pl-ticker-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: var(--accent);
    animation: blink 2s ease-in-out infinite;
}

/* ── Section headers — V5.0 ── */
.section-header {
    font-family: var(--font-display) !important;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--text3);
    margin: 1.75rem 0 0.75rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 8px;
}
.section-header::before {
    content: '';
    display: inline-block;
    width: 3px; height: 14px;
    background: var(--accent);
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── Stat cards — V5.0 elevated glass ── */
.stat-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 1rem 1.1rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
    animation: fadeUp 0.35s ease both;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}
.stat-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.07), transparent);
}
.stat-card:hover {
    border-color: var(--border2);
    background: var(--bg3);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}
.stat-card:active { transform: scale(0.98); }

.stat-label {
    font-family: var(--font-mono) !important;
    font-size: 0.55rem;
    color: var(--text3);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 6px;
    display: flex; align-items: center; gap: 4px;
}
.stat-label .tip {
    display: inline-flex; align-items: center; justify-content: center;
    width: 13px; height: 13px;
    background: var(--border2); color: var(--text3);
    font-size: 0.48rem; cursor: default; flex-shrink: 0;
}
.stat-value {
    font-family: var(--font-display) !important;
    font-size: 2rem; font-weight: 800;
    color: var(--text); letter-spacing: -0.5px; line-height: 1;
}
.stat-value.orange { color: var(--accent); }
.stat-value.green  { color: var(--green); }
.stat-value.red    { color: var(--red); }
.stat-value.yellow { color: var(--yellow); }
.stat-hint {
    font-family: var(--font-mono) !important;
    font-size: 0.58rem; color: var(--text3); margin-top: 5px; line-height: 1.5;
}

/* ── Defense card — V5.0 ── */
.defense-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 1rem 1.1rem; margin-bottom: 0.5rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: var(--shadow-sm);
}
.defense-badge {
    font-family: var(--font-mono) !important;
    font-size: 0.6rem; font-weight: 700;
    padding: 4px 12px; letter-spacing: 0.06em;
    text-transform: uppercase;
    border-radius: var(--r-full);
}
.defense-badge.good    { background: rgba(16,245,144,0.12); color: var(--green);  border: 1px solid rgba(16,245,144,0.25); }
.defense-badge.neutral { background: var(--bg3); color: var(--text2); border: 1px solid var(--border); }
.defense-badge.bad     { background: rgba(255,69,96,0.12);  color: var(--red);   border: 1px solid rgba(255,69,96,0.25); }

/* ── Verdict banner — V5.0 premium card ── */
.verdict-banner {
    padding: 1.25rem 1.5rem;
    margin: 0.75rem 0;
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    display: flex; align-items: flex-start;
    justify-content: space-between; flex-wrap: wrap; gap: 1rem;
    animation: fadeUp 0.4s ease both;
    position: relative;
    overflow: hidden;
    background: var(--bg2);
    box-shadow: var(--shadow-md);
    transition: transform 0.15s, box-shadow 0.2s;
}
.verdict-banner:active { transform: scale(0.99); }
.verdict-banner::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    border-radius: var(--r-lg) var(--r-lg) 0 0;
}
.verdict-banner::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.02) 0%, transparent 60%);
    pointer-events: none;
}
.verdict-banner.green  { border-color: rgba(16,245,144,0.2); background: linear-gradient(135deg,#041a0e 0%,var(--bg2) 100%); box-shadow: 0 4px 24px rgba(16,245,144,0.08); }
.verdict-banner.green::before  { background: linear-gradient(90deg,var(--green),#00c853); }
.verdict-banner.yellow { border-color: rgba(251,191,36,0.2); background: linear-gradient(135deg,#1a1200 0%,var(--bg2) 100%); box-shadow: 0 4px 24px rgba(251,191,36,0.08); }
.verdict-banner.yellow::before { background: linear-gradient(90deg,var(--yellow),#f59e0b); }
.verdict-banner.orange { border-color: rgba(249,115,22,0.2); background: linear-gradient(135deg,#1a0d00 0%,var(--bg2) 100%); box-shadow: 0 4px 24px rgba(249,115,22,0.08); }
.verdict-banner.orange::before { background: linear-gradient(90deg,var(--orange),#ea580c); }
.verdict-banner.red    { border-color: rgba(255,69,96,0.2);  background: linear-gradient(135deg,#1a0008 0%,var(--bg2) 100%); box-shadow: 0 4px 24px rgba(255,69,96,0.08); }
.verdict-banner.red::before    { background: linear-gradient(90deg,var(--red),#dc2626); }
.verdict-banner.gray   { border-color: var(--border); background: var(--bg2); }
.verdict-banner.gray::before   { background: var(--text3); }

.verdict-label {
    font-family: var(--font-mono) !important;
    font-size: 0.55rem; letter-spacing: 0.2em;
    text-transform: uppercase; color: var(--text3); margin-bottom: 5px;
}
.verdict-tier {
    font-family: var(--font-display) !important;
    font-size: 2.4rem; font-weight: 900; letter-spacing: -1px; line-height: 1;
    text-transform: uppercase;
}
.verdict-tier.green  { color: var(--green); }
.verdict-tier.yellow { color: var(--yellow); }
.verdict-tier.orange { color: var(--orange); }
.verdict-tier.red    { color: var(--red); }
.verdict-tier.gray   { color: var(--text3); }

/* ── Pills ── */
.flag-row { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 0.5rem; align-items: center; }
.flag-pill {
    font-family: var(--font-mono) !important;
    font-size: 0.6rem;
    padding: 3px 10px;
    letter-spacing: 0.06em;
    display: inline-flex; align-items: center;
    white-space: nowrap; line-height: 1.5;
    border: 1px solid transparent;
    border-radius: var(--r-full);
}
.flag-pill.up     { background: rgba(0,230,118,0.1);  color: var(--green);  border-color: rgba(0,230,118,0.2); }
.flag-pill.down   { background: rgba(255,61,87,0.1);   color: var(--red);    border-color: rgba(255,61,87,0.2); }
.flag-pill.flat   { background: var(--bg3); color: var(--text2); border-color: var(--border); }
.flag-pill.nodata { background: var(--bg3); color: var(--text3); border-color: var(--border); }

/* ── AI box — V5.0 ── */
.ai-box {
    background: var(--bg2);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: var(--r-lg);
    padding: 1.25rem 1.35rem;
    margin-top: 0.75rem;
    font-size: 0.875rem; line-height: 1.8; color: var(--text2);
    animation: fadeUp 0.4s ease both;
    position: relative;
    box-shadow: 0 4px 20px rgba(59,130,246,0.08);
}
.ai-box::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, var(--accent), transparent);
    border-radius: var(--r-lg) var(--r-lg) 0 0;
}

/* ── Explainer box ── */
.explainer {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    padding: 0.7rem 1rem;
    margin-bottom: 0.75rem;
    font-size: 0.8rem; color: var(--text2); line-height: 1.6;
}
.explainer strong { color: var(--text); }

/* ── Model note ── */
.model-note {
    background: var(--bg2); border: 1px solid var(--border);
    padding: 0.7rem 0.9rem; margin-top: 0.5rem;
    font-family: var(--font-mono) !important;
    font-size: 0.62rem; color: var(--text3); line-height: 1.6;
}

/* ── Buttons — V5.0 premium pill ── */
.stButton > button {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--r-md) !important;
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    padding: 0.8rem 1.4rem !important;
    transition: all 0.18s cubic-bezier(0.34,1.56,0.64,1) !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.35) !important;
    width: 100% !important;
    clip-path: none !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important; left: 0 !important; right: 0 !important;
    height: 1px !important;
    background: rgba(255,255,255,0.25) !important;
}
.stButton > button:hover {
    background: var(--accent2) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(59,130,246,0.45) !important;
}
.stButton > button:active {
    transform: scale(0.97) translateY(0) !important;
    box-shadow: 0 2px 8px rgba(59,130,246,0.3) !important;
}

/* ── Inputs ── */
.stSelectbox label, .stTextInput label, .stNumberInput label {
    font-family: var(--font-mono) !important;
    font-size: 0.58rem !important;
    color: var(--text3) !important;
    text-transform: uppercase;
    letter-spacing: 0.15em;
}
div[data-testid="stSelectbox"] > div > div {
    border-radius: var(--r-sm) !important;
    border-color: var(--border2) !important;
    background: var(--bg2) !important;
    color: var(--text) !important;
}
div[data-testid="stSelectbox"] > div > div > div { color: var(--text) !important; }
div[data-testid="stSelectbox"] span,
div[data-testid="stSelectbox"] p { color: var(--text) !important; }
div[data-testid="stNumberInput"] input {
    color: var(--text) !important;
    background: var(--bg2) !important;
    border-color: var(--border2) !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--font-mono) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stSelectbox"] > div:focus-within > div {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}
div[data-testid="stTextInput"] input {
    color: var(--text) !important;
    background: var(--bg2) !important;
    border-color: var(--border2) !important;
    border-radius: var(--r-sm) !important;
}
div[data-testid="stSelectbox"] input,
div[data-baseweb="select"] input,
input[aria-autocomplete="list"],
input[type="text"] {
    color: var(--text) !important;
    caret-color: var(--accent) !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li,
div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li {
    color: var(--text) !important;
    background: var(--bg2) !important;
    font-family: var(--font-body) !important;
}
div[data-baseweb="menu"] li:hover {
    background: var(--bg3) !important;
}

/* ── Tabs ── */
button[data-testid="baseButton-secondary"][key="tab_player"],
button[data-testid="baseButton-secondary"][key="tab_scanner"],
button[data-testid="baseButton-primary"][key="tab_player"],
button[data-testid="baseButton-primary"][key="tab_scanner"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    color: var(--text3) !important;
    font-family: var(--font-display) !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.5rem 0.25rem !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: color 0.2s, border-color 0.2s !important;
    text-align: left !important;
}
button[data-testid="baseButton-secondary"][key="tab_player"]:hover,
button[data-testid="baseButton-secondary"][key="tab_scanner"]:hover {
    color: var(--text) !important;
    background: transparent !important;
    box-shadow: none !important;
    transform: none !important;
    border-bottom: 2px solid var(--border2) !important;
}
button[data-testid="baseButton-primary"][key="tab_player"],
button[data-testid="baseButton-primary"][key="tab_scanner"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}
.ul-tab-bar { height: 1px; background: var(--border); margin: 0 0 0.75rem 0; }
.ul-tab-underline {
    position: absolute; top: 0; height: 2px;
    background: var(--accent);
    transition: transform 0.25s cubic-bezier(0.4,0,0.2,1);
}

/* ── Sport switcher buttons — V5.0 ── */
button[data-testid="baseButton-primary"][key="sport_nba"],
button[data-testid="baseButton-primary"][key="sport_mlb"] {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    clip-path: none !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.35) !important;
}
button[data-testid="baseButton-secondary"][key="sport_nba"],
button[data-testid="baseButton-secondary"][key="sport_mlb"] {
    background: var(--bg2) !important;
    color: var(--text3) !important;
    border: 1px solid var(--border) !important;
    clip-path: none !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    box-shadow: none !important;
}
button[data-testid="baseButton-secondary"][key="sport_nba"]:hover,
button[data-testid="baseButton-secondary"][key="sport_mlb"]:hover {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border-color: rgba(59,130,246,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ── Expanders ── */
div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    background: var(--bg2) !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] p,
div[data-testid="stExpander"] li,
div[data-testid="stExpander"] span,
div[data-testid="stExpander"] label,
div[data-testid="stExpander"] div { color: var(--text2) !important; }
div[data-testid="stExpander"] summary { color: var(--text2) !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
    overflow: hidden !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Number input ── */
div[data-testid="stNumberInput"] input {
    border-color: var(--border2) !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent) !important;
    outline: none !important;
}

/* ── Staggered animations ── */
.stat-card:nth-child(1) { animation-delay: 0.05s; }
.stat-card:nth-child(2) { animation-delay: 0.10s; }
.stat-card:nth-child(3) { animation-delay: 0.15s; }
.stat-card:nth-child(4) { animation-delay: 0.20s; }

/* ── How it works ── */
.how-it-works {
    background: var(--bg2); border: 1px solid var(--border);
    padding: 1rem 1.1rem; margin-bottom: 1rem;
}
.how-step { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 0.75rem; }
.how-step:last-child { margin-bottom: 0; }
.how-num {
    min-width: 22px; height: 22px;
    background: var(--accent); color: #0a0a0a;
    font-family: var(--font-mono) !important;
    font-size: 0.65rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.how-text { font-size: 0.82rem; color: var(--text2); line-height: 1.45; }
.how-text strong { color: var(--text); }

/* ── Clear button ── */
div[data-testid="column"]:first-child { position: relative; }
div[data-testid="column"]:first-child .stButton { position: absolute; top: 2px; right: 2px; z-index: 100; width: auto !important; }
div[data-testid="column"]:first-child .stButton > button {
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: var(--text3) !important; font-size: 0.78rem !important;
    padding: 0.3rem 0.5rem !important;
    min-width: unset !important; line-height: 1 !important;
    transform: none !important; width: auto !important;
    clip-path: none !important; text-transform: none !important;
    letter-spacing: 0 !important; font-weight: 400 !important;
}
div[data-testid="column"]:first-child .stButton > button:hover {
    color: var(--red) !important; background: rgba(255,61,87,0.08) !important;
    transform: none !important; box-shadow: none !important;
}

/* ── Secondary buttons — V5.0 ── */
button[data-testid="baseButton-secondary"] {
    background: var(--bg2) !important; color: var(--text2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--font-body) !important; font-size: 0.82rem !important;
    font-weight: 500 !important; padding: 0.5rem 0.9rem !important;
    box-shadow: var(--shadow-sm) !important; transition: all 0.15s !important;
    margin-bottom: 2px !important; width: 100% !important;
}
button[data-testid="baseButton-secondary"]:hover {
    background: var(--bg3) !important; color: var(--text) !important;
    border-color: var(--border2) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-md) !important;
}

/* ── Mobile — App Store optimized ── */
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
        padding-top: 0 !important;
        padding-bottom: 5rem !important;
    }
    .pl-logo { font-size: 1.7rem !important; }
    .stat-value { font-size: 1.7rem !important; }
    .verdict-tier { font-size: 2.2rem !important; }
    .verdict-banner {
        padding: 1.1rem 1.2rem;
        border-radius: var(--r-md);
    }
    div[data-testid="stColumn"] { padding: 0 3px !important; }
    .stButton > button {
        padding: 1rem 1.2rem !important;
        min-height: 52px !important;
        font-size: 0.9rem !important;
        border-radius: var(--r-md) !important;
    }
    .stat-card {
        border-radius: var(--r-sm) !important;
        padding: 0.85rem 0.9rem !important;
    }
    .pl-header {
        padding: 0.85rem 1rem !important;
    }
}

/* ── Verdict glow animations — V5.0 ── */
@keyframes verdict-pulse-green {
    0%, 100% { box-shadow: 0 4px 24px rgba(16,245,144,0.06), 0 0 0 1px rgba(16,245,144,0.12); }
    50%       { box-shadow: 0 8px 40px rgba(16,245,144,0.14), 0 0 0 1px rgba(16,245,144,0.2); }
}
@keyframes verdict-pulse-red {
    0%, 100% { box-shadow: 0 4px 24px rgba(255,69,96,0.06), 0 0 0 1px rgba(255,69,96,0.12); }
    50%       { box-shadow: 0 8px 40px rgba(255,69,96,0.14), 0 0 0 1px rgba(255,69,96,0.2); }
}
.verdict-banner.green { animation: fadeUp 0.4s ease both, verdict-pulse-green 3s ease-in-out 0.5s infinite; }
.verdict-banner.red   { animation: fadeUp 0.4s ease both, verdict-pulse-red   3s ease-in-out 0.5s infinite; }

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────

# Generate a unique session ID for this user session
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

for key, default in [
    ("logs", None), ("ai_analysis", None), ("ai_error", None),
    ("defense_data", None), ("tracker", []), ("active_tab", "player"),
    ("recent_players", []), ("supabase_loaded", False), ("show_share", False),
    ("active_sport", "nba"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Load tracker from Supabase on first load
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# Data layer — ESPN (schedule) + nba_api (game logs)
# ESPN for schedule: fast, reliable, no key needed
# nba_api for game logs: direct player stats, well-structured
# ─────────────────────────────────────────────

from nba_api.stats.static import players as nba_players
from nba_api.stats.endpoints import playergamelog, commonplayerinfo

# ── Cache date key — forces daily reset at midnight ET ────────
def _cache_date() -> str:
    """Returns today's date in ET — used to bust caches at midnight."""
    try:
        import pytz
        et = pytz.timezone("America/New_York")
        return datetime.now(et).strftime("%Y-%m-%d")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d")


ESPN_SITE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"

ESPN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

@st.cache_data(ttl=900, show_spinner=False)
def espn_get_cached(url: str) -> dict:
    """Cached version for parameterless ESPN calls."""
    for attempt in range(3):
        try:
            r = requests.get(url, headers=ESPN_HEADERS, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    return {}

def espn_get(url: str, params: dict = None, retries: int = 3) -> dict:
    # Use cache for parameterless calls (vast majority)
    if not params:
        return espn_get_cached(url)
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

@st.cache_data(ttl=21600, show_spinner=False)
def espn_get_all_players(_date: str = None) -> List[dict]:
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
    all_players = espn_get_all_players(_date=_cache_date())
    matches = [
        p for p in all_players
        if query_norm in normalize_name(p["full_name"])
    ]
    return sorted(matches, key=lambda x: x["full_name"].split()[-1])

def find_player(player_name: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Returns (espn_player_id, full_name, team_abbreviation)."""
    name_norm = normalize_name(player_name)
    all_players = espn_get_all_players(_date=_cache_date())
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

@st.cache_data(ttl=86400, show_spinner=False)
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

def _nba_get_game_logs_uncached(player_id: int, season: str, n: int = 10, _date: str = None) -> pd.DataFrame:
    """Internal uncached fetch — called by the cached wrapper below."""
    empty = pd.DataFrame(columns=["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A","FG3M","PLUS_MINUS","WL"])

    def _process(df):
        if df is None or df.empty:
            return None
        df = df.copy()
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
        df = df.sort_values("GAME_DATE", ascending=False).head(n).reset_index(drop=True)
        for c in ["MATCHUP","MIN","PTS","FGA","FTA","FG3A"]:
            if c not in df.columns: df[c] = None
        for c in ["FG3M"]:
            if c not in df.columns: df[c] = 0
        for c in ["PLUS_MINUS","WL"]:
            if c not in df.columns: df[c] = None
        return df[["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A","FG3M","PLUS_MINUS","WL"]]

    def _save(df):
        try: save_logs_to_supabase(player_id, season, df)
        except Exception: pass

    import requests as _req

    # ── Method 0: Supabase cache ──────────────────────────────────
    try:
        _cached = get_cached_logs_from_supabase(player_id, season)
        if _cached is not None and not _cached.empty:
            result = _process(_cached)
            if result is not None:
                return result
    except Exception:
        pass

    # ── Method 1: nba_api library ────────────────────────────────
    import concurrent.futures
    _HEADERS = {
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
    for attempt in range(3):
        try:
            def _fetch():
                try:
                    from nba_api.library.http import NBAStatsHTTP
                    NBAStatsHTTP.nba_response.headers = _HEADERS
                except Exception:
                    pass
                return playergamelog.PlayerGameLog(
                    player_id=player_id, season=season, timeout=20,
                ).get_data_frames()[0]

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                df = ex.submit(_fetch).result(timeout=22)
            result = _process(df)
            if result is not None:
                _save(result)
                return result
        except Exception:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))

    return empty


@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_playoff_game_logs_raw(player_id: int, season: str) -> pd.DataFrame:
    """
    Fetch playoff game logs from NBA Stats API.
    Cached separately with short TTL so it updates quickly after games.
    """
    _HEADERS = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
    }
    empty = pd.DataFrame(columns=["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A","FG3M","PLUS_MINUS","WL"])
    try:
        import requests as _req
        r = _req.get(
            "https://stats.nba.com/stats/playergamelog",
            params={"PlayerID": player_id, "Season": season,
                    "SeasonType": "Playoffs", "LeagueID": "00"},
            headers=_HEADERS, timeout=10
        )
        if not r.ok:
            return empty
        rs   = r.json().get("resultSets", [{}])[0]
        hdrs = rs.get("headers", [])
        rows = rs.get("rowSet", [])
        if not rows:
            return empty
        df = pd.DataFrame(rows, columns=hdrs)
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"], errors="coerce")
        for c in ["MATCHUP","MIN","PTS","FGA","FTA","FG3A"]:
            if c not in df.columns: df[c] = None
        for c in ["FG3M"]:
            if c not in df.columns: df[c] = 0
        for c in ["PLUS_MINUS","WL"]:
            if c not in df.columns: df[c] = None
        return df[["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A","FG3M","PLUS_MINUS","WL"]]
    except Exception:
        return empty


def _merge_playoff_logs(reg_logs: pd.DataFrame, player_id: int, season: str, n: int) -> pd.DataFrame:
    """
    During playoffs, merge playoff game logs on top of regular season logs.
    Playoff games sort to the top (most recent), ensuring rest/form/H2H
    all see the actual last game played including playoff games.
    Uses date check instead of _IS_PLAYOFFS to avoid forward-reference issues.
    """
    import datetime as _dtm
    _today = _dtm.date.today()
    _in_playoffs = ((_today.month == 4 and _today.day >= 14) or
                    _today.month == 5 or
                    (_today.month == 6 and _today.day <= 25))
    if not _in_playoffs:
        return reg_logs
    try:
        po_logs = _fetch_playoff_game_logs_raw(player_id, season)
        if po_logs is None or po_logs.empty:
            return reg_logs
        # Combine and re-sort by date descending, keep top n
        combined = pd.concat([po_logs, reg_logs], ignore_index=True)
        combined["GAME_DATE"] = pd.to_datetime(combined["GAME_DATE"], errors="coerce")
        combined = combined.sort_values("GAME_DATE", ascending=False).head(n).reset_index(drop=True)
        return combined
    except Exception:
        return reg_logs


@st.cache_data(ttl=1800, show_spinner=False)
def nba_get_game_logs(player_id: int, season: str, n: int = 10, _date: str = None) -> pd.DataFrame:
    """
    Cached wrapper — only caches successful (non-empty) results.
    Falls back to uncached fetch on every call if cache misses.
    TTL set to 30min during playoffs so game logs refresh quickly after games.
    """
    # Check Supabase first — fastest path
    try:
        _cached = get_cached_logs_from_supabase(player_id, season)
        if _cached is not None and not _cached.empty:
            _df = _cached.copy()
            _df["GAME_DATE"] = pd.to_datetime(_df["GAME_DATE"])
            _df = _df.sort_values("GAME_DATE", ascending=False).head(n).reset_index(drop=True)
            for c in ["MATCHUP","MIN","PTS","FGA","FTA","FG3A"]:
                if c not in _df.columns: _df[c] = None
            for c in ["FG3M"]:
                if c not in _df.columns: _df[c] = 0
            for c in ["PLUS_MINUS","WL"]:
                if c not in _df.columns: _df[c] = None
            return _df[["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A","FG3M","PLUS_MINUS","WL"]]
    except Exception:
        pass
    # Hit NBA API — result gets cached by st.cache_data only if non-empty
    result = _nba_get_game_logs_uncached(player_id, season, n, _date)
    if result is None or result.empty:
        raise RuntimeError("NBA API returned no data — do not cache this failure")
    return result

@st.cache_data(ttl=21600, show_spinner=False)
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
        info = commonplayerinfo.CommonPlayerInfo(player_id=player_id, timeout=12).get_data_frames()[0]
        return info["TEAM_ABBREVIATION"].iloc[0] if not info.empty else None
    except Exception:
        return None

def season_str_to_season(season_str: str) -> str:
    """Return season string as-is for nba_api e.g. '2025-26'."""
    return season_str.strip()

# ── H2H vs opponent ───────────────────────────

@st.cache_data(ttl=43200, show_spinner=False)
def get_h2h_logs(player_id: int, opp_abbr: str, season: str, _date: str = None) -> pd.DataFrame:
    """
    Fetch full season logs and filter for games vs opp_abbr.
    Hard 15s timeout per season, max 3 seasons.
    """
    empty = pd.DataFrame(columns=["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A","FG3M"])
    if not opp_abbr:
        return empty

    _HEADERS = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
    }

    try:
        start_year = int(season.split("-")[0])
    except Exception:
        start_year = 2025

    import concurrent.futures
    all_rows = []

    def _fetch_season(yr):
        try:
            from nba_api.library.http import NBAStatsHTTP
            NBAStatsHTTP.nba_response.headers = _HEADERS
        except Exception:
            pass
        season_str = f"{yr}-{str(yr+1)[-2:]}"
        df = playergamelog.PlayerGameLog(
            player_id=player_id, season=season_str, timeout=12,
        ).get_data_frames()[0]
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
        for c in ["MATCHUP","MIN","PTS","FGA","FTA","FG3A"]:
            if c not in df.columns:
                df[c] = None
        mask = df["MATCHUP"].astype(str).str.contains(opp_abbr, na=False)
        return df[mask][["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A"]]

    # Fetch all 3 seasons in parallel with hard timeout
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(_fetch_season, yr): yr
                   for yr in [start_year, start_year - 1, start_year - 2]}
        for future in concurrent.futures.as_completed(futures, timeout=20):
            try:
                df = future.result(timeout=15)
                if not df.empty:
                    all_rows.append(df)
            except Exception:
                pass

    if not all_rows:
        return empty

    combined = pd.concat(all_rows).sort_values("GAME_DATE", ascending=False).reset_index(drop=True)

    # In playoffs: only show this series (games since April 14)
    import datetime as _dtm2
    _today2 = _dtm2.date.today()
    _in_po2 = ((_today2.month == 4 and _today2.day >= 14) or
               _today2.month == 5 or
               (_today2.month == 6 and _today2.day <= 25))
    if _in_po2:
        try:
            _playoff_start = pd.Timestamp("2026-04-14")
            combined["GAME_DATE"] = pd.to_datetime(combined["GAME_DATE"], errors="coerce")
            series_games = combined[combined["GAME_DATE"] >= _playoff_start]
            if not series_games.empty:
                return series_games.reset_index(drop=True)
            # No playoff games found yet — return empty so it shows "no series data"
            return pd.DataFrame(columns=combined.columns)
        except Exception:
            pass

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


def series_coverage_signal(
    logs: pd.DataFrame,
    opp_abbr: Optional[str],
    line: float,
    side: str,
    season_avg: Optional[float],
) -> Tuple[str, Optional[float], int]:
    """
    How has this specific defense guarded this player IN THIS SERIES?
    Returns (signal, this_series_avg, games_count).
    Only activates in playoffs — looks at games vs opp_abbr in last 30 days.

    signal:
      "Strong"   — player has outperformed season avg vs this defense
      "Risk"     — player has underperformed vs this defense
      "Neutral"  — performance in line or insufficient data
    """
    if not _IS_PLAYOFFS or not opp_abbr or logs is None or logs.empty:
        return "Neutral", None, 0
    if "MATCHUP" not in logs.columns or "GAME_DATE" not in logs.columns:
        return "Neutral", None, 0

    try:
        opp_up   = opp_abbr.upper()
        df       = logs.copy().reset_index(drop=True)
        df["GD"] = pd.to_datetime(df["GAME_DATE"], errors="coerce")
        today    = pd.Timestamp.now().normalize()
        # Filter to games vs this opponent — in playoffs use stricter date filter
        # Only count games from playoff start (April 14) to avoid regular season contamination
        mask = df["GD"].notna() & df["MATCHUP"].astype(str).str.upper().str.contains(opp_up, na=False)
        recent_opp = df[mask].copy()
        import datetime as _dtm3
        _td3 = _dtm3.date.today()
        _in_po3 = ((_td3.month == 4 and _td3.day >= 14) or _td3.month == 5 or
                   (_td3.month == 6 and _td3.day <= 25))
        if _in_po3:
            # Only this year's playoff games vs this opponent (after April 13)
            _playoff_start = pd.Timestamp("2026-04-14").normalize()
            recent_opp = recent_opp[recent_opp["GD"].dt.normalize() >= _playoff_start]
        else:
            recent_opp = recent_opp[(today - recent_opp["GD"].dt.normalize()).dt.days <= 30]
        if recent_opp.empty:
            return "Neutral", None, 0

        pts = pd.to_numeric(recent_opp["PTS"], errors="coerce").dropna()
        if len(pts) == 0:
            return "Neutral", None, 0

        series_avg = float(pts.mean())
        n = len(pts)

        # Compare to season avg if available, otherwise to line
        benchmark = season_avg if season_avg else line

        if side == "Over":
            if series_avg > benchmark + 2 and series_avg > line:
                return "Strong", series_avg, n
            if series_avg < benchmark - 2 or series_avg < line - 2:
                return "Risk", series_avg, n
        else:  # Under
            if series_avg < benchmark - 2 and series_avg < line:
                return "Strong", series_avg, n
            if series_avg > benchmark + 2 or series_avg > line + 2:
                return "Risk", series_avg, n
        return "Neutral", series_avg, n
    except Exception:
        return "Neutral", None, 0


# ── Back-to-back detection ────────────────────

def detect_b2b(logs: pd.DataFrame, game_date: Optional[str]) -> str:
    """
    Returns 'B2B' if tonight's game is the day after a logged game, else 'Normal'.
    Uses game_date (next game date string) + logs to check.
    """
    if game_date is None or logs is None or logs.empty:
        return "Normal"

    try:
        tonight   = pd.to_datetime(game_date)
        log_dates = pd.to_datetime(logs["GAME_DATE"], errors="coerce").dropna()
        yesterday = tonight - pd.Timedelta(days=1)
        if any(abs((d - yesterday).days) == 0 for d in log_dates):
            return "B2B"
        return "Normal"
    except Exception:
        return "Normal"


def detect_rest_days(logs: pd.DataFrame, game_date: Optional[str]) -> str:
    """
    Returns rest days signal based on days since last game.
    - 'B2B'      → 0 days rest (handled by detect_b2b)
    - 'Short'    → 1 day rest (played 2 days ago)
    - 'Normal'   → 2 days rest
    - 'Rested'   → 3+ days rest → small scoring boost

    Research shows players score ~2-3 pts more with 3+ days rest.
    """
    if game_date is None or logs is None or logs.empty:
        return "Normal"

    try:
        tonight   = pd.to_datetime(game_date)
        log_dates = pd.to_datetime(logs["GAME_DATE"], errors="coerce").dropna()
        if log_dates.empty:
            return "Normal"

        last_game  = log_dates.max()
        days_since = (tonight - last_game).days

        if days_since <= 1:
            return "B2B"      # handled by b2b signal
        elif days_since == 2:
            return "Short"    # 1 full day rest — slightly tired
        elif days_since == 3:
            return "Normal"   # 2 days rest — standard
        else:
            return "Rested"   # 3+ days rest — fresh legs
    except Exception:
        return "Normal"


def minutes_adjusted_scoring(
    avg_pts: float,
    season_avg_min: Optional[float],
    recent_avg_min: float,
    line: float,
    side: str,
) -> str:
    """
    Adjusts the matchup/role signal based on minutes restriction.

    If a player is playing significantly fewer minutes than their season average,
    their expected scoring should scale down proportionally.

    Returns an override signal: "Risk", "Okay", or None (no override needed).
    """
    if season_avg_min is None or season_avg_min < 10 or recent_avg_min < 5:
        return None

    minutes_ratio = recent_avg_min / season_avg_min

    # Significant restriction: playing ≥20% fewer minutes than season avg
    if minutes_ratio <= 0.80:
        # Scale expected points by minutes ratio
        expected_pts = avg_pts * minutes_ratio
        edge_with_restriction = expected_pts - line

        # If restriction pushes expected pts below line → Risk signal for Over
        if side == "Over" and edge_with_restriction < -1.0:
            return "Risk"
        # If restriction pushes expected pts well below line → boost Under
        elif side == "Under" and edge_with_restriction < -3.0:
            return "Strong"
    return None

def season_str_to_int(season_str: str) -> int:
    """Convert '2025-26' -> 2025 for ESPN year param."""
    try:
        return int(season_str.split("-")[0])
    except Exception:
        return 2025

# ── Season average fetch + divergence signal ─────────────────────

@st.cache_data(ttl=1800, show_spinner=False)
def nba_get_full_season_logs_cached(player_id: int, season: str, _date: str = None) -> Optional[pd.DataFrame]:
    """
    Fetch full season game log via direct REST API. Cached 24hrs.
    Used for season avg pts and avg min calculations.
    """
    _URL = "https://stats.nba.com/stats/playergamelog"
    _HEADERS = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
        "Connection": "keep-alive",
    }
    import requests as _req
    for attempt in range(2):
        try:
            r = _req.get(_URL, headers=_HEADERS, params={
                "PlayerID": player_id,
                "Season": season,
                "SeasonType": "Regular Season",
                "LeagueID": "00",
            }, timeout=12)
            r.raise_for_status()
            data    = r.json()
            headers = data["resultSets"][0]["headers"]
            rows    = data["resultSets"][0]["rowSet"]
            if rows:
                return pd.DataFrame(rows, columns=headers)
        except Exception:
            if attempt == 0:
                time.sleep(1)
    return None


def nba_get_season_avg(player_id: int, season: str, logs_l10: pd.DataFrame = None) -> Optional[float]:
    """
    Get season avg pts. Uses cached full season log.
    Falls back to L10 sample if API is slow — still useful for form divergence.
    """
    # Fast path: use already-fetched L10 as approximation if full season unavailable
    df = nba_get_full_season_logs_cached(player_id, season)
    if df is not None:
        pts = pd.to_numeric(df["PTS"], errors="coerce").dropna()
        if len(pts) >= 5:
            return round(float(pts.mean()), 1)
    # Fallback to L10 sample
    if logs_l10 is not None and not logs_l10.empty:
        pts = pd.to_numeric(logs_l10["PTS"], errors="coerce").dropna()
        if len(pts) >= 3:
            return round(float(pts.mean()), 1)
    return None


def nba_get_season_avg_min(player_id: int, season: str, logs_l10: pd.DataFrame = None) -> Optional[float]:
    """
    Get season avg minutes. Uses cached full season log.
    Falls back to L10 sample if API is slow.
    """
    df = nba_get_full_season_logs_cached(player_id, season)
    if df is not None:
        mins = pd.to_numeric(df["MIN"], errors="coerce").dropna()
        if len(mins) >= 5:
            return round(float(mins.mean()), 1)
    # Fallback to L10 sample
    if logs_l10 is not None and not logs_l10.empty:
        mins = pd.to_numeric(logs_l10["MIN"], errors="coerce").dropna()
        if len(mins) >= 3:
            return round(float(mins.mean()), 1)
    return None


def minutes_restriction_alert(
    recent_avg_min: float,
    season_avg_min: Optional[float],
    last_3_mins: Optional[list],
) -> str:
    """
    Detect if a player's minutes have dropped significantly recently,
    which may indicate injury recovery, load management, or a role change.
    Returns an HTML alert string or empty string if no concern.
    """
    # In playoffs nobody rests — suppress load management warning
    if _IS_PLAYOFFS:
        return ""

    if season_avg_min is None or season_avg_min < 10:
        return ""

    # Check L3 average vs season average
    if last_3_mins and len(last_3_mins) >= 2:
        l3_avg = sum(last_3_mins) / len(last_3_mins)
        drop = season_avg_min - l3_avg

        if drop >= 7:
            severity = "significant"
            bg, border, color = "#1c1005", "#854d0e", "#f97316"
            icon = "⚠️"
        elif drop >= 4:
            severity = "moderate"
            bg, border, color = "#0c1018", "#243044", "#60a5fa"
            icon = "📉"
        else:
            return ""

        return (
            f"<div style='background:{bg};border:1px solid {border};border-radius:10px;"
            f"padding:0.65rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:10px;'>"
            f"<span style='font-size:1.1rem;'>{icon}</span>"
            f"<div style='font-family:DM Mono;font-size:0.7rem;'>"
            f"<span style='color:{color};font-weight:800;text-transform:uppercase;letter-spacing:0.08em;'>"
            f"Minutes restriction detected</span>"
            f"<span style='color:#475569;'> · L3 avg {l3_avg:.1f} min vs season avg {season_avg_min:.1f} min "
            f"({drop:+.1f}) — possible injury or load management</span>"
            f"</div>"
            f"</div>"
        )
    return ""


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

@st.cache_data(ttl=1800, show_spinner=False)
@st.cache_data(ttl=1800, show_spinner=False)
def espn_get_player_news(player_name: str) -> list:
    """
    Fetch latest news headlines for a player from ESPN.
    Returns list of {headline, description, date} dicts.
    No API key needed.
    """
    try:
        import requests as _req
        # Search ESPN for the player
        r = _req.get(
            "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news",
            params={"limit": 50},
            timeout=6
        )
        if not r.ok:
            return []
        articles = r.json().get("articles", [])
        # Filter for articles mentioning this player
        name_parts = player_name.lower().split()
        last_name  = name_parts[-1] if name_parts else ""
        first_name = name_parts[0]  if name_parts else ""
        results = []
        for a in articles:
            headline = a.get("headline", "")
            desc     = a.get("description", "") or a.get("summary", "")
            text     = (headline + " " + desc).lower()
            if last_name in text and (len(last_name) > 4 or first_name in text):
                # Parse date
                date_str = a.get("published", "")[:10]
                results.append({
                    "headline":    headline,
                    "description": desc,
                    "date":        date_str,
                    "link":        a.get("links", {}).get("web", {}).get("href", ""),
                })
            if len(results) >= 3:
                break
        return results
    except Exception:
        return []


@st.cache_data(ttl=900, show_spinner=False)
def espn_get_last_game_date(team_abbr: str) -> Optional[str]:
    """
    Returns the date of the team's most recent completed game from ESPN.
    Much more reliable than game logs for rest detection — updates immediately.
    Returns date string 'YYYY-MM-DD' or None.
    """
    if not team_abbr:
        return None
    try:
        import pytz
        et    = pytz.timezone("America/New_York")
        today = datetime.now(et).date()
    except Exception:
        today = datetime.today().date()

    _ESPN_REVERSE = {
        "GSW":"GS","SAS":"SA","NYK":"NY","NOP":"NO",
        "UTA":"UTAH","PHX":"PHX","MEM":"MEM","OKC":"OKC",
    }
    _candidates = {team_abbr, _ESPN_REVERSE.get(team_abbr, team_abbr)}

    def _team_matches(abbr: str) -> bool:
        return abbr == team_abbr or _norm_team_abbr(abbr) == team_abbr or abbr in _candidates

    # Look back up to 10 days for most recent completed game
    for offset in range(1, 11):
        check    = today - timedelta(days=offset)
        date_str = check.strftime("%Y%m%d")
        try:
            data   = espn_get(f"{ESPN_SITE}/scoreboard", params={"dates": date_str})
            events = data.get("events", [])
            for ev in events:
                status = ev.get("status", {}).get("type", {}).get("name", "")
                if "final" not in status.lower() and "complete" not in status.lower():
                    continue
                comps       = ev.get("competitions", [{}])[0]
                competitors = comps.get("competitors", [])
                my_comp = next(
                    (c for c in competitors
                     if _team_matches(c.get("team", {}).get("abbreviation", ""))),
                    None
                )
                if my_comp:
                    return check.strftime("%Y-%m-%d")
        except Exception:
            continue
    return None


def espn_get_next_game(team_abbr: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Find next upcoming game for a team using ESPN scoreboard.
    Returns (opp_abbr, game_date_str, venue).
    Skips completed games. Handles ESPN abbreviation mismatches.
    """
    if not team_abbr:
        return None, None, None

    try:
        import pytz
        et    = pytz.timezone("America/New_York")
        today = datetime.now(et).date()
    except Exception:
        today = datetime.today().date()

    # ESPN uses different abbreviations — build reverse lookup
    # so GSW→GS, SAS→SA, NYK→NY, etc.
    _ESPN_REVERSE = {
        "GSW": "GS", "SAS": "SA", "NYK": "NY", "NOP": "NO",
        "UTA": "UTAH", "PHX": "PHX", "MEM": "MEM", "OKC": "OKC",
    }
    # Candidates to match against — try normalized and ESPN variants
    _candidates = {team_abbr, _ESPN_REVERSE.get(team_abbr, team_abbr)}

    def _team_matches(abbr: str) -> bool:
        return (abbr == team_abbr or
                _norm_team_abbr(abbr) == team_abbr or
                abbr in _candidates)

    for offset in range(10):
        check    = today + timedelta(days=offset)
        date_str = check.strftime("%Y%m%d")
        try:
            data   = espn_get(f"{ESPN_SITE}/scoreboard", params={"dates": date_str})
            events = data.get("events", [])
            for ev in events:
                comps       = ev.get("competitions", [{}])[0]
                competitors = comps.get("competitors", [])

                # Skip if final/completed
                status = ev.get("status", {}).get("type", {}).get("name", "")
                if "final" in status.lower() or "complete" in status.lower():
                    continue

                # Find our team using fuzzy abbreviation match
                my_comp = next(
                    (c for c in competitors
                     if _team_matches(c.get("team", {}).get("abbreviation", ""))),
                    None
                )
                if not my_comp:
                    continue

                # Find opponent
                opp_comp = next(
                    (c for c in competitors if c is not my_comp), None
                )
                if not opp_comp:
                    continue

                opp_abbr_raw   = opp_comp.get("team", {}).get("abbreviation", "")
                opp_abbr_found = _norm_team_abbr(opp_abbr_raw)
                home_away      = "Home" if my_comp.get("homeAway", "") == "home" else "Away"
                game_date_str  = check.strftime("%b %d, %Y")

                return opp_abbr_found, game_date_str, home_away
        except Exception:
            continue

    return None, None, None

# ── Opponent defense rating ───────────────────

@st.cache_data(ttl=21600, show_spinner=False)
def espn_get_opp_pts_allowed(opp_abbr: str, _date: str = None) -> Optional[float]:
    """
    Calculate pts allowed per game. Tries NBA Stats API first (most reliable),
    falls back to ESPN scoreboard scrape.
    """
    # Method 1: NBA Stats leaguedashteamstats — direct pts allowed
    _NBA_ABBR_TO_ID = {
        "ATL":1610612737,"BOS":1610612738,"BKN":1610612751,"CHA":1610612766,
        "CHI":1610612741,"CLE":1610612739,"DAL":1610612742,"DEN":1610612743,
        "DET":1610612765,"GSW":1610612744,"HOU":1610612745,"IND":1610612754,
        "LAC":1610612746,"LAL":1610612747,"MEM":1610612763,"MIA":1610612748,
        "MIL":1610612749,"MIN":1610612750,"NOP":1610612740,"NYK":1610612752,
        "OKC":1610612760,"ORL":1610612753,"PHI":1610612755,"PHX":1610612756,
        "POR":1610612757,"SAC":1610612758,"SAS":1610612759,"TOR":1610612761,
        "UTA":1610612762,"WAS":1610612764,
    }
    try:
        import requests as _req
        _hdrs = {"User-Agent":"Mozilla/5.0","Referer":"https://www.nba.com/",
                 "x-nba-stats-origin":"stats","x-nba-stats-token":"true","Accept":"application/json"}
        r = _req.get(
            "https://stats.nba.com/stats/leaguedashteamstats",
            params={"Season":"2025-26","SeasonType":"Playoffs" if _date is None else "Regular Season",
                    "PerMode":"PerGame","MeasureType":"Base","LeagueID":"00"},
            headers=_hdrs, timeout=8
        )
        if r.ok:
            rs = r.json().get("resultSets",[{}])[0]
            hs = rs.get("headers",[])
            rows = rs.get("rowSet",[])
            if hs and rows:
                abbr_i = hs.index("TEAM_ABBREVIATION") if "TEAM_ABBREVIATION" in hs else -1
                opp_i  = hs.index("OPP_PTS") if "OPP_PTS" in hs else -1
                if abbr_i >= 0 and opp_i >= 0:
                    for row in rows:
                        if str(row[abbr_i]).upper() == opp_abbr.upper():
                            val = float(row[opp_i])
                            if val > 80:
                                return round(val, 1)
    except Exception:
        pass
    # Method 2: ESPN scoreboard scrape (original method)
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

@st.cache_data(ttl=3600, show_spinner=False)
def get_opp_recent_defensive_form(opp_abbr: str) -> dict:
    """
    Compare opponent's last 5 games pts allowed vs their L15 season avg.
    Returns dict with:
      - recent_avg: pts allowed in last 5 games
      - season_avg: pts allowed in last 15 games
      - trend: "Tightening" | "Neutral" | "Softening"
      - diff: recent_avg - season_avg (positive = allowing more = worse defense)
    """
    empty = {"recent_avg": None, "season_avg": None, "trend": "Neutral", "diff": 0}
    if not opp_abbr:
        return empty
    try:
        import pytz
        et    = pytz.timezone("America/New_York")
        today = datetime.now(et).date()

        pts_by_game = []   # (date, pts_allowed) newest first
        for offset in range(1, 40):
            if len(pts_by_game) >= 15:
                break
            check    = today - timedelta(days=offset)
            date_str = check.strftime("%Y%m%d")
            try:
                data   = espn_get(f"{ESPN_SITE}/scoreboard", params={"dates": date_str})
                events = data.get("events", [])
                for ev in events:
                    comp        = ev.get("competitions", [{}])[0]
                    competitors = comp.get("competitors", [])
                    team_comp   = next(
                        (c for c in competitors
                         if c.get("team", {}).get("abbreviation", "") == opp_abbr),
                        None
                    )
                    if not team_comp:
                        continue
                    status = ev.get("status", {}).get("type", {}).get("name", "")
                    if "final" not in status.lower() and "complete" not in status.lower():
                        continue
                    opp_comp = next(
                        (c for c in competitors
                         if c.get("team", {}).get("abbreviation", "") != opp_abbr),
                        None
                    )
                    if opp_comp:
                        try:
                            pts_by_game.append(float(opp_comp.get("score", 0)))
                        except Exception:
                            pass
            except Exception:
                continue

        if len(pts_by_game) < 5:
            return empty

        recent_5  = pts_by_game[:5]
        season_15 = pts_by_game[:15]
        recent_avg = sum(recent_5) / len(recent_5)
        season_avg = sum(season_15) / len(season_15)
        diff = recent_avg - season_avg

        # Tightening = allowing fewer pts recently = better defense
        # Softening  = allowing more pts recently = worse defense
        if diff <= -3.0:
            trend = "Tightening"   # defense locking in — harder to score
        elif diff >= 3.0:
            trend = "Softening"    # defense breaking down — easier to score
        else:
            trend = "Neutral"

        return {
            "recent_avg": round(recent_avg, 1),
            "season_avg": round(season_avg, 1),
            "trend":      trend,
            "diff":       round(diff, 1),
        }
    except Exception:
        return empty


# ── Game number in series adjustment ────────────────────────────────
def get_series_game_number(series_wins: int, series_losses: int) -> int:
    """Returns the current game number in the series (1-7)."""
    return series_wins + series_losses + 1

def game_number_adjustment(game_num: int, side: str) -> Tuple[str, float]:
    """
    Apply scoring adjustment based on game number in playoff series.
    Returns (label, adjustment) where adjustment is additive pp.

    Game 1: conservative, feeling-out period → lower scoring
    Games 2-5: normal playoff intensity
    Game 6-7: pressure reduces scoring, starters may be fatigued
    """
    if not _IS_PLAYOFFS:
        return "N/A", 0.0

    _flip = 1.0 if side == "Over" else -1.0

    if game_num == 1:
        return "Game 1 (feeling out)", -0.03 * _flip
    elif game_num in (2, 3, 4, 5):
        return f"Game {game_num} (normal)", 0.0
    elif game_num == 6:
        return "Game 6 (pressure)", -0.02 * _flip
    elif game_num >= 7:
        return "Game 7 (max pressure)", -0.03 * _flip
    return "Normal", 0.0


# ── Playoff usage spike detector ────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_playoff_game_logs(player_id: int, season: str) -> pd.DataFrame:
    """
    Fetch playoff game logs for a player.
    Uses NBA Stats API with SeasonType=Playoffs.
    """
    _URL = "https://stats.nba.com/stats/playergamelog"
    _HEADERS = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
    }
    try:
        import requests as _req
        r = _req.get(_URL, headers=_HEADERS, params={
            "PlayerID":   player_id,
            "Season":     season,
            "SeasonType": "Playoffs",
            "LeagueID":   "00",
        }, timeout=10)
        if not r.ok:
            return pd.DataFrame()
        rs = r.json().get("resultSets", [{}])[0]
        headers = rs.get("headers", [])
        rows    = rs.get("rowSet", [])
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows, columns=headers)
    except Exception:
        return pd.DataFrame()


def playoff_usage_spike_signal(
    player_id: int,
    season: str,
    reg_avg_pts: float,
    reg_avg_min: float,
    line: float,
    side: str,
) -> Tuple[str, Optional[float], Optional[float]]:
    """
    Compare player's current playoff stats (this postseason) vs regular season.
    Returns (signal, playoff_avg_pts, playoff_avg_min).

    signal:
      "Spike"   — scoring/minutes significantly up in playoffs → boost Over
      "Drop"    — scoring/minutes down in playoffs → penalize Over
      "Neutral" — consistent with regular season
    """
    if not _IS_PLAYOFFS:
        return "Neutral", None, None

    try:
        logs = get_playoff_game_logs(player_id, season)
        if logs.empty or "PTS" not in logs.columns:
            return "Neutral", None, None

        pts = pd.to_numeric(logs["PTS"], errors="coerce").dropna()
        mins = pd.to_numeric(logs["MIN"], errors="coerce").dropna()

        if len(pts) < 2:
            return "Neutral", None, None

        playoff_avg_pts = float(pts.mean())
        playoff_avg_min = float(mins.mean()) if len(mins) >= 2 else None

        pts_diff = playoff_avg_pts - reg_avg_pts
        min_diff = (playoff_avg_min - reg_avg_min) if playoff_avg_min and reg_avg_min else 0

        _flip = 1.0 if side == "Over" else -1.0

        # Spike: scoring AND minutes both up significantly
        if pts_diff >= 3.0 and min_diff >= 2.0:
            return "Spike", playoff_avg_pts, playoff_avg_min
        # Partial spike: just scoring up (usage increase, not minutes)
        if pts_diff >= 3.0:
            return "Spike", playoff_avg_pts, playoff_avg_min
        # Drop: scoring down — coach tightened rotation or player struggling
        if pts_diff <= -3.0:
            return "Drop", playoff_avg_pts, playoff_avg_min

        return "Neutral", playoff_avg_pts, playoff_avg_min
    except Exception:
        return "Neutral", None, None


# ── Supabase ──────────────────────────────────────────────────

def get_supabase_client():
    """Get Supabase client using credentials from Streamlit secrets."""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        import requests as _req

        class _SupabaseClient:
            def __init__(self, url, key):
                self.url  = url.rstrip("/")
                self.key  = key
                self.hdrs = {
                    "apikey":        key,
                    "Authorization": f"Bearer {key}",
                    "Content-Type":  "application/json",
                    "Prefer":        "return=representation",
                }

            def select(self, table, filters=None):
                url = f"{self.url}/rest/v1/{table}?order=created_at.desc"
                if filters:
                    for k, v in filters.items():
                        url += f"&{k}=eq.{v}"
                r = _req.get(url, headers=self.hdrs, timeout=10)
                return r.json() if r.ok else []

            def insert(self, table, data):
                r = _req.post(
                    f"{self.url}/rest/v1/{table}",
                    headers=self.hdrs, json=data, timeout=10
                )
                return r.json() if r.ok else None

            def update(self, table, row_id, data):
                r = _req.patch(
                    f"{self.url}/rest/v1/{table}?id=eq.{row_id}",
                    headers=self.hdrs, json=data, timeout=10
                )
                return r.ok

            def delete(self, table, row_id):
                r = _req.delete(
                    f"{self.url}/rest/v1/{table}?id=eq.{row_id}",
                    headers=self.hdrs, timeout=10
                )
                return r.ok

            def delete_all(self, table, session_id):
                r = _req.delete(
                    f"{self.url}/rest/v1/{table}?session_id=eq.{session_id}",
                    headers=self.hdrs, timeout=10
                )
                return r.ok

        return _SupabaseClient(url, key)
    except Exception:
        return None


def get_cached_logs_from_supabase(player_id: int, season: str) -> Optional[pd.DataFrame]:
    """Check Supabase for today's already-fetched game logs. Returns df or None."""
    try:
        sb = get_supabase_client()
        if not sb:
            return None
        import requests as _req, json as _json
        hdrs = {
            "apikey":        sb.key,
            "Authorization": f"Bearer {sb.key}",
            "Content-Type":  "application/json",
        }
        url = (f"{sb.url}/rest/v1/game_logs_cache"
               f"?player_id=eq.{player_id}"
               f"&season=eq.{season}"
               f"&fetch_date=eq.{_cache_date()}"
               f"&select=logs_json"
               f"&limit=1")
        r = _req.get(url, headers=hdrs, timeout=5)
        if not r.ok:
            return None
        rows = r.json()
        if not rows:
            return None
        data = _json.loads(rows[0]["logs_json"])
        df = pd.DataFrame(data)
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
        return df
    except Exception:
        return None


def save_logs_to_supabase(player_id: int, season: str, df: pd.DataFrame) -> bool:
    """Save today's game logs to Supabase. Uses upsert to avoid duplicates."""
    try:
        sb = get_supabase_client()
        if not sb:
            return False
        import requests as _req
        hdrs = {
            "apikey":        sb.key,
            "Authorization": f"Bearer {sb.key}",
            "Content-Type":  "application/json",
            "Prefer":        "resolution=merge-duplicates,return=minimal",
        }
        logs_json = df.to_json(orient="records", date_format="iso")
        r = _req.post(
            f"{sb.url}/rest/v1/game_logs_cache",
            headers=hdrs,
            json={
                "player_id":  player_id,
                "season":     season,
                "fetch_date": _cache_date(),
                "logs_json":  logs_json,
            },
            timeout=6,
        )
        return r.ok
    except Exception:
        return False


def load_tracker_from_supabase(session_id: str) -> list:
    """Load tracker entries for this session from Supabase."""
    try:
        sb = get_supabase_client()
        if not sb:
            return []
        rows = sb.select("prop_tracker", {"session_id": session_id})
        if not rows or not isinstance(rows, list):
            return []
        return [{
            "id":          r.get("id"),
            "Player":      r.get("player", ""),
            "Line":        r.get("line", ""),
            "Opponent":    r.get("opponent", "—"),
            "Matchup":     r.get("matchup", ""),
            "Venue":       r.get("venue", ""),
            "Avg PTS":     r.get("avg_pts", 0),
            "Hit Rate":    r.get("hit_rate", ""),
            "Adjusted":    r.get("adjusted", ""),
            "Consistency": r.get("consistency", ""),
            "Verdict":     r.get("verdict", ""),
            "Result":      r.get("result", "Pending"),
        } for r in rows]
    except Exception:
        return []


def save_to_supabase(session_id: str, entry: dict) -> str:
    """Save a tracker entry to Supabase. Returns the new row id."""
    try:
        sb = get_supabase_client()
        if not sb:
            return None
        row = {
            "session_id":  session_id,
            "player":      entry.get("Player", ""),
            "line":        entry.get("Line", ""),
            "opponent":    entry.get("Opponent", "—"),
            "matchup":     entry.get("Matchup", ""),
            "venue":       entry.get("Venue", ""),
            "avg_pts":     float(entry.get("Avg PTS", 0)),
            "hit_rate":    entry.get("Hit Rate", ""),
            "adjusted":    entry.get("Adjusted", ""),
            "consistency": entry.get("Consistency", ""),
            "verdict":     entry.get("Verdict", ""),
            "result":      entry.get("Result", "Pending"),
        }
        result = sb.insert("prop_tracker", row)
        if result and isinstance(result, list) and len(result) > 0:
            return result[0].get("id")
        return None
    except Exception:
        return None


def update_result_in_supabase(row_id: str, result: str) -> bool:
    """Update the result (Hit/Miss/Pending) of a tracker entry."""
    try:
        sb = get_supabase_client()
        if not sb:
            return False
        return sb.update("prop_tracker", row_id, {"result": result})
    except Exception:
        return False


def delete_from_supabase(row_id: str) -> bool:
    """Delete a tracker entry from Supabase."""
    try:
        sb = get_supabase_client()
        if not sb:
            return False
        return sb.delete("prop_tracker", row_id)
    except Exception:
        return False


# ── Auto prop result detection ───────────────────────────────

def auto_detect_result(entry: dict) -> Optional[str]:
    """
    Check if a tracked prop has a result by looking at the player's
    most recent game log. Returns 'Hit', 'Miss', or None if game
    hasn't been played yet.
    """
    try:
        player_name = entry.get("Player", "")
        line_str    = entry.get("Line", "")  # e.g. "24.5 Over" or "17.0 Under"

        if not player_name or not line_str:
            return None

        # Parse line and side
        parts = line_str.strip().split()
        if len(parts) < 2:
            return None
        try:
            line_val = float(parts[0])
        except ValueError:
            return None
        side = parts[1] if len(parts) > 1 else "Over"

        # Find player ID
        nba_id, _ = nba_find_player(player_name)
        if not nba_id:
            return None

        # Get most recent game log (uses cache)
        from datetime import datetime, timedelta
        import pytz
        et  = pytz.timezone("America/New_York")
        now = datetime.now(et)

        # Reuse the n=15 cache — just take head(1)
        _det_logs = nba_get_game_logs(nba_id, "2025-26", n=15, _date=_cache_date())
        logs = _det_logs.head(1) if _det_logs is not None and not _det_logs.empty else _det_logs
        if logs.empty:
            return None

        # Check if the most recent game was today or yesterday
        last_game_date = pd.to_datetime(logs.iloc[0]["GAME_DATE"])
        days_ago = (now.date() - last_game_date.date()).days

        # Only auto-detect if game was within last 2 days
        if days_ago > 2:
            return None

        # Get actual points
        actual_pts = pd.to_numeric(logs.iloc[0]["PTS"], errors="coerce")
        if pd.isna(actual_pts):
            return None

        # Determine result
        if side == "Over":
            return "Hit" if actual_pts >= line_val else "Miss"
        else:
            return "Hit" if actual_pts <= line_val else "Miss"

    except Exception:
        return None


# ── Injury status ─────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)  # refresh every 5 mins — injury status can change fast
def get_player_injury_status(player_name: str) -> Tuple[str, str]:
    """
    Fetch current NBA injury status for a player.
    Returns (status, reason) where status is one of:
      'Out', 'Doubtful', 'Questionable', 'Probable', 'Active', 'Unknown'

    Sources tried in order:
    1. NBA official injury report via nbainjuries package
    2. ESPN injuries endpoint as fallback
    """
    norm = normalize_name(player_name)

    # ── Source 1: nbainjuries package (NBA official data) ──
    try:
        from nbainjuries import injury
        from datetime import datetime
        import pytz
        et = pytz.timezone("America/New_York")
        now = datetime.now(et)
        report = injury.get_reportdata(now)
        if report:
            for entry in report:
                entry_name = normalize_name(entry.get("Player Name", ""))
                # NBA report uses "Last, First" format
                parts = entry_name.split(", ")
                if len(parts) == 2:
                    entry_name = f"{parts[1]} {parts[0]}"
                if norm in entry_name or entry_name in norm:
                    status = entry.get("Current Status", "Unknown")
                    reason = entry.get("Reason", "")
                    return status, reason
    except Exception:
        pass

    # ── Source 2: ESPN injuries endpoint ──
    try:
        data = espn_get(f"{ESPN_SITE}/injuries")
        for team in data.get("injuries", []):
            for item in team.get("injuries", []):
                ath  = item.get("athlete", {})
                name = normalize_name(ath.get("displayName", ""))
                if norm in name or name in norm:
                    status = item.get("status", "Unknown")
                    detail = item.get("shortComment", item.get("longComment", ""))
                    return status, detail
    except Exception:
        pass

    # ── Source 3: ESPN team-specific injuries ──
    # More reliable — fetches per team roster injury data
    try:
        # Find the player's ESPN team first
        all_players = espn_get_all_players(_date=_cache_date())
        ep = next((p for p in all_players if normalize_name(p["full_name"]) == norm), None)
        if ep:
            team_id = None
            # Get team ID from team abbr
            teams_data = espn_get(f"{ESPN_SITE}/teams")
            teams_list = (
                teams_data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
                or teams_data.get("teams", [])
            )
            for t in teams_list:
                team = t.get("team", t)
                if team.get("abbreviation", "") == ep["team_abbr"]:
                    team_id = team.get("id")
                    break
            if team_id:
                roster = espn_get(f"{ESPN_SITE}/teams/{team_id}/roster")
                for athlete in roster.get("athletes", []):
                    for item in (athlete.get("items") or [athlete]):
                        aname = normalize_name(item.get("displayName", ""))
                        if norm in aname or aname in norm:
                            injuries = item.get("injuries", [])
                            if injuries:
                                inj = injuries[0]
                                status = inj.get("status", "Unknown")
                                detail = inj.get("shortComment", inj.get("longComment", ""))
                                if status and status != "Active":
                                    return status, detail
    except Exception:
        pass

    return "Active", ""


# ── Usage spike detector ─────────────────────────────────

# ESPN uses non-standard abbreviations for some teams — normalize them
_ESPN_ABBR_MAP = {
    "GS":  "GSW", "SA":  "SAS", "NY":  "NYK", "NO":  "NOP",
    "OKC": "OKC", "UTA": "UTA", "PHX": "PHX", "LAC": "LAC",
    "LAL": "LAL", "BKN": "BKN", "CHA": "CHA", "WSH": "WAS",
    "MEM": "MEM", "MIN": "MIN",
}

def _norm_team_abbr(abbr: str) -> str:
    """Normalize ESPN team abbreviation to standard 3-letter NBA abbr."""
    return _ESPN_ABBR_MAP.get(abbr, abbr)


@st.cache_data(ttl=300, show_spinner=False)
def get_team_injury_report(team_abbr: str) -> list:
    """
    Fetch all injured players for a given team from NBA official report.
    Returns list of dicts: {name, status, reason}
    """
    # Normalize incoming abbr
    team_abbr = _norm_team_abbr(team_abbr)
    results = []

    # Source 0: ESPN injuries endpoint — try multiple URL patterns
    for _inj_url in [
        f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries",
        f"https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/injuries?limit=300",
    ]:
        try:
            inj_data = espn_get(_inj_url)
            # Pattern 1: {injuries: [{team: {abbreviation}, injuries: [...]}]}
            for team_entry in inj_data.get("injuries", []):
                raw_abbr  = team_entry.get("team", {}).get("abbreviation", "")
                norm_abbr = _norm_team_abbr(raw_abbr)
                if norm_abbr != team_abbr and raw_abbr != team_abbr:
                    continue
                for item in team_entry.get("injuries", []):
                    ath    = item.get("athlete", {})
                    name   = ath.get("displayName", "")
                    status = item.get("status", item.get("type", {}).get("description", ""))
                    detail = item.get("shortComment", item.get("longComment", ""))
                    if name and status:
                        results.append({
                            "name":   name,
                            "status": status,
                            "reason": detail,
                        })
            # Pattern 2: flat items list
            for item in inj_data.get("items", []):
                ath      = item.get("athlete", {})
                name     = ath.get("displayName", "")
                team_ref = item.get("team", {})
                raw_abbr = team_ref.get("abbreviation", "")
                if _norm_team_abbr(raw_abbr) != team_abbr and raw_abbr != team_abbr:
                    continue
                status = item.get("status", item.get("type", {}).get("description", ""))
                detail = item.get("shortComment", item.get("longComment", ""))
                if name and status:
                    results.append({
                        "name":   name,
                        "status": status,
                        "reason": detail,
                    })
            if results:
                return results
        except Exception:
            continue

    # Source 1: nbainjuries package
    try:
        from nbainjuries import injury
        from datetime import datetime
        import pytz
        et = pytz.timezone("America/New_York")
        now = datetime.now(et)
        report = injury.get_reportdata(now)
        if report:
            # Build team name → abbr mapping
            _team_map = {
                "Atlanta Hawks": "ATL", "Boston Celtics": "BOS",
                "Brooklyn Nets": "BKN", "Charlotte Hornets": "CHA",
                "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
                "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN",
                "Detroit Pistons": "DET", "Golden State Warriors": "GSW",
                "Houston Rockets": "HOU", "Indiana Pacers": "IND",
                "LA Clippers": "LAC", "Los Angeles Clippers": "LAC",
                "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
                "Miami Heat": "MIA", "Milwaukee Bucks": "MIL",
                "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP",
                "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
                "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI",
                "Phoenix Suns": "PHX", "Portland Trail Blazers": "POR",
                "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
                "Toronto Raptors": "TOR", "Utah Jazz": "UTA",
                "Washington Wizards": "WAS",
            }
            for entry in report:
                entry_team = entry.get("Team", "")
                entry_abbr = _team_map.get(entry_team, "")
                if entry_abbr != team_abbr:
                    continue
                raw_name = entry.get("Player Name", "")
                parts = raw_name.split(", ")
                name = f"{parts[1]} {parts[0]}" if len(parts) == 2 else raw_name
                results.append({
                    "name":   name,
                    "status": entry.get("Current Status", "Unknown"),
                    "reason": entry.get("Reason", ""),
                })
        if results:
            return results
    except Exception:
        pass

    # Source 2: ESPN team roster injuries
    try:
        teams_data = espn_get(f"{ESPN_SITE}/teams")
        teams_list = (
            teams_data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
            or teams_data.get("teams", [])
        )
        team_id = None
        for t in teams_list:
            team = t.get("team", t)
            if team.get("abbreviation", "") == team_abbr:
                team_id = team.get("id")
                break
        if team_id:
            roster = espn_get(f"{ESPN_SITE}/teams/{team_id}/roster")
            for athlete in roster.get("athletes", []):
                for item in (athlete.get("items") or [athlete]):
                    injuries = item.get("injuries", [])
                    if injuries:
                        inj    = injuries[0]
                        status = inj.get("status", "Unknown")
                        if status and status not in ("Active", ""):
                            results.append({
                                "name":   item.get("displayName", ""),
                                "status": status,
                                "reason": inj.get("shortComment", ""),
                            })
    except Exception:
        pass

    return results


@st.cache_data(ttl=21600, show_spinner=False)
def get_teammate_minutes(team_abbr: str, season: str = "2025-26", _date: str = None) -> dict:
    """
    Returns dict of {normalized_player_name: avg_minutes} for all players on a team.
    Uses ESPN athlete stats endpoint which returns per-game averages.
    """
    team_abbr = _norm_team_abbr(team_abbr)
    result = {}

    try:
        # Get team ID using normalized abbr
        teams_data = espn_get(f"{ESPN_SITE}/teams")
        teams_list = (
            teams_data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
            or teams_data.get("teams", [])
        )
        team_id = None
        for t in teams_list:
            team = t.get("team", t)
            # Match against both ESPN abbr and normalized abbr
            t_abbr = team.get("abbreviation", "")
            if t_abbr == team_abbr or _norm_team_abbr(t_abbr) == team_abbr:
                team_id = team.get("id")
                break

        if team_id:
            # ESPN athlete stats — includes season averages per player
            url = (
                f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
                f"/teams/{team_id}/athletes?season=2026"
            )
            athletes_data = espn_get(url)
            for item in athletes_data.get("athletes", []):
                name  = item.get("displayName", "")
                stats = item.get("stats", [])
                # Stats array: index 9 is usually MIN in ESPN's athlete endpoint
                # Try to find by label first
                labels = athletes_data.get("labels", [])
                if labels and "MIN" in labels:
                    idx = labels.index("MIN")
                    if idx < len(stats):
                        val = float(stats[idx] or 0)
                        if val > 0 and name:
                            result[normalize_name(name)] = round(val, 1)
                elif len(stats) > 9:
                    # Fallback: index 9 is typically MIN
                    try:
                        val = float(stats[9] or 0)
                        if 5 < val < 48 and name:  # sanity check range
                            result[normalize_name(name)] = round(val, 1)
                    except Exception:
                        pass
    except Exception:
        pass

    # Fallback: use nba_api player game logs for each player on the team
    if not result:
        try:
            from nba_api.stats.static import players as nba_static
            from nba_api.stats.endpoints import commonteamroster
            # Find team ID in nba_api
            from nba_api.stats.static import teams as nba_teams
            nba_team = next(
                (t for t in nba_teams.get_teams()
                 if t.get("abbreviation") == team_abbr),
                None
            )
            if nba_team:
                roster_df = commonteamroster.CommonTeamRoster(
                    team_id=nba_team["id"], season=season, timeout=30,
                ).get_data_frames()[0]
                for _, row in roster_df.iterrows():
                    pid  = row.get("PLAYER_ID")
                    name = str(row.get("PLAYER", ""))
                    if pid and name:
                        try:
                            logs = playergamelog.PlayerGameLog(
                                player_id=pid, season=season, timeout=15,
                            ).get_data_frames()[0]
                            mins = pd.to_numeric(logs["MIN"], errors="coerce").dropna().mean()
                            if mins > 0:
                                result[normalize_name(name)] = round(float(mins), 1)
                        except Exception:
                            pass
        except Exception:
            pass

    return result


def detect_usage_spike(
    player_name: str,
    player_team: str,
    side: str,
    teammate_mins: dict,
) -> Tuple[str, list, str]:
    """
    Checks if key teammates are out tonight using get_player_injury_status
    (already proven working) on each high-minute teammate individually.

    teammate_mins: pre-fetched dict of {normalized_name: avg_minutes}
    """
    if not player_team or not teammate_mins:
        return "Neutral", [], ""

    player_norm = normalize_name(player_name)

    # Top 5 key teammates by minutes (>22 mpg), excluding the player
    key_teammates = sorted(
        [(name, mins) for name, mins in teammate_mins.items()
         if mins >= 22 and name != player_norm],
        key=lambda x: -x[1]
    )[:5]

    if not key_teammates:
        return "Neutral", [], ""

    # Pre-fetch all ESPN players once
    all_players = espn_get_all_players(_date=_cache_date())

    def _check_teammate(norm_name_mins):
        norm_name, mins = norm_name_mins
        display_name = next(
            (p["full_name"] for p in all_players
             if normalize_name(p["full_name"]) == norm_name
             and _norm_team_abbr(p.get("team_abbr", "")) == player_team),
            norm_name.title()
        )
        status, reason = get_player_injury_status(display_name)
        return display_name, status, reason, mins

    # Check all key teammates in parallel
    import concurrent.futures
    key_absent = []
    total_redistributed = 0.0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_check_teammate, t): t for t in key_teammates}
        for future in concurrent.futures.as_completed(futures, timeout=6):
            try:
                display_name, status, reason, mins = future.result()
                if status.upper() in ("OUT", "DOUBTFUL"):
                    key_absent.append({
                        "name":    display_name,
                        "status":  status,
                        "minutes": mins,
                        "reason":  reason.replace("Injury/Illness - ", "").strip(),
                    })
                    total_redistributed += mins * 0.4
            except Exception:
                pass

    if not key_absent:
        return "Neutral", [], ""

    _names = ", ".join(f"{p['name']} ({p['minutes']:.0f} mpg)" for p in key_absent)
    _total = f"+{total_redistributed:.0f} min available"

    alert_html = (
        f"<div style='background:#0c1a0c;border:1px solid #166534;border-radius:10px;"
        f"padding:0.65rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:10px;'>"
        f"<span style='font-size:1.1rem;'>📈</span>"
        f"<div style='font-family:DM Mono;font-size:0.7rem;'>"
        f"<span style='color:#22c55e;font-weight:800;text-transform:uppercase;"
        f"letter-spacing:0.08em;'>Usage spike detected</span>"
        f"<span style='color:#475569;'> · {_names} out — {_total} to redistribute</span>"
        f"</div>"
        f"</div>"
    )
    return "Boost", key_absent, alert_html


def injury_alert_html(status: str, reason: str) -> str:
    """
    Returns an HTML alert string for the injury status.
    Returns empty string if player is Active/Unknown (no issue).
    """
    status_upper = status.upper()

    if "OUT" in status_upper:
        bg, border, color, icon = "#1c0505", "#991b1b", "#ef4444", "🚫"
        label = "OUT"
        block_verdict = True
    elif "DOUBTFUL" in status_upper:
        bg, border, color, icon = "#1c0505", "#991b1b", "#ef4444", "⛔"
        label = "DOUBTFUL"
        block_verdict = True
    elif "QUESTIONABLE" in status_upper:
        bg, border, color, icon = "#1c1005", "#854d0e", "#f97316", "⚠️"
        label = "QUESTIONABLE"
        block_verdict = False
    elif "PROBABLE" in status_upper:
        bg, border, color, icon = "#0c1a0c", "#166534", "#86efac", "🟡"
        label = "PROBABLE"
        block_verdict = False
    else:
        return "", False

    reason_short = reason.replace("Injury/Illness - ", "").replace("Injury/Illness -", "").strip()
    reason_html  = f"<span style='color:#64748b;'> · {reason_short}</span>" if reason_short else ""

    html = (
        f"<div style='background:{bg};border:1px solid {border};border-radius:10px;"
        f"padding:0.7rem 1rem;margin-bottom:0.75rem;display:flex;align-items:center;gap:10px;'>"
        f"<span style='font-size:1.2rem;'>{icon}</span>"
        f"<div>"
        f"<span style='font-family:DM Mono;font-size:0.7rem;font-weight:800;color:{color};"
        f"letter-spacing:0.08em;text-transform:uppercase;'>{label}</span>"
        f"{reason_html}"
        f"</div>"
        f"</div>"
    )
    return html, block_verdict


@st.cache_data(ttl=21600, show_spinner=False)
def classify_matchup_espn(opp_abbr: Optional[str], _date: str = None) -> Tuple[str, Optional[float], str]:
    """Classify opponent defense quality using ESPN team stats."""
    league_avg = 114.5
    if not opp_abbr:
        return "Neutral", None, str(league_avg)

    opp_pts = espn_get_opp_pts_allowed(opp_abbr, _date=_cache_date())

    if opp_pts is None:
        return "Neutral", None, str(league_avg)

    diff = opp_pts - league_avg
    if diff >= 1.5:
        return "Good", opp_pts, str(league_avg)
    if diff <= -1.5:
        return "Bad", opp_pts, str(league_avg)
    return "Neutral", opp_pts, str(league_avg)

# ── Pace of play ─────────────────────────────────────────────

# ── Playoff Mode Detection ──────────────────────────────────────────
def is_playoff_mode() -> bool:
    """
    Returns True if we're in NBA playoff season.
    Play-in: ~April 14-17. Playoffs: ~April 19 - June 22.
    Automatically resets for next regular season (Oct onwards).
    """
    import datetime
    today = datetime.date.today()
    # Playoffs run mid-April through late June each year
    return (today.month == 4 and today.day >= 14) or            (today.month == 5) or            (today.month == 6 and today.day <= 25)

_IS_PLAYOFFS = is_playoff_mode()

# ── 2026 Playoff Bracket — first round matchups only ────────────────
# Used as FALLBACK if NBA Stats API is unavailable.
# Wins/losses are auto-fetched from leaguegamefinder — no manual updates needed.
_PLAYOFF_BRACKET_2026 = {
    # EAST
    "NYK": {"opp": "ATL"}, "ATL": {"opp": "NYK"},
    "DET": {"opp": "ORL"}, "ORL": {"opp": "DET"},
    "CLE": {"opp": "TOR"}, "TOR": {"opp": "CLE"},
    "BOS": {"opp": "PHI"}, "PHI": {"opp": "BOS"},
    # WEST
    "OKC": {"opp": "PHX"}, "PHX": {"opp": "OKC"},
    "SAS": {"opp": "POR"}, "POR": {"opp": "SAS"},
    "DEN": {"opp": "MIN"}, "MIN": {"opp": "DEN"},
    "LAL": {"opp": "HOU"}, "HOU": {"opp": "LAL"},
}


@st.cache_data(ttl=900, show_spinner=False)
def get_playoff_series_context(team_abbr: str) -> dict:
    """
    Auto-fetches current playoff series W/L from NBA Stats API.
    Uses leaguegamefinder with SeasonType=Playoffs — updates automatically
    after every game, no manual maintenance needed.
    Falls back to bracket matchup dict for opponent name only.
    """
    empty = {"series_wins": 0, "series_losses": 0, "is_elimination": False,
             "is_closeout": False, "opp_abbr": None, "found": False}
    if not _IS_PLAYOFFS or not team_abbr:
        return empty

    abbr = team_abbr.upper()

    try:
        import requests as _req
        r = _req.get(
            "https://stats.nba.com/stats/leaguegamefinder",
            params={
                "LeagueID":          "00",
                "Season":            "2025-26",
                "SeasonType":        "Playoffs",
                "TeamAbbreviation":  abbr,
            },
            headers={
                "User-Agent":         "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer":            "https://www.nba.com/",
                "x-nba-stats-origin": "stats",
                "x-nba-stats-token":  "true",
                "Accept":             "application/json",
            },
            timeout=10,
        )
        if not r.ok:
            raise ValueError(f"HTTP {r.status_code}")

        rs       = r.json().get("resultSets", [{}])[0]
        hdrs     = rs.get("headers", [])
        rows     = rs.get("rowSet", [])

        if not rows or not hdrs:
            raise ValueError("Empty resultset")

        wl_i  = hdrs.index("WL")       if "WL"      in hdrs else -1
        mu_i  = hdrs.index("MATCHUP")  if "MATCHUP" in hdrs else -1

        if wl_i < 0:
            raise ValueError("No WL column")

        wins   = sum(1 for row in rows if str(row[wl_i]).upper() == "W")
        losses = sum(1 for row in rows if str(row[wl_i]).upper() == "L")

        # Parse opponent from most recent game matchup string
        # e.g. "ATL @ NYK" or "ATL vs. NYK"
        opp_abbr = _PLAYOFF_BRACKET_2026.get(abbr, {}).get("opp", "")
        if mu_i >= 0 and rows:
            mu    = str(rows[0][mu_i])  # most recent game first
            parts = mu.replace("vs.", "@").split("@")
            if len(parts) == 2:
                candidate = parts[1].strip().split()[0].upper()
                if len(candidate) <= 4:
                    opp_abbr = candidate

        return {
            "series_wins":    wins,
            "series_losses":  losses,
            "is_elimination": losses == 3 and wins < 3,
            "is_closeout":    wins == 3 and losses < 3,
            "opp_abbr":       opp_abbr,
            "found":          True,
        }

    except Exception:
        pass

    # ── Fallback: bracket opponent only, 0-0 record ───────────────
    if abbr in _PLAYOFF_BRACKET_2026:
        opp = _PLAYOFF_BRACKET_2026[abbr].get("opp", "")
        return {
            "series_wins":    0,
            "series_losses":  0,
            "is_elimination": False,
            "is_closeout":    False,
            "opp_abbr":       opp,
            "found":          False,   # found=False signals data unavailable
        }

    return empty

# ── Playoff pace table — slower than regular season ─────────────────
# Playoff games average ~2-3 fewer possessions than reg season
# These are estimates based on historical playoff pace reductions
_NBA_PACE_PLAYOFFS = {
    "ATL": 98.5,  "BOS": 92.8,  "BKN": 100.1, "CHA": 100.2, "CHI": 99.0,
    "CLE": 96.8,  "DAL": 101.2, "DEN": 99.0,  "DET": 104.0, "GSW": 99.8,
    "HOU": 103.0, "IND": 104.5, "LAC": 98.5,  "LAL": 99.0,  "MEM": 101.0,
    "MIA": 97.0,  "MIL": 100.2, "MIN": 97.8,  "NOP": 100.5, "NYK": 96.0,
    "OKC": 99.2,  "ORL": 97.5,  "PHI": 99.8,  "PHX": 101.5, "POR": 102.0,
    "SAC": 102.2, "SAS": 101.0, "TOR": 101.0, "UTA": 102.0, "WAS": 103.0,
}

# Static pace lookup — derived from NBA advanced stats (2025-26 season)
# Updated periodically. Fast enough for Streamlit Cloud with no API call needed.
_NBA_PACE_2526 = {
    "ATL": 101.1, "BOS": 95.0, "BKN": 103.2, "CHA": 103.5, "CHI": 101.8,
    "CLE": 99.2,  "DAL": 104.1, "DEN": 101.5, "DET": 107.2, "GSW": 102.8,
    "HOU": 106.4, "IND": 107.8, "LAC": 101.3, "LAL": 102.0, "MEM": 103.9,
    "MIA": 99.8,  "MIL": 103.1, "MIN": 100.4, "NOP": 103.7, "NYK": 98.5,
    "OKC": 101.9, "ORL": 100.1, "PHI": 102.5, "PHX": 104.8, "POR": 105.3,
    "SAC": 105.6, "SAS": 104.2, "TOR": 104.0, "UTA": 105.1, "WAS": 106.2,
}

@st.cache_data(ttl=86400, show_spinner=False)
def get_team_pace(team_abbr: str) -> Optional[float]:
    """
    Return team pace (possessions per game) for 2025-26.
    Uses static lookup first, falls back to ESPN team stats.
    """
    if not team_abbr:
        return None

    # Static lookup — use playoff pace if in playoff mode
    if _IS_PLAYOFFS and team_abbr in _NBA_PACE_PLAYOFFS:
        return _NBA_PACE_PLAYOFFS[team_abbr]
    if team_abbr in _NBA_PACE_2526:
        return _NBA_PACE_2526[team_abbr]

    # ESPN core API fallback — team advanced stats
    try:
        teams_data = espn_get(f"{ESPN_SITE}/teams")
        teams_list = (
            teams_data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
            or teams_data.get("teams", [])
        )
        team_id = None
        for t in teams_list:
            team = t.get("team", t)
            if team.get("abbreviation", "") == team_abbr:
                team_id = team.get("id")
                break
        if team_id:
            stats = espn_get(f"{ESPN_SITE}/teams/{team_id}/statistics")
            results = stats.get("results", {}).get("stats", {})
            cats = results.get("categories", [])
            for cat in cats:
                for stat in cat.get("stats", []):
                    name = stat.get("name", "").lower()
                    if "pace" in name or "possession" in name:
                        val = stat.get("value", 0)
                        if val and float(val) > 80:
                            return round(float(val), 1)
    except Exception:
        pass

    return None


# ── Referee foul tendency table ─────────────────────────────────────
# Points per game in games officiated — 2025-26 season
# High = whistle-happy refs = more FTs = more scoring
# Low = let-them-play refs = fewer FTs = lower scoring
# Source: NBAstuffer.com 2025-26 referee stats
_REF_PPG = {
    # High whistle (>225 pts/game)
    "Zach Zarba":        231.4, "Scott Foster":      229.8,
    "Tony Brothers":     228.6, "James Capers":      227.1,
    "Marc Davis":        226.5, "Ed Malloy":         226.0,
    "Bill Kennedy":      225.8, "Josh Tiven":        225.3,
    # Neutral (218-225)
    "John Goble":        224.1, "Derek Richardson":  223.7,
    "Eric Lewis":        223.2, "Sean Wright":       222.8,
    "Kevin Scott":       222.1, "Courtney Kirkland": 221.5,
    "Ben Taylor":        221.0, "Dedric Taylor":     220.4,
    "Tom Washington":    220.1, "JT Orr":            219.6,
    "Gediminas Petraitis": 219.2, "Nick Buchert":    218.5,
    "Pat Fraher":        218.3, "Matt Boland":       218.0,
    # Low whistle (<218)
    "Mark Lindsay":      219.8,
    "Kane Fitzgerald":   217.4, "Brian Forte":       216.9,
    "Phenizee Ransom":   216.2, "Rodney Mott":       215.8,
    "Justin Van Duyne":  215.1, "Marat Kogut":       214.7,
    "Leon Wood":         214.2, "CJ Washington":     213.8,
    "Eric Dalen":        213.1, "Tre Maddox":        212.6,
}
_REF_LEAGUE_AVG_PPG = 221.0  # league average pts/game 2025-26

@st.cache_data(ttl=3600, show_spinner=False)
def get_todays_referees(game_team_abbr: Optional[str]) -> Tuple[List[str], str]:
    """
    Fetch today's referee assignments from NBA official site.
    Returns (ref_names, raw_text) for the game involving game_team_abbr.
    Falls back to empty list on failure.
    """
    if not game_team_abbr:
        return [], ""
    try:
        import datetime, pytz
        et    = pytz.timezone("America/New_York")
        today = datetime.datetime.now(et).strftime("%Y-%m-%d")
        r = requests.get(
            "https://official.nba.com/referee-assignments/",
            headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"},
            timeout=10
        )
        if not r.ok:
            return [], ""
        from html.parser import HTMLParser
        class _RefParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.rows = []; self._row = []; self._in_td = False
            def handle_starttag(self, tag, attrs):
                if tag == "tr": self._row = []
                if tag in ("td","th"): self._in_td = True
            def handle_endtag(self, tag):
                if tag in ("td","th"): self._in_td = False
                if tag == "tr" and self._row: self.rows.append(self._row[:])
            def handle_data(self, data):
                if self._in_td: self._row.append(data.strip())
        p = _RefParser()
        p.feed(r.text)
        # Find row containing our team
        abbr_up = game_team_abbr.upper()
        # NBA site shows team names not abbrs — build a mapping
        _ABBR_TO_NAME = {
            "ATL":"Atlanta","BOS":"Boston","BKN":"Brooklyn","CHA":"Charlotte",
            "CHI":"Chicago","CLE":"Cleveland","DAL":"Dallas","DEN":"Denver",
            "DET":"Detroit","GSW":"Golden State","HOU":"Houston","IND":"Indiana",
            "LAC":"LA Clippers","LAL":"LA Lakers","MEM":"Memphis","MIA":"Miami",
            "MIL":"Milwaukee","MIN":"Minnesota","NOP":"New Orleans","NYK":"New York",
            "OKC":"Oklahoma City","ORL":"Orlando","PHI":"Philadelphia","PHX":"Phoenix",
            "POR":"Portland","SAC":"Sacramento","SAS":"San Antonio","TOR":"Toronto",
            "UTA":"Utah","WAS":"Washington",
        }
        team_name = _ABBR_TO_NAME.get(abbr_up, abbr_up).lower()
        refs = []
        for row in p.rows:
            if len(row) >= 4:
                game_cell = row[0].lower()
                if team_name in game_cell or abbr_up.lower() in game_cell:
                    # Cols: Game, Crew Chief, Referee, Umpire, [Alternate]
                    refs = [row[i] for i in range(1, min(4, len(row))) if row[i]]
                    break
        return refs, ""
    except Exception:
        return [], ""


def referee_signal(
    player_team: Optional[str],
    side: str,
) -> Tuple[str, Optional[float], List[str]]:
    """
    Returns (signal, avg_ppg, ref_names).
    signal: "High FT" (boosts Over), "Neutral", "Low FT" (hurts Over)
    """
    refs, _ = get_todays_referees(player_team)
    if not refs:
        return "Neutral", None, []

    # Clean ref names — site returns "Marc Davis (#8)", table has "Marc Davis"
    import re as _re
    def _clean_ref(name):
        # Remove jersey number like '(#8)' or '(8)'
        n = name.split('(')[0].strip()
        return n

    clean_refs = [_clean_ref(r) for r in refs]

    # Average PPG for tonight's crew
    known = [_REF_PPG[r] for r in clean_refs if r in _REF_PPG]
    if not known:
        return "Neutral", None, clean_refs

    crew_avg = sum(known) / len(known)
    diff = crew_avg - _REF_LEAGUE_AVG_PPG

    if side == "Over":
        if diff >= 3.0:
            return "High FT", crew_avg, clean_refs
        if diff <= -3.0:
            return "Low FT", crew_avg, clean_refs
    else:  # Under
        if diff >= 3.0:
            return "Low FT", crew_avg, clean_refs
        if diff <= -3.0:
            return "High FT", crew_avg, clean_refs

    return "Neutral", crew_avg, clean_refs


def get_opponent_injury_report(
    opp_abbr: Optional[str],
    player_position: Optional[str] = None,
) -> Tuple[List[dict], str]:
    """
    Check if the opposing team has key players out tonight.
    Returns (absent_players, alert_html).
    Focuses on high-minute defenders and primary scorers.
    """
    if not opp_abbr:
        return [], ""
    try:
        all_players = espn_get_all_players(_date=_cache_date())
        # Get all players on opponent team
        opp_players = [
            p for p in all_players
            if _norm_team_abbr(p.get("team_abbr", "")) == opp_abbr.upper()
        ]
        if not opp_players:
            return [], ""

        # Check top 8 by roster position (starters/key rotation)
        import concurrent.futures as _cf
        absent = []

        def _check(player):
            status, reason = get_player_injury_status(player["full_name"])
            return player["full_name"], status, reason

        with _cf.ThreadPoolExecutor(max_workers=6) as ex:
            futures = {ex.submit(_check, p): p for p in opp_players[:10]}
            for f in _cf.as_completed(futures, timeout=8):
                try:
                    name, status, reason = f.result()
                    if status.upper() in ("OUT", "DOUBTFUL"):
                        absent.append({
                            "name":   name,
                            "status": status,
                            "reason": reason.replace("Injury/Illness - ", "").strip(),
                        })
                except Exception:
                    pass

        if not absent:
            return [], ""

        _names = ", ".join(f"{p['name']} ({p['status']})" for p in absent[:3])
        alert_html = (
            f"<div style='background:#0c1a2e;border:1px solid #1e3a5f;"
            f"border-left:4px solid #3b82f6;"
            f"border-radius:0;padding:0.65rem 1rem;margin-bottom:0.5rem;"
            f"font-family:JetBrains Mono,monospace;'>"
            f"<div style='font-size:0.7rem;'>"
            f"<span style='color:#3b82f6;font-weight:800;letter-spacing:0.08em;'>"
            f"🏀 OPP INJURY REPORT</span>"
            f"<span style='color:#94a3b8;'> · {opp_abbr} missing: "
            f"<span style='color:#f1f5f9;font-weight:700;'>{_names}</span>"
            f" — matchup quality upgrade</span></div></div>"
        )
        return absent, alert_html
    except Exception:
        return [], ""


def pace_adjustment(
    player_team_abbr: Optional[str],
    opp_abbr: Optional[str],
    side: str,
) -> Tuple[str, Optional[float], Optional[float]]:
    """
    Compare expected game pace vs league average.
    Returns (signal, player_team_pace, opp_pace).

    Game pace = average of both teams' pace.
    League avg pace = 104.5 possessions (2025-26 season).

    Fast game (>107 poss) → more scoring opportunities → boosts Over / hurts Under
    Slow game (<102 poss) → fewer opportunities → hurts Over / boosts Under
    """
    LEAGUE_AVG_PACE = 101.5 if _IS_PLAYOFFS else 104.5  # playoffs ~3 fewer possessions

    p1 = get_team_pace(player_team_abbr) if player_team_abbr else None
    p2 = get_team_pace(opp_abbr) if opp_abbr else None

    if p1 is None and p2 is None:
        return "Neutral", None, None

    # Use available data — average if both, otherwise use what we have
    if p1 and p2:
        game_pace = (p1 + p2) / 2
    else:
        game_pace = p1 or p2

    diff = game_pace - LEAGUE_AVG_PACE

    # Align with bet side
    if side == "Over":
        if diff >= 2.5:
            signal = "Boost"    # fast game = more possessions = more scoring
        elif diff <= -2.5:
            signal = "Penalty"  # slow game = fewer possessions
        else:
            signal = "Neutral"
    else:  # Under
        if diff >= 2.5:
            signal = "Penalty"  # fast game hurts Under
        elif diff <= -2.5:
            signal = "Boost"    # slow game helps Under
        else:
            signal = "Neutral"

    return signal, p1, p2


# Prediction engine (unchanged)
# ─────────────────────────────────────────────

def hit_rate(df: pd.DataFrame, line: float, side: str) -> float:
    pts = pd.to_numeric(df["PTS"], errors="coerce").dropna()
    if len(pts) == 0:
        return 0.0
    hits = (pts >= line).sum() if side == "Over" else (pts <= line).sum()
    return float(hits / len(pts))

def weighted_hit_rate(df: pd.DataFrame, line: float, side: str, stat_col: str = "PTS",
                      opp_abbr: Optional[str] = None) -> float:
    """
    Weighted hit rate with optional playoff series boost.
    If in playoffs and opp_abbr is given, games vs that opponent in the last
    ~30 days get weighted 3x heavier — they represent this current series.
    """
    pts_series = pd.to_numeric(df[stat_col], errors="coerce").dropna().reset_index(drop=True)
    n = len(pts_series)
    if n == 0:
        return 0.0

    # Base weights: most recent game has heaviest weight
    weights = [n - i for i in range(n)]

    # ── Playoff series boost: games vs same opponent in last 30 days = this series ──
    if _IS_PLAYOFFS and opp_abbr and "MATCHUP" in df.columns and "GAME_DATE" in df.columns:
        try:
            opp_up = opp_abbr.upper()
            dates  = pd.to_datetime(df["GAME_DATE"], errors="coerce").reset_index(drop=True)
            matchups = df["MATCHUP"].astype(str).reset_index(drop=True)
            # Only actual playoff games (on or after April 14) count as this series
            _playoff_start = pd.Timestamp("2026-04-14").normalize()
            for i in range(n):
                if pd.notna(dates[i]) and opp_up in matchups[i].upper():
                    if dates[i].normalize() >= _playoff_start:
                        weights[i] *= 3  # 3x boost for actual playoff series games only
        except Exception:
            pass

    total_weight = sum(weights)
    if side == "Over":
        weighted_hits = sum(w for p, w in zip(pts_series, weights) if p >= line)
    else:
        weighted_hits = sum(w for p, w in zip(pts_series, weights) if p <= line)
    return weighted_hits / total_weight

def consistency_score(df: pd.DataFrame, line: float, stat_col: str = "PTS") -> float:
    """
    Measures how predictable a player is relative to their OWN average,
    scaled by their distance from the line.

    Logic:
    - If a player averages 14 on a 5.5 line (edge = +8.5), their scores
      don't need to be near the line to be consistent — they need to be
      near THEIR OWN average. A player who reliably scores 12-18 is
      highly consistent against a 5.5 line.
    - We use coefficient of variation (std/mean) normalized to 0-1.
    - Then boost consistency when the player's average is far from the line
      because large-edge props have more margin for error.

    Returns 0.0 (extremely volatile) to 1.0 (perfectly predictable).
    """
    pts = pd.to_numeric(df[stat_col], errors="coerce").dropna()
    if len(pts) == 0:
        return 0.5

    avg = pts.mean()
    std = pts.std()

    if avg <= 0:
        return 0.1

    # Coefficient of variation — lower = more consistent
    cv = std / avg  # typically 0.2 (very consistent) to 1.0+ (volatile)

    # Base consistency score from CV (inverted — low CV = high consistency)
    # CV of 0.2 → 0.9, CV of 0.5 → 0.6, CV of 1.0 → 0.1
    base = max(0.05, min(0.95, 1.0 - (cv * 0.8)))

    # Edge bonus: if avg is far from line, small score variance doesn't matter much
    # A player averaging 14 on a 5.5 line can drop to 8 and still hit
    edge = abs(avg - line)
    if edge >= 8:
        # Very large edge — boost consistency, player would need catastrophic game to miss
        edge_boost = 0.20
    elif edge >= 5:
        edge_boost = 0.12
    elif edge >= 3:
        edge_boost = 0.06
    else:
        edge_boost = 0.0

    return min(0.95, base + edge_boost)

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

def apply_adjustments(weighted: float, context: dict, side: str = "Over") -> float:
    """
    Apply context signals as additive pp adjustments.

    weighted = probability that THIS BET SIDE hits (already side-aware from weighted_hit_rate).
    So 89% for an Under means the Under has an 89% hit rate.

    Signals are defined in terms of "scoring volume":
      - High scoring signals (Strong minutes, Good matchup, Hot form) boost Over / hurt Under
      - Low scoring signals (Risk minutes, Bad matchup, B2B) hurt Over / boost Under

    For Under bets we flip the sign of every adjustment so the direction is always correct.
    """
    # Adjustments defined as: positive = MORE scoring = good for Over
    adj_map = {
        "minutes":  {"Strong": +0.05, "Okay": 0.00, "Risk": -0.07},
        "role":     {"Strong": +0.04, "Okay": 0.00, "Risk": -0.05},
        "shots":    {"High":   +0.03, "Medium": 0.00, "Low": -0.06},
        "matchup":  {"Good":   +0.06, "Neutral": 0.00, "Bad": -0.06},
        "script":   {"Competitive": +0.02, "Neutral": 0.00, "Blowout risk": -0.04},
        "venue":    {"Boost": +0.04, "Neutral": 0.00, "Penalty": -0.05},
        "h2h":      {"Strong": +0.09 if _IS_PLAYOFFS else +0.05,
                       "Neutral": 0.00,
                       "Risk":   -0.10 if _IS_PLAYOFFS else -0.06},
        "b2b":      {"Normal": 0.00, "B2B": -0.06},
        # Rest days: 3+ days rest = small scoring boost
        "rest":     {"Rested": +0.03, "Normal": 0.00, "Short": -0.02, "B2B": -0.06},
        "form":     {"Boost": +0.05, "Neutral": 0.00, "Penalty": -0.05},
        # Pace: fast game = more possessions = more scoring opportunities
        "pace":     {"Boost": +0.04, "Neutral": 0.00, "Penalty": -0.04},
        # Shooting efficiency: hot/cold streak over last 3 games
        "shoot":    {"Boost": +0.05, "Neutral": 0.00, "Penalty": -0.05},
        # Elimination/closeout — handled separately below, 0 here to avoid double-counting
        "elim_game": {"Elimination": 0.00, "Closeout": 0.00, "Normal": 0.00},
        # Playoffs only — how this specific defense has covered this player in this series
        "series_cov": {"Strong": +0.07, "Neutral": 0.00, "Risk": -0.08},
        # Referee foul tendency — high whistle = more FTs = more scoring
        "ref":        {"High FT": +0.04, "Neutral": 0.00, "Low FT": -0.04},
        # Shot volume in playoffs — high usage players hold, low usage get buried
        "shot_vol":   {"Star": +0.04, "Neutral": 0.00, "Risk": -0.05},
        # Playoff game number — Game 1 and 6/7 see lower scoring
        "game_num":   {"Spike": +0.05, "Neutral": 0.00, "Drop": -0.05, "N/A": 0.00,
                       "Game 1 (feeling out)": -0.03, "Game 2 (normal)": 0.00,
                       "Game 3 (normal)": 0.00, "Game 4 (normal)": 0.00,
                       "Game 5 (normal)": 0.00, "Game 6 (pressure)": -0.02,
                       "Game 7 (max pressure)": -0.03},
        # Playoff usage spike vs regular season
        "pu_spike":   {"Spike": +0.05, "Neutral": 0.00, "Drop": -0.05},
    }
    # For Under bets, flip every signal: high scoring hurts the Under, low scoring helps it
    _flip = -1.0 if side == "Under" else 1.0

    adjusted = weighted
    for key, val in context.items():
        adjusted += adj_map.get(key, {}).get(val, 0.0) * _flip
    adjusted = max(0.0, min(1.0, adjusted))

    # ── Elimination game boost ──────────────────────────────────
    # Do-or-die games: stars score MORE (desperation), role players score LESS
    # This is applied after context signals — it's an override layer
    if context.get("elim_game") == "Elimination":
        # Stars (high minutes) go up, role players go down
        if context.get("minutes") == "Strong":
            adjusted = min(0.95, adjusted + (0.04 * _flip))
        else:
            adjusted = max(0.05, adjusted - (0.03 * _flip))
    elif context.get("elim_game") == "Closeout":
        # Team trying to close out plays aggressive — slight boost
        adjusted = min(0.95, adjusted + (0.02 * _flip))

    # Cap: context can shift probability from weighted base
    # Wider in playoffs — more signals are active and meaningful
    max_shift = 0.18 if _IS_PLAYOFFS else 0.12
    if adjusted > weighted + max_shift:
        adjusted = weighted + max_shift
    if adjusted < weighted - max_shift:
        adjusted = weighted - max_shift

    return max(0.0, min(1.0, adjusted))

def get_confidence_tier(adjusted: float, line_diff: float, consistency: float, side: str = "Over") -> str:
    """
    Assign confidence tier.

    adjusted = probability that THIS BET SIDE hits (side-aware).
    line_diff = avg_pts - line (positive = avg above line = good for Over).

    For Over:  high adjusted + positive edge = Strong Over
    For Under: high adjusted + negative edge = Strong Under
               (edge is negative because avg is below the line)

    We unify the logic: strong = adjusted >= 0.64 AND edge favors the side.
    """
    if side == "Over":
        edge_favors = line_diff >= 1.5
        edge_any    = line_diff > 0
        if adjusted >= 0.64 and edge_favors:
            tier = "Strong Over"
        elif adjusted >= 0.55 and edge_any:
            tier = "Lean Over"
        else:
            tier = "Pass"
    else:  # Under
        edge_favors = line_diff <= -1.5   # avg well below line = good for Under
        edge_any    = line_diff < 0
        if adjusted >= 0.64 and edge_favors:
            tier = "Strong Under"
        elif adjusted >= 0.55 and edge_any:
            tier = "Lean Under"
        else:
            tier = "Pass"

    # Consistency downgrade rules:
    #
    # Rule 1 — Extremely volatile (<= 20%) WITHOUT dominant hit rate:
    #   Always downgrade. A player this unpredictable can't be trusted.
    #   EXCEPTION: if hit rate >= 65%, they consistently beat the line
    #   even if they land far above/below it — keep Strong verdict.
    #
    # Rule 2 — Low consistency (21-35%) with tight edge (< 3pts)
    #   and weak hit rate (< 65%): downgrade. Too close to call.

    extremely_volatile = consistency <= 0.20
    edge_is_tight      = abs(line_diff) < 3.0
    # For extremely volatile players, require higher hit rate to keep Strong verdict
    # 70%+ means player overwhelmingly beats the line even if inconsistently
    hit_rate_dominant  = adjusted >= 0.70 if extremely_volatile else adjusted >= 0.65

    if extremely_volatile and not hit_rate_dominant:
        if tier == "Strong Over":    tier = "Lean Over"
        elif tier == "Strong Under": tier = "Lean Under"
    elif consistency < 0.35 and edge_is_tight and not hit_rate_dominant:
        if tier == "Strong Over":    tier = "Lean Over"
        elif tier == "Strong Under": tier = "Lean Under"

    return tier

# ─────────────────────────────────────────────
# Backtesting engine
# ─────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def nba_get_full_season_logs(player_id: int, season: str) -> pd.DataFrame:
    """Fetch ALL games for a season (not capped at N)."""
    empty = pd.DataFrame(columns=["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A","FG3M"])
    try:
        from nba_api.library.http import NBAStatsHTTP
        NBAStatsHTTP.nba_response.headers = {
            "Host": "stats.nba.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "x-nba-stats-origin": "stats",
            "x-nba-stats-token": "true",
            "Referer": "https://www.nba.com/",
            "Origin": "https://www.nba.com",
        }
    except Exception:
        pass
    for attempt in range(3):
        try:
            df = playergamelog.PlayerGameLog(
                player_id=player_id, season=season, timeout=60,
            ).get_data_frames()[0]
            df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
            df = df.sort_values("GAME_DATE", ascending=True).copy()
            for c in ["MATCHUP","MIN","PTS","FGA","FTA","FG3A"]:
                if c not in df.columns:
                    df[c] = None
            return df[["GAME_DATE","MATCHUP","MIN","PTS","FGA","FTA","FG3A"]]
        except Exception:
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
    return empty


def run_backtest(
    full_logs: pd.DataFrame,
    line: float,
    side: str,
    window: int = 10,
    min_games: int = 5,
) -> pd.DataFrame:
    """
    Simulate the PropLens model game-by-game over a full season.

    For each game G, uses the prior `window` games as the sample,
    runs apply_adjustments with neutral context (no live signals),
    records the verdict, then checks if the actual outcome matched.

    Returns a DataFrame with one row per game showing:
    - date, matchup, actual pts, hit (bool), tier, adjusted prob, correct (bool)
    """
    results = []
    logs_sorted = full_logs.sort_values("GAME_DATE", ascending=True).reset_index(drop=True)

    for i in range(len(logs_sorted)):
        if i < min_games:
            continue  # need enough history

        # Sample = prior window games
        start  = max(0, i - window)
        sample = logs_sorted.iloc[start:i].copy()

        if len(sample) < min_games:
            continue

        actual_pts = pd.to_numeric(logs_sorted.iloc[i]["PTS"], errors="coerce")
        if pd.isna(actual_pts):
            continue

        # Core stats from sample (most recent first for weighted calc)
        sample_rev = sample.sort_values("GAME_DATE", ascending=False)
        wb   = weighted_hit_rate(sample_rev, line, side)
        cons = consistency_score(sample_rev, line)
        avg_pts = pd.to_numeric(sample_rev["PTS"], errors="coerce").dropna().mean()
        line_diff = avg_pts - line

        # Neutral context — no live signals available for historical games
        ctx = {
            "minutes": "Okay", "role": "Okay", "shots": "Medium",
            "matchup": "Neutral", "script": "Neutral", "venue": "Neutral",
            "h2h": "Neutral", "b2b": "Normal", "form": "Neutral",
        }
        adj  = apply_adjustments(wb, ctx, side)
        tier = get_confidence_tier(adj, line_diff, cons, side)

        # Did the bet actually hit?
        if side == "Over":
            hit = bool(actual_pts >= line)
        else:
            hit = bool(actual_pts <= line)

        # Was the model right?
        model_says_bet = tier not in ("Pass",)
        model_direction = "Over" if "Over" in tier else ("Under" if "Under" in tier else "Pass")
        correct = (model_direction == side and hit) or (model_direction != side and not hit and model_direction != "Pass")
        if model_direction == "Pass":
            correct = None  # Pass = no prediction

        results.append({
            "Date":        logs_sorted.iloc[i]["GAME_DATE"].strftime("%b %d"),
            "Matchup":     str(logs_sorted.iloc[i].get("MATCHUP", "")),
            "Actual PTS":  int(actual_pts),
            "Hit":         "✅" if hit else "❌",
            "Tier":        tier,
            "Adjusted":    f"{adj:.0%}",
            "Weighted HR": f"{wb:.0%}",
            "Correct":     ("✅" if correct else "❌") if correct is not None else "—",
            "_hit":        hit,
            "_tier":       tier,
            "_adj":        adj,
            "_correct":    correct,
        })

    return pd.DataFrame(results)


def backtest_summary(bt_df: pd.DataFrame) -> dict:
    """Compute accuracy stats by tier from backtest results."""
    if bt_df.empty:
        return {}

    summary = {}
    tiers = ["Strong Over", "Lean Over", "Pass", "Lean Under", "Strong Under"]

    for tier in tiers:
        rows = bt_df[bt_df["_tier"] == tier]
        if rows.empty:
            continue
        hits    = rows["_hit"].sum()
        total   = len(rows)
        correct = rows["_correct"].sum() if rows["_correct"].notna().any() else 0
        summary[tier] = {
            "games":   total,
            "hits":    int(hits),
            "hit_pct": round(hits / total * 100, 1),
            "correct": int(correct) if correct is not None else 0,
        }

    # Overall (excluding Pass)
    bet_rows = bt_df[bt_df["_tier"] != "Pass"]
    if not bet_rows.empty:
        summary["Overall (bet)"] = {
            "games":   len(bet_rows),
            "hits":    int(bet_rows["_hit"].sum()),
            "hit_pct": round(bet_rows["_hit"].sum() / len(bet_rows) * 100, 1),
            "correct": int(bet_rows["_correct"].sum()),
        }

    return summary


# ── Recent shooting efficiency signal ─────────────────────────

def shooting_efficiency_signal(
    logs: pd.DataFrame,
    side: str,
    n_recent: int = 3,
) -> Tuple[str, Optional[float], Optional[float]]:
    """
    Detects if a player is on a hot or cold shooting streak.

    Uses last 3 games 3PT% as the primary signal — three-point shooting
    is the strongest short-term predictor of scoring output for perimeter players.
    Also checks TS% (true shooting) for all players.

    Returns (signal, recent_3pt_pct, recent_ts_pct)
    signal: "Boost", "Penalty", "Neutral"
    """
    if logs is None or logs.empty or len(logs) < 2:
        return "Neutral", None, None

    try:
        recent = logs.head(n_recent).copy()

        # 3PT% over last N games
        fga3  = pd.to_numeric(recent.get("FG3A", pd.Series(dtype=float)), errors="coerce").fillna(0)
        fgm3  = pd.to_numeric(recent.get("FG3M", pd.Series(dtype=float)), errors="coerce").fillna(0)
        total_3pa = fga3.sum()
        total_3pm = fgm3.sum()
        recent_3pt = (total_3pm / total_3pa) if total_3pa >= 3 else None

        # TS% over last N games: pts / (2 * (FGA + 0.44 * FTA))
        pts  = pd.to_numeric(recent.get("PTS",  pd.Series(dtype=float)), errors="coerce").fillna(0)
        fga  = pd.to_numeric(recent.get("FGA",  pd.Series(dtype=float)), errors="coerce").fillna(0)
        fta  = pd.to_numeric(recent.get("FTA",  pd.Series(dtype=float)), errors="coerce").fillna(0)
        total_pts  = pts.sum()
        total_fga  = fga.sum()
        total_fta  = fta.sum()
        denom = 2 * (total_fga + 0.44 * total_fta)
        recent_ts  = (total_pts / denom) if denom > 0 else None

        # Signal logic
        signal = "Neutral"

        # Hot shooting — boosts Over, hurts Under
        if recent_3pt is not None and recent_3pt >= 0.42:
            signal = "Boost" if side == "Over" else "Penalty"
        elif recent_ts is not None and recent_ts >= 0.62:
            signal = "Boost" if side == "Over" else "Penalty"

        # Cold shooting — hurts Over, boosts Under
        elif recent_3pt is not None and total_3pa >= 3 and recent_3pt <= 0.28:
            signal = "Penalty" if side == "Over" else "Boost"
        elif recent_ts is not None and recent_ts <= 0.46:
            signal = "Penalty" if side == "Over" else "Boost"

        return signal, recent_3pt, recent_ts

    except Exception:
        return "Neutral", None, None


# ── Blowout filter ────────────────────────────────────────────

def filter_blowouts(df: pd.DataFrame, threshold: int = 15) -> tuple:
    """
    Remove blowout games (margin ≥ threshold in either direction).
    Returns (filtered_df, blowout_count, blowout_games).
    Uses PLUS_MINUS column — positive = player's team won by that margin.
    """
    if df is None or df.empty:
        return df, 0, []

    if "PLUS_MINUS" not in df.columns:
        return df, 0, []

    pm = pd.to_numeric(df["PLUS_MINUS"], errors="coerce")
    blowout_mask = pm.abs() >= threshold
    blowout_count = int(blowout_mask.sum())

    if blowout_count == 0:
        return df, 0, []

    blowout_games = []
    for _, row in df[blowout_mask].iterrows():
        try:
            date = pd.to_datetime(row["GAME_DATE"]).strftime("%b %d")
            matchup = str(row.get("MATCHUP", "")).replace("vs.", "vs").strip()
            margin = int(pd.to_numeric(row["PLUS_MINUS"], errors="coerce"))
            pts = int(pd.to_numeric(row["PTS"], errors="coerce"))
            direction = f"+{margin}" if margin > 0 else str(margin)
            blowout_games.append(f"{date} {matchup} ({direction} pts, scored {pts})")
        except Exception:
            pass

    filtered = df[~blowout_mask].copy()
    return filtered, blowout_count, blowout_games


# ── Playoff picture context ────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def get_playoff_picture(team_abbr: str) -> dict:
    """
    Fetches NBA standings from ESPN. Tries multiple endpoints.
    """
    if not team_abbr:
        return {}

    def _parse_entries(entries):
        for entry in entries:
            abbr = entry.get("team", {}).get("abbreviation", "")
            if _norm_team_abbr(abbr) != _norm_team_abbr(team_abbr):
                continue
            stats = {s["name"]: s.get("value", s.get("displayValue", ""))
                     for s in entry.get("stats", [])}
            wins   = float(stats.get("wins", 0) or 0)
            losses = float(stats.get("losses", 0) or 0)
            gb     = stats.get("gamesBehind", stats.get("differential", "—"))
            seed   = int(float(stats.get("playoffSeed", stats.get("seed", 0)) or 0))
            note   = str(entry.get("note", ""))
            clinched   = any(x in note.lower() for x in ["clinched", "x -", "x-", "- x"])
            eliminated = any(x in note.lower() for x in ["eliminated", "e -", "- e"])

            if eliminated:
                return {"status":"eliminated","label":"🔴 Eliminated","color":"#ef4444","seed":seed,"wins":int(wins),"losses":int(losses),"gb":gb}
            elif clinched and seed <= 2:
                return {"status":"locked","label":f"🏆 #{seed} Seed Locked","color":"#3b82f6","seed":seed,"wins":int(wins),"losses":int(losses),"gb":gb}
            elif clinched:
                return {"status":"clinched","label":f"✅ Clinched (#{seed})","color":"#22c55e","seed":seed,"wins":int(wins),"losses":int(losses),"gb":gb}
            elif seed <= 6:
                return {"status":"contending","label":f"🟡 #{seed} Seed · {gb} GB","color":"#eab308","seed":seed,"wins":int(wins),"losses":int(losses),"gb":gb}
            elif seed <= 10:
                return {"status":"bubble","label":f"⚠️ Play-In ({seed}th) · {gb} GB","color":"#f97316","seed":seed,"wins":int(wins),"losses":int(losses),"gb":gb}
            else:
                return {"status":"out","label":"🔴 Out of Race","color":"#ef4444","seed":seed,"wins":int(wins),"losses":int(losses),"gb":gb}
        return None

    # ESPN standings — /apis/v2/ is correct for standings (not /apis/site/v2/)
    # Try with and without season param
    import requests as _req
    urls_params = [
        ("https://site.api.espn.com/apis/v2/sports/basketball/nba/standings", {"season": "2026"}),
        ("https://site.api.espn.com/apis/v2/sports/basketball/nba/standings", {}),
        ("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/standings", {"season": "2026"}),
    ]
    for url, params in urls_params:
        try:
            r = _req.get(url, params=params,
                        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
                        timeout=8)
            if not r.ok:
                continue
            data = r.json()
            if not data:
                continue
            # Structure 1: children → standings → entries
            for conf in data.get("children", []):
                entries = conf.get("standings", {}).get("entries", [])
                result = _parse_entries(entries)
                if result:
                    return result
            # Structure 2: direct entries
            result = _parse_entries(data.get("entries", []))
            if result:
                return result
            # Structure 3: groups
            for group in data.get("groups", []):
                result = _parse_entries(group.get("entries", []))
                if result:
                    return result
        except Exception:
            continue
    return {}


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
- Schedule: {b2b_status}{"  — FATIGUE RISK, second night of back-to-back" if b2b_status == "B2B" else ""} · Rest: {rest_status}
- Injury status: {_inj_status}{f" ({_inj_reason})" if _inj_reason else ""}
- Usage spike: {f"YES — {', '.join(p['name'] for p in _spike_players)} out ({', '.join(str(p['minutes']) for p in _spike_players)} mpg)" if _spike_players else "None detected"}
- Recent shooting (L3): 3PT% {f"{recent_3pt:.0%}" if recent_3pt is not None else "N/A"} · TS% {f"{recent_ts:.0%}" if recent_ts is not None else "N/A"} → {shoot_sig} signal
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

# ── Pre-warm cache from tonight's PrizePicks slate ───────────
def _prewarm_cache():
    """
    Silently pre-fetch game logs for tonight's PrizePicks NBA players.
    Runs once per day as a background daemon thread.
    After this runs, any player on tonight's slate loads instantly.
    """
    try:
        import requests as _req
        r = _req.get(
            "https://api.prizepicks.com/projections",
            params={"league_id": "7", "per_page": "250", "single_stat": "true"},
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            timeout=10,
        )
        if not r.ok:
            return
        data = r.json()
        included = data.get("included", [])
        player_names = list({
            p.get("attributes", {}).get("name", "")
            for p in included
            if p.get("type") == "new_player"
            and p.get("attributes", {}).get("name")
        })
        if not player_names:
            return
        import concurrent.futures as _cf
        _date = _cache_date()
        def _warm(name):
            try:
                nba_id, _ = nba_find_player(name)
                if nba_id:
                    nba_get_game_logs(nba_id, "2025-26", n=15, _date=_date)
                    nba_get_full_season_logs_cached(nba_id, "2025-26", _date=_date)
            except Exception:
                pass
        with _cf.ThreadPoolExecutor(max_workers=5) as ex:
            ex.map(_warm, player_names[:40])
    except Exception:
        pass


# ── Load tracker from Supabase on first run ──
if not st.session_state.supabase_loaded:
    _sb_entries = load_tracker_from_supabase(st.session_state.session_id)
    if _sb_entries:
        st.session_state.tracker = _sb_entries
    st.session_state.supabase_loaded = True

# ── Trigger pre-warm once per day per session ─────────────────
if st.session_state.get("prewarm_date") != _cache_date():
    st.session_state.prewarm_date = _cache_date()
    import threading as _t
    _t.Thread(target=_prewarm_cache, daemon=True).start()

st.markdown("""
<div class="pl-header">
    <div class="pl-logo-wrap">
        <div class="pl-icon" style="position:relative;overflow:hidden;width:52px;height:44px;">
            <svg width="52" height="44" viewBox="0 0 52 44" fill="none" style="display:block;">
                <!-- Left bars growing up -->
                <rect class="pl-bar pl-bar-1" x="0"  y="30" width="6" height="10" fill="#1e40af" rx="0.5"/>
                <rect class="pl-bar pl-bar-2" x="7"  y="22" width="6" height="18" fill="#1d4ed8" rx="0.5"/>
                <rect class="pl-bar pl-bar-3" x="14" y="14" width="6" height="26" fill="#2563eb" rx="0.5"/>
                <rect class="pl-bar pl-bar-4" x="21" y="8"  width="6" height="32" fill="#3b82f6" rx="0.5"/>
                <!-- Divider -->
                <rect x="29" y="16" width="2" height="24" fill="#1e2a3a" rx="0.5"/>
                <!-- Right bars growing up -->
                <rect class="pl-bar pl-bar-5" x="33" y="8"  width="6" height="32" fill="#3b82f6" rx="0.5"/>
                <rect class="pl-bar pl-bar-6" x="40" y="14" width="6" height="26" fill="#2563eb" rx="0.5"/>
                <rect class="pl-bar pl-bar-7" x="47" y="22" width="5" height="18" fill="#1d4ed8" rx="0.5"/>
                <!-- Basketball bouncing on left peak -->
                <g class="pl-bball">
                    <circle cx="24" cy="6" r="6" fill="#ea580c"/>
                    <path d="M18 6 Q24 3 30 6" fill="none" stroke="#7c2d12" stroke-width="0.9"/>
                    <path d="M18 6 Q24 9 30 6" fill="none" stroke="#7c2d12" stroke-width="0.9"/>
                    <line x1="24" y1="0" x2="24" y2="12" stroke="#7c2d12" stroke-width="0.9"/>
                </g>
                <!-- Baseball bouncing on right peak -->
                <g class="pl-bbase">
                    <circle cx="36" cy="6" r="5" fill="#f1f5f9"/>
                    <path d="M32 4 Q34 6 32 8"  fill="none" stroke="#ef4444" stroke-width="0.9" stroke-linecap="round"/>
                    <path d="M40 4 Q38 6 40 8"  fill="none" stroke="#ef4444" stroke-width="0.9" stroke-linecap="round"/>
                </g>
                <!-- Scan line sweeping across -->
                <rect class="pl-scan" x="0" y="0" width="3" height="44" fill="#3b82f6" opacity="0.5" rx="1"/>
            </svg>
        </div>
        <div>
            <div class="pl-logo">Prop<span>Lens</span></div>
            <div class="pl-sub">Sports Prop Analyzer · AI-Powered</div>
        </div>
    </div>
    <div style="display:flex; align-items:center; gap:10px;">
        <span class="pl-badge">V5.0</span>
    </div>
</div>
<div class="pl-ticker">
    <div class="pl-ticker-item">
        <div class="pl-ticker-dot"></div>
        <span>LIVE · NBA PLAYOFFS 2026 · MLB 2026</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sport Switcher
# ─────────────────────────────────────────────
_sp1, _sp2, _sp3 = st.columns([1, 1, 3])
with _sp1:
    if st.button(
        "🏀  NBA",
        key="sport_nba",
        use_container_width=True,
        type="primary" if st.session_state.active_sport == "nba" else "secondary"
    ):
        st.session_state.active_sport = "nba"
        st.rerun()
with _sp2:
    if st.button(
        "⚾  MLB",
        key="sport_mlb",
        use_container_width=True,
        type="primary" if st.session_state.active_sport == "mlb" else "secondary"
    ):
        st.session_state.active_sport = "mlb"
        st.rerun()


st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1rem 0; border-bottom:2px solid #3b82f6; margin-bottom:1rem;'>
        <div style='font-family:Barlow Condensed,sans-serif; font-size:1.3rem; font-weight:900; color:#f0f0f0; letter-spacing:-0.5px; text-transform:uppercase; margin-bottom:2px;'>Prop<span style="color:#3b82f6;">Lens</span></div>
        <div style='font-family:JetBrains Mono,monospace; font-size:0.55rem; color:#555; letter-spacing:0.18em; text-transform:uppercase;'>Sports Prop Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>How To Use PropLens</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex;flex-direction:column;gap:8px;'>
        <div style='display:flex;gap:12px;align-items:flex-start;background:#0d1520;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:0.75rem 1rem;'>
            <div style='min-width:28px;height:28px;background:#3b82f6;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:Outfit,sans-serif;font-weight:800;font-size:0.9rem;color:#fff;flex-shrink:0;'>1</div>
            <div>
                <div style='font-family:Outfit,sans-serif;font-weight:600;color:#f1f5f9;font-size:0.85rem;'>Open PrizePicks and find a prop you like</div>
                <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;margin-top:3px;'>Example: LeBron James — 22.5 pts — Over</div>
            </div>
        </div>
        <div style='display:flex;gap:12px;align-items:flex-start;background:#0d1520;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:0.75rem 1rem;'>
            <div style='min-width:28px;height:28px;background:#3b82f6;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:Outfit,sans-serif;font-weight:800;font-size:0.9rem;color:#fff;flex-shrink:0;'>2</div>
            <div>
                <div style='font-family:Outfit,sans-serif;font-weight:600;color:#f1f5f9;font-size:0.85rem;'>Type the player name, enter the line and pick Over or Under</div>
                <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;margin-top:3px;'>Always use the standard line — not the goblin (lower) or demon (higher)</div>
            </div>
        </div>
        <div style='display:flex;gap:12px;align-items:flex-start;background:#0d1520;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:0.75rem 1rem;'>
            <div style='min-width:28px;height:28px;background:#3b82f6;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:Outfit,sans-serif;font-weight:800;font-size:0.9rem;color:#fff;flex-shrink:0;'>3</div>
            <div>
                <div style='font-family:Outfit,sans-serif;font-weight:600;color:#f1f5f9;font-size:0.85rem;'>Hit Analyze Prop and wait ~10 seconds</div>
                <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;margin-top:3px;'>PropLens pulls live stats, injuries, matchups, referee data, and more</div>
            </div>
        </div>
        <div style='display:flex;gap:12px;align-items:flex-start;background:#0d1520;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:0.75rem 1rem;'>
            <div style='min-width:28px;height:28px;background:#10f590;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:Outfit,sans-serif;font-weight:800;font-size:0.9rem;color:#041a0e;flex-shrink:0;'>4</div>
            <div>
                <div style='font-family:Outfit,sans-serif;font-weight:600;color:#f1f5f9;font-size:0.85rem;'>Read the verdict — only play Strong Over / Strong Under</div>
                <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;margin-top:3px;'>Lean picks are OK in 2-leg entries only. Always skip Pass.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Verdict Guide</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex;flex-direction:column;gap:6px;'>
        <div style='background:#041a0e;border:1px solid rgba(16,245,144,0.2);border-radius:10px;padding:0.6rem 0.9rem;display:flex;justify-content:space-between;align-items:center;'>
            <div><span style='font-size:1rem;'>🟢</span> <span style='color:#10f590;font-weight:700;font-family:Outfit,sans-serif;'>Strong Over / Strong Under</span></div>
            <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;text-align:right;'>64%+ hit rate · edge ≥1.5pts<br><span style='color:#10f590;'>Best bets — play these</span></div>
        </div>
        <div style='background:#1a1200;border:1px solid rgba(251,191,36,0.2);border-radius:10px;padding:0.6rem 0.9rem;display:flex;justify-content:space-between;align-items:center;'>
            <div><span style='font-size:1rem;'>🟡</span> <span style='color:#fbbf24;font-weight:700;font-family:Outfit,sans-serif;'>Lean Over</span> &nbsp;<span style='font-size:1rem;'>🟠</span> <span style='color:#f97316;font-weight:700;font-family:Outfit,sans-serif;'>Lean Under</span></div>
            <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;text-align:right;'>55–63% hit rate<br><span style='color:#fbbf24;'>OK for 2-leg entries only</span></div>
        </div>
        <div style='background:#111;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:0.6rem 0.9rem;display:flex;justify-content:space-between;align-items:center;'>
            <div><span style='font-size:1rem;'>⚪</span> <span style='color:#475569;font-weight:700;font-family:Outfit,sans-serif;'>Pass</span></div>
            <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;text-align:right;'>No clear edge<br><span style='color:#ef4444;'>Skip this prop</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Confidence Score</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:JetBrains Mono,monospace;font-size:0.68rem;color:#475569;line-height:1.9;
                background:#0d1520;border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:0.75rem 1rem;'>
        The <span style='color:#f1f5f9;'>confidence score (0–100)</span> combines three things:<br>
        &nbsp;&nbsp;<span style='color:#3b82f6;'>●</span> <span style='color:#94a3b8;'>Hit rate</span> — how often has this player cleared this line?<br>
        &nbsp;&nbsp;<span style='color:#3b82f6;'>●</span> <span style='color:#94a3b8;'>Edge</span> — how far is their average above/below the line?<br>
        &nbsp;&nbsp;<span style='color:#3b82f6;'>●</span> <span style='color:#94a3b8;'>Consistency</span> — do they score reliably or all over the place?<br><br>
        <span style='color:#10f590;'>80+</span> = elite pick &nbsp;·&nbsp; <span style='color:#fbbf24;'>65–79</span> = solid &nbsp;·&nbsp; <span style='color:#ef4444;'>below 65</span> = skip
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

    st.markdown("<div class='section-header'>Advanced Tools</div>", unsafe_allow_html=True)
    with st.expander("📊  Backtest Engine"):
        st.markdown("""
        <div style='font-family:DM Mono;font-size:0.68rem;color:#475569;line-height:1.6;margin-bottom:0.75rem;'>
        Simulate PropLens on a full season to see how often each verdict tier actually hit.
        Use this to validate the model on specific players and lines.
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Mode selector
# ─────────────────────────────────────────────

for _k in ["scanner_results", "scanner_error"]:
    if _k not in st.session_state:
        st.session_state[_k] = None

# ═══════════════════════════════════════════════════════
# MLB MODE
# ═══════════════════════════════════════════════════════

if st.session_state.active_sport == "mlb":

    # ── MLB Data Functions ─────────────────────────────

    @st.cache_data(ttl=14400, show_spinner=False)
    def mlb_get_pitcher_logs(player_name: str, n: int = 10) -> pd.DataFrame:
        """
        Fetch pitcher game logs from MLB Stats API.
        Returns last N starts with K, IP, outs recorded.
        """
        empty = pd.DataFrame(columns=["DATE","OPP","IP","OUTS","K","BB","ER","RESULT"])
        try:
            import requests as _req

            # Step 1: Get all active MLB players (much more reliable than people/search)
            _norm_name = lambda s: s.lower().strip()
            _target = _norm_name(player_name)
            _parts  = [p for p in _target.split() if len(p) > 2]
            _last   = _target.split()[-1]

            people = []

            # Try all-players endpoint first
            _all_r = _req.get(
                "https://statsapi.mlb.com/api/v1/sports/1/players",
                params={"season": datetime.datetime.now().year, "gameType": "R"},
                timeout=10
            )
            if _all_r.ok:
                _all   = _all_r.json().get("people", [])
                # Exact full name match first
                people = [p for p in _all if _norm_name(p.get("fullName","")) == _target]
                # Last name exact match
                if not people:
                    people = [p for p in _all if _norm_name(p.get("fullName","")).split()[-1] == _last]
                # Partial match — all parts present
                if not people:
                    people = [p for p in _all if all(pt in _norm_name(p.get("fullName","")) for pt in _parts)]

            # Fallback: old search endpoint
            if not people:
                _s = _req.get(
                    "https://statsapi.mlb.com/api/v1/people/search",
                    params={"names": player_name, "sportIds": 1},
                    timeout=8
                )
                if _s.ok:
                    people = _s.json().get("people", [])

            # Last resort: search by last name only
            if not people:
                _s2 = _req.get(
                    "https://statsapi.mlb.com/api/v1/people/search",
                    params={"names": _last, "sportIds": 1},
                    timeout=8
                )
                if _s2.ok:
                    _res2 = _s2.json().get("people", [])
                    _first = _target.split()[0]
                    people = [p for p in _res2 if _first in _norm_name(p.get("fullName",""))] or _res2

            if not people:
                return empty

            # Find pitcher
            pitcher = next(
                (p for p in people if p.get("primaryPosition", {}).get("code") == "1"),
                people[0]
            )
            pid = pitcher["id"]

            # Get game logs
            import datetime
            season = datetime.datetime.now().year
            logs_r = _req.get(
                f"https://statsapi.mlb.com/api/v1/people/{pid}/stats",
                params={
                    "stats": "gameLog",
                    "group": "pitching",
                    "season": season,
                    "gameType": "R",
                    "limit": n + 5,
                },
                timeout=10
            )
            if not logs_r.ok:
                return empty

            splits = logs_r.json().get("stats", [{}])[0].get("splits", [])
            if not splits:
                return empty

            rows = []
            for s in splits[:n]:
                stat = s.get("stat", {})
                game = s.get("game", {})
                team = s.get("opponent", {}).get("abbreviation", "?")
                date = s.get("date", "")[:10]

                ip_str = str(stat.get("inningsPitched", "0"))
                try:
                    ip_parts = ip_str.split(".")
                    full_inn = int(ip_parts[0])
                    partial  = int(ip_parts[1]) if len(ip_parts) > 1 else 0
                    outs = full_inn * 3 + partial
                except Exception:
                    outs = 0

                rows.append({
                    "DATE":   date,
                    "OPP":    team,
                    "IP":     ip_str,
                    "OUTS":   outs,
                    "K":      int(stat.get("strikeOuts", 0)),
                    "BB":     int(stat.get("baseOnBalls", 0)),
                    "ER":     int(stat.get("earnedRuns", 0)),
                    "RESULT": stat.get("note", ""),
                })

            df = pd.DataFrame(rows)
            df["DATE"] = pd.to_datetime(df["DATE"])
            return df.sort_values("DATE", ascending=False).reset_index(drop=True)

        except Exception:
            return empty

    # ── MLB Park factors ──────────────────────────────────────
    _MLB_PARK_FACTORS = {
        "COL": 1.30, "CIN": 1.10, "BOS": 1.08, "PHI": 1.06,
        "TEX": 1.05, "NYY": 1.04, "CHC": 1.03, "HOU": 1.02,
        "ATL": 1.01, "MIL": 1.01, "STL": 1.00, "LAD": 0.99,
        "NYM": 0.99, "TOR": 0.98, "DET": 0.98, "MIN": 0.97,
        "CLE": 0.97, "ARI": 0.97, "BAL": 0.97, "KCR": 0.96,
        "PIT": 0.96, "TBR": 0.96, "CHW": 0.95, "SEA": 0.95,
        "SFG": 0.94, "MIA": 0.94, "LAA": 0.94, "WSN": 0.93,
        "OAK": 0.93, "SDP": 0.92,
    }

    @st.cache_data(ttl=3600, show_spinner=False)
    def mlb_get_opp_k_rate(opp_abbr: str) -> Optional[float]:
        try:
            import requests as _req, datetime
            season = datetime.datetime.now().year
            teams_r = _req.get("https://statsapi.mlb.com/api/v1/teams",
                params={"sportId":1,"season":season}, timeout=8)
            if not teams_r.ok: return None
            teams = teams_r.json().get("teams",[])
            team  = next((t for t in teams if t.get("abbreviation","").upper()==opp_abbr.upper()),None)
            if not team: return None
            stats_r = _req.get(f"https://statsapi.mlb.com/api/v1/teams/{team['id']}/stats",
                params={"stats":"season","group":"hitting","season":season}, timeout=8)
            if not stats_r.ok: return None
            stat = stats_r.json().get("stats",[{}])[0].get("splits",[{}])[0].get("stat",{})
            ab = int(stat.get("atBats",0)); k = int(stat.get("strikeOuts",0))
            return round(k/ab,3) if ab>0 else None
        except Exception: return None

    @st.cache_data(ttl=1800, show_spinner=False)
    @st.cache_data(ttl=900, show_spinner=False)
    def mlb_get_tonight_game(pitcher_name: str, team_abbr: str = "") -> dict:
        """
        Find tonight's game for a pitcher.
        Primary: match by team abbreviation (from PrizePicks).
        Fallback: match by pitcher name in probable pitchers.
        """
        import requests as _req, datetime, pytz
        try:
            et    = pytz.timezone("America/New_York")
            today = datetime.datetime.now(et).strftime("%Y-%m-%d")
            sched = _req.get(
                "https://statsapi.mlb.com/api/v1/schedule",
                params={"sportId":1,"date":today,"hydrate":"probablePitcher,team,venue"},
                timeout=10
            )
            if not sched.ok: return {}
            games = []
            for d in sched.json().get("dates",[]): games.extend(d.get("games",[]))

            def _build(game, side):
                home  = game["teams"]["home"]["team"]["abbreviation"]
                away  = game["teams"]["away"]["team"]["abbreviation"]
                opp   = away if side=="home" else home
                venue = game.get("venue",{}).get("name","")
                return {"opp":opp,"home_team":home,"away_team":away,
                        "pitcher_side":side,"venue":venue,"game_date":today,
                        "pitcher_team":home if side=="home" else away}

            # Pass 1: match by team abbreviation (most reliable)
            if team_abbr:
                for game in games:
                    for side in ["home","away"]:
                        abbr = game["teams"][side]["team"].get("abbreviation","")
                        if abbr.upper() == team_abbr.upper():
                            return _build(game, side)

            # Pass 2: match by probable pitcher last name
            _norm  = lambda s: s.lower().replace("-"," ").replace(".","").strip()
            _last  = _norm(pitcher_name).split()[-1] if pitcher_name else ""
            _parts = [p for p in _norm(pitcher_name).split() if len(p) > 3]
            for game in games:
                for side in ["home","away"]:
                    prob  = game.get("teams",{}).get(side,{}).get("probablePitcher",{})
                    pname = _norm(prob.get("fullName","") or prob.get("lastName",""))
                    if not pname: continue
                    if (_last and _last == pname.split()[-1]) or any(p in pname for p in _parts):
                        return _build(game, side)

        except Exception:
            pass
        return {}

    @st.cache_data(ttl=1800, show_spinner=False)
    def _mlb_get_opp_from_team(team_abbr: str) -> str:
        """Get tonight's opponent for a team by abbreviation."""
        try:
            import requests as _req, datetime, pytz
            et    = pytz.timezone("America/New_York")
            today = datetime.datetime.now(et).strftime("%Y-%m-%d")
            r = _req.get(
                "https://statsapi.mlb.com/api/v1/schedule",
                params={"sportId": 1, "date": today, "hydrate": "team"},
                timeout=8
            )
            if not r.ok: return ""
            for d in r.json().get("dates", []):
                for game in d.get("games", []):
                    home = game["teams"]["home"]["team"].get("abbreviation","")
                    away = game["teams"]["away"]["team"].get("abbreviation","")
                    if home.upper() == team_abbr.upper():
                        return away
                    if away.upper() == team_abbr.upper():
                        return home
        except Exception:
            pass
        return ""

    def mlb_weighted_hr(logs, line, stat, side):
        vals = pd.to_numeric(logs[stat], errors="coerce").dropna().reset_index(drop=True)
        n = len(vals)
        if n==0: return 0.0
        weights=[n-i for i in range(n)]; tw=sum(weights)
        hits=sum(w for v,w in zip(vals,weights) if (v>=line if side=="Over" else v<=line))
        return hits/tw

    def mlb_park_signal(home_team):
        pf = _MLB_PARK_FACTORS.get(home_team,1.00)
        if pf<=0.95: return "Boost"
        elif pf>=1.06: return "Penalty"
        return "Neutral"

    def mlb_apply_adj(weighted, opp_k, park, side):
        adj = weighted
        if opp_k is not None:
            if opp_k>=0.26:   adj += 0.06 if side=="Over" else -0.06
            elif opp_k<=0.18: adj += -0.06 if side=="Over" else 0.06
        adj += {"Boost":+0.04,"Neutral":0.0,"Penalty":-0.04}.get(park,0.0)*(1 if side=="Over" else -1)
        return max(0.05,min(0.95,adj))

    def mlb_verdict(adj, edge, side):
        if side=="Over":
            if adj>=0.64 and edge>=1.0: return "Strong Over"
            if adj>=0.55 and edge>0:    return "Lean Over"
        else:
            if adj>=0.64 and edge<=-1.0: return "Strong Under"
            if adj>=0.55 and edge<0:     return "Lean Under"
        return "Pass"

    # ── MLB UI ────────────────────────────────────────────────
    st.markdown("<div class='section-header'>⚾ MLB Pitcher Prop Analyzer</div>", unsafe_allow_html=True)

    _mlb_pitchers = sorted([
        # Dodgers
        "Yoshinobu Yamamoto","Tyler Glasnow","Shohei Ohtani","Roki Sasaki","Emmet Sheehan",
        # Yankees
        "Gerrit Cole","Carlos Rodon","Luis Gil","Clarke Schmidt","Will Warren",
        # Phillies
        "Zack Wheeler","Aaron Nola","Cristopher Sanchez","Jesus Luzardo",
        # Braves
        "Spencer Strider","Max Fried","Charlie Morton","Reynaldo Lopez",
        # Cubs
        "Shota Imanaga","Justin Steele","Kyle Hendricks","Jameson Taillon",
        # Mariners
        "Luis Castillo","George Kirby","Logan Gilbert","Bryan Woo","Bryce Miller",
        # Brewers
        "Corbin Burnes","Freddy Peralta","Colin Rea","Jacob Misiorowski",
        # Giants
        "Logan Webb","Blake Snell","Keaton Winn","Hayden Birdsong",
        # Astros
        "Framber Valdez","Hunter Brown","Ronel Blanco","Spencer Arrighetti",
        # Cardinals
        "Sonny Gray","Miles Mikolas","Lance Lynn","Matthew Liberatore",
        # Pirates
        "Paul Skenes","Mitch Keller","Marco Gonzales","Bubba Chandler",
        # Twins
        "Pablo Lopez","Joe Ryan","Bailey Ober","David Festa",
        # Rangers
        "Nathan Eovaldi","Andrew Heaney","Michael Lorenzen","Dane Dunning",
        # Red Sox
        "Garrett Crochet","Tanner Houck","Kutter Crawford","Quinn Priester",
        # Padres
        "Dylan Cease","Yu Darvish","Randy Vasquez","Michael King",
        # Guardians
        "Shane Bieber","Tanner Bibee","Gavin Williams","Matthew Boyd",
        # Tigers
        "Tarik Skubal","Casey Mize","Jackson Jobe","Keider Montero",
        # Mets
        "Kodai Senga","Sean Manaea","Clay Holmes","Frankie Montas",
        # Marlins
        "Sandy Alcantara","Braxton Garrett","Cal Quantrill","Trevor Rogers",
        # Dbacks
        "Zac Gallen","Merrill Kelly","Brandon Pfaadt","Ryne Nelson",
        # White Sox
        "Garrett Crochet","Chris Flexen","Jonathan Cannon","Davis Martin",
        # Athletics
        "JP Sears","Ross Stripling","Joey Estes","Mitch Spence",
        # Blue Jays
        "Kevin Gausman","Chris Bassitt","Bowden Francis","Yariel Rodriguez",
        # Orioles
        "Corbin Burnes","Kyle Bradish","Grayson Rodriguez","Trevor Rogers",
        # Nationals
        "MacKenzie Gore","Patrick Corbin","Jake Irvin","Mitchell Parker",
        # Reds
        "Hunter Greene","Andrew Abbott","Nick Lodolo","Rhett Lowder",
        # Rockies
        "Kyle Freeland","Austin Gomber","Ryan Feltner","Cal Quantrill",
        # Angels
        "Tyler Anderson","Patrick Sandoval","Griffin Canning","Reid Detmers",
        # Royals
        "Seth Lugo","Cole Ragans","Michael Wacha","Brady Singer",
        # Cubs additional
        "Kyle Hendricks",
        # Additional notable arms
        "Max Scherzer","Justin Verlander","Chris Sale","Yusei Kikuchi",
        "Lucas Giolito","Bobby Miller","Dustin May","Michael Lorenzen",
        "Cam Schlittler","Will Warren",
    ])
    # Deduplicate
    _mlb_pitchers = sorted(set(_mlb_pitchers))

    _mc1,_mc2,_mc3,_mc4 = st.columns([2.5,1,1,1])
    with _mc1:
        mlb_pitcher = st.selectbox("Pitcher — type to search",
            options=[""]+_mlb_pitchers,
            format_func=lambda x:"— select a pitcher —" if x=="" else x,
            key="mlb_pitcher_sel")
    with _mc2:
        mlb_prop = st.selectbox("Prop",["Strikeouts","Outs Recorded"],key="mlb_prop_type")
    with _mc3:
        mlb_line = st.number_input("Line",min_value=0.5,max_value=30.0,value=5.5,step=0.5,key="mlb_line")
    with _mc4:
        mlb_side = st.selectbox("Over / Under",["Over","Under"],key="mlb_side")

    _tonight = mlb_get_tonight_game(mlb_pitcher) if mlb_pitcher else {}
    mlb_opp  = _tonight.get("opp","")
    mlb_home = _tonight.get("home_team","")

    if mlb_pitcher and _tonight:
        _od = f"vs {mlb_opp} · {_tonight.get('venue','')} · {'Home' if _tonight.get('pitcher_side')=='home' else 'Away'}"
        st.markdown(f"<div style='background:#111;border:1px solid #1e2a3a;border-left:3px solid #3b82f6;"
                    f"padding:0.5rem 1rem;margin-bottom:0.5rem;font-family:JetBrains Mono,monospace;"
                    f"font-size:0.68rem;color:#3b82f6;'>🎯 TONIGHT: {_od}</div>",unsafe_allow_html=True)
    elif mlb_pitcher:
        # Try to figure out next start from recent logs
        _last_date = None
        try:
            _tmp_logs = mlb_get_pitcher_logs(mlb_pitcher, n=1)
            if not _tmp_logs.empty:
                _last_date = pd.to_datetime(_tmp_logs.iloc[0]["DATE"]).strftime("%b %d")
        except Exception:
            pass
        _last_str = f" · Last start: {_last_date}" if _last_date else ""
        st.markdown(
            f"<div style='background:#111;border:1px solid #1e2a3a;border-left:3px solid #f97316;"
            f"padding:0.5rem 1rem;margin-bottom:0.5rem;font-family:JetBrains Mono,monospace;"
            f"font-size:0.68rem;color:#f97316;'>⚠️ No game found for today — {mlb_pitcher} may not be scheduled to pitch{_last_str}."
            f" Park + opponent signals will be unavailable.</div>",
            unsafe_allow_html=True
        )

    mlb_fetch = st.button("⚾  Analyze Pitcher Prop", key="mlb_analyze")

    if not mlb_pitcher:
        st.markdown("<div style='color:#555;font-family:JetBrains Mono,monospace;font-size:0.75rem;"
                    "margin-top:0.5rem;'>↑ Select a pitcher to get started.</div>",unsafe_allow_html=True)

    if mlb_fetch and mlb_pitcher:
        _stat = "K" if mlb_prop=="Strikeouts" else "OUTS"
        _lbl  = "K" if mlb_prop=="Strikeouts" else "Outs"

        _mlb_ph = st.empty()
        _mlb_ph.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;"
                         "color:#555;padding:0.5rem 0;'>⏳ FETCHING GAME LOGS...</div>",
                         unsafe_allow_html=True)
        mlb_logs = mlb_get_pitcher_logs(mlb_pitcher, n=10)

        _mlb_ph.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;"
                         "color:#555;padding:0.5rem 0;'>⏳ LOADING MATCHUP + CONTEXT...</div>",
                         unsafe_allow_html=True)

        if mlb_logs.empty:
            _mlb_ph.empty()
            st.error("Could not fetch pitcher data. Check the name and try again.")
        else:
            vals    = pd.to_numeric(mlb_logs[_stat], errors="coerce").dropna()
            avg_val = vals.mean()
            edge    = avg_val - mlb_line

            # ── Signal 1: Weighted hit rate
            whr = mlb_weighted_hr(mlb_logs, mlb_line, _stat, mlb_side)

            # ── Signal 2: Opponent K% (from tonight's game)
            okpct = mlb_get_opp_k_rate(mlb_opp) if mlb_opp else None

            # ── Signal 3: Park factor
            psig = mlb_park_signal(mlb_home) if mlb_home else "Neutral"

            # ── Signal 4: Home/Away split from logs
            _home_logs = mlb_logs[mlb_logs.get("HOME", pd.Series([True]*len(mlb_logs))).astype(bool)] if "HOME" in mlb_logs.columns else mlb_logs
            _away_logs = mlb_logs[~mlb_logs.get("HOME", pd.Series([True]*len(mlb_logs))).astype(bool)] if "HOME" in mlb_logs.columns else pd.DataFrame()
            _ha_adj = 0.0
            if len(_home_logs) >= 3 and len(_away_logs) >= 3:
                _home_avg = pd.to_numeric(_home_logs[_stat], errors="coerce").dropna().mean()
                _away_avg = pd.to_numeric(_away_logs[_stat], errors="coerce").dropna().mean()
                _ha_diff  = _home_avg - _away_avg
                _is_home  = _tonight.get("pitcher_side","") == "home"
                if abs(_ha_diff) >= 1.0:
                    _ha_adj = 0.04 if (_is_home and _ha_diff > 0) or (not _is_home and _ha_diff < 0) else -0.04

            # ── Signal 5: Recent form — L3 vs L10
            _l3_avg = pd.to_numeric(mlb_logs.head(3)[_stat], errors="coerce").dropna().mean()
            _form_diff = _l3_avg - avg_val if not pd.isna(_l3_avg) else 0
            _form_adj = 0.0
            if _form_diff >= 1.5:   _form_adj = +0.04   # trending up
            elif _form_diff <= -1.5: _form_adj = -0.04  # trending down

            # ── Signal 6: Rest days
            _rest_adj = 0.0
            if len(mlb_logs) >= 2 and "DATE" in mlb_logs.columns:
                try:
                    _last_start = pd.to_datetime(mlb_logs.iloc[0]["DATE"])
                    _rest_days  = (pd.Timestamp.now() - _last_start).days
                    if _rest_days <= 3:   _rest_adj = -0.03  # short rest
                    elif _rest_days >= 7: _rest_adj = +0.02  # extra rest
                except Exception:
                    pass

            # ── Apply all adjustments
            adj = mlb_apply_adj(whr, okpct, psig, mlb_side)
            adj = max(0.05, min(0.95, adj + _ha_adj + _form_adj + _rest_adj))
            tier = mlb_verdict(adj, edge, mlb_side)

            # Consistency
            cv   = vals.std()/avg_val if avg_val>0 else 1.0
            cons = max(0.1, min(0.95, 1.0 - cv*0.8))

            # Confidence — hit rate dominant, edge matters less in MLB
            _sc = min(99, int(
                max(0, min((adj-0.50)/0.45, 1.0)*70) +
                min(abs(edge)/8.0, 1.0)*15 +
                cons*10 +
                (5 if okpct is not None else 0)  # bonus for having opponent data
            ))
            _cc  = "#3b82f6" if _sc>=80 else ("#eab308" if _sc>=65 else "#f97316")
            css  = {"Strong Over":"green","Lean Over":"yellow","Strong Under":"red","Lean Under":"orange","Pass":"gray"}.get(tier,"gray")

            _mlb_ph.empty()

            # ── Signal summary pills
            _pills = []
            if okpct is not None:
                _opp_lbl = "High-K opp" if okpct>=0.26 else ("Low-K opp" if okpct<=0.18 else "Avg-K opp")
                _opp_flag = "up" if okpct>=0.26 else ("down" if okpct<=0.18 else "flat")
                _pills.append(f"<span class='flag-pill {_opp_flag}'>{_opp_lbl} {okpct:.0%}</span>")
            _pills.append(f"<span class='flag-pill {"up" if psig=="Boost" else "down" if psig=="Penalty" else "flat"}'>{psig} park</span>")
            if _form_adj > 0:  _pills.append("<span class='flag-pill up'>Form ↑ trending</span>")
            if _form_adj < 0:  _pills.append("<span class='flag-pill down'>Form ↓ trending</span>")
            if _rest_adj < 0:  _pills.append("<span class='flag-pill down'>Short rest</span>")
            if _rest_adj > 0:  _pills.append("<span class='flag-pill up'>Extra rest</span>")
            _is_home_txt = _tonight.get("pitcher_side","")
            if _is_home_txt:
                _pills.append(f"<span class='flag-pill flat'>{'Home' if _is_home_txt=='home' else 'Away'} start</span>")

            st.markdown("<div class='section-header'>Key Stats</div>", unsafe_allow_html=True)
            _c1,_c2,_c3,_c4 = st.columns(4)
            with _c1:
                _ac="green" if (edge>0 and mlb_side=="Over") or (edge<0 and mlb_side=="Under") else "red"
                st.markdown(f"<div class='stat-card'><div class='stat-label'>Avg {_lbl} (L{len(vals)})</div>"
                            f"<div class='stat-value {_ac}'>{avg_val:.1f}</div>"
                            f"<div class='stat-hint'>Line {mlb_line} · edge {edge:+.1f}</div></div>",unsafe_allow_html=True)
            with _c2:
                hc="green" if whr>=0.64 else ("yellow" if whr>=0.55 else "red")
                st.markdown(f"<div class='stat-card'><div class='stat-label'>Hit Rate</div>"
                            f"<div class='stat-value {hc}'>{whr:.0%}</div>"
                            f"<div class='stat-hint'>Weighted L10</div></div>",unsafe_allow_html=True)
            with _c3:
                cc2="green" if cons>=0.5 else ("yellow" if cons>=0.35 else "red")
                st.markdown(f"<div class='stat-card'><div class='stat-label'>Consistency</div>"
                            f"<div class='stat-value {cc2}'>{cons:.0%}</div>"
                            f"<div class='stat-hint'>Start variance</div></div>",unsafe_allow_html=True)
            with _c4:
                _opp_str = f"vs {mlb_opp}" if mlb_opp else "Opp: TBD"
                st.markdown(f"<div class='stat-card'><div class='stat-label'>Confidence</div>"
                            f"<div class='stat-value' style='color:{_cc};'>{_sc}</div>"
                            f"<div class='stat-hint'>{_opp_str} · {psig} park</div></div>",unsafe_allow_html=True)

            # Signal pills
            if _pills:
                st.markdown(f"<div class='flag-row'>{''.join(_pills)}</div>", unsafe_allow_html=True)
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            st.markdown("<div class='section-header'>Last 10 Starts</div>",unsafe_allow_html=True)
            _d = mlb_logs.copy()
            _d["HIT"] = _d[_stat].apply(lambda x:"✅" if (mlb_side=="Over" and float(x)>=mlb_line) or (mlb_side=="Under" and float(x)<=mlb_line) else "❌")
            _d["DATE"] = _d["DATE"].dt.strftime("%b %d")
            st.dataframe(_d[["DATE","OPP","IP","K","OUTS","BB","ER","HIT"]],use_container_width=True,hide_index=True)

            tier_emoji={"Strong Over":"🟢","Lean Over":"🟡","Strong Under":"🔴","Lean Under":"🟠","Pass":"⚪"}
            _cl="Predictable" if cons>=0.5 else ("Variable" if cons>=0.35 else "Volatile")
            st.markdown("<div class='section-header'>Verdict</div>",unsafe_allow_html=True)
            st.markdown(
                f"<div class='verdict-banner {css}'>"
                f"<div><div class='verdict-label'>{mlb_pitcher} · {mlb_line} {_lbl} · {mlb_side}</div>"
                f"<div class='verdict-tier {css}'>{tier_emoji.get(tier,'⚪')} {tier}</div></div>"
                f"<div style='display:flex;gap:2rem;flex-wrap:wrap;align-items:flex-start;'>"
                f"<div><div class='verdict-label'>Confidence</div>"
                f"<div style='font-family:Barlow Condensed,sans-serif;font-size:1.8rem;font-weight:900;color:{_cc};'>{_sc}</div>"
                f"<div style='font-family:JetBrains Mono,monospace;font-size:0.55rem;color:#555;'>/100</div></div>"
                f"<div><div class='verdict-label'>Adjusted HR</div><div style='font-size:1.4rem;font-weight:800;color:#f0f0f0;'>{adj:.0%}</div></div>"
                f"<div><div class='verdict-label'>Edge</div><div style='font-size:1.4rem;font-weight:800;color:#f0f0f0;'>{edge:+.1f}</div></div>"
                f"<div><div class='verdict-label'>Consistency</div><div style='font-size:1.4rem;font-weight:800;color:#f0f0f0;'>{cons:.0%}</div>"
                f"<div style='font-family:JetBrains Mono,monospace;font-size:0.6rem;color:#555;'>{_cl}</div></div>"
                f"</div></div>",unsafe_allow_html=True)

    # ── MLB Slate Scanner ────────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⚾ MLB Pitcher Slate Scanner</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='explainer'>
        Pulls tonight's pitcher strikeout props from PrizePicks and runs each through the model.
        <strong>Strong Only</strong> shows pitchers with 80%+ adjusted hit rate.
    </div>
    """, unsafe_allow_html=True)

    _ms1, _ms2, _ms3 = st.columns([1, 1, 2])
    with _ms1:
        _mlb_scan_run = st.button("🔍  Scan MLB Slate", key="mlb_scan_run")
    with _ms2:
        _mlb_filter = st.selectbox(
            "Show", ["All results", "Strong Only", "Strong + Lean"],
            key="mlb_scan_filter", label_visibility="collapsed"
        )

    if "mlb_scanner_results" not in st.session_state:
        st.session_state.mlb_scanner_results = None
    if "mlb_scanner_error" not in st.session_state:
        st.session_state.mlb_scanner_error = None

    if _mlb_scan_run:
        st.session_state.mlb_scanner_results = None
        st.session_state.mlb_scanner_error   = None
        _mlb_results = []

        _mlb_status = st.empty()
        _mlb_status.markdown(
            "<div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;"
            "color:#555;padding:0.5rem 0;'>⏳ FETCHING MLB SLATE FROM PRIZEPICKS...</div>",
            unsafe_allow_html=True
        )
        _mlb_slate = []
        try:
            import requests as _mreq
            _mr = _mreq.get(
                "https://api.prizepicks.com/projections",
                params={"league_id": 2, "per_page": 250, "single_stat": "true"},
                headers={"User-Agent":"Mozilla/5.0","Accept":"application/json",
                         "Referer":"https://prizepicks.com/"},
                timeout=15
            )
            _mdata = _mr.json()
            _mpmap = {}
            for _item in _mdata.get("included",[]):
                if _item.get("type") == "new_player":
                    _a = _item.get("attributes",{})
                    _mpmap[_item["id"]] = {
                        "name": _a.get("display_name", _a.get("name","")),
                        "team": _a.get("team_abbreviation",""),
                    }
            # Collect all stat types for debug
            _all_stat_types = set()
            for _proj in _mdata.get("data",[]):
                _st = _proj.get("attributes",{}).get("stat_type","")
                if _st: _all_stat_types.add(_st)
            st.session_state["mlb_debug_stat_types"] = sorted(_all_stat_types)

            # Pull ALL MLB props — filter to pitchers by position or stat type
            _PITCHER_STATS = {
                "strikeouts","strikeout","pitcher strikeouts","pitcher strikeout",
                "strike outs","strike out","ks","k's","pitching strikeouts",
                "pitching outs","outs recorded","innings pitched",
            }
            _seen_pitchers = set()
            for _proj in _mdata.get("data",[]):
                _a     = _proj.get("attributes",{})
                _stype = _a.get("stat_type","").lower().strip()
                _ln    = _a.get("line_score")
                if not _ln: continue
                _pid = _proj.get("relationships",{}).get("new_player",{}).get("data",{}).get("id")
                _pi  = _mpmap.get(_pid,{})
                _pname = _pi.get("name","")
                _pos   = _pi.get("position","").upper()
                if not _pname: continue
                # Include if it's a strikeout/pitcher stat OR if position is SP/RP/P
                _is_k_stat = ("strikeout" in _stype or "strike out" in _stype or
                              _stype in _PITCHER_STATS)
                _is_pitcher = _pos in ("SP","RP","P","PITCHER","LHP","RHP")
                if not (_is_k_stat or _is_pitcher):
                    continue
                if _pname in _seen_pitchers:
                    continue
                _seen_pitchers.add(_pname)
                _mlb_slate.append({
                    "pitcher":   _pname,
                    "team":      _pi.get("team",""),
                    "line":      float(_ln),
                    "stat_type": _stype,
                })
        except Exception as _me:
            st.session_state.mlb_scanner_error = f"Could not fetch slate: {_me}"

        _mlb_status.empty()

        if _mlb_slate:
            _mprog = st.progress(0)
            _mstat = st.empty()

            def _analyze_mlb_prop(_prop):
                try:
                    _pname = _prop["pitcher"]
                    _ln    = _prop["line"]
                    _logs  = mlb_get_pitcher_logs(_pname, n=10)
                    if _logs.empty or len(_logs) < 3:
                        return None
                    _vals  = pd.to_numeric(_logs["K"], errors="coerce").dropna()
                    if len(_vals) < 3:
                        return None
                    _avg   = _vals.mean()
                    _edge  = _avg - _ln
                    _whr   = mlb_weighted_hr(_logs, _ln, "K", "Over")
                    _tonight_g = mlb_get_tonight_game(_pname)
                    # Fallback: try last name only
                    if not _tonight_g and " " in _pname:
                        _tonight_g = mlb_get_tonight_game(_pname.split()[-1])
                    # Fallback: try first + last without middle
                    if not _tonight_g and len(_pname.split()) > 2:
                        _short = _pname.split()[0] + " " + _pname.split()[-1]
                        _tonight_g = mlb_get_tonight_game(_short)
                    _opp   = _tonight_g.get("opp","")
                    _home  = _tonight_g.get("home_team","")
                    # If still no opp, try to look up by team abbr from PrizePicks
                    if not _opp and _prop.get("team"):
                        _opp = _mlb_get_opp_from_team(_prop["team"])
                    _okpct = mlb_get_opp_k_rate(_opp) if _opp else None
                    _psig  = mlb_park_signal(_home) if _home else "Neutral"
                    _adj   = mlb_apply_adj(_whr, _okpct, _psig, "Over")
                    _tier  = mlb_verdict(_adj, _edge, "Over")
                    _cv    = _vals.std()/_avg if _avg>0 else 1.0
                    _cons  = max(0.1, min(0.95, 1.0-_cv*0.8))
                    # MLB: hit rate dominates — edge is less reliable predictor
                    _sc    = min(99, int(
                        max(0, min((_adj-0.50)/0.45,1.0)*80) +
                        min(abs(_edge)/10.0,1.0)*10 +
                        _cons*10
                    ))
                    return {
                        "Pitcher":    _pname,
                        "Team":       _prop.get("team",""),
                        "Opp":        _opp or "?",
                        "Line":       _ln,
                        "Avg K":      round(_avg,1),
                        "Edge":       round(_edge,1),
                        "Hit Rate":   f"{_whr:.0%}",
                        "Adjusted":   f"{_adj:.0%}",
                        "Park":       _psig,
                        "Tier":       _tier,
                        "_adj_raw":   _adj,
                        "_conf":      _sc,
                    }
                except Exception:
                    return None

            from concurrent.futures import ThreadPoolExecutor, as_completed
            _mfutures = {}
            with ThreadPoolExecutor(max_workers=4) as _mex:
                for _mp in _mlb_slate:
                    _mf = _mex.submit(_analyze_mlb_prop, _mp)
                    _mfutures[_mf] = _mp["pitcher"]
                _mdone = 0
                for _mf in as_completed(_mfutures):
                    _mdone += 1
                    _mprog.progress(_mdone/len(_mlb_slate))
                    _mstat.text(f"Analyzed {_mdone}/{len(_mlb_slate)} pitchers...")
                    _mres = _mf.result()
                    if _mres:
                        _mlb_results.append(_mres)

            _mprog.empty()
            _mstat.empty()
            st.session_state.mlb_scanner_results = sorted(
                _mlb_results, key=lambda x: -x.get("_conf",0)
            )

    if st.session_state.mlb_scanner_error:
        st.error(st.session_state.mlb_scanner_error)

    if st.session_state.mlb_scanner_results is not None:
        # Deduplicate by pitcher — keep highest confidence entry
        _seen = {}
        for _r in st.session_state.mlb_scanner_results:
            _pn = _r.get("Pitcher","")
            if _pn not in _seen or _r.get("_conf",0) > _seen[_pn].get("_conf",0):
                _seen[_pn] = _r
        _mres_all = sorted(_seen.values(), key=lambda x: -x.get("_conf",0))

        if _mlb_filter == "Strong Only":
            _mshow = [r for r in _mres_all if r["Tier"]=="Strong Over" and r.get("_adj_raw",0)>=0.80]
        elif _mlb_filter == "Strong + Lean":
            _mshow = [r for r in _mres_all if "Strong" in r["Tier"] or "Lean" in r["Tier"]]
        else:
            _mshow = _mres_all

        _mtc = {"Strong Over":"green","Lean Over":"yellow","Lean Under":"orange","Strong Under":"red","Pass":"gray"}
        _mte = {"Strong Over":"🟢","Lean Over":"🟡","Lean Under":"🟠","Strong Under":"🔴","Pass":"⚪"}

        if not _mshow:
            st.markdown(
                f"<div style='background:#111;border:1px solid #1e2a3a;border-left:3px solid #555;"
                f"padding:0.75rem 1rem;font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#555;'>"
                f"No {'Strong Overs with 80%+' if _mlb_filter=='Strong Only' else 'matching'} results on tonight's MLB slate.</div>",
                unsafe_allow_html=True
            )
            with st.expander("🛠️ Debug — what did the scanner find?"):
                _debug_types = st.session_state.get("mlb_debug_stat_types", [])
                if _debug_types:
                    st.write("All stat types returned by PrizePicks MLB:", _debug_types)
                st.write(f"Total pitchers on PrizePicks slate: {len(_mres_all)}")
                if _mres_all:
                    for _dbg in _mres_all:
                        st.write(f"{_dbg['Pitcher']} — Line: {_dbg['Line']} | Adj: {_dbg['Adjusted']} | Tier: {_dbg['Tier']} | Conf: {_dbg.get('_conf',0)}")
                else:
                    st.write("No pitchers were successfully analyzed.")
                    st.write("Try switching filter to 'All results' to see raw data.")
        else:
            st.markdown(
                f"<div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;"
                f"color:#555;margin-bottom:0.75rem;letter-spacing:0.08em;'>"
                f"{len(_mshow)} PITCHER{'S' if len(_mshow)!=1 else ''} · STRIKEOUT PROPS · SORTED BY CONFIDENCE</div>",
                unsafe_allow_html=True
            )
            for _mi, _mr in enumerate(_mshow):
                _mt   = _mr["Tier"]
                _mcs  = _mtc.get(_mt,"gray")
                _mem  = _mte.get(_mt,"⚪")
                _mec  = "#00e676" if _mr["Edge"]>0 else "#ff3d57"
                _mconf= _mr.get("_conf",0)
                _mcc  = "#3b82f6" if _mconf>=80 else ("#eab308" if _mconf>=65 else "#f97316")

                st.markdown(f"""
                <div class='verdict-banner {_mcs}' style='margin:0.4rem 0;padding:1rem 1.4rem;'>
                    <div>
                        <div class='verdict-label'>{_mr["Line"]} K Over · PrizePicks</div>
                        <div style='display:flex;align-items:center;gap:8px;'>
                            <div style='font-size:1.1rem;font-weight:800;color:#f0f0f0;'>{_mr["Pitcher"]}</div>
                            <div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;
                                        color:#3b82f6;background:#111;border:1px solid #1e2a3a;
                                        padding:1px 7px;letter-spacing:0.08em;'>{_mr["Team"]}</div>
                            <div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#555;'>
                                vs {_mr["Opp"]}</div>
                        </div>
                        <div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#555;margin-top:4px;'>
                            {_mr["Park"]} park · Avg {_mr["Avg K"]}K/start
                        </div>
                    </div>
                    <div style='display:flex;gap:1.5rem;flex-wrap:wrap;align-items:center;'>
                        <div>
                            <div class='verdict-label'>Confidence</div>
                            <div style='font-family:Barlow Condensed,sans-serif;font-size:1.6rem;
                                        font-weight:900;color:{_mcc};line-height:1;'>{_mconf}</div>
                            <div style='font-family:JetBrains Mono,monospace;font-size:0.55rem;color:#555;'>/100</div>
                        </div>
                        <div><div class='verdict-label'>Adjusted HR</div>
                             <div style='font-size:1rem;font-weight:700;color:#f0f0f0;'>{_mr["Adjusted"]}</div></div>
                        <div><div class='verdict-label'>Edge</div>
                             <div style='font-size:1rem;font-weight:700;color:{_mec};'>{_mr["Edge"]:+.1f}</div></div>
                        <div><div class='verdict-label'>Hit Rate</div>
                             <div style='font-size:1rem;font-weight:700;color:#f0f0f0;'>{_mr["Hit Rate"]}</div></div>
                        <div><div class='verdict-label'>Tier</div>
                             <div class='verdict-tier {_mcs}' style='font-size:1rem;'>{_mem} {_mt}</div></div>
                    </div>
                </div>""", unsafe_allow_html=True)

    st.stop()


# ── NBA Mode guard — stop here if MLB or Soccer selected ─────
if st.session_state.active_sport != "nba":
    st.stop()

# ── Tab switcher ────────────────────────────────────────────
_p_active = st.session_state.active_tab == "player"
_s_active = st.session_state.active_tab == "scanner"

st.markdown(f"""
<style>
/* Force equal height and width on tab buttons */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {{
    height: 44px !important;
    min-height: 44px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    clip-path: none !important;
    border-radius: 0 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    font-size: 0.78rem !important;
}}
</style>
""", unsafe_allow_html=True)

_ul_c1, _ul_c2, _ul_c3 = st.columns([1, 1, 3])
with _ul_c1:
    if st.button("Player Prop", key="tab_player", use_container_width=True,
                 type="primary" if _p_active else "secondary"):
        st.session_state.active_tab = "player"
        st.rerun()
with _ul_c2:
    if st.button("Slate Scanner", key="tab_scanner", use_container_width=True,
                 type="primary" if _s_active else "secondary"):
        st.session_state.active_tab = "scanner"
        st.rerun()

# Underline bar
st.markdown(f"""
<div class="ul-tab-bar" style="position:relative; margin-top:-4px;">
    <div class="ul-tab-underline" style="
        width: 50%;
        transform: translateX({'0%' if _p_active else '100%'});
    "></div>
</div>
""", unsafe_allow_html=True)

_mode = "🎯  Scanner" if st.session_state.active_tab == "scanner" else "🏀  Player Prop"
st.markdown("<div style='height:0.1rem'></div>", unsafe_allow_html=True)

if _IS_PLAYOFFS:
    st.markdown(
        "<div style='background:linear-gradient(90deg,#0c1a2e,#111e2e);border:1px solid #3b82f6;"
        "border-radius:10px;padding:0.75rem 1.1rem;margin-bottom:0.75rem;"
        "display:flex;align-items:center;justify-content:space-between;gap:12px;'>"
        "<div style='display:flex;align-items:center;gap:10px;'>"
        "<span style='font-size:1.3rem;'>🏆</span>"
        "<div>"
        "<div style='font-family:Outfit,sans-serif;font-size:0.9rem;font-weight:700;"
        "color:#60a5fa;letter-spacing:0.05em;'>PLAYOFF MODE ACTIVE</div>"
        "<div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;margin-top:2px;'>"
        "H2H signal boosted · Playoff pace calibrated · Load mgmt warnings off</div>"
        "</div></div>"
        "<div style='font-family:JetBrains Mono,monospace;font-size:0.6rem;color:#3b82f6;"
        "background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);"
        "padding:3px 10px;border-radius:999px;white-space:nowrap;'>NBA 2026</div>"
        "</div>",
        unsafe_allow_html=True
    )



# ─────────────────────────────────────────────
# Slate Scanner
# ─────────────────────────────────────────────

if _mode == "🎯  Scanner":
    st.markdown("<div class='section-header'>PrizePicks NBA — Today's Slate</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='explainer'>
        <strong>How it works:</strong> Scans every player on today's PrizePicks NBA slate and runs each
        one through the PropLens model automatically. Only shows <strong>Strong Over</strong> results by default
        — these are the highest-confidence picks. Change the filter to see more.
        Takes 2–4 minutes to scan the full slate.
        <br><br>
        <span style='color:#475569;font-size:0.75rem;'>
        💡 Tip: Run this every evening after 6pm ET when lines are finalized. 
        Use <strong>Strong Only</strong> filter and only play props showing 80%+ adjusted hit rate.
        </span>
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

    _stat_types_sel = ["PTS"]  # Points only for now — keeps scanner fast
    _inj_filter = False         # Injury pre-filter disabled — too slow in parallel
    _min_conf   = 0

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
                _seen  = set()
                for _proj in _data.get("data", []):
                    _a = _proj.get("attributes", {})
                    if _a.get("stat_type", "").lower() not in ("points", "pts"):
                        continue
                    _ln = _a.get("line_score")
                    if not _ln:
                        continue
                    _pid   = _proj.get("relationships", {}).get("new_player", {}).get("data", {}).get("id")
                    _pi    = _pmap.get(_pid, {})
                    _pname = _pi.get("name", "")
                    if not _pname or _pname in _seen:
                        continue
                    _seen.add(_pname)
                    _slate.append({"player_name": _pname, "line": float(_ln), "team": _pi.get("team", "")})
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

                    _logs = nba_get_game_logs(_nid, _season, n=15, _date=_cache_date())
                    _logs = _merge_playoff_logs(_logs, _nid, _season, 15)
                    if _logs.empty:
                        return None

                    _ln   = _prop["line"]
                    _wb   = weighted_hit_rate(_logs, _ln, "Over", opp_abbr=_opp)
                    _avgp = pd.to_numeric(_logs["PTS"], errors="coerce").dropna().mean()
                    _ld   = _avgp - _ln

                    # Early exit: dead zone
                    if 0.44 <= _wb <= 0.56 and abs(_ld) < 1.0:
                        return None

                    _cons = consistency_score(_logs, _ln)
                    _avgm = pd.to_numeric(_logs["MIN"], errors="coerce").dropna().mean()
                    _avgf = pd.to_numeric(_logs["FGA"], errors="coerce").dropna().mean()
                    _avgt = pd.to_numeric(_logs["FTA"], errors="coerce").dropna().mean()
                    _ep   = next((p for p in espn_get_all_players(_date=_cache_date())
                                  if normalize_name(p["full_name"]) == normalize_name(_fn)), None)
                    _team = _ep["team_abbr"] if _ep else None
                    _opp, _gd, _ven = espn_get_next_game(_team) if _team else (None, None, None)
                    _mq, _, _  = classify_matchup_espn(_opp)
                    _sp        = home_away_split(_logs, _ln, "Over", _team)
                    _vadj      = venue_adjustment(_sp, _ven, "Over")
                    _b2b       = detect_b2b(_logs, _gd)
                    _h2hdf     = get_h2h_logs(_nid, _opp, _season, _date=_cache_date()) if _opp else pd.DataFrame()
                    _hsig, _, _= h2h_signal(_h2hdf, _ln, "Over")
                    _savg      = nba_get_season_avg(_nid, _season, logs_l10=_logs)
                    _fsig, _   = form_divergence_signal(_avgp, _savg, _ln, "Over")
                    _ctx = {
                        "minutes":   suggest_bucket(_avgm, 32, 26),
                        "role":      suggest_bucket(_avgf + 0.5 * _avgt, 18, 12),
                        "shots":     "High" if _avgf >= 15 else ("Low" if _avgf < 10 else "Medium"),
                        "matchup":   _mq, "script": "Neutral", "venue": _vadj,
                        "h2h":       _hsig, "b2b": _b2b, "form": _fsig,
                        "rest":       "Normal", "pace": "Neutral", "shoot": "Neutral",
                        "elim_game":  "Normal",
                        "series_cov": "Neutral",
                        "ref":        "Neutral",
                        "game_num":   "N/A",
                        "pu_spike":   "Neutral",
                        "shot_vol":   "Neutral",
                    }
                    _adj  = apply_adjustments(_wb, _ctx, "Over")
                    _tier = get_confidence_tier(_adj, _ld, _cons, "Over")

                    _score_adj  = max(0, min((_adj - 0.50) / 0.45, 1.0) * 65)
                    _score_edge = min(abs(_ld) / 7.0, 1.0) * 25
                    _score_cons = _cons * 10
                    _conf_score = min(99, int(_score_adj + _score_edge + _score_cons))

                    return {
                        "Player": _fn, "Line": _ln, "Avg PTS": round(_avgp, 1),
                        "Edge": round(_ld, 1), "Weighted HR": f"{_wb:.0%}",
                        "Adjusted": f"{_adj:.0%}", "Matchup": _mq,
                        "B2B": _b2b, "Form": _fsig, "Venue": _ven or "?",
                        "Tier": _tier, "_adj_raw": _adj,
                        "_conf": _conf_score,
                        "_nid": _nid, "_line": _ln,
                        "_team": _norm_team_abbr(_team) if _team else "",
                        "_opp":  _norm_team_abbr(_opp)  if _opp  else "",
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
                key=lambda x: -x.get("_conf", 0)
            )
            st.session_state["scanner_day_label"] = _day_sel

    if st.session_state.scanner_error:
        st.error(st.session_state.scanner_error)

    if st.session_state.scanner_results is not None:
        _res = st.session_state.scanner_results

        # ── Deduplicate by player name — keep highest adjusted hit rate ──
        _seen_players = {}
        for _r in _res:
            _pname = _r.get("Player", "")
            _adj   = float(str(_r.get("Adjusted", "0")).replace("%","")) / 100                      if "%" in str(_r.get("Adjusted",""))                      else float(_r.get("Adjusted", 0))
            if _pname not in _seen_players or _adj > _seen_players[_pname]["_adj"]:
                _r["_adj"] = _adj
                _seen_players[_pname] = _r
        _deduped = list(_seen_players.values())

        # ── Apply filter ──────────────────────────────────────────────
        if _filter == "Strong Only":
            _show = [r for r in _deduped
                     if r["Tier"] == "Strong Over"
                     and r.get("_adj", 0) >= 0.80]
        elif _filter == "Strong + Lean":
            _show = [r for r in _deduped if "Strong" in r["Tier"] or "Lean" in r["Tier"]]
        else:
            _show = _deduped

        # Sort by confidence score descending
        _show = sorted(_show, key=lambda r: r.get("_conf", 0), reverse=True)

        # ── Best bets summary ──────────────────────────────────────
        _strong_count = len([r for r in _deduped if r["Tier"] == "Strong Over" and r.get("_adj",0) >= 0.80])
        _grade = "🔥 HOT" if _strong_count >= 5 else ("✅ GOOD" if _strong_count >= 3 else ("⚠️ THIN" if _strong_count >= 1 else "❌ DEAD"))
        _gcol  = "#00e676" if _strong_count >= 5 else ("#3b82f6" if _strong_count >= 3 else ("#f97316" if _strong_count >= 1 else "#555"))
        st.markdown(
            f"<div style='display:flex;gap:1rem;align-items:center;margin-bottom:0.75rem;'>"
            f"<div style='background:#111;border:1px solid #1e2a3a;padding:0.4rem 1rem;"
            f"font-family:JetBrains Mono,monospace;font-size:0.65rem;'>"
            f"<span style='color:#555;'>SLATE </span>"
            f"<span style='color:{_gcol};font-weight:700;'>{_grade}</span>"
            f"</div>"
            f"<div style='background:#111;border:1px solid #1e2a3a;padding:0.4rem 1rem;"
            f"font-family:JetBrains Mono,monospace;font-size:0.65rem;'>"
            f"<span style='color:#555;'>STRONG OVERS </span>"
            f"<span style='color:#3b82f6;font-weight:700;'>{_strong_count}</span>"
            f"</div></div>",
            unsafe_allow_html=True
        )

        _tc = {"Strong Over":"green","Lean Over":"yellow","Lean Under":"orange","Strong Under":"red","Pass":"gray"}
        _te = {"Strong Over":"🟢","Lean Over":"🟡","Lean Under":"🟠","Strong Under":"🔴","Pass":"⚪"}

        # ── Correlated picks warning ──────────────────────────────
        # Find players from the same game (same team OR same opponent)
        _game_groups = {}
        for _r in _show:
            _t = _r.get("_team", "")
            _o = _r.get("_opp", "")
            if _t and _o:
                # Game key = sorted pair of teams
                _gkey = "_".join(sorted([_t, _o]))
                _game_groups.setdefault(_gkey, []).append(_r["Player"])

        _correlated_games = {k: v for k, v in _game_groups.items() if len(v) >= 2}

        if _correlated_games:
            for _gkey, _players in _correlated_games.items():
                _teams = _gkey.split("_")
                _plist = ", ".join(_players)
                st.markdown(
                    f"<div style='background:#1c1005;border:1px solid #854d0e;"
                    f"border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.5rem;"
                    f"display:flex;align-items:center;gap:10px;'>"
                    f"<span style='font-size:1.1rem;'>⚠️</span>"
                    f"<div style='font-family:DM Mono;font-size:0.7rem;'>"
                    f"<span style='color:#f97316;font-weight:800;text-transform:uppercase;"
                    f"letter-spacing:0.08em;'>Correlated picks</span>"
                    f"<span style='color:#475569;'> · {_plist} are all in the same game "
                    f"({_teams[0]} vs {_teams[1]}) — a blowout tanks all of them</span>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

        if not _show:
            _no_res_msg = (
                "No Strong Overs with 80%+ hit rate found on today's slate. "
                "Try 'Strong + Lean' to see more results."
            ) if _filter == "Strong Only" else "No results match the filter."
            st.markdown(
                f"<div style='background:#111;border:1px solid #2a2a2a;border-left:3px solid #555;"
                f"padding:0.75rem 1rem;font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#555;'>"
                f"{_no_res_msg}</div>",
                unsafe_allow_html=True
            )
        else:
            _day_label = st.session_state.get("scanner_day_label", "Today")
            _filter_label = " · Strong Over ≥80% only" if _filter == "Strong Only" else ""
            st.markdown(
                f"<div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;"
                f"color:#555;margin-bottom:0.75rem;letter-spacing:0.08em;'>"
                f"{len(_show)} RESULT{'S' if len(_show) != 1 else ''} · {_day_label.upper()}"
                f"{_filter_label.upper()} · SORTED BY HIT RATE</div>",
                unsafe_allow_html=True
            )
            for _ri, _r in enumerate(_show):
                _t    = _r["Tier"]
                _cs   = _tc.get(_t, "gray")
                _em   = _te.get(_t, "⚪")
                _ec   = "#22c55e" if _r["Edge"] > 0 else "#ef4444"
                _conf = _r.get("_conf", 0)
                # Confidence color
                _cc   = "#3b82f6" if _conf >= 80 else ("#eab308" if _conf >= 65 else "#f97316")

                _card_col, _btn_col = st.columns([5, 1])
                with _card_col:
                    st.markdown(f"""
                    <div class='verdict-banner {_cs}' style='margin:0.4rem 0;padding:1rem 1.4rem;'>
                        <div>
                            <div class='verdict-label'>{_r["Line"]} pts Over · PrizePicks</div>
                            <div style='display:flex;align-items:center;gap:8px;'>
                                <div style='font-size:1.1rem;font-weight:800;color:#f1f5f9;'>{_r["Player"]}</div>
                                <div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;
                                            color:#3b82f6;background:#111;border:1px solid #2a2a2a;
                                            padding:1px 7px;letter-spacing:0.08em;'>
                                    {_r.get("_team","?")}</div>
                                <div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#555;'>
                                    vs {_r.get("_opp","?")}</div>
                            </div>
                            <div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#555;margin-top:4px;'>
                                {_r["Venue"]} · {_r["Matchup"]} defense · {_r["B2B"]} · Form: {_r["Form"]}
                            </div>
                        </div>
                        <div style='display:flex;gap:1.5rem;flex-wrap:wrap;align-items:center;'>
                            <div>
                                <div class='verdict-label'>Confidence</div>
                                <div style='font-family:Barlow Condensed,sans-serif;font-size:1.6rem;
                                            font-weight:900;color:{_cc};line-height:1;'>{_conf}</div>
                                <div style='font-family:JetBrains Mono,monospace;font-size:0.55rem;color:#555;'>/100</div>
                            </div>
                            <div><div class='verdict-label'>Adjusted HR</div>
                                 <div style='font-size:1rem;font-weight:700;color:#f1f5f9;'>{_r["Adjusted"]}</div></div>
                            <div><div class='verdict-label'>Edge</div>
                                 <div style='font-size:1rem;font-weight:700;color:{_ec};'>{_r["Edge"]:+.1f}</div></div>
                            <div><div class='verdict-label'>Avg PTS</div>
                                 <div style='font-size:1rem;font-weight:700;color:#f1f5f9;'>{_r["Avg PTS"]}</div></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                with _btn_col:
                    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                    if st.button("Full Analysis →", key=f"drill_{_ri}_{_r['Player']}", use_container_width=True):
                        # Pre-fill player prop form and switch tab
                        st.session_state.active_tab       = "player"
                        st.session_state.player_key       = st.session_state.get("player_key", 0) + 1
                        st.session_state._recent_pick     = _r["Player"]
                        st.session_state._drilldown_line  = float(_r["Line"])
                        st.session_state._drilldown_side  = "Over"
                        st.session_state.logs             = None
                        st.session_state.ai_analysis      = None
                        st.session_state._drilldown_fetch = True
                        st.rerun()



    st.stop()  # prevents player prop section rendering in scanner mode



# Load player list
with st.spinner("Loading players..."):
    try:
        all_players_list = espn_get_all_players(_date=_cache_date())
        # Build both full names AND common aliases for fuzzy matching
        _raw_names = [p["full_name"] for p in all_players_list]

        # Add nickname/abbreviation mappings
        _aliases = {
            "LeBron": "LeBron James",
            "SGA": "Shai Gilgeous-Alexander",
            "KD": "Kevin Durant",
            "PG": "Paul George",
            "AD": "Anthony Davis",
            "Giannis": "Giannis Antetokounmpo",
            "Luka": "Luka Doncic",
            "Steph": "Stephen Curry",
            "Bron": "LeBron James",
            "Embiid": "Joel Embiid",
            "Jokic": "Nikola Jokic",
            "Wemby": "Victor Wembanyama",
            "CP3": "Chris Paul",
            "Dame": "Damian Lillard",
            "Trae": "Trae Young",
            "Ja": "Ja Morant",
            "Zion": "Zion Williamson",
            "KAT": "Karl-Anthony Towns",
            "Kawhi": "Kawhi Leonard",
            "Draymond": "Draymond Green",
        }

        # Sort by last name
        player_names_list = sorted(_raw_names, key=lambda x: x.split()[-1])
    except Exception:
        player_names_list = []
        _aliases = {}

# ─────────────────────────────────────────────
# Quick Entry — batch manual input
# ─────────────────────────────────────────────

if "quick_entry_results" not in st.session_state:
    st.session_state.quick_entry_results = None

with st.expander("⚡  Quick Entry — analyze multiple props at once"):
    st.markdown("""
    <div class='explainer'>
        Enter up to 6 props manually — useful when browsing Underdog or any other platform.
        Hit <strong>Run All</strong> and PropLens analyzes each one instantly.
    </div>
    """, unsafe_allow_html=True)

    _qe_players = player_names_list if player_names_list else []

    # Build 6-row entry table
    _qe_rows = []
    _hc1, _hc2, _hc3, _hc4 = st.columns([3, 1.2, 1, 1])
    _hc1.markdown("<div style='font-family:DM Mono;font-size:0.65rem;color:#475569;letter-spacing:0.1em;text-transform:uppercase;'>Player</div>", unsafe_allow_html=True)
    _hc2.markdown("<div style='font-family:DM Mono;font-size:0.65rem;color:#475569;letter-spacing:0.1em;text-transform:uppercase;'>Line</div>", unsafe_allow_html=True)
    _hc3.markdown("<div style='font-family:DM Mono;font-size:0.65rem;color:#475569;letter-spacing:0.1em;text-transform:uppercase;'>Over/Under</div>", unsafe_allow_html=True)
    _hc4.markdown("<div style='font-family:DM Mono;font-size:0.65rem;color:#475569;letter-spacing:0.1em;text-transform:uppercase;'>Platform</div>", unsafe_allow_html=True)

    for _ri in range(6):
        _rc1, _rc2, _rc3, _rc4 = st.columns([3, 1.2, 1, 1])
        with _rc1:
            _pname = st.selectbox(
                f"p{_ri}", options=[""] + _qe_players,
                format_func=lambda x: "— player —" if x == "" else x,
                key=f"qe_player_{_ri}", label_visibility="collapsed"
            )
        with _rc2:
            _pline = st.number_input(
                f"l{_ri}", min_value=0.0, value=20.0, step=0.5,
                key=f"qe_line_{_ri}", label_visibility="collapsed"
            )
        with _rc3:
            _pside = st.selectbox(
                f"s{_ri}", ["Over", "Under"],
                key=f"qe_side_{_ri}", label_visibility="collapsed"
            )
        with _rc4:
            _pplat = st.selectbox(
                f"pl{_ri}", ["Underdog", "PrizePicks", "Other"],
                key=f"qe_plat_{_ri}", label_visibility="collapsed"
            )
        if _pname:
            _qe_rows.append({
                "player": _pname, "line": _pline,
                "side": _pside, "platform": _pplat
            })

    _run_qe = st.button("⚡  Run All", key="run_quick_entry")

    if _run_qe and _qe_rows:
        _qe_results = []
        _qe_prog = st.progress(0)
        _season_qe = season_str_to_season("2025-26")

        for _qi, _qrow in enumerate(_qe_rows):
            _qe_prog.progress((_qi + 1) / len(_qe_rows))
            try:
                _qnid, _qfn = nba_find_player(_qrow["player"])
                if not _qnid:
                    continue
                _qlogs = nba_get_game_logs(_qnid, _season_qe, n=15, _date=_cache_date())
                if _qlogs.empty:
                    continue
                _qln   = _qrow["line"]
                _qside = _qrow["side"]
                _qwb   = weighted_hit_rate(_qlogs, _qln, _qside)
                _qcons = consistency_score(_qlogs, _qln)
                _qavgp = pd.to_numeric(_qlogs["PTS"], errors="coerce").dropna().mean()
                _qavgm = pd.to_numeric(_qlogs["MIN"], errors="coerce").dropna().mean()
                _qavgf = pd.to_numeric(_qlogs["FGA"], errors="coerce").dropna().mean()
                _qavgt = pd.to_numeric(_qlogs["FTA"], errors="coerce").dropna().mean()
                _qld   = _qavgp - _qln
                _qep   = next((p for p in espn_get_all_players(_date=_cache_date())
                               if normalize_name(p["full_name"]) == normalize_name(_qfn)), None)
                _qteam = _qep["team_abbr"] if _qep else None
                _qopp, _qgd, _qven = espn_get_next_game(_qteam) if _qteam else (None, None, None)
                _qmq, _, _ = classify_matchup_espn(_qopp)
                _qsp   = home_away_split(_qlogs, _qln, _qside, _qteam)
                _qvadj = venue_adjustment(_qsp, _qven, _qside)
                _qb2b  = detect_b2b(_qlogs, _qgd)
                _qh2h  = get_h2h_logs(_qnid, _qopp, _season_qe, _date=_cache_date()) if _qopp else pd.DataFrame()
                _qhsig, _, _ = h2h_signal(_qh2h, _qln, _qside)
                _qsavg = nba_get_season_avg(_qnid, _season_qe, logs_l10=_qlogs)
                _qfsig, _ = form_divergence_signal(_qavgp, _qsavg, _qln, _qside)
                _qctx  = {
                    "minutes": suggest_bucket(_qavgm, 32, 26),
                    "role":    suggest_bucket(_qavgf + 0.5 * _qavgt, 18, 12),
                    "shots":   "High" if _qavgf >= 15 else ("Low" if _qavgf < 10 else "Medium"),
                    "matchup": _qmq, "script": "Neutral", "venue": _qvadj,
                    "h2h": _qhsig, "b2b": _qb2b, "form": _qfsig,
                }
                _qadj  = apply_adjustments(_qwb, _qctx, _qside)
                _qtier = get_confidence_tier(_qadj, _qld, _qcons, _qside)
                _qe_results.append({
                    "Player":    _qfn,
                    "Platform":  _qrow["platform"],
                    "Line":      f"{_qln} {_qside}",
                    "Avg PTS":   round(_qavgp, 1),
                    "Edge":      round(_qld, 1),
                    "Hit Rate":  f"{_qwb:.0%}",
                    "Adjusted":  f"{_qadj:.0%}",
                    "Tier":      _qtier,
                    "_adj_raw":  _qadj,
                })
            except Exception:
                continue

        _qe_prog.empty()
        st.session_state.quick_entry_results = _qe_results

    if st.session_state.quick_entry_results:
        _qtc = {"Strong Over":"green","Lean Over":"yellow","Lean Under":"orange","Strong Under":"red","Pass":"gray"}
        _qte = {"Strong Over":"🟢","Lean Over":"🟡","Lean Under":"🟠","Strong Under":"🔴","Pass":"⚪"}
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        for _qr in st.session_state.quick_entry_results:
            _qt  = _qr["Tier"]
            _qcs = _qtc.get(_qt, "gray")
            _qem = _qte.get(_qt, "⚪")
            _qec = "#22c55e" if _qr["Edge"] > 0 else "#ef4444"
            st.markdown(f"""
            <div class='verdict-banner {_qcs}' style='margin:0.3rem 0;padding:0.9rem 1.3rem;'>
                <div>
                    <div class='verdict-label'>{_qr["Line"]} · {_qr["Platform"]}</div>
                    <div style='font-size:1rem;font-weight:800;color:#f1f5f9;'>{_qr["Player"]}</div>
                </div>
                <div style='display:flex;gap:1.5rem;flex-wrap:wrap;align-items:center;'>
                    <div><div class='verdict-label'>Verdict</div>
                         <div class='verdict-tier {_qcs}' style='font-size:0.95rem;'>{_qem} {_qt}</div></div>
                    <div><div class='verdict-label'>Avg PTS</div>
                         <div style='font-size:0.95rem;font-weight:700;color:#f1f5f9;'>{_qr["Avg PTS"]}</div></div>
                    <div><div class='verdict-label'>Edge</div>
                         <div style='font-size:0.95rem;font-weight:700;color:{_qec};'>{_qr["Edge"]:+.1f}</div></div>
                    <div><div class='verdict-label'>Hit Rate</div>
                         <div style='font-size:0.95rem;font-weight:700;color:#f1f5f9;'>{_qr["Hit Rate"]}</div></div>
                    <div><div class='verdict-label'>Adjusted</div>
                         <div style='font-size:0.95rem;font-weight:700;color:#f1f5f9;'>{_qr["Adjusted"]}</div></div>
                </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Parlay Checker + Best Entry Builder
# ─────────────────────────────────────────────

if "parlay_results" not in st.session_state:
    st.session_state.parlay_results = None

with st.expander("🎯  Parlay Checker — validate your entry before locking"):
    st.markdown("""
    <div class='explainer'>
        <strong>Before you lock your entry on PrizePicks — check it here first.</strong>
        Enter each leg of your parlay, hit Check Entry, and PropLens will:
        <br>• Show your <strong>real combined probability</strong> of hitting
        <br>• Flag any <strong>weak legs</strong> that are dragging the entry down
        <br>• Warn you about <strong>correlated picks</strong> (same game players)
        <br>• Suggest a <strong>trimmed entry</strong> using only your strongest legs
        <br><br>
        <span style='color:#475569;font-size:0.75rem;'>
        💡 Rule of thumb: 3-leg entries with all Strong picks beat 5-leg entries with mixed results every time.
        </span>
    </div>
    """, unsafe_allow_html=True)

    _pc_players = player_names_list if player_names_list else []

    # Entry rows
    _pc_hc1, _pc_hc2, _pc_hc3 = st.columns([3, 1.2, 1])
    _pc_hc1.markdown("<div style='font-family:DM Mono;font-size:0.65rem;color:#475569;letter-spacing:0.1em;text-transform:uppercase;'>Player</div>", unsafe_allow_html=True)
    _pc_hc2.markdown("<div style='font-family:DM Mono;font-size:0.65rem;color:#475569;letter-spacing:0.1em;text-transform:uppercase;'>Line</div>", unsafe_allow_html=True)
    _pc_hc3.markdown("<div style='font-family:DM Mono;font-size:0.65rem;color:#475569;letter-spacing:0.1em;text-transform:uppercase;'>Over/Under</div>", unsafe_allow_html=True)

    _pc_rows = []
    for _pi in range(5):
        _pc1, _pc2, _pc3 = st.columns([3, 1.2, 1])
        with _pc1:
            _pp = st.selectbox(f"pp{_pi}", options=[""] + _pc_players,
                               format_func=lambda x: "— player —" if x == "" else x,
                               key=f"pc_player_{_pi}", label_visibility="collapsed")
        with _pc2:
            _pl = st.number_input(f"pl{_pi}", min_value=0.0, value=20.0, step=0.5,
                                  key=f"pc_line_{_pi}", label_visibility="collapsed")
        with _pc3:
            _ps = st.selectbox(f"ps{_pi}", ["Over", "Under"],
                               key=f"pc_side_{_pi}", label_visibility="collapsed")
        if _pp:
            _pc_rows.append({"player": _pp, "line": _pl, "side": _ps})

    _run_pc = st.button("🎯  Check Entry", key="run_parlay_checker")

    if _run_pc and _pc_rows:
        st.session_state.parlay_results = None
        _pc_season = "2025-26"
        _pc_results = []
        with st.spinner(f"Analyzing {len(_pc_rows)} legs — all 17 signals..."):
            from concurrent.futures import ThreadPoolExecutor, as_completed as _afc

            def _analyze_pc_leg(_pc_row):
                """Full signal analysis for one parlay leg — matches player prop analyzer."""
                try:
                    _pc_nid, _pc_fn = nba_find_player(_pc_row["player"])
                    if not _pc_nid:
                        return None
                    _pc_logs = nba_get_game_logs(_pc_nid, _pc_season, n=15, _date=_cache_date())
                    if _pc_logs is None or _pc_logs.empty:
                        return None

                    _pc_ln   = _pc_row["line"]
                    _pc_side = _pc_row["side"]
                    _pc_avgp = pd.to_numeric(_pc_logs["PTS"], errors="coerce").dropna().mean()
                    _pc_edge = _pc_avgp - _pc_ln if _pc_side == "Over" else _pc_ln - _pc_avgp
                    _pc_cons = consistency_score(_pc_logs, _pc_ln)
                    _pc_avgm = pd.to_numeric(_pc_logs["MIN"], errors="coerce").dropna().mean()
                    _pc_avgf = pd.to_numeric(_pc_logs["FGA"], errors="coerce").dropna().mean()
                    _pc_avgt = pd.to_numeric(_pc_logs["FTA"], errors="coerce").dropna().mean()

                    # ESPN team + opponent
                    _pc_ep   = next((p for p in espn_get_all_players(_date=_cache_date())
                                     if normalize_name(p["full_name"]) == normalize_name(_pc_fn)), None)
                    _pc_team = _norm_team_abbr(_pc_ep["team_abbr"]) if _pc_ep else None
                    _pc_opp, _pc_gd, _pc_ven = espn_get_next_game(_pc_team) if _pc_team else (None, None, None)

                    # Run slow calls in parallel
                    with ThreadPoolExecutor(max_workers=6) as _ex:
                        _f_mq    = _ex.submit(classify_matchup_espn, _pc_opp)
                        _f_h2h   = _ex.submit(get_h2h_logs, _pc_nid, _pc_opp, _pc_season, _cache_date()) if _pc_opp else None
                        _f_savg  = _ex.submit(nba_get_season_avg, _pc_nid, _pc_season, _pc_logs)
                        _f_pace  = _ex.submit(pace_adjustment, _pc_team, _pc_opp, _pc_side) if _pc_team else None
                        _f_shoot = _ex.submit(shooting_efficiency_signal, _pc_logs, _pc_side, 3)
                        _f_ref   = _ex.submit(referee_signal, _pc_team, _pc_side) if _pc_team else None
                        _f_def   = _ex.submit(get_opp_recent_defensive_form, _pc_opp) if _pc_opp else None
                        _f_ser   = _ex.submit(get_playoff_series_context, _pc_team) if (_IS_PLAYOFFS and _pc_team) else None
                        _f_polog = _ex.submit(get_playoff_game_logs, _pc_nid, _pc_season) if _IS_PLAYOFFS else None

                        try: _pc_mq, _, _ = _f_mq.result(timeout=8)
                        except: _pc_mq = "Neutral"

                        try: _pc_h2hdf = _f_h2h.result(timeout=10) if _f_h2h else pd.DataFrame()
                        except: _pc_h2hdf = pd.DataFrame()

                        try: _pc_savg = _f_savg.result(timeout=8)
                        except: _pc_savg = None

                        try: _pc_pace_sig, _, _ = _f_pace.result(timeout=8) if _f_pace else ("Neutral", None, None)
                        except: _pc_pace_sig = "Neutral"

                        try: _pc_shoot_sig, _, _ = _f_shoot.result(timeout=8)
                        except: _pc_shoot_sig = "Neutral"

                        try: _pc_ref_sig, _, _ = _f_ref.result(timeout=8) if _f_ref else ("Neutral", None, [])
                        except: _pc_ref_sig = "Neutral"

                        try: _pc_def = _f_def.result(timeout=8) if _f_def else {}
                        except: _pc_def = {}

                        try: _pc_ser = _f_ser.result(timeout=8) if _f_ser else {}
                        except: _pc_ser = {}

                        try: _pc_polog = _f_polog.result(timeout=10) if _f_polog else pd.DataFrame()
                        except: _pc_polog = pd.DataFrame()

                    # Defensive form — blend into matchup
                    _pc_def_trend = _pc_def.get("trend", "Neutral")
                    if _pc_def_trend == "Softening" and _pc_mq in ("Neutral", "Bad"):
                        _pc_mq = "Good" if _pc_mq == "Neutral" else "Neutral"
                    elif _pc_def_trend == "Tightening" and _pc_mq in ("Neutral", "Good"):
                        _pc_mq = "Bad" if _pc_mq == "Neutral" else "Neutral"

                    # Series context
                    _pc_elim = "Normal"
                    _pc_gnum_label = "N/A"
                    if _IS_PLAYOFFS and _pc_ser and _pc_ser.get("found"):
                        if _pc_ser.get("is_elimination"): _pc_elim = "Elimination"
                        elif _pc_ser.get("is_closeout"):  _pc_elim = "Closeout"
                        _pc_gn = get_series_game_number(_pc_ser.get("series_wins",0), _pc_ser.get("series_losses",0))
                        _pc_gnum_label, _ = game_number_adjustment(_pc_gn, _pc_side)

                    # Playoff usage spike
                    _pc_pu_sig = "Neutral"
                    if _IS_PLAYOFFS and not _pc_polog.empty and "PTS" in _pc_polog.columns:
                        _po_pts = pd.to_numeric(_pc_polog["PTS"], errors="coerce").dropna()
                        if len(_po_pts) >= 2:
                            _po_avg = float(_po_pts.mean())
                            if _po_avg - _pc_avgp >= 3.0: _pc_pu_sig = "Spike"
                            elif _pc_avgp - _po_avg >= 3.0: _pc_pu_sig = "Drop"

                    # Series coverage
                    _pc_scov_sig, _, _ = series_coverage_signal(_pc_logs, _pc_opp, _pc_ln, _pc_side, _pc_savg)

                    # Weighted hit rate with playoff boost
                    _pc_wb = weighted_hit_rate(_pc_logs, _pc_ln, _pc_side, opp_abbr=_pc_opp if _IS_PLAYOFFS else None)

                    # All signals
                    _pc_sp   = home_away_split(_pc_logs, _pc_ln, _pc_side, _pc_team)
                    _pc_vadj = venue_adjustment(_pc_sp, _pc_ven, _pc_side)
                    _pc_b2b  = detect_b2b(_pc_logs, _pc_gd)
                    _pc_rest = detect_rest_days(_pc_logs, _pc_gd)
                    if _pc_b2b == "B2B": _pc_rest = "B2B"
                    _pc_hsig, _, _ = h2h_signal(_pc_h2hdf, _pc_ln, _pc_side)
                    _pc_fsig, _    = form_divergence_signal(_pc_avgp, _pc_savg, _pc_ln, _pc_side)

                    _pc_ctx = {
                        "minutes":    suggest_bucket(_pc_avgm, 32, 26),
                        "role":       suggest_bucket(_pc_avgf + 0.5 * _pc_avgt, 18, 12),
                        "shots":      "High" if _pc_avgf >= 15 else ("Low" if _pc_avgf < 10 else "Medium"),
                        "matchup":    _pc_mq,
                        "script":     "Neutral",
                        "venue":      _pc_vadj,
                        "h2h":        _pc_hsig,
                        "series_cov": _pc_scov_sig,
                        "b2b":        _pc_b2b,
                        "rest":       _pc_rest,
                        "form":       _pc_fsig,
                        "pace":       _pc_pace_sig,
                        "shoot":      _pc_shoot_sig,
                        "elim_game":  _pc_elim,
                        "ref":        _pc_ref_sig,
                        "game_num":   _pc_gnum_label,
                        "pu_spike":   _pc_pu_sig,
                    }
                    _pc_adj  = apply_adjustments(_pc_wb, _pc_ctx, _pc_side)
                    _pc_tier = get_confidence_tier(_pc_adj, _pc_edge, _pc_cons, _pc_side)

                    # Confidence score
                    _pc_score_adj  = max(0, min((_pc_adj - 0.50) / 0.45, 1.0) * 65)
                    _pc_score_edge = min(abs(_pc_edge) / 7.0, 1.0) * 25
                    _pc_score_cons = _pc_cons * 10
                    _pc_conf = min(99, int(_pc_score_adj + _pc_score_edge + _pc_score_cons))

                    return {
                        "player":  _pc_fn,
                        "line":    _pc_ln,
                        "side":    _pc_side,
                        "adj":     _pc_adj,
                        "edge":    round(_pc_edge, 1),
                        "tier":    _pc_tier,
                        "cons":    _pc_cons,
                        "conf":    _pc_conf,
                        "team":    _norm_team_abbr(_pc_team) if _pc_team else "?",
                        "opp":     _norm_team_abbr(_pc_opp) if _pc_opp else "?",
                        "matchup": _pc_mq,
                        "ref":     _pc_ref_sig,
                        "pace":    _pc_pace_sig,
                        "inj_flag": "",
                    }
                except Exception:
                    return None

            # Run all legs in parallel
            with ThreadPoolExecutor(max_workers=5) as _ex:
                _futures = {_ex.submit(_analyze_pc_leg, row): row for row in _pc_rows}
                for _f in _afc(_futures, timeout=60):
                    _res = _f.result()
                    if _res:
                        _pc_results.append(_res)

        st.session_state.parlay_results = _pc_results

    if st.session_state.parlay_results:
        _pr = st.session_state.parlay_results
        if not _pr:
            st.warning("No results — check player names.")
        else:
            # ── Combined probability ──────────────────────────────
            _combined = 1.0
            for _r in _pr:
                _combined *= _r["adj"]
            _legs = len(_pr)
            # ── Correlated picks — same game ──────────────────────
            _game_map = {}
            for _r in _pr:
                _gk = "_".join(sorted([_r["team"], _r["opp"]]))
                _game_map.setdefault(_gk, []).append(_r["player"])
            _corr = {k: v for k, v in _game_map.items() if len(v) >= 2}
            # ── Weakest leg ───────────────────────────────────────
            _weakest = min(_pr, key=lambda x: x["adj"])
            # ── Weak legs (Pass or Lean with small edge) ──────────
            _weak_flags = [r for r in _pr if r["tier"] == "Pass" or
                           ("Lean" in r["tier"] and abs(r["edge"]) < 1.5)]

            # Grade
            _grade_pct = _combined * 100
            _grade     = "🔥 STRONG" if _grade_pct >= 35 else ("✅ GOOD" if _grade_pct >= 20 else ("⚠️ RISKY" if _grade_pct >= 10 else "❌ DON'T BET"))
            _grade_col = "#22c55e" if _grade_pct >= 35 else ("#3b82f6" if _grade_pct >= 20 else ("#f97316" if _grade_pct >= 10 else "#ef4444"))

            # ── Summary banner ────────────────────────────────────
            st.markdown(
                f"<div style='background:#111;border:1px solid #1e2a3a;padding:1rem 1.2rem;margin:0.5rem 0 0.75rem;'>"
                f"<div style='display:flex;gap:2rem;flex-wrap:wrap;align-items:center;'>"
                f"<div><div class='verdict-label'>Entry grade</div>"
                f"<div style='font-size:1.4rem;font-weight:900;color:{_grade_col};'>{_grade}</div></div>"
                f"<div><div class='verdict-label'>Combined probability</div>"
                f"<div style='font-size:1.4rem;font-weight:900;color:{_grade_col};'>{_combined:.1%}</div></div>"
                f"<div><div class='verdict-label'>Legs</div>"
                f"<div style='font-size:1.4rem;font-weight:900;color:#f1f5f9;'>{_legs}</div></div>"
                f"<div><div class='verdict-label'>Weakest leg</div>"
                f"<div style='font-size:1rem;font-weight:700;color:#f97316;'>{_weakest['player']} ({_weakest['adj']:.0%})</div></div>"
                f"</div></div>",
                unsafe_allow_html=True
            )

            # ── Correlated warning ────────────────────────────────
            for _gk, _gps in _corr.items():
                _gteams = _gk.split("_")
                st.markdown(
                    f"<div style='background:#1c1005;border:1px solid #854d0e;border-left:3px solid #f97316;"
                    f"padding:0.6rem 1rem;margin-bottom:0.4rem;font-family:JetBrains Mono,monospace;font-size:0.68rem;'>"
                    f"⚠️ <span style='color:#f97316;font-weight:700;'>CORRELATED PICKS</span>"
                    f"<span style='color:#475569;'> · {', '.join(_gps)} are in the same game "
                    f"({_gteams[0]} vs {_gteams[1]}) — a blowout tanks both</span></div>",
                    unsafe_allow_html=True
                )

            # ── Weak leg warnings ─────────────────────────────────
            for _wf in _weak_flags:
                st.markdown(
                    f"<div style='background:#0c1018;border:1px solid #1e3a5f;border-left:3px solid #3b82f6;"
                    f"padding:0.6rem 1rem;margin-bottom:0.4rem;font-family:JetBrains Mono,monospace;font-size:0.68rem;'>"
                    f"⚡ <span style='color:#3b82f6;font-weight:700;'>WEAK LEG</span>"
                    f"<span style='color:#475569;'> · {_wf['player']} — {_wf['tier']} at {_wf['adj']:.0%} "
                    f"with {_wf['edge']:+.1f} edge. Consider dropping this leg.</span></div>",
                    unsafe_allow_html=True
                )

            # ── Leg breakdown ranked worst to best ───────────────
            st.markdown(
                "<div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#555;"
                "letter-spacing:0.08em;margin:0.75rem 0 0.4rem;'>LEGS · WEAKEST → STRONGEST</div>",
                unsafe_allow_html=True
            )
            _tc = {"Strong Over":"green","Lean Over":"yellow","Lean Under":"orange","Strong Under":"red","Pass":"gray"}
            _te = {"Strong Over":"🟢","Lean Over":"🟡","Lean Under":"🟠","Strong Under":"🔴","Pass":"⚪"}
            for _ri, _r in enumerate(sorted(_pr, key=lambda x: x["adj"])):
                _rc   = _tc.get(_r["tier"], "gray")
                _em   = _te.get(_r["tier"], "⚪")
                _ecol = "#22c55e" if _r["edge"] > 0 else "#ef4444"
                _vol  = "⚠️ volatile · " if _r["cons"] < 0.65 else ""
                _conf = _r.get("conf", 0)
                _cc   = "#10f590" if _conf >= 80 else ("#fbbf24" if _conf >= 65 else "#ef4444")
                _ref_note = f" · 🧑‍⚖️ {_r.get('ref','')}" if _r.get("ref") not in ("Neutral","","N/A",None) else ""
                _pace_note = f" · 🐢 Slow pace" if _r.get("pace") == "Penalty" else (" · 🚀 Fast pace" if _r.get("pace") == "Boost" else "")
                # Rank badge
                _rank_colors = ["#ef4444","#f97316","#fbbf24","#22c55e","#10f590"]
                _rank_col = _rank_colors[min(_ri, 4)]
                st.markdown(f"""
                <div class='verdict-banner {_rc}' style='margin:0.3rem 0;padding:0.9rem 1.2rem;'>
                    <div style='flex:1;min-width:200px;'>
                        <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                            <div style='background:{_rank_col}22;border:1px solid {_rank_col}44;
                                        border-radius:6px;padding:1px 8px;font-family:JetBrains Mono,monospace;
                                        font-size:0.6rem;color:{_rank_col};font-weight:700;'>
                                #{_ri+1} LEG</div>
                            <div class='verdict-label' style='margin:0;'>{_r["line"]} pts {_r["side"]} · vs {_r["opp"]}</div>
                        </div>
                        <div style='font-size:1.05rem;font-weight:800;color:#f1f5f9;'>{_r["player"]}</div>
                        <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;margin-top:3px;'>
                            {_vol}{_r["matchup"]} def{_ref_note}{_pace_note}</div>
                    </div>
                    <div style='display:flex;gap:1.2rem;flex-wrap:wrap;align-items:center;'>
                        <div>
                            <div class='verdict-label'>Confidence</div>
                            <div style='font-size:1.3rem;font-weight:900;color:{_cc};line-height:1;'>{_conf}</div>
                            <div style='font-family:JetBrains Mono,monospace;font-size:0.5rem;color:#475569;'>/100</div>
                        </div>
                        <div><div class='verdict-label'>Hit Rate</div>
                             <div style='font-size:1rem;font-weight:700;color:#f1f5f9;'>{_r["adj"]:.0%}</div></div>
                        <div><div class='verdict-label'>Edge</div>
                             <div style='font-size:1rem;font-weight:700;color:{_ecol};'>{_r["edge"]:+.1f}</div></div>
                        <div><div class='verdict-label'>Signal</div>
                             <div style='font-size:0.85rem;font-weight:700;'>{_em} {_r["tier"].replace(" Over","").replace(" Under","")}</div></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # ── Best entry suggestion ─────────────────────────────
            _strong_legs = [r for r in _pr if "Strong" in r["tier"] and abs(r["edge"]) >= 2.0]
            if _strong_legs:
                _best_combined = 1.0
                for _r in _strong_legs:
                    _best_combined *= _r["adj"]
                st.markdown(
                    f"<div style='background:#052e16;border:1px solid #166534;border-left:4px solid #22c55e;"
                    f"padding:0.75rem 1rem;margin-top:0.75rem;font-family:JetBrains Mono,monospace;font-size:0.7rem;'>"
                    f"<span style='color:#22c55e;font-weight:700;letter-spacing:0.08em;'>💡 BEST ENTRY</span>"
                    f"<span style='color:#94a3b8;'> · Drop the weak legs. Play only: "
                    f"<span style='color:#f1f5f9;font-weight:700;'>"
                    f"{', '.join(r['player'] for r in _strong_legs)}</span>"
                    f" — {len(_strong_legs)}-leg entry at <span style='color:#22c55e;font-weight:700;'>"
                    f"{_best_combined:.1%}</span> combined probability.</span></div>",
                    unsafe_allow_html=True
                )
            elif _legs >= 3:
                st.markdown(
                    f"<div style='background:#1c0505;border:1px solid #991b1b;border-left:4px solid #ef4444;"
                    f"padding:0.75rem 1rem;margin-top:0.75rem;font-family:JetBrains Mono,monospace;font-size:0.7rem;'>"
                    f"<span style='color:#ef4444;font-weight:700;'>⛔ SKIP THIS ENTRY</span>"
                    f"<span style='color:#94a3b8;'> · No strong legs with 2+ edge found. "
                    f"This entry doesn't have enough edge to beat the vig.</span></div>",
                    unsafe_allow_html=True
                )

# ─────────────────────────────────────────────
# Player & Prop inputs
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Player & Prop</div>", unsafe_allow_html=True)
st.markdown("""
<div style='background:#0d1520;border:1px solid rgba(59,130,246,0.15);border-radius:10px;
            padding:0.65rem 1rem;margin-bottom:0.75rem;display:flex;align-items:center;gap:10px;'>
    <span style='font-size:1.1rem;'>💡</span>
    <span style='font-family:JetBrains Mono,monospace;font-size:0.67rem;color:#475569;'>
        <span style='color:#94a3b8;'>Enter a player from tonight's PrizePicks slate, set the line, choose Over or Under, and hit </span>
        <span style='color:#3b82f6;font-weight:700;'>Analyze Prop</span><span style='color:#94a3b8;'>. Takes ~10 seconds.</span>
    </span>
</div>
""", unsafe_allow_html=True)

# Session state for player clear
if "player_key" not in st.session_state:
    st.session_state.player_key = 0

col_a, col_b, col_c, col_d, col_e = st.columns([2.5, 1, 1, 1, 0.8])

with col_a:
    # Fuzzy search — resolve alias before passing to selectbox
    if "player_alias_input" not in st.session_state:
        st.session_state.player_alias_input = ""

    # Pre-select if a recent player was tapped
    _recent_pick = st.session_state.pop("_recent_pick", None)
    _preselect_idx = 0
    if _recent_pick and _recent_pick in player_names_list:
        _preselect_idx = player_names_list.index(_recent_pick) + 1  # +1 for blank option

    player_query = st.selectbox(
        "Player — type name, nickname, or initials",
        options=[""] + player_names_list,
        index=_preselect_idx,
        format_func=lambda x: "— search by name, nickname, or initials —" if x == "" else x,
        key=f"player_sel_{st.session_state.player_key}",
    )

    # Resolve alias: if user typed a known nickname, swap to full name
    if player_query and player_query in _aliases:
        player_query = _aliases[player_query]

    # Overlay ✕ button — only visible when a player is selected
    if player_query:
        if st.button("✕", key="clear_player_x", help="Clear player"):
            st.session_state.player_key += 1
            st.session_state.logs = None
            st.session_state.ai_analysis = None
            st.rerun()

    # Recent players — quick tap chips
    if st.session_state.recent_players and not player_query:
        st.markdown(
            "<div style='font-family:DM Mono;font-size:0.58rem;color:#475569;"
            "letter-spacing:0.1em;text-transform:uppercase;margin:6px 0 4px 0;'>"
            "Recent</div>",
            unsafe_allow_html=True
        )
        for _rp in st.session_state.recent_players:
            if st.button(_rp, key=f"recent_{_rp}", use_container_width=True):
                st.session_state.player_key += 1
                st.session_state._recent_pick = _rp
                st.rerun()

with col_b:
    _dd_line = st.session_state.get("_drilldown_line", None)
    line = st.number_input(
        "Points Line",
        min_value=0.5,
        max_value=80.0,
        value=float(_dd_line) if _dd_line else 24.5,
        step=0.5,
        format="%.1f",
        help="The number shown on PrizePicks — use the standard line, not goblin/demon"
    )
with col_c:
    _dd_side = st.session_state.get("_drilldown_side", None)
    side = st.selectbox(
        "Over / Under", ["Over", "Under"],
        index=0 if not _dd_side or _dd_side == "Over" else 1,
        help="Match what PrizePicks shows. Over = player scores MORE than the line"
    )
with col_d:
    n_games = st.selectbox("Sample", [5, 10, 15], index=1,
                           help="How many recent games to analyze. 10 is the sweet spot.")
with col_e:
    season_str = st.text_input("Season", value="2025-26",
                               help="Leave this as 2025-26 unless analyzing a past season")

season_int = season_str_to_int(season_str)
season_str_clean = season_str_to_season(season_str)

# Fuzzy alias resolution — catches nicknames typed directly
_resolved_player = player_query
if player_query:
    # Check alias map first
    for alias, full in _aliases.items():
        if alias.lower() == normalize_name(player_query):
            _resolved_player = full
            break
    # Fuzzy partial match — if typed value not in list, find closest
    if _resolved_player not in player_names_list and _resolved_player:
        _q = normalize_name(_resolved_player)
        _fuzzy_match = next(
            (n for n in player_names_list
             if _q in normalize_name(n) or
             all(part in normalize_name(n) for part in _q.split() if len(part) > 2)),
            None
        )
        if _fuzzy_match:
            _resolved_player = _fuzzy_match

selected_player = _resolved_player if _resolved_player else None
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
espn_player = next((p for p in espn_get_all_players(_date=_cache_date()) if normalize_name(p["full_name"]) == normalize_name(selected_player)), None)
player_team = _norm_team_abbr(espn_player["team_abbr"]) if espn_player else None

# Pre-fetch teammate minutes in background thread so it doesn't block button render
if player_team:
    import threading as _threading
    _warm_thread = _threading.Thread(
        target=get_teammate_minutes, args=(player_team,), daemon=True
    )
    _warm_thread.start()
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

# ── Injury status check ──────────────────────────────────────
with st.spinner("Checking injury status..."):
    _inj_status, _inj_reason = get_player_injury_status(selected_player)
    _inj_html, _inj_blocks   = injury_alert_html(_inj_status, _inj_reason)

if _inj_html:
    st.markdown(_inj_html, unsafe_allow_html=True)
    if _inj_blocks:
        st.warning(
            f"⚠️ {selected_player} is listed as **{_inj_status}** — verdict may be unreliable. "
            f"Check the latest injury report before betting."
        )

# Auto-trigger if coming from scanner drill-down
_drilldown_fetch = st.session_state.get("_drilldown_fetch", False)
if _drilldown_fetch:
    # Clear drilldown state so it doesn't re-trigger on next rerun
    st.session_state.pop("_drilldown_fetch", None)
    st.session_state.pop("_drilldown_line", None)
    st.session_state.pop("_drilldown_side", None)
fetch = st.button("🔍  Analyze Prop") or _drilldown_fetch
_status_ph = st.empty()  # persistent status placeholder across fetch + parallel block
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

if not fetch and st.session_state.logs is None:
    st.markdown("<div style='color:#475569; font-family:DM Mono; font-size:0.8rem; margin-top:1rem;'>↑ Select a player, set the line, then click Analyze Prop.</div>", unsafe_allow_html=True)

# Loading animation — shows immediately when button is clicked
if fetch:
    st.markdown("""
    <style>
    @keyframes ball-bounce {
        0%   { transform: translateY(0px);   animation-timing-function: ease-in; }
        45%  { transform: translateY(36px);  animation-timing-function: ease-out; }
        55%  { transform: translateY(36px);  animation-timing-function: ease-in; }
        100% { transform: translateY(0px);   animation-timing-function: ease-out; }
    }
    @keyframes shadow-pulse {
        0%   { transform: scaleX(1);   opacity: 0.4; }
        45%  { transform: scaleX(1.5); opacity: 0.15; }
        55%  { transform: scaleX(1.5); opacity: 0.15; }
        100% { transform: scaleX(1);   opacity: 0.4; }
    }
    @keyframes txt-fade {
        0%, 100% { opacity: 0.5; }
        50%       { opacity: 1.0; }
    }
    .bb-loader {
        background: linear-gradient(145deg, #0c1424, #080d18);
        border: 1px solid #1e2840;
        border-radius: 16px;
        padding: 1.75rem 1.5rem 1.5rem 1.5rem;
        margin: 0.5rem 0 1rem 0;
        animation: fadeUp 0.3s ease both;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0;
    }
    .bb-court {
        position: relative;
        width: 60px;
        height: 70px;
        display: flex;
        align-items: flex-start;
        justify-content: center;
    }
    .bb-ball {
        font-size: 2rem;
        line-height: 1;
        animation: ball-bounce 0.65s cubic-bezier(0.33,0,0.66,1) infinite;
        filter: drop-shadow(0 2px 6px rgba(249,115,22,0.4));
    }
    .bb-shadow {
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 28px;
        height: 6px;
        border-radius: 50%;
        background: rgba(249,115,22,0.25);
        animation: shadow-pulse 0.65s cubic-bezier(0.33,0,0.66,1) infinite;
        filter: blur(3px);
    }
    .bb-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: #edf2f8;
        margin-top: 0.6rem;
        text-align: center;
    }
    .bb-sub {
        font-family: 'DM Mono', monospace;
        font-size: 0.6rem;
        color: #4a6080;
        letter-spacing: 0.1em;
        text-align: center;
        margin-top: 4px;
        animation: txt-fade 2s ease-in-out infinite;
    }
    </style>
    <div class="bb-loader">
        <div class="bb-court">
            <div class="bb-ball">🏀</div>
            <div class="bb-shadow"></div>
        </div>
        <div class="bb-title">Analyzing prop...</div>
        <div class="bb-sub">FETCHING NBA DATA · MAY TAKE 5–15 SEC AT PEAK HOURS</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Fetch logs
# ─────────────────────────────────────────────

if fetch:
    st.session_state.ai_analysis = None
    st.session_state.ai_error    = None
    st.session_state.show_share  = False
    st.session_state.logs        = None  # clear stale logs before fresh fetch
    # Save to recent players (max 5, no duplicates)
    if selected_player:
        _recent = st.session_state.recent_players
        if selected_player in _recent:
            _recent.remove(selected_player)
        _recent.insert(0, selected_player)
        st.session_state.recent_players = _recent[:5]
    try:
        _status_ph.markdown("""
        <div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;
                    color:#555;padding:0.5rem 0;letter-spacing:0.1em;'>
            ⏳ FETCHING GAME LOGS...
        </div>""", unsafe_allow_html=True)
        # Always fetch n=15 and slice — one cache entry per player per day
        try:
            _all_logs = nba_get_game_logs(
                player_id=player_id, season=season_str_clean, n=15, _date=_cache_date()
            )
            # Merge playoff games OUTSIDE the cache so they always reflect latest
            _all_logs = _merge_playoff_logs(_all_logs, player_id, season_str_clean, 15)
        except RuntimeError:
            _all_logs = None  # NBA API failed — don't cache, show retry
        st.session_state.logs = _all_logs.head(n_games) if _all_logs is not None and not getattr(_all_logs, "empty", True) else None
        _status_ph.markdown("""
        <div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;
                    color:#555;padding:0.5rem 0;letter-spacing:0.1em;'>
            ⏳ LOADING MATCHUP + CONTEXT DATA...
        </div>""", unsafe_allow_html=True)
    except Exception as e:
        if not manual_mode:
            st.markdown("""
            <div style='background:#1c1005;border:1px solid #854d0e;border-radius:12px;
                        padding:1rem 1.2rem;margin:0.5rem 0;'>
                <div style='font-family:DM Mono;font-size:0.7rem;color:#f97316;
                            font-weight:800;letter-spacing:0.08em;margin-bottom:6px;'>
                    ⏱️ NBA STATS SERVER TIMEOUT
                </div>
                <div style='font-size:0.85rem;color:#94a3b8;line-height:1.6;'>
                    stats.nba.com is slow during peak game hours (evenings ET).<br>
                    <strong style='color:#f1f5f9;'>Click Analyze Prop again</strong> — 
                    it usually works on the second try.
                </div>
            </div>
            """, unsafe_allow_html=True)
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
        st.markdown("""
        <div style='background:#1c0505;border:1px solid #991b1b;border-radius:8px;
                    padding:1rem 1.2rem;margin:0.5rem 0;'>
            <div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;
                        color:#ef4444;font-weight:700;letter-spacing:0.08em;margin-bottom:6px;'>
                ⚠️ NBA STATS SERVER SLOW
            </div>
            <div style='font-size:0.85rem;color:#94a3b8;line-height:1.6;'>
                stats.nba.com didn't respond in time.<br>
                This is common during peak hours (evenings ET).<br>
                <strong style='color:#f1f5f9;'>Click the button below to try again — usually works on 2nd attempt.</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄  Try Again", use_container_width=True):
            # Clear all caches for this player and retry
            nba_get_game_logs.clear()
            nba_get_full_season_logs_cached.clear()
            st.session_state.logs = None
            st.rerun()
        st.stop()

    # ── Blowout filter ───────────────────────
    logs_raw = logs.copy()  # keep raw for game log display
    logs_filtered, _blowout_count, _blowout_games = filter_blowouts(logs, threshold=15)
    # Use filtered logs for all calculations if enough games remain
    if len(logs_filtered) >= 4:
        logs = logs_filtered
    else:
        logs_filtered = logs_raw  # not enough games after filter, use all
        _blowout_count = 0
        _blowout_games = []

    # ── Core stats ────────────────────────────
    baseline       = hit_rate(logs, line, side)
    weighted_base  = weighted_hit_rate(logs, line, side)  # recomputed after opp_abbr is set
    consistency    = consistency_score(logs, line)
    avg_min        = pd.to_numeric(logs["MIN"],  errors="coerce").dropna().mean()
    avg_fga        = pd.to_numeric(logs["FGA"],  errors="coerce").dropna().mean()
    avg_fta        = pd.to_numeric(logs["FTA"],  errors="coerce").dropna().mean()
    sample_avg_pts = pd.to_numeric(logs["PTS"],  errors="coerce").dropna().mean()

    minutes_suggest = suggest_bucket(avg_min, 32, 26)
    shots_suggest   = "High" if avg_fga >= 15 else ("Low" if avg_fga < 10 else "Medium")
    role_suggest    = suggest_bucket(avg_fga + 0.5 * avg_fta, 18, 12)

    # (Minutes restriction downgrade applied after season_avg_min is fetched below)

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

    # ── Fire slow calls in parallel ──────────────────────────────
    import concurrent.futures as _cf
    with _cf.ThreadPoolExecutor(max_workers=4) as _pool:
        _f_matchup  = _pool.submit(classify_matchup_espn, opp_abbr)
        _f_h2h      = _pool.submit(get_h2h_logs, player_id, opp_abbr, season_str_clean) if opp_abbr else None
        _f_season   = _pool.submit(nba_get_full_season_logs_cached, player_id, season_str_clean)
        _f_playoff  = _pool.submit(get_playoff_picture, player_team) if player_team else None
        _f_series   = _pool.submit(get_playoff_series_context, player_team) if (_IS_PLAYOFFS and player_team) else None
        _f_refs     = _pool.submit(referee_signal, player_team, side) if player_team else None
        _f_opp_inj   = _pool.submit(get_opponent_injury_report, opp_abbr) if opp_abbr else None
        _f_def_form  = _pool.submit(get_opp_recent_defensive_form, opp_abbr) if opp_abbr else None
        _f_po_logs   = _pool.submit(get_playoff_game_logs, player_id, season_str_clean) if _IS_PLAYOFFS else None
        _f_last_game = _pool.submit(espn_get_last_game_date, player_team) if player_team else None
        _f_news      = _pool.submit(espn_get_player_news, full_name)

        try:
            matchup_auto, opp_pts, league_avg = _f_matchup.result(timeout=10)
        except Exception:
            matchup_auto, opp_pts, league_avg = "Neutral", None, "114.5"

        try:
            h2h_df = _f_h2h.result(timeout=22) if _f_h2h else pd.DataFrame()
        except Exception:
            h2h_df = pd.DataFrame()

        try:
            _f_season.result(timeout=20)
        except Exception:
            pass

        try:
            _playoff = _f_playoff.result(timeout=8) if _f_playoff else {}
        except Exception:
            _playoff = {}

        try:
            _series = _f_series.result(timeout=8) if _f_series else {}
        except Exception:
            _series = {}

        try:
            _ref_sig, _ref_ppg, _ref_names = _f_refs.result(timeout=8) if _f_refs else ("Neutral", None, [])
        except Exception:
            _ref_sig, _ref_ppg, _ref_names = "Neutral", None, []

        try:
            _opp_absent, _opp_inj_html = _f_opp_inj.result(timeout=10) if _f_opp_inj else ([], "")
        except Exception:
            _opp_absent, _opp_inj_html = [], ""

        try:
            _def_form = _f_def_form.result(timeout=10) if _f_def_form else {}
        except Exception:
            _def_form = {}

        try:
            _po_logs = _f_po_logs.result(timeout=12) if _f_po_logs else pd.DataFrame()
        except Exception:
            _po_logs = pd.DataFrame()

        try:
            _espn_last_game = _f_last_game.result(timeout=8) if _f_last_game else None
        except Exception:
            _espn_last_game = None

        try:
            _player_news = _f_news.result(timeout=8)
        except Exception:
            _player_news = []

    # ── Matchup upgrade if key opp players out ──────────────────────────
    if _opp_absent and len(_opp_absent) >= 2 and matchup_auto == "Neutral":
        matchup_auto = "Good"
    elif _opp_absent and len(_opp_absent) >= 1 and matchup_auto == "Bad":
        matchup_auto = "Neutral"

    # ── Blend in recent defensive form ───────────────────────────────────
    # Override matchup_auto with recent trend if it's strong enough
    _def_trend = _def_form.get("trend", "Neutral")
    _def_diff  = _def_form.get("diff", 0)
    if _def_trend == "Softening" and matchup_auto in ("Neutral", "Bad"):
        # Defense is breaking down — upgrade matchup
        matchup_auto = "Good" if matchup_auto == "Neutral" else "Neutral"
    elif _def_trend == "Tightening" and matchup_auto in ("Neutral", "Good"):
        # Defense is locking in — downgrade matchup
        matchup_auto = "Bad" if matchup_auto == "Neutral" else "Neutral"

    _status_ph.empty()  # clear loading message — results are about to render
    h2h_sig, h2h_avg, h2h_count = h2h_signal(h2h_df, line, side)
    # Use ESPN last game date for rest detection — more reliable than game logs
    # Game logs lag 24-48hrs during playoffs; ESPN scoreboard updates immediately
    if _espn_last_game and game_date:
        try:
            _last_dt   = pd.Timestamp(_espn_last_game)
            _next_dt   = pd.Timestamp(game_date)
            _days_rest = (_next_dt - _last_dt).days
            if _days_rest <= 1:
                b2b_status  = "B2B"
                rest_status = "B2B"
            elif _days_rest == 2:
                b2b_status  = "Normal"
                rest_status = "Short"
            elif _days_rest == 3:
                b2b_status  = "Normal"
                rest_status = "Normal"
            else:
                b2b_status  = "Normal"
                rest_status = "Rested"
        except Exception:
            b2b_status  = detect_b2b(logs, game_date)
            rest_status = detect_rest_days(logs, game_date)
    else:
        b2b_status  = detect_b2b(logs, game_date)
        rest_status = detect_rest_days(logs, game_date)
    if b2b_status == "B2B":
        rest_status = "B2B"
    season_avg     = nba_get_season_avg(player_id, season_str_clean, logs_l10=logs)
    season_avg_min = nba_get_season_avg_min(player_id, season_str_clean, logs_l10=logs)

    # ── Playoff minutes floor warning ────────────────────────────────
    # In playoffs, role players get buried. Flag anyone under 28 min avg
    _playoff_mins_warning = ""
    if _IS_PLAYOFFS and avg_min < 28 and avg_min > 0:
        _playoff_mins_warning = (
            f"<div style='background:#1c1005;border:1px solid #854d0e;"
            f"border-radius:10px;padding:0.75rem 1rem;margin-bottom:0.5rem;"
            f"display:flex;align-items:center;gap:10px;'>"
            f"<span style='font-size:1.2rem;'>⚠️</span>"
            f"<div>"
            f"<div style='font-family:Outfit,sans-serif;font-size:0.85rem;font-weight:700;color:#f97316;'>"
            f"Playoff Minutes Risk</div>"
            f"<div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#94a3b8;margin-top:2px;'>"
            f"Avg {avg_min:.0f} min/game — role players often get buried in playoffs. "
            f"This line may not reflect reduced possessions.</div>"
            f"</div></div>"
        )

    # ── Minutes restriction downgrade ─────────────────────────────
    # Now that season_avg_min is available, downgrade minutes/role
    # if player is playing significantly fewer minutes than season avg.
    if season_avg_min and season_avg_min >= 10:
        _min_ratio = avg_min / season_avg_min
        if _min_ratio <= 0.80:
            minutes_suggest = "Risk"
            role_suggest    = "Risk"
        elif _min_ratio <= 0.90 and minutes_suggest == "Strong":
            minutes_suggest = "Okay"
            role_suggest    = "Okay" if role_suggest == "Strong" else role_suggest

    form_sig, form_diff = form_divergence_signal(sample_avg_pts, season_avg, line, side)

    # Usage spike — uses pre-warmed cache so runs fast
    _teammate_mins = get_teammate_minutes(player_team, _date=_cache_date()) if player_team else {}
    try:
        _spike_sig, _spike_players, _spike_html = detect_usage_spike(
            selected_player, player_team, side, _teammate_mins
        )
    except Exception:
        _spike_sig, _spike_players, _spike_html = "Neutral", [], ""
    # Recompute weighted base with playoff series boost now that opp_abbr is known
    if _IS_PLAYOFFS and opp_abbr:
        weighted_base = weighted_hit_rate(logs, line, side, opp_abbr=opp_abbr)

    pace_sig, player_pace, opp_pace = pace_adjustment(player_team, opp_abbr, side)
    shoot_sig, recent_3pt, recent_ts = shooting_efficiency_signal(logs, side, n_recent=3)

    # Get last 3 games minutes for restriction check
    _last3_mins = (
        pd.to_numeric(logs["MIN"], errors="coerce")
        .dropna().head(3).tolist()
        if logs is not None and not logs.empty else []
    )
    _min_alert_html = minutes_restriction_alert(avg_min, season_avg_min, _last3_mins)

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
            <div class='stat-hint'>Avg FGA: {avg_fga:.1f} · FTA: {avg_fta:.1f}{f" · Season avg: {season_avg_min:.1f} min" if season_avg_min else ""}</div>
        </div>""", unsafe_allow_html=True)

    # ── Shot Attempts Card ───────────────────
    _fga_trend_color = "#10f590" if fga_flag == "↑" else ("#ef4444" if fga_flag == "↓" else "#94a3b8")
    _fga_label = "Trending Up" if fga_flag == "↑" else ("Trending Down" if fga_flag == "↓" else "Stable")
    _fga_pts_per_attempt = round(sample_avg_pts / avg_fga, 2) if avg_fga > 0 else 0

    # Playoff FGA context — star players shoot more in playoffs
    _fga_playoff_note = ""
    if _IS_PLAYOFFS:
        if avg_fga >= 15:
            _fga_playoff_note = "High-volume scorer · playoff usage likely holds"
        elif avg_fga < 10:
            _fga_playoff_note = "⚠️ Low volume · watch for playoff rotation cut"
        else:
            _fga_playoff_note = "Role player volume · may fluctuate in playoffs"

    # FTA adds free throw scoring — important for foul-prone matchups
    _fta_note = f"{avg_fta:.1f} FTA/game" if avg_fta else ""
    _fta_pts  = round(avg_fta * 0.78, 1) if avg_fta else 0  # ~78% FT avg

    _fga_bg     = "#0d1520"
    _fga_border = "rgba(255,255,255,0.06)"
    if avg_fga >= 15:
        _fga_bg = "#041a0e"; _fga_border = "rgba(16,245,144,0.15)"
    elif avg_fga < 10:
        _fga_bg = "#1a0008"; _fga_border = "rgba(255,69,96,0.15)"

    st.markdown(f"""
    <div style='background:{_fga_bg};border:1px solid {_fga_border};border-radius:12px;
                padding:1rem 1.1rem;margin-bottom:0.5rem;'>
        <div style='font-family:JetBrains Mono,monospace;font-size:0.58rem;color:#475569;
                    letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;'>
            Shot Attempts (L{n_games})
            <span style='color:#475569;font-size:0.55rem;margin-left:6px;'>
            — attempts = scoring opportunities</span>
        </div>
        <div style='display:flex;gap:2rem;flex-wrap:wrap;align-items:flex-end;'>
            <div>
                <div style='font-family:Outfit,sans-serif;font-size:2rem;font-weight:800;
                            color:{_fga_trend_color};line-height:1;'>{avg_fga:.1f}</div>
                <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;
                            color:#475569;margin-top:3px;'>FGA per game
                    <span style='color:{_fga_trend_color};margin-left:6px;'>{fga_flag} {_fga_label}</span>
                </div>
            </div>
            <div>
                <div style='font-family:Outfit,sans-serif;font-size:2rem;font-weight:800;
                            color:#60a5fa;line-height:1;'>{avg_fta:.1f}</div>
                <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;
                            color:#475569;margin-top:3px;'>FTA per game
                    <span style='color:#60a5fa;margin-left:6px;'>≈ {_fta_pts} pts from FTs</span>
                </div>
            </div>
            <div>
                <div style='font-family:Outfit,sans-serif;font-size:2rem;font-weight:800;
                            color:#94a3b8;line-height:1;'>{_fga_pts_per_attempt}</div>
                <div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;
                            color:#475569;margin-top:3px;'>pts per attempt</div>
            </div>
        </div>
        {f"<div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#475569;margin-top:8px;border-top:1px solid rgba(255,255,255,0.05);padding-top:8px;'>{_fga_playoff_note}</div>" if _fga_playoff_note else ""}
    </div>
    """, unsafe_allow_html=True)

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

        # Defensive form trend badge
        _df_trend  = _def_form.get("trend", "Neutral")
        _df_recent = _def_form.get("recent_avg")
        _df_season = _def_form.get("season_avg")
        _df_diff   = _def_form.get("diff", 0)
        if _df_trend == "Tightening":
            _trend_badge = (f"<span style='font-family:DM Mono;font-size:0.63rem;font-weight:700;"
                            f"color:#ef4444;margin-left:10px;'>🔒 L5 tightening "
                            f"({_df_recent:.1f} vs {_df_season:.1f} season)</span>")
        elif _df_trend == "Softening":
            _trend_badge = (f"<span style='font-family:DM Mono;font-size:0.63rem;font-weight:700;"
                            f"color:#22c55e;margin-left:10px;'>📈 L5 softening "
                            f"({_df_recent:.1f} vs {_df_season:.1f} season)</span>")
        else:
            _trend_badge = ""

        pts_line = (
            f"{opp_pts:.1f} pts allowed/game (L15)"
            f"<span style='font-family:DM Mono; font-size:0.72rem; color:#475569; margin-left:8px;'>league avg {league_avg}</span>"
            f"{_trend_badge}"
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
        st.markdown(
            "<div style='background:#0d1520;border:1px solid rgba(255,255,255,0.06);border-radius:10px;"
            "padding:0.75rem 1rem;color:#475569;font-family:JetBrains Mono,monospace;font-size:0.68rem;'>"
            "Opponent defensive stats not available — matchup set to Neutral</div>",
            unsafe_allow_html=True
        )
        matchup_auto = "Neutral"

    # Pre-build all pills to avoid f-string rendering issues
    _pill_min = flag_pill("MIN", min_flag)
    _pill_fga = flag_pill("FGA", fga_flag)
    _pill_pts = flag_pill("PTS", pts_flag)
    if recent_3pt is not None and recent_3pt > 0:
        _3pt_label = f"3PT {recent_3pt:.0%}"
        _3pt_flag  = "up" if shoot_sig == "Boost" else ("down" if shoot_sig == "Penalty" else "flat")
        _pill_3pt  = flag_pill(_3pt_label, _3pt_flag)
    else:
        _pill_3pt  = ""

    # Trend flags
    st.markdown(
        f"<div class='flag-row'>{_pill_min}{_pill_fga}{_pill_pts}{_pill_3pt}</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Blowout filter alert
    if _blowout_count > 0:
        _bl_games_str = " · ".join(_blowout_games[:3])
        st.markdown(
            f"<div style='background:#0d0d1a;border:1px solid #2e2e5a;"
            f"border-left:3px solid #3b82f6;"
            f"padding:0.6rem 0.9rem;margin-bottom:0.4rem;'>"
            f"<span style='font-family:JetBrains Mono,monospace;font-size:0.6rem;"
            f"color:#3b82f6;font-weight:700;letter-spacing:0.1em;'>"
            f"BLOWOUT FILTER ACTIVE</span>"
            f"<span style='font-family:JetBrains Mono,monospace;font-size:0.6rem;"
            f"color:#555;'> · {_blowout_count} game{'s' if _blowout_count > 1 else ''} "
            f"excluded (±15pt margin) — {_bl_games_str}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    # Minutes restriction alert
    if _min_alert_html:
        st.markdown(_min_alert_html, unsafe_allow_html=True)

    # Usage spike alert
    if _spike_html:
        st.markdown(_spike_html, unsafe_allow_html=True)

    # Opponent injury report
    if _opp_inj_html:
        st.markdown(_opp_inj_html, unsafe_allow_html=True)

    # ── H2H + B2B + Form cards ───────────────
    # Series context header in playoffs
    _section_title = "H2H, Form, Schedule & Pace"
    if _IS_PLAYOFFS and _series and _series.get("found"):
        _sw = _series["series_wins"]; _sl = _series["series_losses"]
        _elim  = _series.get("is_elimination", False)
        _close = _series.get("is_closeout", False)
        _series_tag = f"{'⚠️ ELIM GAME' if _elim else ('🏆 CLOSEOUT' if _close else f'Series {_sw}-{_sl}')}"
        _section_title = f"H2H · Form · Schedule · Pace &nbsp;·&nbsp; <span style='color:#3b82f6;font-size:0.75rem;'>{_series_tag}</span>"

    st.markdown(f"<div class='section-header'>{_section_title}</div>", unsafe_allow_html=True)

    # Playoff minutes warning
    if _playoff_mins_warning:
        st.markdown(_playoff_mins_warning, unsafe_allow_html=True)

    hb1, hb2, hb3, hb4 = st.columns(4)

    with hb1:
        if h2h_count >= 2:
            sig_color = {"Strong": "#22c55e", "Neutral": "#94a3b8", "Risk": "#ef4444"}.get(h2h_sig, "#94a3b8")
            sig_bg    = {"Strong": "#052e16", "Neutral": "#0f172a",  "Risk": "#1c0505"}.get(h2h_sig, "#0f172a")
            sig_border= {"Strong": "#166534", "Neutral": "#1e293b",  "Risk": "#991b1b"}.get(h2h_sig, "#1e293b")
            _h2h_label = f"Avg pts vs {opp_abbr} · this series ({h2h_count}G)" if _IS_PLAYOFFS else f"Avg pts vs {opp_abbr} (L{h2h_count} games)"
            _h2h_meaning = {"Strong": "✅ Good matchup historically", "Risk": "⚠️ Struggles vs this team", "Neutral": "Neutral history"}.get(h2h_sig, "")
            st.markdown(f"""
            <div class='stat-card' style='border-color:{sig_border};background:{sig_bg};'>
                <div class='stat-label'>{_h2h_label}</div>
                <div style='display:flex;align-items:baseline;gap:12px;margin-top:4px;'>
                    <div class='stat-value' style='color:{sig_color};'>{h2h_avg:.1f}</div>
                    <div style='font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#475569;'>pts avg</div>
                </div>
                <div style='font-family:JetBrains Mono,monospace;font-size:0.68rem;color:{sig_color};margin-top:4px;'>
                    {_h2h_meaning} · line {line}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            _h2h_note = "Building this-series data..." if _IS_PLAYOFFS else ("Not enough H2H data (need 2+ games)" if opp_abbr else "Opponent not detected")
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-label'>{"This Series H2H" if _IS_PLAYOFFS else f"vs {opp_abbr or "opponent"} H2H"}</div>
                <div style='color:#475569;font-size:0.85rem;margin-top:8px;'>{_h2h_note}</div>
            </div>""", unsafe_allow_html=True)

    with hb2:
        # Last game info — use ESPN date (real-time) over log date (can lag 48hrs)
        _last_game_info = ""
        if _espn_last_game:
            try:
                _espn_date_fmt = pd.Timestamp(_espn_last_game).strftime("%b %d")
                # Try to get pts from logs for the matching date
                _espn_pts = ""
                if logs is not None and not logs.empty:
                    _log_dates = pd.to_datetime(logs["GAME_DATE"], errors="coerce")
                    _match = logs[_log_dates.dt.date == pd.Timestamp(_espn_last_game).date()]
                    if not _match.empty:
                        _pts_val = pd.to_numeric(_match.iloc[0].get("PTS", 0), errors="coerce")
                        if pd.notna(_pts_val):
                            _espn_pts = f" — {int(_pts_val)} pts"
                _last_game_info = f"Last: {_espn_date_fmt}{_espn_pts}"
            except Exception:
                pass
        if not _last_game_info and logs is not None and not logs.empty:
            try:
                _last_row  = logs.iloc[0]
                _last_date = pd.to_datetime(_last_row["GAME_DATE"]).strftime("%b %d")
                _last_matchup = str(_last_row.get("MATCHUP", "")).replace("vs.", "vs").replace("@", "@ ").strip()
                _last_pts  = int(pd.to_numeric(_last_row.get("PTS", 0), errors="coerce"))
                _last_game_info = f"Last: {_last_date} {_last_matchup} — {_last_pts} pts"
            except Exception:
                pass

        _rest_cfg = {
            "B2B":    ("😴", "Back-to-Back",   "#ef4444", "#991b1b", "#1c0505", "Fatigue penalty applied"),
            "Short":  ("🥱", "Short Rest",      "#f97316", "#9a3412", "#160800", "1 day rest — slight fatigue"),
            "Normal": ("✅", "Normal Rest",     "#22c55e", "#166534", "#052e16", "No fatigue adjustment"),
            "Rested": ("💪", "Well Rested",     "#22c55e", "#166534", "#052e16", "3+ days rest — boost applied"),
        }
        _ri, _rl, _rc, _rb, _rbg, _rsub = _rest_cfg.get(
            rest_status, ("✅", "Normal Rest", "#22c55e", "#166534", "#052e16", "No fatigue adjustment")
        )
        st.markdown(f"""
        <div class='stat-card' style='border-color:{_rb}; background:linear-gradient(135deg,{_rbg} 0%,#111827 100%);'>
            <div class='stat-label'>Schedule & Rest</div>
            <div style='display:flex; align-items:center; gap:10px; margin-top:6px;'>
                <div style='font-size:1.5rem;'>{_ri}</div>
                <div>
                    <div style='font-size:1rem; font-weight:800; color:{_rc};'>{_rl}</div>
                    <div style='font-family:DM Mono; font-size:0.7rem; color:#475569; margin-top:2px;'>
                        {_rsub}
                    </div>
                    {f"<div style='font-family:DM Mono; font-size:0.65rem; color:#64748b; margin-top:4px;'>{_last_game_info}</div>" if _last_game_info else ""}
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

    with hb4:
        LEAGUE_AVG_PACE = 104.5
        if player_pace or opp_pace:
            _gp = ((player_pace or 0) + (opp_pace or 0)) / (2 if player_pace and opp_pace else 1)
            _pd = _gp - LEAGUE_AVG_PACE
            _pc = "#22c55e" if pace_sig == "Boost" else ("#ef4444" if pace_sig == "Penalty" else "#94a3b8")
            _pb = "#052e16" if pace_sig == "Boost" else ("#1c0505" if pace_sig == "Penalty" else "#0f172a")
            _pborder = "#166534" if pace_sig == "Boost" else ("#991b1b" if pace_sig == "Penalty" else "#1e293b")
            # In playoffs show reg vs playoff pace comparison
            _pace_note = ""
            if _IS_PLAYOFFS and player_pace and opp_pace:
                _reg_pace = ((_NBA_PACE_2526.get(player_team,104.5) + _NBA_PACE_2526.get(opp_abbr,104.5))/2)
                _pl_pace  = (player_pace + opp_pace) / 2
                _pace_note = f" · Reg: {_reg_pace:.1f} → Playoff: {_pl_pace:.1f}"
            _plabel = "🚀 Fast" if _pd >= 2.5 else ("🐢 Slow" if _pd <= -2.5 else "⚖️ Average")
            _psub = f"{_gp:.1f} poss/game · league avg {LEAGUE_AVG_PACE}"
            _pverdict = {
                "Boost":   f"{'More scoring' if side=='Over' else 'Fewer scoring opp'} — applied",
                "Penalty": f"{'Fewer scoring opp' if side=='Over' else 'More scoring'} — applied",
                "Neutral": "No pace adjustment",
            }.get(pace_sig, "No adjustment")
            st.markdown(f"""
            <div class='stat-card' style='border-color:{_pborder};background:linear-gradient(135deg,{_pb} 0%,#111827 100%);'>
                <div class='stat-label'>Game Pace</div>
                <div style='font-size:1rem;font-weight:800;color:{_pc};margin-top:6px;'>{_plabel}</div>
                <div style='font-family:DM Mono;font-size:0.7rem;color:#475569;margin-top:4px;'>{_psub}</div>
                <div style='font-family:DM Mono;font-size:0.68rem;color:{_pc};margin-top:4px;'>{_pverdict}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='stat-card'>
                <div class='stat-label'>Game Pace</div>
                <div style='color:#475569;font-size:0.85rem;margin-top:8px;'>Pace data loading...</div>
            </div>""", unsafe_allow_html=True)

    # ── Playoff context ──────────────────────────────────────────
    st.markdown("<div class='section-header'>Home / Away Splits</div>", unsafe_allow_html=True)
    if splits.get("home_games", 0) > 0 or splits.get("away_games", 0) > 0:
        venue_color = "#22c55e" if tonight_venue == "Home" else "#60a5fa"
        # Include opponent in the tonight badge
        _opp_label = f" vs {opp_abbr}" if opp_abbr else ""
        venue_note_html = (
            f"<span style='background:{venue_color}22; color:{venue_color}; font-family:DM Mono; "
            f"font-size:0.7rem; padding:3px 10px; border-radius:999px; border:1px solid {venue_color}44; "
            f"margin-left:8px;'>Tonight: {tonight_venue}{_opp_label}</span>"
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

    with st.expander("📋  Game Log"):
        st.dataframe(logs.reset_index(drop=True), use_container_width=True)

    # All signals auto-computed — no manual overrides needed
    matchup_sel = matchup_auto
    script_sel  = "Neutral"
    minutes_sel = minutes_suggest
    role_sel    = role_suggest
    shots_sel   = shots_suggest

    # ── Tonight's Game ─────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Tonight's Game</div>", unsafe_allow_html=True)

    if opp_abbr:
        _def_plain = {
            "Good":    ("✅ Soft defense", "#10f590", "This team gives up a lot of points — good for Overs"),
            "Bad":     ("🔴 Tough defense", "#ef4444", "This team is hard to score on — lean Under"),
            "Neutral": ("⚪ Average defense", "#94a3b8", "No clear defensive edge either way"),
        }.get(matchup_auto, ("⚪ Average defense", "#94a3b8", ""))
        _opp_pts_str = f"{opp_pts:.1f} pts allowed/game" if opp_pts else ""
        _venue_icon  = "🏠 Home" if tonight_venue == "Home" else "✈️ Away"
        _venue_col   = "#22c55e" if tonight_venue == "Home" else "#60a5fa"
        st.markdown(
            f"<div style='background:#0d1520;border:1px solid rgba(255,255,255,0.07);"
            f"border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.5rem;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.75rem;'>"
            f"<div>"
            f"<div style='font-family:JetBrains Mono,monospace;font-size:0.58rem;color:#475569;"
            f"letter-spacing:0.15em;text-transform:uppercase;margin-bottom:6px;'>Next Game</div>"
            f"<div style='font-family:Outfit,sans-serif;font-size:1.4rem;font-weight:800;"
            f"color:#f1f5f9;line-height:1;'>vs {opp_abbr}"
            f"<span style='font-size:0.85rem;font-weight:400;color:#475569;margin-left:10px;'>{game_date or ''}</span></div>"
            f"<div style='margin-top:8px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;'>"
            f"<span style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:{_venue_col};"
            f"background:{_venue_col}15;border:1px solid {_venue_col}33;padding:3px 12px;border-radius:999px;'>{_venue_icon}</span>"
            f"<span style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:{_def_plain[1]};"
            f"background:{_def_plain[1]}15;border:1px solid {_def_plain[1]}33;padding:3px 12px;border-radius:999px;'>{_def_plain[0]}</span>"
            f"</div></div>"
            f"<div style='text-align:right;'>"
            f"<div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;color:#475569;'>{_opp_pts_str}</div>"
            f"<div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#475569;margin-top:4px;line-height:1.5;'>{_def_plain[2]}</div>"
            f"</div></div></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background:#0d1520;border:1px solid rgba(255,255,255,0.06);border-radius:14px;"
            "padding:0.75rem 1rem;color:#475569;font-family:JetBrains Mono,monospace;font-size:0.7rem;'>"
            "Next opponent not found — check back closer to tip-off</div>",
            unsafe_allow_html=True
        )

    # ── Latest News ────────────────────────────────────────────────────────
    if _player_news:
        st.markdown("<div class='section-header'>Latest News</div>", unsafe_allow_html=True)
        for _n in _player_news:
            _ndate = _n.get("date", "")
            _nhead = _n.get("headline", "")
            _ndesc = _n.get("description", "")
            _nlink = _n.get("link", "")
            _link_html = (
                f"<a href='{_nlink}' target='_blank' style='color:#3b82f6;"
                f"font-size:0.6rem;font-family:JetBrains Mono,monospace;'>Read more →</a>"
            ) if _nlink else ""
            st.markdown(
                f"<div style='background:#0d1520;border:1px solid rgba(255,255,255,0.06);"
                f"border-left:3px solid #3b82f6;border-radius:0 10px 10px 0;"
                f"padding:0.7rem 1rem;margin-bottom:0.4rem;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:8px;'>"
                f"<div style='font-family:Outfit,sans-serif;font-size:0.82rem;font-weight:600;"
                f"color:#f1f5f9;line-height:1.4;'>{_nhead}</div>"
                f"<div style='font-family:JetBrains Mono,monospace;font-size:0.58rem;color:#475569;"
                f"white-space:nowrap;flex-shrink:0;'>{_ndate}</div></div>"
                f"{f'<div style="font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#475569;margin-top:4px;line-height:1.5;">{_ndesc[:150]}...</div>' if _ndesc else ''}"
                f"<div style='margin-top:6px;'>{_link_html}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    venue_adj = venue_adjustment(splits, tonight_venue, side)

    # ── Referee card ──────────────────────────────────────────────────────
    if _ref_names:
        _ref_col = "#22c55e" if _ref_sig == "High FT" else ("#ef4444" if _ref_sig == "Low FT" else "#94a3b8")
        _ref_bg  = "#052e16" if _ref_sig == "High FT" else ("#1c0505" if _ref_sig == "Low FT" else "#0f172a")
        _ref_bdr = "#166534" if _ref_sig == "High FT" else ("#991b1b" if _ref_sig == "Low FT" else "#1e293b")
        _ref_lbl = "🟢 High-foul crew" if _ref_sig == "High FT" else ("🔴 Low-foul crew" if _ref_sig == "Low FT" else "⚪ Neutral crew")
        _ref_note = f"{_ref_ppg:.1f} pts/game crew avg" if _ref_ppg else "Stats not available"
        st.markdown(
            f"<div style='background:{_ref_bg};border:1px solid {_ref_bdr};border-radius:8px;"
            f"padding:0.6rem 1rem;margin-bottom:0.75rem;font-family:JetBrains Mono,monospace;font-size:0.68rem;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;'>"
            f"<div><span style='color:{_ref_col};font-weight:700;'>🧑‍⚖️ TONIGHT'S REFS</span>"
            f"<span style='color:#475569;margin-left:8px;'>{' · '.join(_ref_names[:3])}</span></div>"
            f"<div><span style='color:{_ref_col};font-weight:700;'>{_ref_lbl}</span>"
            f"<span style='color:#555;margin-left:8px;'>{_ref_note} · league avg {_REF_LEAGUE_AVG_PPG}</span></div>"
            f"</div></div>",
            unsafe_allow_html=True
        )

    # Minutes restriction override — scale down signals if player is on minutes limit
    _min_override = minutes_adjusted_scoring(
        sample_avg_pts, season_avg_min, avg_min, line, side
    )

    # Apply overrides in priority order:
    # 1. Minutes restriction (hard cap on expectations)
    # 2. Usage spike (boost if teammate out)
    if _min_override == "Risk":
        _minutes_ctx = "Risk"
        _role_ctx    = "Risk"
    elif _min_override == "Strong":
        _minutes_ctx = "Strong"
        _role_ctx    = "Strong"
    elif _spike_sig == "Boost" and minutes_sel != "Risk":
        _minutes_ctx = "Strong"
        _role_ctx    = "Strong"
    else:
        _minutes_ctx = minutes_sel
        _role_ctx    = role_sel

    # ── Series coverage signal — this defense vs this player in this series ──
    _series_cov_sig, _series_cov_avg, _series_cov_n = series_coverage_signal(
        logs, opp_abbr, line, side, season_avg
    )

    # ── Playoff shot volume signal ───────────────────────────────────────
    # High-volume scorers maintain usage in playoffs; role players get buried
    _shot_vol_sig = "Neutral"
    if _IS_PLAYOFFS:
        if avg_fga >= 15:
            _shot_vol_sig = "Star"      # 15+ FGA — usage protected in playoffs
        elif avg_fga < 10:
            _shot_vol_sig = "Risk"      # <10 FGA — likely to see rotation cut

    # ── Game number signal ───────────────────────────────────────────────
    _game_num_label = "N/A"
    if _IS_PLAYOFFS and _series and _series.get("found"):
        _gnum = get_series_game_number(
            _series.get("series_wins", 0),
            _series.get("series_losses", 0)
        )
        _game_num_label, _game_num_adj = game_number_adjustment(_gnum, side)
    else:
        _gnum = None
        _game_num_adj = 0.0

    # ── Playoff usage spike signal ────────────────────────────────────────
    _pu_spike_sig, _po_avg_pts, _po_avg_min = playoff_usage_spike_signal(
        player_id, season_str_clean,
        reg_avg_pts=sample_avg_pts,
        reg_avg_min=avg_min,
        line=line,
        side=side,
    ) if _IS_PLAYOFFS else ("Neutral", None, None)

    # Elimination/closeout signal from series context
    _elim_game_ctx = "Normal"
    if _IS_PLAYOFFS and _series and _series.get("found"):
        if _series.get("is_elimination"):
            _elim_game_ctx = "Elimination"
        elif _series.get("is_closeout"):
            _elim_game_ctx = "Closeout"

    context = {
        "minutes":    _minutes_ctx,
        "role":       _role_ctx,
        "shots":      shots_sel,
        "matchup":    matchup_sel,
        "script":     script_sel,
        "venue":      venue_adj,
        "h2h":        h2h_sig,
        "series_cov": _series_cov_sig,
        "b2b":        b2b_status,
        "rest":       rest_status,
        "form":       form_sig,
        "pace":       pace_sig,
        "shoot":      shoot_sig,
        "elim_game":  _elim_game_ctx,
        "ref":        _ref_sig if _ref_sig else "Neutral",
        "game_num":   _game_num_label,
        "pu_spike":   _pu_spike_sig,
        "shot_vol":   _shot_vol_sig,
    }

    adjusted  = apply_adjustments(weighted_base, context, side)
    # In playoffs, weight this-series games 3x for edge calc (matches weighted_hit_rate)
    if _IS_PLAYOFFS and opp_abbr and "MATCHUP" in logs.columns and "GAME_DATE" in logs.columns:
        try:
            _opp_up = opp_abbr.upper()
            _dates  = pd.to_datetime(logs["GAME_DATE"], errors="coerce").reset_index(drop=True)
            _matchups = logs["MATCHUP"].astype(str).reset_index(drop=True)
            _pts_raw  = pd.to_numeric(logs["PTS"], errors="coerce").reset_index(drop=True)
            _today    = pd.Timestamp.now().normalize()
            _weights  = []
            for _i in range(len(_pts_raw)):
                _w = 1.0
                if pd.notna(_dates[_i]) and _opp_up in _matchups[_i].upper():
                    _playoff_start = pd.Timestamp("2026-04-14").normalize()
                    if _dates[_i].normalize() >= _playoff_start:
                        _w = 3.0
                _weights.append(_w)
            _total_w = sum(_weights)
            _weighted_avg_pts = sum(
                float(_pts_raw[_i]) * _weights[_i]
                for _i in range(len(_pts_raw))
                if pd.notna(_pts_raw[_i])
            ) / _total_w if _total_w > 0 else sample_avg_pts
            line_diff = _weighted_avg_pts - line
        except Exception:
            line_diff = sample_avg_pts - line
    else:
        line_diff = sample_avg_pts - line
    tier      = get_confidence_tier(adjusted, line_diff, consistency, side)

    # ── Playoff usage spike banner ───────────────────────────────────────
    if _IS_PLAYOFFS and _pu_spike_sig != "Neutral" and _po_avg_pts is not None:
        _pu_color = "#22c55e" if _pu_spike_sig == "Spike" else "#ef4444"
        _pu_bg    = "#052e16" if _pu_spike_sig == "Spike" else "#1c0505"
        _pu_bdr   = "#166534" if _pu_spike_sig == "Spike" else "#991b1b"
        _pu_arrow = "📈" if _pu_spike_sig == "Spike" else "📉"
        _pu_verb  = "elevated" if _pu_spike_sig == "Spike" else "down"
        _pu_min_str = f" · {_po_avg_min:.0f} min/game playoffs" if _po_avg_min else ""
        st.markdown(
            f"<div style='background:{_pu_bg};border:1px solid {_pu_bdr};border-left:4px solid {_pu_color};"
            f"padding:0.65rem 1rem;margin-bottom:0.5rem;font-family:JetBrains Mono,monospace;font-size:0.7rem;'>"
            f"<span style='color:{_pu_color};font-weight:700;letter-spacing:0.08em;'>"
            f"{_pu_arrow} PLAYOFF USAGE {_pu_spike_sig.upper()}</span>"
            f"<span style='color:#94a3b8;'> · Averaging "
            f"<span style='color:{_pu_color};font-weight:700;'>{_po_avg_pts:.1f} pts</span>"
            f" in playoffs vs <span style='color:#f1f5f9;'>{sample_avg_pts:.1f}</span> reg season avg"
            f"{_pu_min_str}</span></div>",
            unsafe_allow_html=True
        )

    # ── Game number banner ────────────────────────────────────────────────
    if _IS_PLAYOFFS and _gnum and _game_num_label != "N/A" and _gnum in (1, 6, 7):
        _gn_notes = {
            1: "Teams feeling out — conservative scoring expected",
            6: "Elimination pressure — tighter defense, lower scoring",
            7: "Winner-take-all — max pressure, historically lower scoring",
        }
        st.markdown(
            f"<div style='background:#111;border:1px solid #1e2a3a;border-left:4px solid #f97316;"
            f"padding:0.55rem 1rem;margin-bottom:0.5rem;font-family:JetBrains Mono,monospace;font-size:0.68rem;'>"
            f"<span style='color:#f97316;font-weight:700;'>⚠️ GAME {_gnum} OF SERIES</span>"
            f"<span style='color:#475569;'> · {_gn_notes.get(_gnum, '')}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    # ── Series coverage banner ────────────────────────────────────
    if _IS_PLAYOFFS and _series_cov_sig != "Neutral" and _series_cov_n >= 1 and _series_cov_avg is not None:
        _sc_color  = "#22c55e" if _series_cov_sig == "Strong" else "#ef4444"
        _sc_bg     = "#052e16" if _series_cov_sig == "Strong" else "#1c0505"
        _sc_border = "#166534" if _series_cov_sig == "Strong" else "#991b1b"
        _sc_verb   = "outperforming" if _series_cov_sig == "Strong" else "under-performing"
        _sc_bench  = f"{season_avg:.1f} season avg" if season_avg else f"line ({line})"
        st.markdown(
            f"<div style='background:{_sc_bg};border:1px solid {_sc_border};border-left:4px solid {_sc_color};"
            f"padding:0.65rem 1rem;margin-bottom:0.75rem;font-family:JetBrains Mono,monospace;font-size:0.7rem;'>"
            f"<span style='color:{_sc_color};font-weight:700;letter-spacing:0.08em;'>📊 SERIES COVERAGE</span>"
            f"<span style='color:#94a3b8;'> · {_series_cov_n} game{'s' if _series_cov_n!=1 else ''} "
            f"vs {opp_abbr} in this series — averaging </span>"
            f"<span style='color:{_sc_color};font-weight:700;'>{_series_cov_avg:.1f} pts</span>"
            f"<span style='color:#94a3b8;'> · {_sc_verb} vs {_sc_bench}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    # Also compute the opposite side — if it's stronger, flag it
    _opp_side    = "Under" if side == "Over" else "Over"
    _opp_wb      = weighted_hit_rate(logs, line, _opp_side, opp_abbr=opp_abbr if _IS_PLAYOFFS else None)
    _opp_ctx     = dict(context)
    _opp_adj     = apply_adjustments(_opp_wb, _opp_ctx, _opp_side)
    _opp_tier    = get_confidence_tier(_opp_adj, line_diff, consistency, _opp_side)
    _opp_strong  = _opp_tier in ("Strong Over", "Strong Under")
    _selected_pass = tier == "Pass"

    # Auto-flip: if the opposite side has a stronger verdict, show that instead
    _auto_flipped = False
    if _opp_strong and (_selected_pass or "Lean" in tier):
        _display_tier = _opp_tier
        _display_adj  = _opp_adj
        _display_side = _opp_side
        _auto_flipped = True
    else:
        _display_tier = tier
        _display_adj  = adjusted
        _display_side = side

    tier_css   = {"Strong Over": "green", "Lean Over": "yellow", "Lean Under": "orange", "Strong Under": "red", "Pass": "gray"}
    tier_emoji = {"Strong Over": "🟢", "Lean Over": "🟡", "Lean Under": "🟠", "Strong Under": "🔴", "Pass": "⚪"}
    css = tier_css[_display_tier]

    # ── Verdict banner ────────────────────────
    st.markdown("<div class='section-header'>Verdict</div>", unsafe_allow_html=True)

    # Compute confidence score for player prop (same formula as scanner)
    _score_adj  = max(0, min((adjusted - 0.50) / 0.45, 1.0) * 65)
    _score_edge = min(abs(line_diff) / 7.0, 1.0) * 25
    _score_cons = consistency * 10
    _conf_score = min(99, int(_score_adj + _score_edge + _score_cons))

    # Plain language summary — for casual users
    _plain_map = {
        "Strong Over":  ("✅ Strong Over — the model backs this pick", "#10f590", "#041a0e"),
        "Lean Over":    ("👍 Lean Over — slight edge, good in 2-leg entries", "#fbbf24", "#1a1200"),
        "Lean Under":   ("👍 Lean Under — slight edge, good in 2-leg entries", "#f97316", "#1a0d00"),
        "Strong Under": ("✅ Strong Under — the model backs this pick", "#ff4560", "#1a0008"),
        "Pass":         ("⛔ Pass — no clear edge on this prop, skip it", "#475569", "#0d1520"),
    }
    _pm = _plain_map.get(_display_tier, ("", "#475569", "#0d1520"))
    st.markdown(
        f"<div style='background:{_pm[2]};border:1px solid rgba(255,255,255,0.06);"
        f"border-radius:12px;padding:0.75rem 1.1rem;margin-bottom:0.75rem;"
        f"display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;'>"
        f"<span style='font-family:Outfit,sans-serif;font-size:0.95rem;"
        f"font-weight:600;color:{_pm[1]};'>{_pm[0]}</span>"
        f"<span style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#475569;'>"
        f"Confidence {_conf_score}/100 · Adjusted {adjusted:.0%}</span>"
        f"</div>",
        unsafe_allow_html=True
    )


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

    # ── Injury + minutes signals for verdict banner ──────────────
    _verdict_signals = []

    # Usage spike signal — now available since spike runs before verdict
    if _spike_players:
        _spike_names = " · ".join(p["name"].split()[-1] for p in _spike_players[:2])
        _total_spike_mins = sum(p["minutes"] * 0.4 for p in _spike_players)
        _verdict_signals.append(
            f"<span style='font-family:DM Mono;font-size:0.68rem;font-weight:700;"
            f"color:#22c55e;background:#0c1a0c;"
            f"border:1px solid #166534;padding:3px 10px;border-radius:999px;"
            f"display:inline-flex;align-items:center;gap:4px;'>"
            f"📈 Usage ↑ · {_spike_names} out"
            f"<span style='color:#475569;font-weight:400;'>"
            f" +{_total_spike_mins:.0f} min</span></span>"
        )

    # Injury status signal
    if _inj_status not in ("Active", "Unknown", ""):
        _inj_up = _inj_status.upper()
        if "OUT" in _inj_up or "DOUBTFUL" in _inj_up:
            _sig_color = "#ef4444"
            _sig_bg    = "#1c050588"
            _sig_icon  = "🚫"
        elif "QUESTIONABLE" in _inj_up:
            _sig_color = "#f97316"
            _sig_bg    = "#1c100588"
            _sig_icon  = "⚠️"
        else:  # Probable
            _sig_color = "#86efac"
            _sig_bg    = "#0c1a0c88"
            _sig_icon  = "🟡"
        _reason_short = _inj_reason.replace("Injury/Illness - ", "").replace("Injury/Illness -", "").strip()
        _reason_part  = f" · {_reason_short}" if _reason_short else ""
        _verdict_signals.append(
            f"<span style='font-family:DM Mono;font-size:0.68rem;font-weight:700;"
            f"color:{_sig_color};background:{_sig_bg};"
            f"border:1px solid {_sig_color}44;padding:3px 10px;border-radius:999px;"
            f"display:inline-flex;align-items:center;gap:4px;'>"
            f"{_sig_icon} {_inj_status}{_reason_part}</span>"
        )

    # Minutes restriction signal
    if _min_alert_html:
        _last3_avg = sum(_last3_mins) / len(_last3_mins) if _last3_mins else avg_min
        _min_drop  = season_avg_min - _last3_avg if season_avg_min else 0
        if _min_drop >= 7:
            _min_sig_color = "#f97316"
            _min_sig_icon  = "⚠️"
        else:
            _min_sig_color = "#60a5fa"
            _min_sig_icon  = "📉"
        _verdict_signals.append(
            f"<span style='font-family:DM Mono;font-size:0.68rem;font-weight:700;"
            f"color:{_min_sig_color};background:{_min_sig_color}18;"
            f"border:1px solid {_min_sig_color}44;padding:3px 10px;border-radius:999px;"
            f"display:inline-flex;align-items:center;gap:4px;'>"
            f"{_min_sig_icon} Minutes ↓ {_last3_avg:.0f} vs {season_avg_min:.0f} avg</span>"
        )

    _signals_html = (
        f"<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;'>"
        + "".join(_verdict_signals)
        + "</div>"
    ) if _verdict_signals else ""

    # ── Confidence depth within tier ─────────────────────────────
    # How far into the tier are we? Gives "strong lean" vs "weak lean" etc.
    if _display_tier == "Strong Over":
        # 64% - 100% range → how far above 64%?
        _conf_pct  = min(1.0, (_display_adj - 0.64) / 0.36)
        _conf_label = "Deep Strong" if _conf_pct >= 0.5 else "Strong"
        _bar_color  = "#22c55e"
    elif _display_tier == "Lean Over":
        # 55% - 64% range
        _conf_pct  = (_display_adj - 0.55) / 0.09
        _conf_label = "High Lean" if _conf_pct >= 0.5 else "Low Lean"
        _bar_color  = "#eab308"
    elif _display_tier == "Strong Under":
        # 64% - 100% range (same logic, high = more confident)
        _conf_pct  = min(1.0, (_display_adj - 0.64) / 0.36)
        _conf_label = "Deep Strong" if _conf_pct >= 0.5 else "Strong"
        _bar_color  = "#ef4444"
    elif _display_tier == "Lean Under":
        _conf_pct  = (_display_adj - 0.55) / 0.09
        _conf_label = "High Lean" if _conf_pct >= 0.5 else "Low Lean"
        _bar_color  = "#f97316"
    else:  # Pass
        _conf_pct  = 0.0
        _conf_label = "No edge"
        _bar_color  = "#475569"

    # Edge strength label
    _abs_edge = abs(line_diff)
    if _abs_edge >= 5.0:
        _edge_label = "Large edge"
        _edge_color = "#22c55e"
    elif _abs_edge >= 2.5:
        _edge_label = "Solid edge"
        _edge_color = "#86efac"
    elif _abs_edge >= 1.5:
        _edge_label = "Moderate edge"
        _edge_color = "#eab308"
    elif _abs_edge >= 0.5:
        _edge_label = "Small edge"
        _edge_color = "#f97316"
    else:
        _edge_label = "Razor thin"
        _edge_color = "#ef4444"

    # Confidence bar fill width (out of 100%)
    _bar_w = max(4, int(_conf_pct * 100))

    # Pre-compute all string values to avoid complex nested f-strings
    _flip_note_html = (
        "<div style='font-family:DM Mono;font-size:0.65rem;color:#854d0e;"
        "background:#1c1005;border:1px solid #854d0e;border-radius:6px;"
        "padding:3px 10px;display:inline-block;margin-top:6px;'>"
        f"You selected {side} — data favors the {_display_side}</div>"
    ) if _auto_flipped else ""

    _edge_num_color = "#22c55e" if line_diff > 0 else "#ef4444"
    _edge_diff_str  = f"{line_diff:+.1f}"
    _inj_verdict_note = (
        f" · ⚠️ {_inj_status} ({_inj_reason.replace('Injury/Illness - ','').strip()})"
        if _inj_html else ""
    )
    _adj_pct_str    = f"{_display_adj:.0%}"
    _cons_pct_str   = f"{consistency:.0%}"
    if consistency >= 0.5:
        _cons_word = "Predictable"
    elif consistency >= 0.35:
        _cons_word = "Variable"
    elif consistency >= 0.20:
        _cons_word = "Volatile"
    else:
        _cons_word = "⚠️ Extremely Volatile"
    _bar_style      = f"background:{_bar_color};height:6px;width:{_bar_w}%;border-radius:999px;box-shadow:0 0 6px {_bar_color}55;"

    # Ruler pip position: adjusted % mapped to 0-100 scale
    # For Under bets, mirror the position — high adjusted% means strong Under (left side)
    # Ruler pip: always map to the 5-zone scale regardless of side
    # Zones: Strong Under(0-36%) | Lean Under(36-45%) | Pass(45-55%) | Lean Over(55-64%) | Strong Over(64-100%)
    # For Over: high adjusted % → right side (Strong Over zone)
    # For Under: high adjusted % → left side (Strong Under zone), so mirror
    # BUT: if verdict is Pass, pip should sit in the middle (45-55%) regardless
    if _display_tier == "Pass":
        _pip = 50  # always center for Pass
    elif _display_side == "Under":
        # Mirror: 100% adjusted Under → pip at 0% (Strong Under left)
        # 64% adjusted Under → pip at 36% (boundary of Strong Under)
        # 55% adjusted Under → pip at 45% (boundary of Lean Under)
        _pip = max(2, min(44, int((1.0 - _display_adj) * 100)))
    else:
        # Over: 64% → 64%, 100% → 100%
        _pip = max(56, min(98, int(_display_adj * 100))) if _display_adj >= 0.55 else max(2, min(98, int(_display_adj * 100)))
    _pip_style = (
        f"position:absolute;top:1px;left:{_pip}%;"
        f"transform:translateX(-50%);"
        f"width:14px;height:14px;border-radius:50%;"
        f"background:{_bar_color};"
        f"box-shadow:0 0 8px {_bar_color},0 0 16px {_bar_color}88;"
        f"border:2px solid #0c1018;"
        f"z-index:2;"
    )
    _fill_style = (
        f"position:absolute;top:7px;left:0;"
        f"width:{_pip}%;height:4px;"
        f"background:linear-gradient(90deg,{_bar_color}44,{_bar_color});"
        f"border-radius:2px;"
    )

    # Pre-compute zone label opacity/weight for ruler
    _su_op = "1"   if _display_tier == "Strong Under" else "0.4"
    _lu_op = "1"   if _display_tier == "Lean Under"   else "0.4"
    _pa_op = "1"   if _display_tier == "Pass"         else "0.4"
    _lo_op = "1"   if _display_tier == "Lean Over"    else "0.4"
    _so_op = "1"   if _display_tier == "Strong Over"  else "0.4"
    _su_fw = "800" if _display_tier == "Strong Under" else "400"
    _lu_fw = "800" if _display_tier == "Lean Under"   else "400"
    _pa_fw = "800" if _display_tier == "Pass"         else "400"
    _lo_fw = "800" if _display_tier == "Lean Over"    else "400"
    _so_fw = "800" if _display_tier == "Strong Over"  else "400"

    _verdict_html = (
        f"<div class='verdict-banner {css}'>"
        f"<div style='flex:1;min-width:200px;'>"
        f"<div class='verdict-label'>{full_name} · {line} pts · {_display_side}</div>"
        f"<div class='verdict-tier {css}'>{tier_emoji[_display_tier]} {_display_tier}</div>"
        f"<div style='margin-top:14px;margin-bottom:4px;padding-right:4px;'>"
        f"<div style='position:relative;height:18px;'>"
        f"<div style='position:absolute;top:7px;left:0;right:0;height:4px;background:#1e293b;border-radius:2px;'></div>"
        f"<div style='position:absolute;top:7px;left:0;width:36%;height:4px;background:#ef444422;border-radius:2px 0 0 2px;'></div>"
        f"<div style='position:absolute;top:7px;left:36%;width:9%;height:4px;background:#f9731622;'></div>"
        f"<div style='position:absolute;top:7px;left:45%;width:10%;height:4px;background:#47556933;'></div>"
        f"<div style='position:absolute;top:7px;left:55%;width:9%;height:4px;background:#eab30822;'></div>"
        f"<div style='position:absolute;top:7px;left:64%;width:36%;height:4px;background:#22c55e22;border-radius:0 2px 2px 0;'></div>"
        f"<div style='{_fill_style}'></div>"
        f"<div style='position:absolute;top:2px;left:36%;width:2px;height:14px;background:#ef4444;border-radius:1px;opacity:0.5;'></div>"
        f"<div style='position:absolute;top:2px;left:45%;width:2px;height:14px;background:#64748b;border-radius:1px;opacity:0.7;'></div>"
        f"<div style='position:absolute;top:2px;left:55%;width:2px;height:14px;background:#64748b;border-radius:1px;opacity:0.7;'></div>"
        f"<div style='position:absolute;top:2px;left:64%;width:2px;height:14px;background:#22c55e;border-radius:1px;opacity:0.5;'></div>"
        f"<div style='{_pip_style}'></div>"
        f"</div>"
        f"<div style='position:relative;height:22px;margin-top:5px;font-family:DM Mono;'>"
        f"<span style='position:absolute;left:18%;transform:translateX(-50%);font-size:0.48rem;color:#ef4444;opacity:{_su_op};font-weight:{_su_fw};text-align:center;line-height:1.3;'>Strong<br>Under</span>"
        f"<span style='position:absolute;left:40.5%;transform:translateX(-50%);font-size:0.48rem;color:#f97316;opacity:{_lu_op};font-weight:{_lu_fw};text-align:center;line-height:1.3;'>Lean<br>Under</span>"
        f"<span style='position:absolute;left:50%;transform:translateX(-50%);font-size:0.48rem;color:#64748b;opacity:{_pa_op};font-weight:{_pa_fw};text-align:center;line-height:1.3;'>Pass</span>"
        f"<span style='position:absolute;left:59.5%;transform:translateX(-50%);font-size:0.48rem;color:#eab308;opacity:{_lo_op};font-weight:{_lo_fw};text-align:center;line-height:1.3;'>Lean<br>Over</span>"
        f"<span style='position:absolute;left:82%;transform:translateX(-50%);font-size:0.48rem;color:#22c55e;opacity:{_so_op};font-weight:{_so_fw};text-align:center;line-height:1.3;'>Strong<br>Over</span>"
        f"</div>"
        f"<div style='height:0.4rem;'></div>"
        f"</div>"
        f"{_flip_note_html}"
        f"{_signals_html}"
        f"<div style='margin-top:6px;'>{venue_badge_html}</div>"
        f"</div>"
        f"<div style='display:flex;gap:2rem;flex-wrap:wrap;align-items:flex-start;'>"
        f"<div>"
        f"<div class='verdict-label'>Adjusted Hit Rate <span style='font-size:0.55rem;background:#1e293b;color:#64748b;border-radius:50%;padding:1px 4px;margin-left:3px;cursor:default;' title='% of recent games hitting the line, adjusted for context signals'>i</span></div>"
        f"<div style='font-size:1.4rem;font-weight:800;color:#f1f5f9;'>{_adj_pct_str}</div>"
        f"<div style='font-family:DM Mono;font-size:0.65rem;color:#475569;margin-top:2px;'>64%+ = Strong · 55%+ = Lean</div>"
        f"</div>"
        f"<div>"
        f"<div class='verdict-label'>Edge vs Line <span style='font-size:0.55rem;background:#1e293b;color:#64748b;border-radius:50%;padding:1px 4px;margin-left:3px;cursor:default;' title='Player avg pts minus the line. Larger = more confident the line is beatable'>i</span></div>"
        f"<div style='font-size:1.4rem;font-weight:800;color:{_edge_num_color};'>{_edge_diff_str}</div>"
        f"<div style='font-family:DM Mono;font-size:0.65rem;color:{_edge_color};margin-top:2px;'>{_edge_label}</div>"
        f"</div>"
        f"<div>"
        f"<div class='verdict-label'>Consistency <span style='font-size:0.55rem;background:#1e293b;color:#64748b;border-radius:50%;padding:1px 4px;margin-left:3px;cursor:default;' title='% of games pts landed within 3 of the line. Low = unpredictable scorer'>i</span></div>"
        f"<div style='font-size:1.4rem;font-weight:800;color:#f1f5f9;'>{_cons_pct_str}</div>"
        f"<div style='font-family:DM Mono;font-size:0.65rem;color:#475569;margin-top:2px;'>{_cons_word}</div>"
        f"</div>"
        f"</div>"
        f"</div>"
    )
    st.markdown(_verdict_html, unsafe_allow_html=True)

    # ── Playoff picture — right under verdict ─────────────────────
    # Debug: always show something so we can confirm display works
    _pl_status = _playoff.get("status", "") if _playoff else ""
    _pl_label  = _playoff.get("label",  "") if _playoff else ""
    _pl_color  = _playoff.get("color",  "#555555") if _playoff else "#555555"
    _pl_w      = _playoff.get("wins",   0) if _playoff else 0
    _pl_l      = _playoff.get("losses", 0) if _playoff else 0
    _load_mgmt_risk = _pl_status in ("locked", "eliminated")
    _load_note = "" if _IS_PLAYOFFS else ("  ·  ⚠️ Load management risk" if _load_mgmt_risk else "")

    # Show if we have data OR show a debug fallback
    _pl_display_label = _pl_label if _pl_label else f"standings unavailable · {player_team or '?'}"
    _pl_display_color = _pl_color if _pl_label else "#333"

    st.markdown(
        f"<div style='background:#111;border:1px solid #2a2a2a;"
        f"border-left:3px solid {_pl_display_color};"
        f"padding:0.55rem 1rem;margin-top:-0.5rem;margin-bottom:0.5rem;"
        f"display:flex;align-items:center;justify-content:space-between;'>"
        f"<div style='display:flex;align-items:center;gap:10px;'>"
        f"<div style='font-family:JetBrains Mono,monospace;font-size:0.55rem;"
        f"color:#555;letter-spacing:0.15em;'>PLAYOFF PICTURE</div>"
        f"<div style='font-family:Barlow Condensed,sans-serif;font-size:0.95rem;"
        f"font-weight:700;color:{_pl_display_color};'>{_pl_display_label}</div>"
        f"</div>"
        f"<div style='font-family:JetBrains Mono,monospace;font-size:0.58rem;"
        f"color:#555;'>{f'{_pl_w}W–{_pl_l}L' if _pl_w else ''}{_load_note}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── How to read this verdict ──────────────────────────────────
    with st.expander("💡  How to read this verdict"):
        _hr_pct  = f"{adjusted:.0%}"
        _edge_abs = abs(line_diff)
        _edge_dir = "below" if line_diff < 0 else "above"
        _side_word = "Under" if "Under" in tier else "Over"
        _cons_word_tip = (
            "very predictable — you can trust this signal"
            if consistency >= 0.5 else
            "somewhat variable — treat with moderate confidence"
            if consistency >= 0.35 else
            "volatile — player can go way above or below any night"
            if consistency >= 0.20 else
            "extremely volatile — even a strong signal can blow up"
        )
        st.markdown(f"""
        <div style='font-family:DM Mono; font-size:0.75rem; line-height:1.9;
                    color:#94a3b8; padding:0.25rem 0;'>

        <div style='margin-bottom:0.6rem;'>
        <span style='color:#f1f5f9; font-weight:700;'>Adjusted Hit Rate ({_hr_pct})</span><br>
        In roughly <span style='color:#f97316; font-weight:700;'>{round(adjusted*10):.0f} out of 10</span> recent games
        with similar conditions, {full_name.split()[0]} scored
        {'<span style="color:#22c55e;font-weight:700;">under</span>' if _side_word=="Under" else '<span style="color:#22c55e;font-weight:700;">over</span>'}
        {line} pts. This is the core verdict.
        </div>

        <div style='margin-bottom:0.6rem;'>
        <span style='color:#f1f5f9; font-weight:700;'>Edge vs Line ({line_diff:+.1f})</span><br>
        His scoring average is <span style='color:#f97316; font-weight:700;'>{_edge_abs:.1f} pts {_edge_dir}</span>
        the line. A large edge means the hit rate is comfortable — not just squeaking by.
        </div>

        <div>
        <span style='color:#f1f5f9; font-weight:700;'>Consistency ({consistency:.0%})</span><br>
        His scoring is <span style='color:#f97316; font-weight:700;'>{_cons_word_tip}</span>.
        Use this to size your bet — high consistency = bet confidently,
        low consistency = bet smaller or skip.
        </div>

        </div>
        """, unsafe_allow_html=True)

    with st.expander("🔬  Show full signal breakdown (advanced)"):
        st.markdown("""
        <div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#475569;
                    background:#0d1520;border:1px solid rgba(255,255,255,0.06);border-radius:8px;
                    padding:0.65rem 1rem;margin-bottom:0.75rem;line-height:1.8;'>
            This table shows exactly how PropLens arrived at the final probability.
            Each row is a signal that pushed the number up or down.
            <span style='color:#3b82f6;'>Positive adjustments</span> favor the Over.
            <span style='color:#ef4444;'>Negative adjustments</span> favor the Under.
            The final result is capped to prevent any single signal from dominating.
        </div>
        """, unsafe_allow_html=True)

        # ── Step-by-step adjustment trace ────────────────────────────
        multipliers_map = {
            "minutes":  {"Strong": +0.05, "Okay": 0.00, "Risk": -0.07},
            "elim_game":  {"Elimination": +0.04, "Closeout": +0.02, "Normal": 0.00},
            "series_cov": {"Strong": +0.07, "Neutral": 0.00, "Risk": -0.08},
            "ref":        {"High FT": +0.04, "Neutral": 0.00, "Low FT": -0.04},
            "game_num":   {"N/A": 0.00, "Game 1 (feeling out)": -0.03,
                           "Game 2 (normal)": 0.00, "Game 3 (normal)": 0.00,
                           "Game 4 (normal)": 0.00, "Game 5 (normal)": 0.00,
                           "Game 6 (pressure)": -0.02, "Game 7 (max pressure)": -0.03},
            "pu_spike":   {"Spike": +0.05, "Neutral": 0.00, "Drop": -0.05},
            "shot_vol":   {"Star": +0.04, "Neutral": 0.00, "Risk": -0.05},
            "role":     {"Strong": +0.04, "Okay": 0.00, "Risk": -0.05},
            "shots":    {"High":   +0.03, "Medium": 0.00, "Low": -0.06},
            "matchup":  {"Good":   +0.06, "Neutral": 0.00, "Bad": -0.06},
            "script":   {"Competitive": +0.02, "Neutral": 0.00, "Blowout risk": -0.04},
            "venue":    {"Boost": +0.04, "Neutral": 0.00, "Penalty": -0.05},
            "h2h":      {"Strong": +0.09 if _IS_PLAYOFFS else +0.05,
                       "Neutral": 0.00,
                       "Risk":   -0.10 if _IS_PLAYOFFS else -0.06},
            "b2b":      {"Normal": 0.00, "B2B": -0.06},
            "rest":     {"Rested": +0.03, "Normal": 0.00, "Short": -0.02, "B2B": -0.06},
            "form":     {"Boost": +0.05, "Neutral": 0.00, "Penalty": -0.05},
            "pace":     {"Boost": +0.04, "Neutral": 0.00, "Penalty": -0.04},
            "shoot":    {"Boost": +0.05, "Neutral": 0.00, "Penalty": -0.05},
        }
        signal_labels = {
            "minutes":   "Minutes load",
            "role":      "Role/usage",
            "shots":     "Shot volume",
            "matchup":   "Opponent defense",
            "script":    "Game script",
            "venue":     "Home/Away split",
            "h2h":       "H2H vs opponent",
            "b2b":       "Back-to-back rest",
            "rest":      "Rest days",
            "form":      "Recent form vs season",
            "pace":      "Game pace",
            "shoot":     "Recent shooting",
            "elim_game":  "Playoff game type",
            "series_cov": "This series coverage",
            "ref":        "Referee tendency",
            "game_num":   "Series game number",
            "pu_spike":   "Playoff usage vs reg season",
            "shot_vol":   "Playoff shot volume",
        }

        # Simulate the computation step by step (additive, side-aware)
        # NOTE: real apply_adjustments accumulates without per-step clipping,
        # then clips once at the end — we mirror that here for accuracy
        _flip   = -1.0 if side == "Under" else 1.0
        running = weighted_base
        steps   = []
        for key, val in context.items():
            adj    = multipliers_map[key].get(val, 0.0) * _flip
            before = running
            running = running + adj   # no per-step clip — matches real function
            after_raw = running
            after  = max(0.0, min(1.0, after_raw))  # show display-clamped value
            delta  = max(0.0, min(1.0, after_raw)) - max(0.0, min(1.0, before))
            steps.append((key, val, adj, max(0.0, min(1.0, before)), after, delta))

        # Consistency override check
        extremely_volatile = consistency < 0.20
        edge_is_tight      = abs(line_diff) < 3.0
        hit_rate_dominant  = adjusted >= 0.65
        low_cons = extremely_volatile or (consistency < 0.35 and edge_is_tight and not hit_rate_dominant)
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
                <td style='color:#e2e8f0;'>{weighted_base:.1%} ← starting point{"  (playoff series boost applied)" if _IS_PLAYOFFS and opp_abbr and _series_cov_n > 0 else ""}</td>
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
        if consistency < 0.20 and override_relevant:
            cons_note = f"Consistency {consistency:.0%} < 20% · Extremely volatile → downgrade always applied"
        elif low_cons and override_relevant:
            cons_note = f"Consistency {consistency:.0%} < 35% · Edge {line_diff:+.1f} < 3pts → downgrade applied"
        elif consistency < 0.35 and hit_rate_dominant:
            cons_note = f"Consistency {consistency:.0%} < 35% but hit rate {adjusted:.0%} ≥ 65% → override skipped (dominates line)"
        elif consistency < 0.35 and not edge_is_tight:
            cons_note = f"Consistency {consistency:.0%} < 35% but edge {line_diff:+.1f} ≥ 3pts → override skipped"
        else:
            cons_note = f"Consistency {consistency:.0%} · No override needed"

        # Side-aware threshold labels and edge check for debugger
        if side == "Over":
            _strong_label = "Strong Over"
            _lean_label   = "Lean Over"
            _strong_thresh = "≥ 64% AND edge ≥ +1.5"
            _lean_thresh   = "≥ 55% AND edge > 0"
            _edge_ok = line_diff >= 1.5
        else:
            _strong_label = "Strong Under"
            _lean_label   = "Lean Under"
            _strong_thresh = "≥ 64% AND edge ≤ -1.5"
            _lean_thresh   = "≥ 55% AND edge < 0"
            _edge_ok = line_diff <= -1.5

        st.markdown(f"""
        <div style='color:#f97316; font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase;
                    border-bottom:1px solid #1a2333; padding-bottom:4px; margin:14px 0 10px 0;'>
            FINAL DECISION
        </div>
        <table style='width:100%; border-collapse:collapse; font-family:DM Mono; font-size:0.72rem;'>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Adjusted probability</td>
                <td style='color:#e2e8f0; font-weight:700;'>{adjusted:.1%}</td>
                <td style='padding:3px 8px; color:#475569;'>Threshold for {_strong_label}</td>
                <td style='color:#94a3b8;'>{_strong_thresh}</td>
            </tr>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Edge vs line</td>
                <td style='color:{"#22c55e" if _edge_ok else "#ef4444"};'>{line_diff:+.1f} pts {"✓" if abs(line_diff)>=1.5 else "✗ too small"}</td>
                <td style='padding:3px 8px; color:#475569;'>Threshold for {_lean_label}</td>
                <td style='color:#94a3b8;'>{_lean_thresh}</td>
            </tr>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Consistency check</td>
                <td colspan='3' style='color:{"#ef4444" if low_cons else "#475569"};'>{cons_note}</td>
            </tr>
            <tr>
                <td style='padding:3px 8px 3px 0; color:#475569;'>Signal cap</td>
                <td colspan='3' style='color:#475569;'>{"±18pp · playoff mode" if _IS_PLAYOFFS else "±12pp · regular season"}</td>
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



    # ── Share + Add to Tracker ───────────────
    _share_col, _tracker_col = st.columns(2)

    with _share_col:
        # Build share text
        _tier_emoji = {
            "Strong Over":  "🟢", "Lean Over":   "🟡",
            "Strong Under": "🔴", "Lean Under":  "🟠", "Pass": "⚪"
        }.get(tier, "⚪")
        _opp_str    = f"vs {opp_abbr}" if opp_abbr else ""
        _venue_str  = f"({tonight_venue})" if tonight_venue else ""
        # Playoff line — use already-fetched data
        _playoff_str = ""
        if _playoff and _playoff.get("label"):
            _share_pl_label = _playoff.get("label", "")
            _share_pl_risk  = _playoff.get("status", "") in ("locked", "eliminated")
            _playoff_str = f"\n{_share_pl_label}" + (" · ⚠️ Load mgmt risk" if _share_pl_risk else "")
        _blowout_str = f"\n🚫 {_blowout_count} blowout game{'s' if _blowout_count > 1 else ''} excluded" if _blowout_count > 0 else ""

        _share_text = (
            f"{_tier_emoji} {tier.upper()} — {full_name}\n"
            f"📊 {line} pts {side} {_opp_str} {_venue_str}\n"
            f"Hit Rate: {adjusted:.0%} · Edge: {line_diff:+.1f} · Consistency: {consistency:.0%}"
            f"{_blowout_str}"
            f"{_playoff_str}\n"
            f"🏀 PropLens v4.0"
        ).strip()

        # Display share box with copy instruction
        if st.button("📤  Share Pick", use_container_width=True):
            st.session_state.show_share = True

        if st.session_state.get("show_share"):
            st.markdown(
                "<div style='font-family:JetBrains Mono,monospace;font-size:0.55rem;"
                "color:#555;letter-spacing:0.15em;margin:0.5rem 0 0.25rem 0;'>"
                "TAP TO COPY ↓</div>",
                unsafe_allow_html=True
            )
            st.code(_share_text, language=None)

    with _tracker_col:
        if st.button("➕  Add to Prop Tracker", use_container_width=True):
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
                        "Result":      "Pending",
                    }
                    existing = [i for i, e in enumerate(st.session_state.tracker)
                                if e["Player"] == full_name and e["Line"] == f"{line} {side}"]
                    if existing:
                        # Update existing entry
                        old_id = st.session_state.tracker[existing[0]].get("id")
                        entry["id"] = old_id
                        st.session_state.tracker[existing[0]] = entry
                        if old_id:
                            delete_from_supabase(old_id)
                        new_id = save_to_supabase(st.session_state.session_id, entry)
                        if new_id:
                            st.session_state.tracker[existing[0]]["id"] = new_id
                        st.success(f"Updated {full_name} in tracker.")
                    else:
                        # Save to Supabase and store returned ID
                        new_id = save_to_supabase(st.session_state.session_id, entry)
                        if new_id:
                            entry["id"] = new_id
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

    # Auto-detect results for pending picks in background
    _auto_updated = False
    for _i, _e in enumerate(st.session_state.tracker):
        if _e.get("Result", "Pending") == "Pending":
            _detected = auto_detect_result(_e)
            if _detected:
                st.session_state.tracker[_i]["Result"]        = _detected
                st.session_state.tracker[_i]["auto_detected"] = True
                if _e.get("id"):
                    update_result_in_supabase(_e["id"], _detected)
                _auto_updated = True

    if _auto_updated:
        st.rerun()

    # Win rate summary
    _hits    = sum(1 for e in st.session_state.tracker if e.get("Result") == "Hit")
    _misses  = sum(1 for e in st.session_state.tracker if e.get("Result") == "Miss")
    _pending = sum(1 for e in st.session_state.tracker if e.get("Result", "Pending") == "Pending")
    _settled = _hits + _misses
    _wr      = f"{_hits/_settled:.0%}" if _settled > 0 else "—"
    _wr_color = "#22c55e" if _settled > 0 and _hits/_settled >= 0.6 else ("#ef4444" if _settled > 0 and _hits/_settled < 0.4 else "#eab308")

    st.markdown(
        f"<div style='display:flex;gap:1.5rem;flex-wrap:wrap;margin-bottom:0.75rem;"
        f"font-family:DM Mono;font-size:0.7rem;'>"
        f"<span style='color:{_wr_color};font-weight:800;'>Win Rate: {_wr}</span>"
        f"<span style='color:#22c55e;'>✅ {_hits} Hit</span>"
        f"<span style='color:#ef4444;'>❌ {_misses} Miss</span>"
        f"<span style='color:#475569;'>⏳ {_pending} Pending</span>"
        f"</div>",
        unsafe_allow_html=True
    )

    to_remove = None
    for i, entry in enumerate(st.session_state.tracker):
        t   = entry["Verdict"]
        css = tier_css.get(t, "gray")
        em  = tier_emoji.get(t, "⚪")
        col_card, col_remove = st.columns([11, 1])
        _result       = entry.get("Result", "Pending")
        _result_color = {"Hit": "#22c55e", "Miss": "#ef4444", "Pending": "#475569"}.get(_result, "#475569")
        _result_emoji = {"Hit": "✅", "Miss": "❌", "Pending": "⏳"}.get(_result, "⏳")
        _auto_tag     = "<span style='font-family:DM Mono;font-size:0.55rem;color:#475569;margin-left:6px;'>auto</span>" if entry.get("auto_detected") else ""

        with col_card:
            st.markdown(f"""
            <div class='verdict-banner {css}' style='margin:0.3rem 0; padding:1rem 1.4rem;'>
                <div>
                    <div class='verdict-label'>{entry["Line"]} · vs {entry["Opponent"]}</div>
                    <div style='font-size:1.1rem; font-weight:800; color:#f1f5f9;'>{entry["Player"]}</div>
                    <div style='font-family:DM Mono;font-size:0.7rem;color:{_result_color};margin-top:4px;'>
                        {_result_emoji} {_result}{_auto_tag}
                    </div>
                </div>
                <div style='display:flex; gap:1.5rem; flex-wrap:wrap; align-items:center;'>
                    <div><div class='verdict-label'>Verdict</div><div class='verdict-tier {css}' style='font-size:1rem;'>{em} {t}</div></div>
                    <div><div class='verdict-label'>Avg PTS</div><div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Avg PTS"]}</div></div>
                    <div><div class='verdict-label'>Adjusted</div><div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Adjusted"]}</div></div>
                    <div><div class='verdict-label'>Matchup</div><div style='font-size:1rem; font-weight:700; color:#f1f5f9;'>{entry["Matchup"]}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Result logging buttons
            _rc1, _rc2, _rc3 = st.columns(3)
            with _rc1:
                if st.button("✅ Hit", key=f"hit_{i}", use_container_width=True):
                    st.session_state.tracker[i]["Result"] = "Hit"
                    if entry.get("id"):
                        update_result_in_supabase(entry["id"], "Hit")
                    st.rerun()
            with _rc2:
                if st.button("❌ Miss", key=f"miss_{i}", use_container_width=True):
                    st.session_state.tracker[i]["Result"] = "Miss"
                    if entry.get("id"):
                        update_result_in_supabase(entry["id"], "Miss")
                    st.rerun()
            with _rc3:
                if st.button("⏳ Pending", key=f"pending_{i}", use_container_width=True):
                    st.session_state.tracker[i]["Result"] = "Pending"
                    if entry.get("id"):
                        update_result_in_supabase(entry["id"], "Pending")
                    st.rerun()

        with col_remove:
            st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
            if st.button("✕", key=f"remove_{i}", help="Remove"):
                to_remove = i
    if to_remove is not None:
        _removed = st.session_state.tracker.pop(to_remove)
        if _removed.get("id"):
            delete_from_supabase(_removed["id"])
        st.rerun()

    tc1, tc2 = st.columns([1, 1])
    with tc1:
        tracker_df  = pd.DataFrame(st.session_state.tracker)
    with tc2:
        if st.button("🗑️  Clear All"):
            _sb = get_supabase_client()
            if _sb:
                _sb.delete_all("prop_tracker", st.session_state.session_id)
            st.session_state.tracker = []
            st.rerun()



st.markdown("<div style='margin-top:3rem; font-family:DM Mono; font-size:0.65rem; color:#334155; text-align:center;'>PropLens — For educational purposes only. Not financial or betting advice.</div>", unsafe_allow_html=True)
