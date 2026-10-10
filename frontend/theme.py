import streamlit as st

PALETTES = {
    "Dark": {
        "bg": "#0f131c",
        "surface": "#0a0e17",
        "panel": "#181b25",
        "panel_high": "#262a34",
        "border": "#313746",
        "text": "#dfe2ef",
        "muted": "#929bad",
        "blue": "#adc6ff",
        "cyan": "#4cd7f6",
        "green": "#4edea3",
        "red": "#ff8f98",
    },
    "Light": {
        "bg": "#f4f7fb",
        "surface": "#ffffff",
        "panel": "#edf2f8",
        "panel_high": "#e3eaf3",
        "border": "#d5deea",
        "text": "#172033",
        "muted": "#617087",
        "blue": "#245fc4",
        "cyan": "#007e9b",
        "green": "#087f5b",
        "red": "#c43d51",
    },
}

def init_theme():
    if "ql_theme" not in st.session_state:
        st.session_state.ql_theme = "Dark"

def apply_theme():
    init_theme()
    p = PALETTES[st.session_state.ql_theme]
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    :root {{
      --ql-bg:{p['bg']}; --ql-surface:{p['surface']}; --ql-panel:{p['panel']};
      --ql-panel-high:{p['panel_high']}; --ql-border:{p['border']}; --ql-text:{p['text']};
      --ql-muted:{p['muted']}; --ql-blue:{p['blue']}; --ql-cyan:{p['cyan']};
      --ql-green:{p['green']}; --ql-red:{p['red']};
    }}
    html, body, [class*="css"] {{ font-family:Inter,sans-serif; }}
    .stApp {{ background:var(--ql-bg); color:var(--ql-text); }}
    [data-testid="stHeader"] {{ background:transparent; }}
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display:none !important; }}
    .block-container {{ max-width:1440px; padding-top:1.25rem; padding-bottom:2rem; }}
    #MainMenu, footer {{ visibility:hidden; }}
    h1,h2,h3,h4 {{ color:var(--ql-text); letter-spacing:-.035em; }}
    p, label {{ color:var(--ql-muted); }}
    .ql-brand {{ font-size:21px; font-weight:800; letter-spacing:-.8px; color:var(--ql-text); }}
    .ql-brand-mark {{ display:inline-flex; align-items:center; justify-content:center; width:32px; height:32px; margin-right:9px; border-radius:10px; background:linear-gradient(145deg,var(--ql-cyan),var(--ql-blue)); color:#101a2b; font-weight:900; box-shadow:0 5px 18px rgba(76,215,246,.16); }}
    .ql-nav-status {{ color:var(--ql-cyan); font:600 10px 'JetBrains Mono',monospace; letter-spacing:.12em; }}
    .ql-kicker {{ font:600 10px 'JetBrains Mono',monospace; letter-spacing:.14em; color:var(--ql-cyan); text-transform:uppercase; }}
    .ql-hero-title {{ font-size:clamp(34px,4.3vw,58px); line-height:1.06; font-weight:800; letter-spacing:-.055em; max-width:790px; color:var(--ql-text); }}
    .ql-subtitle {{ max-width:650px; font-size:16px; line-height:1.8; color:var(--ql-muted); }}
    .ql-panel {{ background:var(--ql-panel); border:1px solid var(--ql-border); border-radius:12px; padding:18px; }}
    .ql-panel-muted {{ background:var(--ql-surface); border:1px solid var(--ql-border); border-radius:12px; padding:18px; }}
    .ql-label {{ color:var(--ql-muted); font:600 10px 'JetBrains Mono',monospace; letter-spacing:.09em; text-transform:uppercase; }}
    .ql-value {{ color:var(--ql-text); font:600 22px 'JetBrains Mono',monospace; margin-top:8px; }}
    .ql-caption {{ color:var(--ql-muted); font-size:12px; margin-top:6px; line-height:1.6; }}
    .ql-pill {{ display:inline-block; border:1px solid var(--ql-border); background:var(--ql-panel); color:var(--ql-cyan); padding:5px 8px; border-radius:5px; font:500 10px 'JetBrains Mono',monospace; letter-spacing:.04em; }}
    .ql-navline {{ height:1px; border:0; background:linear-gradient(90deg,transparent,var(--ql-border) 10%,var(--ql-cyan) 50%,var(--ql-border) 90%,transparent); margin:14px 0 28px; opacity:.75; }}
    div[data-testid="stButton"] button {{ position:relative; z-index:1; border-radius:10px; min-height:42px; font-weight:650; transition:background .16s ease,border-color .16s ease,box-shadow .16s ease,transform .16s ease; }}
    div[data-testid="stButton"] button:hover {{ border-color:var(--ql-cyan); box-shadow:0 5px 16px rgba(76,215,246,.12); transform:translateY(-1px); }}
    div[data-testid="stButton"] button[kind="primary"] {{ background:linear-gradient(135deg,var(--ql-blue),var(--ql-cyan)); color:#101a2b; border:1px solid transparent; }}
    div[data-testid="stButton"] button[kind="secondary"] {{ color:var(--ql-text); border:1px solid var(--ql-border); background:var(--ql-surface); }}
    div[data-testid="stRadio"] [role="radiogroup"] {{ gap:6px; }}
    div[data-testid="stRadio"] label {{ background:var(--ql-surface); border:1px solid var(--ql-border); border-radius:9px; padding:7px 11px; transition:background .16s ease,border-color .16s ease; }}
    div[data-testid="stRadio"] label:hover {{ border-color:var(--ql-cyan); }}
    div[data-testid="stRadio"] label:has(input:checked) {{ background:var(--ql-panel-high); border-color:var(--ql-cyan); color:var(--ql-cyan); }}
    div[data-baseweb="select"] > div, div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stNumberInput"] input {{
      background:var(--ql-surface); border-color:var(--ql-border); color:var(--ql-text); border-radius:6px;
    }}
    [data-testid="stDataFrame"] {{ border:1px solid var(--ql-border); border-radius:8px; }}
    a {{ color:var(--ql-blue); }}
    .ql-footer {{ border-top:1px solid var(--ql-border); margin-top:48px; padding:22px 0 4px; color:var(--ql-muted); font-size:11px; }}
    @media(max-width:760px) {{
      .block-container {{ padding-left:1rem; padding-right:1rem; }}
      .ql-hero-title {{ font-size:35px; }}
      .ql-subtitle {{ font-size:14px; }}
      div[data-testid="stRadio"] [role="radiogroup"] {{ flex-wrap:wrap; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def panel_metric(label, value, note="", tone=None):
    color = {"green":"var(--ql-green)", "red":"var(--ql-red)", "blue":"var(--ql-blue)"}.get(tone, "var(--ql-text)")
    st.markdown(f"""
    <div class="ql-panel">
      <div class="ql-label">{label}</div>
      <div class="ql-value" style="color:{color}">{value}</div>
      <div class="ql-caption">{note}</div>
    </div>
    """, unsafe_allow_html=True)
