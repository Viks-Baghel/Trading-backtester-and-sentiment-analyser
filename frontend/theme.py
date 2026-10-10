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
    [data-testid="stSidebar"] {{ background:var(--ql-surface); border-right:1px solid var(--ql-border); }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top:1.1rem; }}
    .block-container {{ max-width:1440px; padding-top:1.25rem; padding-bottom:2rem; }}
    #MainMenu, footer {{ visibility:hidden; }}
    h1,h2,h3,h4 {{ color:var(--ql-text); letter-spacing:-.035em; }}
    p, label {{ color:var(--ql-muted); }}
    .ql-brand {{ font-size:21px; font-weight:800; letter-spacing:-.8px; color:var(--ql-text); }}
    .ql-brand-mark {{ display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; margin-right:9px; border-radius:8px; background:var(--ql-blue); color:#101a2b; font-weight:900; }}
    .ql-kicker {{ font:600 10px 'JetBrains Mono',monospace; letter-spacing:.14em; color:var(--ql-cyan); text-transform:uppercase; }}
    .ql-hero-title {{ font-size:clamp(34px,4.3vw,58px); line-height:1.06; font-weight:800; letter-spacing:-.055em; max-width:790px; color:var(--ql-text); }}
    .ql-subtitle {{ max-width:650px; font-size:16px; line-height:1.8; color:var(--ql-muted); }}
    .ql-panel {{ background:var(--ql-panel); border:1px solid var(--ql-border); border-radius:12px; padding:18px; }}
    .ql-panel-muted {{ background:var(--ql-surface); border:1px solid var(--ql-border); border-radius:12px; padding:18px; }}
    .ql-label {{ color:var(--ql-muted); font:600 10px 'JetBrains Mono',monospace; letter-spacing:.09em; text-transform:uppercase; }}
    .ql-value {{ color:var(--ql-text); font:600 22px 'JetBrains Mono',monospace; margin-top:8px; }}
    .ql-caption {{ color:var(--ql-muted); font-size:12px; margin-top:6px; line-height:1.6; }}
    .ql-pill {{ display:inline-block; border:1px solid var(--ql-border); background:var(--ql-panel); color:var(--ql-cyan); padding:5px 8px; border-radius:5px; font:500 10px 'JetBrains Mono',monospace; letter-spacing:.04em; }}
    .ql-navline {{ border-top:1px solid var(--ql-border); border-bottom:1px solid var(--ql-border); background:var(--ql-surface); padding:8px 0; margin:4px 0 24px; }}
    div[data-testid="stButton"] button {{ border-radius:6px; min-height:40px; font-weight:650; }}
    div[data-testid="stButton"] button[kind="primary"] {{ background:var(--ql-blue); color:#101a2b; border:1px solid var(--ql-blue); }}
    div[data-testid="stButton"] button[kind="secondary"] {{ border:1px solid var(--ql-border); }}
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
