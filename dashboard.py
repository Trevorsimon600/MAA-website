import streamlit as st
import os
import json
import math
import time
import plotly.graph_objects as go
from datetime import datetime
from v0_2 import MAA

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="MAA Command Center",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# GLOBAL CSS — JARVIS COMMAND CENTER STYLE
# ============================================================
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;800&family=Rajdhani:wght@300;400;600;700&display=swap');

  /* ── Base ── */
  html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }
  .stApp {
    background: radial-gradient(ellipse at 20% 50%, #040d1e 0%, #020812 60%, #010610 100%);
    color: #a8c5da;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: rgba(4, 10, 28, 0.97) !important;
    border-right: 1px solid rgba(0,210,255,0.12) !important;
  }
  section[data-testid="stSidebar"] .stRadio label {
    color: #7ab8cc !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
    letter-spacing: 0.5px;
  }
  section[data-testid="stSidebar"] .stRadio label:hover {
    color: #00D9FF !important;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #010610; }
  ::-webkit-scrollbar-thumb { background: #0a2a40; border-radius: 10px; }

  /* ── TOP STATUS BAR ── */
  .top-bar {
    background: linear-gradient(90deg, rgba(0,210,255,0.06), rgba(124,58,237,0.06));
    border: 1px solid rgba(0,210,255,0.18);
    border-radius: 8px;
    padding: 10px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    backdrop-filter: blur(12px);
  }
  .top-bar-brand {
    font-family: 'JetBrains Mono', monospace;
    font-size: 17px;
    font-weight: 800;
    color: #00D9FF;
    letter-spacing: 3px;
    text-shadow: 0 0 16px rgba(0,217,255,0.5);
  }
  .top-bar-sub {
    font-size: 11px;
    color: #3a6a7a;
    letter-spacing: 4px;
    text-transform: uppercase;
    display: block;
    margin-top: 2px;
  }
  .top-bar-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    color: #c8dde8;
    letter-spacing: 2px;
  }
  .top-bar-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #22C55E;
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 20px;
    padding: 5px 14px;
    letter-spacing: 1px;
  }

  /* ── Glass Panel ── */
  .glass-panel {
    background: rgba(5,14,35,0.82);
    border: 1px solid rgba(0,210,255,0.13);
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 14px;
    backdrop-filter: blur(16px);
    box-shadow: 0 2px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(0,210,255,0.06);
    transition: border-color 0.3s;
  }
  .glass-panel:hover {
    border-color: rgba(0,210,255,0.28);
  }
  .panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    color: #00D9FF;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(0,210,255,0.1);
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .live-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #22C55E;
    display: inline-block;
    box-shadow: 0 0 8px #22C55E;
    animation: blink 1.4s infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

  /* ── HUD CORE ── */
  .hud-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10px 0 0;
  }
  .hud-svg-container {
    position: relative;
    width: 220px;
    height: 220px;
  }
  .hud-label-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%,-50%);
    text-align: center;
  }
  .hud-core-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    font-weight: 800;
    color: #00D9FF;
    letter-spacing: 3px;
    text-shadow: 0 0 16px rgba(0,217,255,0.7);
    display: block;
  }
  .hud-version-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #4a7a8a;
    letter-spacing: 2px;
    display: block;
    margin-top: 4px;
  }

  /* ── Agent Grid ── */
  .agent-card {
    background: rgba(5,14,35,0.9);
    border: 1px solid rgba(0,210,255,0.14);
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.25s;
  }
  .agent-card:hover {
    border-color: rgba(0,210,255,0.38);
    box-shadow: 0 0 12px rgba(0,210,255,0.08);
    transform: translateX(3px);
  }
  .agent-icon {
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }
  .agent-info { flex: 1; }
  .agent-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    color: #c8dde8;
    display: block;
  }
  .agent-role {
    font-size: 11px;
    color: #3a6070;
    display: block;
    margin-top: 1px;
  }
  .agent-status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22C55E;
    box-shadow: 0 0 6px #22C55E;
    flex-shrink: 0;
  }

  /* ── Metric Tile ── */
  .metric-tile {
    background: rgba(5,14,35,0.88);
    border: 1px solid rgba(0,210,255,0.13);
    border-radius: 8px;
    padding: 16px 18px;
    text-align: left;
    margin-bottom: 12px;
  }
  .metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: #00D9FF;
    display: block;
    text-shadow: 0 0 10px rgba(0,217,255,0.3);
  }
  .metric-lbl {
    font-size: 11px;
    color: #3a6070;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 3px;
    display: block;
  }

  /* ── Timeline / Feed Item ── */
  .feed-item {
    border-left: 2px solid rgba(0,210,255,0.2);
    padding: 6px 0 6px 14px;
    margin-bottom: 10px;
    position: relative;
  }
  .feed-item::before {
    content: '';
    position: absolute;
    left: -5px; top: 10px;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #00D9FF;
    box-shadow: 0 0 6px #00D9FF;
  }
  .feed-title { font-size: 13px; color: #a8c5da; font-weight: 600; }
  .feed-sub { font-size: 11px; color: #3a5a6a; margin-top: 2px; }
  .feed-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 10px;
    float: right;
    letter-spacing: 0.5px;
  }
  .badge-ok { background: rgba(34,197,94,0.12); color: #22C55E; border:1px solid rgba(34,197,94,0.2); }
  .badge-warn { background: rgba(245,158,11,0.12); color: #F59E0B; border:1px solid rgba(245,158,11,0.2); }
  .badge-info { background: rgba(0,210,255,0.1); color: #00D9FF; border:1px solid rgba(0,210,255,0.18); }

  /* ── Terminal ── */
  .terminal {
    background: #010814;
    border: 1px solid rgba(0,210,255,0.1);
    border-radius: 8px;
    padding: 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    color: #38bdf8;
    max-height: 360px;
    overflow-y: auto;
    line-height: 1.7;
  }
  .terminal-prompt { color: #00D9FF; }
  .terminal-ok { color: #22C55E; }
  .terminal-warn { color: #F59E0B; }
  .terminal-err { color: #EF4444; }

  /* ── Mission Button ── */
  .stButton > button {
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 1.5px !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    transition: all 0.25s !important;
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(0,180,220,0.9), rgba(0,120,180,0.9)) !important;
    border: 1px solid rgba(0,217,255,0.4) !important;
    box-shadow: 0 0 20px rgba(0,217,255,0.15) !important;
  }
  .stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 35px rgba(0,217,255,0.35) !important;
    transform: translateY(-1px) !important;
  }

  /* ── Input fields ── */
  .stTextArea textarea, .stTextInput input {
    background: rgba(3,8,22,0.9) !important;
    border: 1px solid rgba(0,210,255,0.2) !important;
    color: #c8dde8 !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
  }
  .stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(0,210,255,0.5) !important;
    box-shadow: 0 0 12px rgba(0,210,255,0.1) !important;
  }

  /* ── Selectbox ── */
  .stSelectbox > div > div {
    background: rgba(3,8,22,0.9) !important;
    border: 1px solid rgba(0,210,255,0.2) !important;
    border-radius: 8px !important;
    color: #c8dde8 !important;
  }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    color: #00D9FF !important;
    background: rgba(5,14,35,0.8) !important;
    border: 1px solid rgba(0,210,255,0.12) !important;
    border-radius: 8px !important;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: rgba(3,8,22,0.7) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    border: 1px solid rgba(0,210,255,0.1) !important;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    color: #3a6070 !important;
  }
  .stTabs [aria-selected="true"] {
    color: #00D9FF !important;
    background: rgba(0,210,255,0.1) !important;
    border-radius: 6px !important;
  }

  /* ── Gauge row ── */
  .gauge-row { display: flex; gap: 14px; justify-content: space-around; flex-wrap: wrap; }

  /* ── LLM status row ── */
  .llm-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 6px;
    background: rgba(0,210,255,0.04);
    border: 1px solid rgba(0,210,255,0.08);
    margin-bottom: 8px;
  }
  .llm-name { font-family:'JetBrains Mono',monospace; font-size:13px; color:#c8dde8; flex:1; }
  .llm-connected { font-size:11px; color:#22C55E; }

</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZATION
# ============================================================
@st.cache_resource
def get_maa_instance():
    return MAA()

maa = get_maa_instance()
status_info = maa.status()
now = datetime.now()

AGENT_META = {
    "Coordinator": {"icon": "🎯", "role": "Leadership & Planning", "color": "#00D9FF"},
    "Planner":     {"icon": "🗺️", "role": "Strategic Planning",    "color": "#7C3AED"},
    "Researcher":  {"icon": "🔍", "role": "Research & Tools",      "color": "#0EA5E9"},
    "Analyst":     {"icon": "📊", "role": "Deep Analysis",         "color": "#8B5CF6"},
    "Writer":      {"icon": "✍️", "role": "Clear Communication",   "color": "#06B6D4"},
    "Critic":      {"icon": "⚡", "role": "Quality Assurance",     "color": "#F59E0B"},
    "Verifier":    {"icon": "✅", "role": "Verification",          "color": "#22C55E"},
    "Archivist":   {"icon": "🗄️", "role": "Knowledge Management",  "color": "#A78BFA"},
}

# ============================================================
# TOP STATUS BAR
# ============================================================
st.markdown(f"""
<div class="top-bar">
  <div>
    <span class="top-bar-brand">◉ MAA COMMAND CENTER</span>
    <span class="top-bar-sub">Mega Agent Association · Autonomous Dynamic Mesh · v{maa.version}</span>
  </div>
  <div class="top-bar-time">{now.strftime("%H:%M:%S")}</div>
  <div class="top-bar-status">● SYSTEM STATUS: OPTIMAL</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 16px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#00D9FF;letter-spacing:2px;font-weight:700;">MAA</div>
      <div style="font-size:11px;color:#2a4a5a;letter-spacing:2px;text-transform:uppercase;">Command Center</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "NAV",
        [
            "⬡  Command Center",
            "⬡  AI Core",
            "⬡  Agents",
            "⬡  Mission Control",
            "⬡  Projects",
            "⬡  Memory & Knowledge",
            "⬡  Mission History",
            "⬡  System & Tools",
        ],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color:rgba(0,210,255,0.08);margin:14px 0'>", unsafe_allow_html=True)

    # Sidebar telemetry
    st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#00D9FF;letter-spacing:2px;margin-bottom:10px;'>LIVE TELEMETRY</div>", unsafe_allow_html=True)

    runs_count = status_info.get("runs", 0)
    agents_count = len(status_info.get("agents", []))
    tools_count = len(status_info.get("tools", []))
    projects_count = status_info.get("projects", 0)

    for label, val, color in [
        ("AGENTS ONLINE", agents_count, "#22C55E"),
        ("TOOLS LOADED", tools_count, "#00D9FF"),
        ("PROJECTS", projects_count, "#7C3AED"),
        ("SAVED RUNS", runs_count, "#F59E0B"),
    ]:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-family:JetBrains Mono,monospace;font-size:10px;color:#2a5a6a;letter-spacing:1px;">{label}</span>
          <span style="font-family:JetBrains Mono,monospace;font-size:14px;font-weight:700;color:{color};">{val}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(0,210,255,0.08);margin:14px 0'>", unsafe_allow_html=True)

    # LLM Status
    st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#00D9FF;letter-spacing:2px;margin-bottom:10px;'>LLM PROVIDERS</div>", unsafe_allow_html=True)
    for llm, connected in [("Groq", True), ("OpenAI", False), ("Qwen", True)]:
        dot_color = "#22C55E" if connected else "#EF4444"
        label = "Connected" if connected else "Offline"
        st.markdown(f"""
        <div class="llm-row">
          <span class="llm-name">{llm}</span>
          <span style="color:{dot_color};font-size:11px;font-family:'JetBrains Mono',monospace;">● {label}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(0,210,255,0.08);margin:14px 0'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#1a3a4a;text-align:center;'>{now.strftime('%A, %d %B %Y')}</div>", unsafe_allow_html=True)


# ============================================================
# ── HELPER: HUD Orb (SVG) ──
# ============================================================
def _build_tick_marks(r):
    """Pre-compute SVG tick mark lines as a plain string (avoids nested f-string in HTML)."""
    lines = []
    for i in range(12):
        angle = math.radians(i * 30)
        x1 = round(r + (r - 8) * math.cos(angle), 1)
        y1 = round(r + (r - 8) * math.sin(angle), 1)
        x2 = round(r + (r - 16) * math.cos(angle), 1)
        y2 = round(r + (r - 16) * math.sin(angle), 1)
        lines.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="rgba(0,210,255,0.3)" stroke-width="1.5"/>'
        )
    return " ".join(lines)


def render_hud_orb(label="MAA CORE", sub="v0.2.0-dev", size=220):
    r = size / 2

    # Pre-compute all dynamic values BEFORE building the HTML string
    r4    = r - 4
    r16   = r - 16
    r24   = r - 24
    r30   = r - 30
    r40   = r - 40
    arc_y1  = int(r * 0.28)
    arc_r   = int(r * 0.72)
    arc_x2  = int(r + r * 0.68)
    arc_y2  = int(r + r * 0.22)
    core_r  = int(r * 0.42)
    inner_r = int(r * 0.18)
    pulse_r1 = int(r * 0.15)
    pulse_r2 = int(r * 0.22)
    ch_x1   = int(r * 0.12)
    ch_x2   = int(r * 0.48)
    ch_x3   = int(r * 1.52)
    ch_x4   = int(r * 1.88)
    ch_y3   = int(r * 0.12)
    ch_y4   = int(r * 0.48)
    ch_y5   = int(r * 1.52)
    ch_y6   = int(r * 1.88)
    tick_marks = _build_tick_marks(r)

    st.markdown(f"""
    <div class="hud-wrapper">
      <div class="hud-svg-container" style="width:{size}px;height:{size}px;">
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <radialGradient id="coreGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%"   stop-color="#00D9FF" stop-opacity="0.35"/>
              <stop offset="50%"  stop-color="#7C3AED" stop-opacity="0.55"/>
              <stop offset="100%" stop-color="#010610" stop-opacity="1"/>
            </radialGradient>
            <radialGradient id="innerGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%"   stop-color="#00D9FF" stop-opacity="0.9"/>
              <stop offset="60%"  stop-color="#7C3AED" stop-opacity="0.6"/>
              <stop offset="100%" stop-color="#010610" stop-opacity="0"/>
            </radialGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          </defs>
          <circle cx="{r}" cy="{r}" r="{r4}"  fill="none" stroke="rgba(0,210,255,0.08)" stroke-width="1"/>
          <circle cx="{r}" cy="{r}" r="{r16}" fill="none" stroke="rgba(0,210,255,0.12)" stroke-width="1.5"/>
          <circle cx="{r}" cy="{r}" r="{r30}" fill="none" stroke="rgba(124,58,237,0.18)" stroke-width="1"/>
          <circle cx="{r}" cy="{r}" r="{r24}" fill="none"
                  stroke="rgba(0,210,255,0.22)" stroke-width="1.5" stroke-dasharray="8 14">
            <animateTransform attributeName="transform" type="rotate"
              from="0 {r} {r}" to="360 {r} {r}" dur="12s" repeatCount="indefinite"/>
          </circle>
          <circle cx="{r}" cy="{r}" r="{r40}" fill="none"
                  stroke="rgba(160,80,240,0.3)" stroke-width="1" stroke-dasharray="4 20">
            <animateTransform attributeName="transform" type="rotate"
              from="360 {r} {r}" to="0 {r} {r}" dur="8s" repeatCount="indefinite"/>
          </circle>
          <path d="M {r},{arc_y1} A {arc_r},{arc_r} 0 0,1 {arc_x2},{arc_y2}"
                fill="none" stroke="rgba(220,80,200,0.45)" stroke-width="2.5" filter="url(#glow)">
            <animateTransform attributeName="transform" type="rotate"
              from="0 {r} {r}" to="360 {r} {r}" dur="6s" repeatCount="indefinite"/>
          </path>
          <circle cx="{r}" cy="{r}" r="{core_r}" fill="url(#coreGrad)" filter="url(#glow)"/>
          <circle cx="{r}" cy="{r}" r="{inner_r}" fill="url(#innerGlow)" filter="url(#glow)">
            <animate attributeName="r" values="{pulse_r1};{pulse_r2};{pulse_r1}" dur="3s" repeatCount="indefinite"/>
          </circle>
          {tick_marks}
          <line x1="{ch_x1}" y1="{r}" x2="{ch_x2}" y2="{r}" stroke="rgba(0,210,255,0.25)" stroke-width="1"/>
          <line x1="{ch_x3}" y1="{r}" x2="{ch_x4}" y2="{r}" stroke="rgba(0,210,255,0.25)" stroke-width="1"/>
          <line x1="{r}" y1="{ch_y3}" x2="{r}" y2="{ch_y4}" stroke="rgba(0,210,255,0.25)" stroke-width="1"/>
          <line x1="{r}" y1="{ch_y5}" x2="{r}" y2="{ch_y6}" stroke="rgba(0,210,255,0.25)" stroke-width="1"/>
        </svg>
        <div class="hud-label-center">
          <span class="hud-core-text">{label}</span>
          <span class="hud-version-text">{sub}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ── HELPER: System Monitor Gauges (Plotly) ──
# ============================================================
def gauge_chart(value, label, color="#00D9FF", max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": "%", "font": {"size": 18, "color": color, "family": "JetBrains Mono"}},
        title={"text": label, "font": {"size": 11, "color": "#3a6070", "family": "JetBrains Mono"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#1a3a4a", "tickwidth": 1,
                     "tickfont": {"size": 8, "color": "#1a3a4a"}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, max_val*0.6], "color": "rgba(0,210,255,0.04)"},
                {"range": [max_val*0.6, max_val*0.85], "color": "rgba(245,158,11,0.05)"},
                {"range": [max_val*0.85, max_val], "color": "rgba(239,68,68,0.06)"},
            ],
            "threshold": {"line": {"color": color, "width": 2}, "thickness": 0.8, "value": value},
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        height=130,
        font=dict(color="#a8c5da"),
    )
    return fig


# ============================================================
# MODULE: COMMAND CENTER (Overview)
# ============================================================
if page == "⬡  Command Center":

    # ── Row 1: Metrics + HUD + Feed ──
    col_left, col_center, col_right = st.columns([1.1, 1, 1.2])

    with col_left:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>AI CORE OVERVIEW</div>", unsafe_allow_html=True)

        agent_names = status_info.get("agents", list(AGENT_META.keys()))
        for agent in agent_names[:5]:
            meta = AGENT_META.get(agent, {"icon": "🤖", "role": "Agent", "color": "#00D9FF"})
            st.markdown(f"""
            <div class="agent-card">
              <div class="agent-icon" style="background:rgba({','.join(str(int(meta['color'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.12);">{meta['icon']}</div>
              <div class="agent-info">
                <span class="agent-name">{agent}</span>
                <span class="agent-role">{meta['role']}</span>
              </div>
              <div class="agent-status-dot"></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_center:
        st.markdown("<div class='glass-panel' style='text-align:center;'>", unsafe_allow_html=True)
        render_hud_orb("MAA CORE", f"v{maa.version}")
        st.markdown(f"""
        <div style="margin-top:12px;display:flex;justify-content:center;gap:18px;flex-wrap:wrap;">
          <div class="metric-tile" style="flex:1;min-width:80px;text-align:center;">
            <span class="metric-val">{agents_count}</span>
            <span class="metric-lbl">Agents</span>
          </div>
          <div class="metric-tile" style="flex:1;min-width:80px;text-align:center;">
            <span class="metric-val">{tools_count}</span>
            <span class="metric-lbl">Tools</span>
          </div>
          <div class="metric-tile" style="flex:1;min-width:80px;text-align:center;">
            <span class="metric-val">{runs_count}</span>
            <span class="metric-lbl">Runs</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'><span class='live-dot'></span> LIVE INTELLIGENCE FEED</div>", unsafe_allow_html=True)

        # Load recent run data for the live feed
        recent_runs = maa.memory.list_runs() if hasattr(maa.memory, "list_runs") else []
        if recent_runs:
            for run_id in recent_runs[-4:][::-1]:
                run = maa.memory.load_run(run_id)
                if run:
                    score = run.get("evaluation", {}).get("score", "—") if isinstance(run.get("evaluation"), dict) else "—"
                    obj = str(run.get("objective", "Unknown"))[:48]
                    badge_class = "badge-ok" if str(score) not in ("—", "5") else "badge-warn"
                    badge_txt = f"Score {score}/10" if score != "—" else "DONE"
                    st.markdown(f"""
                    <div class="feed-item">
                      <span class="feed-badge {badge_class}">{badge_txt}</span>
                      <div class="feed-title">{obj}…</div>
                      <div class="feed-sub">{run_id}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='feed-item'><div class='feed-title'>No runs yet</div><div class='feed-sub'>Run a mission to see results here</div></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 2: System Monitor + Memory + LLM Status ──
    col_sys, col_mem, col_llm = st.columns([1, 1, 1])

    with col_sys:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>SYSTEM MONITOR</div>", unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        g1.plotly_chart(gauge_chart(15, "CPU", "#00D9FF"), use_container_width=True)
        g2.plotly_chart(gauge_chart(54, "MEM", "#7C3AED"), use_container_width=True)
        g3.plotly_chart(gauge_chart(40, "DISK", "#22C55E"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_mem:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>MEMORY INSIGHTS</div>", unsafe_allow_html=True)

        kb_count = 0
        try:
            if hasattr(maa.memory, "load_knowledge_base"):
                kb_count = len(maa.memory.load_knowledge_base())
        except Exception:
            pass

        st.markdown(f"""
        <div style="text-align:center;padding:10px 0;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:38px;font-weight:700;color:#00D9FF;text-shadow:0 0 20px rgba(0,217,255,0.4);">{kb_count}</div>
          <div style="font-size:11px;color:#3a6070;letter-spacing:2px;margin-top:4px;">KNOWLEDGE ENTRIES</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top:8px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="font-size:12px;color:#3a6070;">Saved Runs</span>
            <span style="font-family:'JetBrains Mono',monospace;color:#00D9FF;font-size:13px;">{runs_count}</span>
          </div>
          <div style="display:flex;justify-content:space-between;">
            <span style="font-size:12px;color:#3a6070;">Projects</span>
            <span style="font-family:'JetBrains Mono',monospace;color:#7C3AED;font-size:13px;">{projects_count}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_llm:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>LLM STATUS</div>", unsafe_allow_html=True)
        llm_providers = [
            ("Groq / gpt-oss-20b",  "#22C55E", True),
            ("Groq / gpt-oss-120b", "#22C55E", True),
            ("Groq / qwen3.6-27b",  "#22C55E", True),
            ("OpenAI / gpt-4o",     "#3a6070", False),
        ]
        for name, color, active in llm_providers:
            dot = "#22C55E" if active else "#1a3a4a"
            lbl = "Active" if active else "Offline"
            st.markdown(f"""
            <div class="llm-row">
              <span style="width:8px;height:8px;border-radius:50%;background:{dot};box-shadow:0 0 5px {dot};display:inline-block;flex-shrink:0;"></span>
              <span class="llm-name" style="font-size:12px;">{name}</span>
              <span style="font-size:10px;color:{dot};font-family:'JetBrains Mono',monospace;">{lbl}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("""<div style="margin-top:10px;font-size:11px;color:#3a6070;text-align:right;font-family:'JetBrains Mono',monospace;">3 Connected</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MODULE: AI CORE
# ============================================================
elif page == "⬡  AI Core":
    st.markdown("<h3 style='color:#00D9FF;font-family:JetBrains Mono,monospace;letter-spacing:2px;'>AI CORE</h3>", unsafe_allow_html=True)

    c_orb, c_info = st.columns([1, 1.4])
    with c_orb:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        render_hud_orb("MAA CORE", f"v{maa.version}", size=260)
        st.markdown(f"""
        <div style="text-align:center;margin-top:12px;">
          <span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#22C55E;">● ONLINE / READY</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_info:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>CORE CAPABILITIES</div>", unsafe_allow_html=True)
        capabilities = [
            ("📨", "Typed MessageBus",       "ENABLED",  "#22C55E"),
            ("🛠️", "Universal Tool Access",   "ACTIVE",   "#22C55E"),
            ("💾", "Persistent RunState",     "ONLINE",   "#22C55E"),
            ("⚡", "Model Router",             "GROQ + FALLBACK", "#00D9FF"),
            ("🔁", "Dynamic Agent Mesh",      "V2 ACTIVE","#7C3AED"),
            ("🧠", "Reflection Loops",        "ENABLED",  "#22C55E"),
            ("📊", "Quality Scoring",         "1–10 SCALE","#F59E0B"),
        ]
        for icon, name, status, color in capabilities:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid rgba(0,210,255,0.06);">
              <span style="font-size:16px;">{icon}</span>
              <span style="flex:1;font-size:14px;color:#a8c5da;">{name}</span>
              <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{color};">{status}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Agent Network Graph
    st.markdown("<div class='glass-panel' style='margin-top:14px;'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>AGENT NETWORK MAP</div>", unsafe_allow_html=True)
    agent_names = status_info.get("agents", list(AGENT_META.keys()))
    n = len(agent_names)
    R = 2.2
    x_nodes = [0.0] + [R * math.cos(2 * math.pi * i / (n-1)) for i in range(n-1)]
    y_nodes = [0.0] + [R * math.sin(2 * math.pi * i / (n-1)) for i in range(n-1)]
    node_colors = ["#00D9FF"] + [AGENT_META.get(a, {}).get("color","#7C3AED") for a in agent_names[1:]]
    edge_x, edge_y = [], []
    for i in range(1, n):
        edge_x += [x_nodes[0], x_nodes[i], None]
        edge_y += [y_nodes[0], y_nodes[i], None]
    fig_net = go.Figure()
    fig_net.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines',
        line=dict(color='rgba(0,210,255,0.2)', width=1.5), hoverinfo='none'))
    fig_net.add_trace(go.Scatter(x=x_nodes, y=y_nodes, mode='markers+text',
        text=agent_names, textposition="top center",
        marker=dict(size=[38]+[26]*(n-1), color=node_colors,
                    line=dict(color='rgba(0,0,0,0.5)', width=2)),
        textfont=dict(color='#c8dde8', family='JetBrains Mono', size=11)))
    fig_net.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', height=380,
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
        yaxis=dict(showgrid=False,zeroline=False,showticklabels=False))
    st.plotly_chart(fig_net, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MODULE: AGENTS
# ============================================================
elif page == "⬡  Agents":
    st.markdown("<h3 style='color:#00D9FF;font-family:JetBrains Mono,monospace;letter-spacing:2px;'>ACTIVE AGENTS</h3>", unsafe_allow_html=True)
    agent_names = status_info.get("agents", list(AGENT_META.keys()))
    cols = st.columns(2)
    for i, agent in enumerate(agent_names):
        meta = AGENT_META.get(agent, {"icon":"🤖","role":"Agent","color":"#00D9FF"})
        r, g, b = (int(meta["color"].lstrip("#")[j:j+2], 16) for j in (0, 2, 4))
        with cols[i % 2]:
            st.markdown(f"""
            <div class="glass-panel" style="border-left:3px solid {meta['color']};">
              <div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">
                <div style="font-size:28px;">{meta['icon']}</div>
                <div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700;color:{meta['color']};">{agent}</div>
                  <div style="font-size:12px;color:#3a6070;margin-top:2px;">{meta['role']}</div>
                </div>
                <div style="margin-left:auto;display:flex;align-items:center;gap:6px;">
                  <div style="width:8px;height:8px;border-radius:50%;background:#22C55E;box-shadow:0 0 8px #22C55E;"></div>
                  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#22C55E;">READY</span>
                </div>
              </div>
              <div style="display:flex;gap:8px;flex-wrap:wrap;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 10px;border-radius:12px;background:rgba({r},{g},{b},0.1);color:{meta['color']};border:1px solid rgba({r},{g},{b},0.2);">Tool Access</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 10px;border-radius:12px;background:rgba(34,197,94,0.08);color:#22C55E;border:1px solid rgba(34,197,94,0.15);">ReAct Mode</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 10px;border-radius:12px;background:rgba(0,210,255,0.06);color:#00D9FF;border:1px solid rgba(0,210,255,0.12);">MessageBus</span>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# MODULE: MISSION CONTROL
# ============================================================
elif page == "⬡  Mission Control":
    st.markdown("<h3 style='color:#00D9FF;font-family:JetBrains Mono,monospace;letter-spacing:2px;'>MISSION CONTROL</h3>", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>MISSION OBJECTIVE</div>", unsafe_allow_html=True)
        objective = st.text_area(
            "objective_input", height=120,
            placeholder="Describe the complex objective for the MAA agent mesh to solve...",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>MISSION CONFIG</div>", unsafe_allow_html=True)
        projects = maa.list_projects()
        proj_opts = {"None (Standalone)": None}
        for p in projects:
            proj_opts[f"{p.name}"] = p.id
        selected_proj = st.selectbox("Link to Project", list(proj_opts.keys()), label_visibility="visible")
        proj_id = proj_opts[selected_proj]
        st.markdown("</div>", unsafe_allow_html=True)

    launch = st.button("🔴  INITIATE MISSION", type="primary", use_container_width=True)

    if launch:
        if not objective.strip():
            st.warning("⚠ Enter a mission objective first.")
        else:
            st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
            st.markdown("<div class='panel-title'><span class='live-dot'></span> LIVE MISSION LOG</div>", unsafe_allow_html=True)
            with st.spinner("Executing dynamic agent mesh..."):
                try:
                    results = maa.run(objective, project_id=proj_id)
                    st.success("✅ MISSION COMPLETED")

                    # Telemetry
                    score = results.get("evaluation", {}).get("score", "—") if isinstance(results.get("evaluation"), dict) else "—"
                    steps = results.get("total_steps", len(results.get("steps", [])))
                    tokens = results.get("total_tokens_estimated", 0)

                    mc1, mc2, mc3 = st.columns(3)
                    mc1.markdown(f"<div class='metric-tile'><span class='metric-val'>{score}/10</span><span class='metric-lbl'>Quality Score</span></div>", unsafe_allow_html=True)
                    mc2.markdown(f"<div class='metric-tile'><span class='metric-val'>{steps}</span><span class='metric-lbl'>Steps Executed</span></div>", unsafe_allow_html=True)
                    mc3.markdown(f"<div class='metric-tile'><span class='metric-val'>{tokens:,}</span><span class='metric-lbl'>Estimated Tokens</span></div>", unsafe_allow_html=True)

                    st.markdown("<div class='panel-title' style='margin-top:16px;'>FINAL SOLUTION</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='terminal' style='color:#c8dde8;'>{results.get('final','No output.')}</div>", unsafe_allow_html=True)

                    with st.expander("🔍 Full Step Trace & Raw JSON"):
                        st.json(results)

                except Exception as e:
                    st.error(f"Execution Error: {e}")
            st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MODULE: PROJECTS
# ============================================================
elif page == "⬡  Projects":
    st.markdown("<h3 style='color:#00D9FF;font-family:JetBrains Mono,monospace;letter-spacing:2px;'>PROJECT REGISTRY</h3>", unsafe_allow_html=True)

    with st.expander("➕  CREATE NEW PROJECT"):
        name = st.text_input("Project Name")
        goal = st.text_area("Project Goal / Scope")
        if st.button("Create Project"):
            if name and goal:
                p = maa.create_project(name, goal)
                st.success(f"Created: **{p.name}** (`{p.id}`)")
            else:
                st.warning("Enter both name and goal.")

    projects = maa.list_projects()
    if not projects:
        st.markdown("<div class='glass-panel' style='text-align:center;color:#3a6070;padding:40px;'>No active projects. Create one above.</div>", unsafe_allow_html=True)
    else:
        for p in projects:
            status_color = "#22C55E" if p.status == "active" else "#F59E0B"
            st.markdown(f"""
            <div class="glass-panel" style="border-left:3px solid {status_color};">
              <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px;">
                <div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700;color:#c8dde8;">{p.name}</div>
                  <div style="font-size:11px;color:#3a6070;margin-top:2px;font-family:'JetBrains Mono',monospace;">{p.id}</div>
                </div>
                <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{status_color};background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);padding:4px 12px;border-radius:12px;">{p.status.upper()}</span>
              </div>
              <div style="font-size:14px;color:#7a9aaa;margin-bottom:10px;">{p.goal}</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#00D9FF;">Linked Runs: {len(p.run_ids)}</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# MODULE: MEMORY & KNOWLEDGE
# ============================================================
elif page == "⬡  Memory & Knowledge":
    st.markdown("<h3 style='color:#00D9FF;font-family:JetBrains Mono,monospace;letter-spacing:2px;'>LONG-TERM KNOWLEDGE BASE</h3>", unsafe_allow_html=True)

    if hasattr(maa.memory, "load_knowledge_base"):
        kb_data = maa.memory.load_knowledge_base()
    else:
        try:
            with open("knowledge_base.json", "r", encoding="utf-8") as f:
                kb_data = json.load(f).get("entries", [])
        except Exception:
            kb_data = []

    st.markdown(f"""
    <div class="glass-panel" style="display:flex;gap:24px;align-items:center;">
      <div class="metric-tile" style="flex:1;text-align:center;">
        <span class="metric-val">{len(kb_data)}</span>
        <span class="metric-lbl">Knowledge Entries</span>
      </div>
      <div class="metric-tile" style="flex:1;text-align:center;">
        <span class="metric-val" style="color:#7C3AED;">{runs_count}</span>
        <span class="metric-lbl">Saved Runs</span>
      </div>
      <div class="metric-tile" style="flex:1;text-align:center;">
        <span class="metric-val" style="color:#22C55E;">{projects_count}</span>
        <span class="metric-lbl">Projects</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    query = st.text_input("🔍 Search Knowledge Base", placeholder="Enter topic or keyword...")
    if query:
        results_k = maa.memory.retrieve_relevant_knowledge(query)
        st.markdown("<div class='panel-title'>MATCHING KNOWLEDGE</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='terminal'>{results_k}</div>", unsafe_allow_html=True)
    else:
        with st.expander("📂 View Raw Knowledge Entries"):
            st.json(kb_data)


# ============================================================
# MODULE: MISSION HISTORY
# ============================================================
elif page == "⬡  Mission History":
    st.markdown("<h3 style='color:#00D9FF;font-family:JetBrains Mono,monospace;letter-spacing:2px;'>MISSION HISTORY</h3>", unsafe_allow_html=True)

    runs = maa.memory.list_runs()
    if not runs:
        st.markdown("<div class='glass-panel' style='text-align:center;color:#3a6070;padding:40px;'>No mission history found.</div>", unsafe_allow_html=True)
    else:
        col_list, col_detail = st.columns([1, 2])
        with col_list:
            selected_run = st.selectbox("Select Run", runs, label_visibility="collapsed")

        with col_detail:
            run_data = maa.memory.load_run(selected_run)
            if run_data:
                score = run_data.get("evaluation", {}).get("score", "—") if isinstance(run_data.get("evaluation"), dict) else "—"
                st.markdown(f"""
                <div class="glass-panel">
                  <div class="panel-title">RUN DETAILS · {selected_run}</div>
                  <div style="font-size:15px;font-weight:600;color:#a8c5da;margin-bottom:14px;">{run_data.get('objective','')}</div>
                """, unsafe_allow_html=True)

                mc1, mc2 = st.columns(2)
                mc1.markdown(f"<div class='metric-tile'><span class='metric-val'>{score}/10</span><span class='metric-lbl'>Quality Score</span></div>", unsafe_allow_html=True)
                steps = run_data.get("steps", [])
                mc2.markdown(f"<div class='metric-tile'><span class='metric-val'>{len(steps)}</span><span class='metric-lbl'>Steps</span></div>", unsafe_allow_html=True)

                t1, t2, t3 = st.tabs(["Final Solution", "Step Trace", "Raw JSON"])
                with t1:
                    st.markdown(f"<div class='terminal' style='color:#c8dde8;'>{run_data.get('final','—')}</div>", unsafe_allow_html=True)
                with t2:
                    if steps:
                        for s in steps:
                            st.markdown(f"""
                            <div class="feed-item">
                              <div class="feed-title">Step {s.get('step_number','?')}: [{s.get('agent_name','?')}] — {s.get('task_title','')}</div>
                              <div class="feed-sub" style="margin-top:4px;color:#5a8a9a;">{str(s.get('output',''))[:200]}…</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("No step trace available.")
                with t3:
                    st.json(run_data)
                st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# MODULE: SYSTEM & TOOLS
# ============================================================
elif page == "⬡  System & Tools":
    st.markdown("<h3 style='color:#00D9FF;font-family:JetBrains Mono,monospace;letter-spacing:2px;'>SYSTEM & TOOLS</h3>", unsafe_allow_html=True)

    t_tools, t_upload, t_image = st.tabs(["🧰 Universal Tool Matrix", "📂 File Ingestion", "🎨 Image Engine"])

    with t_tools:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>REGISTERED TOOLS</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='terminal'>{maa.tools.get_tool_info()}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with t_upload:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>FILE INGESTION</div>", unsafe_allow_html=True)
        up_file = st.file_uploader(
            "Upload document for agent mesh access",
            type=["txt", "pdf", "md", "csv", "json", "jpg", "png"]
        )
        if up_file is not None:
            os.makedirs("uploads", exist_ok=True)
            path = os.path.join("uploads", up_file.name)
            with open(path, "wb") as f:
                f.write(up_file.getbuffer())
            st.success(f"✅ File uploaded → `{path}`")
        st.markdown("</div>", unsafe_allow_html=True)

    with t_image:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>IMAGE GENERATION ENGINE</div>", unsafe_allow_html=True)
        img_prompt = st.text_area("Image Prompt", placeholder="A futuristic cybernetic core glowing with blue and purple light...")
        if st.button("⚡ Generate Image"):
            if img_prompt.strip():
                try:
                    from tools.image_generator import generate_image
                    img_path = generate_image(img_prompt)
                    if img_path.endswith((".jpg", ".png")):
                        st.image(img_path, caption=img_prompt, use_container_width=True)
                    else:
                        st.error(img_path)
                except Exception as e:
                    st.error(f"Image generation failed: {e}")
            else:
                st.warning("Enter a prompt first.")
        st.markdown("</div>", unsafe_allow_html=True)