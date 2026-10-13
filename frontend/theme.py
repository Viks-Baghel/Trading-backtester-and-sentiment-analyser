"""QuantLab retro theme.

Two palettes (rich, muted, no neon):
  * Dark  -> "Leather & Brass" (espresso brown, brass, burgundy, teal, gold)
  * Light -> "Cream Paper"     (parchment, dark ink, burgundy, teal, ochre)
(Key names like "pink"/"cyan" are kept for compatibility; they hold
burgundy and teal now.)

Public API (unchanged from the previous theme module):
    init_theme(), apply_theme(), panel_metric(...)
New helper:
    palette() -> dict of colours for the active theme (used by Plotly charts)
"""

import streamlit as st

PALETTES = {
    "Dark": {
        "bg": "#0b1630",
        "bg2": "#122246",
        "panel": "#162a54",
        "panel_muted": "#0f1d3d",
        "border": "#4f6ca6",
        "shadow": "#040a1a",
        "text": "#e8edf7",
        "muted": "#9aabcb",
        "cyan": "#5aa9b8",
        "pink": "#b04552",
        "yellow": "#d1a54a",
        "green": "#5fa37a",
        "red": "#d25a4b",
        "on_accent": "#0b1630",
        "grid": "rgba(111,143,199,0.07)",
        "scan": "rgba(255,255,255,0.02)",
        "plotly": "plotly_dark",
    },
    "Light": {
        "bg": "#ede3cd",
        "bg2": "#e1d3b4",
        "panel": "#f9f2e2",
        "panel_muted": "#efe4cb",
        "border": "#3b2a20",
        "shadow": "#3b2a20",
        "text": "#2e2420",
        "muted": "#6e5f52",
        "cyan": "#1f6f78",
        "pink": "#8f2d3a",
        "yellow": "#b07c1c",
        "green": "#2f6b45",
        "red": "#a8372b",
        "on_accent": "#f9f2e2",
        "grid": "rgba(46,36,32,0.05)",
        "scan": "rgba(46,36,32,0.012)",
        "plotly": "plotly_white",
    },
}


def init_theme():
    if "ql_theme" not in st.session_state:
        st.session_state["ql_theme"] = "Dark"


def palette():
    name = st.session_state.get("ql_theme", "Dark")
    return PALETTES.get(name, PALETTES["Dark"])


def _root_vars(p):
    return f"""
:root {{
  --ql-bg: {p['bg']};
  --ql-bg2: {p['bg2']};
  --ql-panel: {p['panel']};
  --ql-panel-muted: {p['panel_muted']};
  --ql-border: {p['border']};
  --ql-shadow: {p['shadow']};
  --ql-text: {p['text']};
  --ql-muted: {p['muted']};
  --ql-cyan: {p['cyan']};
  --ql-pink: {p['pink']};
  --ql-yellow: {p['yellow']};
  --ql-green: {p['green']};
  --ql-red: {p['red']};
  --ql-on-accent: {p['on_accent']};
  --ql-grid: {p['grid']};
  --ql-scan: {p['scan']};
}}
"""


_STATIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, p, li, label, input, textarea, select {
  font-family: 'Space Mono', ui-monospace, Menlo, Consolas, monospace !important;
}
.stApp {
  color: var(--ql-text);
  background-color: var(--ql-bg);
  background-image:
    linear-gradient(var(--ql-grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--ql-grid) 1px, transparent 1px);
  background-size: 34px 34px, 34px 34px;
  background-attachment: fixed;
}
/* CRT scanlines */
.stApp::before {
  content: "";
  position: fixed; inset: 0; z-index: 9999; pointer-events: none;
  background: repeating-linear-gradient(0deg, var(--ql-scan) 0, var(--ql-scan) 1px, transparent 1px, transparent 3px);
}
:root { --ql-pad: 1.25rem; }
html, body, .stApp, [data-testid="stAppViewContainer"] { min-height: 100vh; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], [data-testid="stAppDeployButton"], #MainMenu,
footer[data-testid="stFooter"], .stDeployButton { display: none !important; }
/* Full-width, tight layout */
[data-testid="stMainBlockContainer"], .block-container {
  max-width: 100% !important; width: 100% !important;
  padding: 0.35rem var(--ql-pad) 1rem var(--ql-pad) !important;
}
[data-testid="stVerticalBlock"] { gap: 0.6rem; }
/* Collapse invisible elements (injected <style>, cookie-manager iframe) that
   would otherwise each add an empty gap at the top of the page */
[data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] style),
[data-testid="stElementContainer"]:has(iframe[height="0"]),
[data-testid="stElementContainer"]:has(iframe[title*="cookie"]) {
  display: none !important;
}
/* Header floats over the page (no layout space); keep the sidebar toggle usable */
header[data-testid="stHeader"] { position: fixed; height: 0; min-height: 0; z-index: 10001; }
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] {
  position: fixed; top: 0.45rem; left: 0.45rem; z-index: 10002;
  background: var(--ql-panel); border: 2px solid var(--ql-border);
  box-shadow: 2px 2px 0 var(--ql-shadow); border-radius: 0;
}
h1, h2, h3, h4 { padding: 0.15rem 0 !important; margin: 0 !important; }

h1, h2, h3, h4 {
  font-family: 'Press Start 2P', monospace !important;
  color: var(--ql-text) !important;
  letter-spacing: 0.5px;
  line-height: 1.5 !important;
}
h1 { font-size: clamp(20px, 2.6vw, 30px) !important; }
h2 { font-size: clamp(15px, 1.8vw, 20px) !important; }
h3 { font-size: clamp(12px, 1.4vw, 15px) !important; }
h4 { font-size: 12px !important; }
a { color: var(--ql-cyan) !important; }
hr { border-color: var(--ql-border) !important; opacity: .5; }

/* ---------- Brand + ticker + navline ---------- */
.ql-ticker {
  overflow: hidden; white-space: nowrap;
  border: 2px solid var(--ql-border); border-left: 0; border-right: 0;
  background: linear-gradient(90deg, var(--ql-pink), var(--ql-yellow), var(--ql-cyan));
  color: var(--ql-on-accent);
  font-family: 'Press Start 2P', monospace; font-size: 9px;
  padding: 7px 0; margin: 0 calc(-1 * var(--ql-pad)) 10px calc(-1 * var(--ql-pad));
}
.ql-ticker span { display: inline-block; padding-left: 100%; animation: ql-scroll 34s linear infinite; }
@keyframes ql-scroll { to { transform: translateX(-100%); } }

.ql-brand {
  font-family: 'Press Start 2P', monospace; font-size: 15px;
  display: flex; align-items: center; gap: 11px; color: var(--ql-text);
  text-shadow: 2px 2px 0 var(--ql-pink);
}
.ql-brand-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 30px; height: 30px; background: var(--ql-yellow); color: var(--ql-on-accent);
  border: 2px solid var(--ql-border); box-shadow: 3px 3px 0 var(--ql-pink);
  text-shadow: none; font-size: 15px;
}
.ql-nav-status {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: 'Press Start 2P', monospace; font-size: 9px; letter-spacing: 1px;
  padding: 7px 10px; border: 2px solid var(--ql-border);
  background: var(--ql-panel); color: var(--ql-green);
  box-shadow: 3px 3px 0 var(--ql-shadow);
}
.ql-nav-status::before {
  content: ""; width: 8px; height: 8px; background: var(--ql-green);
  animation: ql-blink 1.2s steps(2) infinite;
}
@keyframes ql-blink { 50% { opacity: .2; } }
.ql-navline {
  height: 6px; margin: 6px 0 12px 0;
  background: repeating-linear-gradient(90deg,
    var(--ql-pink) 0 40px, var(--ql-yellow) 40px 80px,
    var(--ql-cyan) 80px 120px, var(--ql-green) 120px 160px);
  border-top: 2px solid var(--ql-border); border-bottom: 2px solid var(--ql-border);
}

/* ---------- Typography helpers ---------- */
.ql-kicker {
  font-family: 'Press Start 2P', monospace; font-size: 10px;
  color: var(--ql-yellow); letter-spacing: 1.5px; margin-bottom: 6px;
}
.ql-label {
  font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: var(--ql-muted);
}
.ql-caption, .stCaption, [data-testid="stCaptionContainer"] { color: var(--ql-muted) !important; font-size: 12.5px; }
.ql-subtitle { color: var(--ql-muted); font-size: 15px; line-height: 1.7; max-width: 640px; }
.ql-hero-title {
  font-family: 'Press Start 2P', monospace; font-size: clamp(22px, 3.2vw, 40px);
  line-height: 1.55; color: var(--ql-text); margin: 6px 0 16px 0;
  text-shadow: 4px 4px 0 var(--ql-pink);
}
.ql-pill {
  display: inline-block; padding: 6px 10px; font-size: 10px; letter-spacing: 2px;
  font-family: 'Press Start 2P', monospace; text-transform: uppercase;
  color: var(--ql-on-accent); background: var(--ql-yellow);
  border: 2px solid var(--ql-border); box-shadow: 3px 3px 0 var(--ql-shadow);
}

/* ---------- Panels ---------- */
.ql-panel {
  background: var(--ql-panel); border: 2px solid var(--ql-border);
  box-shadow: 6px 6px 0 var(--ql-shadow); padding: 18px 20px; position: relative;
}
.ql-panel::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 5px;
  background: linear-gradient(90deg, var(--ql-pink), var(--ql-yellow), var(--ql-cyan));
}
.ql-panel-muted {
  background: var(--ql-panel-muted); border: 2px dashed var(--ql-border); padding: 16px 20px;
}
.ql-metric {
  background: var(--ql-panel); border: 2px solid var(--ql-border);
  box-shadow: 5px 5px 0 var(--ql-shadow); padding: 14px 16px; margin-bottom: 14px;
}
.ql-metric .v { font-family: 'Press Start 2P', monospace; font-size: 18px; margin: 10px 0 8px 0; }
.ql-metric .v.green { color: var(--ql-green); }
.ql-metric .v.red { color: var(--ql-red); }
.ql-metric .v.plain { color: var(--ql-cyan); }

.ql-footer {
  margin-top: 40px; padding-top: 18px; border-top: 3px dashed var(--ql-border);
  color: var(--ql-muted); font-size: 12px;
}

/* ---------- Buttons ---------- */
.stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button {
  font-family: 'Space Mono', monospace !important; font-weight: 700; text-transform: uppercase;
  letter-spacing: .6px; font-size: 12.5px;
  border-radius: 0 !important; border: 2px solid var(--ql-border) !important;
  background: var(--ql-panel) !important; color: var(--ql-text) !important;
  box-shadow: 4px 4px 0 var(--ql-shadow); transition: transform .08s, box-shadow .08s, background .12s;
}
.stButton button p, .stDownloadButton button p { font-weight: 700; }
.stButton button:hover, .stDownloadButton button:hover, [data-testid="stFormSubmitButton"] button:hover {
  transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--ql-shadow);
  background: var(--ql-bg2) !important; color: var(--ql-cyan) !important;
}
.stButton button:active, [data-testid="stFormSubmitButton"] button:active {
  transform: translate(3px, 3px); box-shadow: 1px 1px 0 var(--ql-shadow);
}
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"],
.stButton button[data-testid="stBaseButton-primary"], [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--ql-pink) !important; color: #ffffff !important;
}
.stButton button[kind="primary"]:hover, .stButton button[data-testid="stBaseButton-primary"]:hover,
[data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
  background: var(--ql-yellow) !important; color: var(--ql-on-accent) !important;
}

/* ---------- Inputs ---------- */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="base-input"],
div[data-baseweb="textarea"], .stTextArea textarea, .stNumberInput input, .stDateInput input {
  background: var(--ql-panel-muted) !important; color: var(--ql-text) !important;
  border-radius: 0 !important; border: 2px solid var(--ql-border) !important;
}
div[data-baseweb="input"] input, div[data-baseweb="select"] div { color: var(--ql-text) !important; }
div[data-baseweb="input"]:focus-within > div, .stTextArea textarea:focus {
  border-color: var(--ql-cyan) !important; box-shadow: 3px 3px 0 var(--ql-cyan);
}
.stTextInput label, .stSelectbox label, .stNumberInput label, .stDateInput label, .stTextArea label {
  font-size: 11px !important; letter-spacing: 1.5px; text-transform: uppercase; color: var(--ql-muted) !important;
}
[data-testid="stForm"] {
  border: 2px solid var(--ql-border) !important; border-radius: 0 !important;
  background: var(--ql-panel); box-shadow: 5px 5px 0 var(--ql-shadow);
}

/* ---------- Workspace tab-style radio ---------- */
div[role="radiogroup"] { gap: 10px; flex-wrap: wrap; }
div[role="radiogroup"] > label {
  background: var(--ql-panel); border: 2px solid var(--ql-border); padding: 8px 14px;
  box-shadow: 3px 3px 0 var(--ql-shadow); cursor: pointer; margin: 0;
  transition: transform .08s, background .12s;
}
div[role="radiogroup"] > label > div:first-child { display: none; }
div[role="radiogroup"] > label p {
  font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .6px; color: var(--ql-text);
}
div[role="radiogroup"] > label:hover { transform: translate(-1px, -1px); background: var(--ql-bg2); }
div[role="radiogroup"] > label:has(input:checked) {
  background: var(--ql-cyan); border-color: var(--ql-border);
  box-shadow: 3px 3px 0 var(--ql-pink);
}
div[role="radiogroup"] > label:has(input:checked) p { color: var(--ql-on-accent) !important; }

/* ---------- Metrics, tables, alerts, containers ---------- */
[data-testid="stMetric"] {
  background: var(--ql-panel); border: 2px solid var(--ql-border);
  box-shadow: 4px 4px 0 var(--ql-shadow); padding: 12px 14px;
}
[data-testid="stMetricLabel"] p { font-size: 10.5px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--ql-muted); }
[data-testid="stMetricValue"] { font-family: 'Press Start 2P', monospace !important; font-size: 18px !important; color: var(--ql-cyan); }
[data-testid="stDataFrame"] { border: 2px solid var(--ql-border); box-shadow: 4px 4px 0 var(--ql-shadow); }
[data-testid="stAlert"] { border-radius: 0 !important; border: 2px solid var(--ql-border); box-shadow: 4px 4px 0 var(--ql-shadow); }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 0 !important; }
[data-testid="stVerticalBlockBorderWrapper"] > div[style*="border"] {
  border: 2px solid var(--ql-border) !important; border-radius: 0 !important; background: var(--ql-panel);
  box-shadow: 4px 4px 0 var(--ql-shadow);
}
.stPlotlyChart { border: 2px solid var(--ql-border); background: var(--ql-panel); box-shadow: 5px 5px 0 var(--ql-shadow); padding: 6px; }
[data-testid="stVerticalBlockBorderWrapper"] .stPlotlyChart { border: 0; box-shadow: none; padding: 0; background: transparent; }
[data-testid="stSpinner"] { color: var(--ql-yellow); }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--ql-bg2) 0%, var(--ql-bg) 100%) !important;
  border-right: 4px solid var(--ql-pink);
  box-shadow: 6px 0 0 var(--ql-shadow);
}
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarUserContent"] { padding-top: 1rem; }
[data-testid="stSidebar"] .stButton button { justify-content: flex-start; text-align: left; width: 100%; }
[data-testid="stSidebar"] .stButton button p { text-align: left; }
.ql-side-brand {
  font-family: 'Press Start 2P', monospace; font-size: 14px; color: var(--ql-text);
  text-shadow: 3px 3px 0 var(--ql-pink); display: flex; align-items: center; gap: 10px;
}
.ql-side-card {
  margin: 14px 0; padding: 14px; background: var(--ql-panel);
  border: 2px solid var(--ql-border); box-shadow: 4px 4px 0 var(--ql-shadow);
  display: flex; gap: 12px; align-items: center;
}
.ql-avatar {
  width: 44px; height: 44px; flex: 0 0 44px; display: flex; align-items: center; justify-content: center;
  background: var(--ql-pink); color: #fff; border: 2px solid var(--ql-border);
  box-shadow: 3px 3px 0 var(--ql-yellow); font-family: 'Press Start 2P', monospace; font-size: 16px;
}
.ql-side-name { font-weight: 700; font-size: 13.5px; word-break: break-all; }
.ql-side-role { font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--ql-green); margin-top: 3px; }
.ql-side-heading {
  font-family: 'Press Start 2P', monospace; font-size: 9px; letter-spacing: 1px;
  color: var(--ql-yellow); margin: 18px 0 8px 0;
}
.ql-stat-row {
  display: flex; justify-content: space-between; font-size: 12px; padding: 7px 10px;
  border: 2px solid var(--ql-border); background: var(--ql-panel-muted); margin-bottom: 6px;
}
.ql-stat-row b { color: var(--ql-cyan); }
.ql-stat-row b.green { color: var(--ql-green); }
.ql-stat-row b.red { color: var(--ql-red); }

/* ---------- Scrollbar ---------- */
::-webkit-scrollbar { width: 12px; height: 12px; }
::-webkit-scrollbar-track { background: var(--ql-bg); }
::-webkit-scrollbar-thumb { background: var(--ql-pink); border: 2px solid var(--ql-bg); }
::selection { background: var(--ql-yellow); color: var(--ql-on-accent); }

/* Hide "Press Enter to submit form / apply" hints inside inputs */
[data-testid="InputInstructions"] { display: none !important; }

/* ---------- Responsive ---------- */
[data-testid="stSidebar"] { min-height: 100vh; }
.ql-panel, .ql-metric, .ql-side-card { overflow-wrap: anywhere; }
.ql-footer { margin-top: 18px; }

@media (max-width: 1100px) {
  :root { --ql-pad: 1rem; }
  .ql-hero-title { font-size: clamp(18px, 3.6vw, 28px); }
  .ql-metric .v { font-size: 15px; }
  [data-testid="stMetricValue"] { font-size: 15px !important; }
  div[role="radiogroup"] > label { padding: 6px 10px; }
  div[role="radiogroup"] > label p { font-size: 10.5px; }
}
@media (max-width: 760px) {
  :root { --ql-pad: 0.6rem; }
  [data-testid="stMainBlockContainer"], .block-container {
    padding-top: 0.35rem !important; padding-bottom: 0.8rem !important;
  }
  .ql-ticker { font-size: 7px; padding: 5px 0; }
  .ql-brand { font-size: 12px; }
  .ql-brand-mark { width: 24px; height: 24px; font-size: 12px; }
  .ql-nav-status { font-size: 7px; padding: 5px 7px; }
  .ql-hero-title { font-size: 17px; text-shadow: 2px 2px 0 var(--ql-pink); }
  .ql-subtitle { font-size: 13px; }
  .ql-panel { padding: 12px 12px; box-shadow: 4px 4px 0 var(--ql-shadow); }
  .ql-panel[style*="min-height"] { min-height: 0 !important; }
  .ql-metric { padding: 10px 12px; }
  .ql-metric .v { font-size: 13px; }
  .ql-pill { font-size: 8px; padding: 5px 7px; }
  h1 { font-size: 16px !important; }
  h2 { font-size: 13px !important; }
  h3 { font-size: 11px !important; }
  .stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button {
    font-size: 11px; box-shadow: 3px 3px 0 var(--ql-shadow);
  }
  div[role="radiogroup"] { gap: 6px; }
  div[role="radiogroup"] > label { padding: 5px 8px; box-shadow: 2px 2px 0 var(--ql-shadow); }
  [data-testid="stSidebar"] { border-right-width: 3px; }
}
"""


def apply_theme():
    p = palette()
    st.markdown(
        f"<style>{_root_vars(p)}{_STATIC_CSS}</style>",
        unsafe_allow_html=True,
    )


def panel_metric(label, value, caption="", tone=""):
    """Retro metric card. tone: 'green', 'red' or '' (cyan)."""
    cls = tone if tone in ("green", "red") else "plain"
    st.markdown(
        '<div class="ql-metric">'
        f'<div class="ql-label">{label}</div>'
        f'<div class="v {cls}">{value}</div>'
        f'<div class="ql-caption">{caption}</div>'
        "</div>",
        unsafe_allow_html=True,
    )