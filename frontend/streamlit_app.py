import os
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from theme import apply_theme, init_theme, panel_metric

API_URL = os.getenv("QUANTLAB_API_URL", "http://127.0.0.1:8000").rstrip("/")
AUTH_URL = f"{API_URL}/api/v1/auth"
STRATEGIES = {
    "Technical Strategy": "technical",
    "FinBERT Sentiment": "sentiment",
    "AI Hybrid + ARIMA": "hybrid_arima",
    "AI Hybrid + LSTM": "hybrid_lstm",
}

st.set_page_config(
    page_title="QuantLab | Systematic Research",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
init_theme()

# Public navigation and theme control. Keep route state separate from widget state.
if "public_nav" not in st.session_state:
    st.session_state.public_nav = "Home"

def navigate_to(route):
    st.session_state.public_nav = route

def toggle_theme():
    st.session_state.ql_theme = "Light" if st.session_state.ql_theme == "Dark" else "Dark"

def clear_auth_session():
    for key in ("ql_access_token", "ql_user", "backtest_result"):
        st.session_state.pop(key, None)
    st.session_state.public_nav = "Home"

nav_left, nav_mid, nav_right = st.columns([2.2, 4.5, 3.0], vertical_alignment="center")
with nav_left:
    st.markdown(
        '<div class="ql-brand"><span class="ql-brand-mark">Q</span>QUANTLAB</div>'
        '<div class="ql-label" style="margin-left:39px;margin-top:-2px">SYSTEMATIC RESEARCH</div>',
        unsafe_allow_html=True,
    )
with nav_mid:
    public_pages = ["Home", "Products", "About", "Contact"]
    nav_cols = st.columns(len(public_pages))
    for nav_col, page in zip(nav_cols, public_pages):
        with nav_col:
            st.button(page, key=f"nav_{page}", type="primary" if st.session_state.public_nav == page else "secondary",
                      use_container_width=True, on_click=navigate_to, args=(page,))
with nav_right:
    if st.session_state.get("ql_access_token") and st.session_state.get("ql_user"):
        theme_col, workspace_col, logout_col = st.columns([0.7, 1.4, 1.0], vertical_alignment="center")
        with theme_col:
            st.button("☼ / ◐", key="theme_auth", help="Switch theme", use_container_width=True, on_click=toggle_theme)
        with workspace_col:
            st.button("Workspace", key="nav_workspace", type="primary", use_container_width=True, on_click=navigate_to, args=("Workspace",))
        with logout_col:
            st.button("Log out", key="nav_logout", use_container_width=True, on_click=clear_auth_session)
    else:
        theme_col, login_col, signup_col = st.columns([0.7, 1, 1.2], vertical_alignment="center")
        with theme_col:
            st.button("☼ / ◐", key="theme_public", help="Switch theme", use_container_width=True, on_click=toggle_theme)
        with login_col:
            st.button("Log in", key="nav_login", use_container_width=True, on_click=navigate_to, args=("Login",))
        with signup_col:
            st.button("Sign up", key="nav_signup", type="primary", use_container_width=True, on_click=navigate_to, args=("Sign up",))

apply_theme()
st.markdown('<div class="ql-navline"></div>', unsafe_allow_html=True)

def footer():
    st.markdown('<div class="ql-footer">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([2.2, 1, 1, 1])
    with f1:
        st.markdown("**QUANTLAB**")
        st.caption("Research tools for systematic strategy evaluation.")
    with f2:
        st.caption("PLATFORM")
        st.markdown("Products")
        st.markdown("About")
    with f3:
        st.caption("COMPANY")
        st.markdown("Contact")
        st.markdown("Privacy Policy")
    with f4:
        st.caption("LEGAL")
        st.markdown("Terms of Use")
        st.markdown("Risk Disclosure")
    st.markdown(
        '<div style="border-top:1px solid var(--ql-border);padding-top:12px;margin-top:10px">'
        '© 2026 QuantLab · For research and educational use. Historical backtests do not guarantee future results. '
        'This platform does not execute live trades.</div></div>',
        unsafe_allow_html=True,
    )

def hero_visual():
    # Decorative market visualization only: not presented as live market data.
    fig = go.Figure()
    x = list(range(80))
    y = [100 + i * 0.22 + 2.7 * __import__("math").sin(i / 5.0) + 1.2 * __import__("math").sin(i / 2.8) for i in x]
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines", line=dict(color="#4cd7f6", width=2),
        fill="tozeroy", fillcolor="rgba(76,215,246,0.08)",
        hoverinfo="skip", name="Illustrative curve"
    ))
    fig.update_layout(
        template="plotly_dark", height=260, margin=dict(l=4,r=4,t=20,b=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def public_home():
    st.markdown(
        '<div class="ql-pill">AI-ASSISTED QUANTITATIVE RESEARCH</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    left, right = st.columns([1.25, 1], gap="large", vertical_alignment="center")
    with left:
        st.markdown(
            '<div class="ql-hero-title">Build strategies.<br>Test assumptions.<br><span style="color:var(--ql-cyan)">Measure what matters.</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="ql-subtitle">A focused research workspace for algorithmic backtesting, financial-news sentiment, '
            'forecasting experiments, and risk analysis — built to help you evaluate strategies with evidence.</p>',
            unsafe_allow_html=True,
        )
        a, b = st.columns([1.2, 1])
        with a:
            if st.button("Explore the platform  →", type="primary", use_container_width=True):
                st.session_state.public_nav = "Products"
                st.rerun()
        with b:
            if st.button("View research workflow", use_container_width=True):
                st.session_state.public_nav = "About"
                st.rerun()
        st.write("")
        st.markdown(
            '<div class="ql-label">TECHNICAL INDICATORS · FINBERT SENTIMENT · ARIMA · LSTM</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="ql-panel">', unsafe_allow_html=True)
        st.markdown(
            '<div style="display:flex;justify-content:space-between;align-items:center">'
            '<div><div class="ql-label">RESEARCH PREVIEW</div><div style="font-weight:700;margin-top:5px">Strategy evaluation workspace</div></div>'
            '<span class="ql-pill">ILLUSTRATIVE</span></div>',
            unsafe_allow_html=True,
        )
        hero_visual()
        st.markdown(
            '<div class="ql-caption">Illustrative visual only. Actual portfolio charts and metrics appear after a backtest is run.</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown('<div class="ql-kicker">ONE WORKSPACE, FOUR RESEARCH LENSES</div>', unsafe_allow_html=True)
    st.markdown("## From market data to measurable decisions")
    cards = st.columns(4)
    feature_data = [
        ("01", "Strategy Backtesting", "Evaluate entry/exit rules on historical price data."),
        ("02", "News Sentiment", "Analyze financial headlines with a FinBERT model."),
        ("03", "Forecasting", "Experiment with ARIMA and LSTM price forecasts."),
        ("04", "Risk Analytics", "Review returns, drawdown, Sharpe ratio and trade outcomes."),
    ]
    for col, (num, title, desc) in zip(cards, feature_data):
        with col:
            st.markdown(
                f'<div class="ql-panel" style="height:170px"><div class="ql-kicker">{num}</div>'
                f'<div style="font-weight:700;font-size:16px;margin-top:17px">{title}</div>'
                f'<div class="ql-caption" style="font-size:13px;margin-top:10px">{desc}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown('<div class="ql-kicker">RESEARCH PRINCIPLE</div>', unsafe_allow_html=True)
        st.markdown("### Results before claims")
        st.markdown(
            "Every strategy should be judged on the same historical period, with transparent assumptions, "
            "trade-level detail and risk metrics. A forecast score alone is not proof of a profitable strategy."
        )
    with c2:
        st.markdown('<div class="ql-panel-muted">', unsafe_allow_html=True)
        st.markdown("**Designed for experimentation**")
        st.markdown("- Compare technical and AI-assisted strategies")
        st.markdown("- Inspect trade history and signal explanations")
        st.markdown("- Keep research separate from live execution")
        st.markdown("</div>", unsafe_allow_html=True)

def public_products():
    st.markdown('<div class="ql-kicker">PLATFORM</div>', unsafe_allow_html=True)
    st.title("Research tools")
    st.markdown("A practical set of tools for testing and understanding systematic strategies.")
    for title, body in [
        ("Backtest Engine", "Run historical simulations using the connected FastAPI engine and inspect portfolio performance."),
        ("Technical Strategies", "Explore indicator-driven rules using moving averages, RSI, MACD and other supported indicators."),
        ("FinBERT Sentiment", "Score financial headlines and align sentiment with market dates for research."),
        ("ARIMA & LSTM Forecasting", "Experiment with statistical and sequence-based forecasts; compare prediction errors and directional accuracy."),
        ("Trade Journal & Risk", "Review completed trades, signal reasons, returns, win rate and drawdown."),
    ]:
        st.markdown(f'<div class="ql-panel" style="margin-bottom:12px"><b>{title}</b><div class="ql-caption">{body}</div></div>', unsafe_allow_html=True)

def public_about():
    st.markdown('<div class="ql-kicker">ABOUT QUANTLAB</div>', unsafe_allow_html=True)
    st.title("Research with transparency at its core")
    st.markdown(
        "QuantLab is an educational algorithmic-trading research project focused on connecting historical market data, "
        "rule-based strategies, financial-news sentiment and forecasting models in one workflow."
    )
    st.markdown("### Our principles")
    st.markdown("- **Reproducibility:** compare models over consistent date ranges and assumptions.")
    st.markdown("- **Explainability:** inspect signals and completed trades, not just headline returns.")
    st.markdown("- **Risk awareness:** show drawdowns and negative outcomes as clearly as positive ones.")
    st.markdown("- **Honest reporting:** no guaranteed-return claims and no invented market statistics.")
    st.info("QuantLab is a research and educational platform, not a broker, investment adviser or live order execution system.")

def public_contact():
    st.markdown('<div class="ql-kicker">CONTACT</div>', unsafe_allow_html=True)
    st.title("Contact the team")
    st.markdown("Send a message about the project, technical issues or collaboration.")
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        topic = st.selectbox("Topic", ["General enquiry", "Technical support", "Research collaboration", "Feedback"])
        message = st.text_area("Message", height=140)
        submitted = st.form_submit_button("Submit enquiry", type="primary")
    if submitted:
        if not name.strip() or not email.strip() or not message.strip():
            st.error("Please complete your name, email and message.")
        else:
            st.warning(
                f"The contact form UI is not connected to a message-delivery endpoint yet. "
                f"Your selected topic ({topic}) has not been sent."
            )

def _api_error_message(response):
    try:
        detail = response.json().get("detail", "")
    except (ValueError, AttributeError):
        detail = ""
    return str(detail or f"Request failed (HTTP {response.status_code}).")

def _load_current_user(token):
    response = requests.get(
        f"{AUTH_URL}/me", headers={"Authorization": f"Bearer {token}"}, timeout=15
    )
    if response.status_code == 401:
        return None
    response.raise_for_status()
    return response.json()

def _save_authenticated_session(token):
    user = _load_current_user(token)
    if not user:
        raise ValueError("The API returned a token, but the session could not be verified. Please log in again.")
    st.session_state.ql_access_token = token
    st.session_state.ql_user = user
    st.session_state.public_nav = "Workspace"

def auth_screen(mode):
    is_signup = mode == "Sign up"
    left, right = st.columns([1.05, 1], gap="large", vertical_alignment="center")
    with left:
        st.markdown('<div class="ql-kicker">QUANTLAB ACCOUNT</div>', unsafe_allow_html=True)
        st.markdown('<div class="ql-hero-title" style="font-size:clamp(32px,3.5vw,46px)">' +
                    ("Your research desk, in one place." if is_signup else "Welcome back to your research desk.") + '</div>', unsafe_allow_html=True)
        st.markdown('<p class="ql-subtitle">Sign in to run historical strategy experiments, review risk metrics, and keep your research workflow together.</p>', unsafe_allow_html=True)
        st.markdown('<div class="ql-panel-muted"><div class="ql-label">ACCOUNT SECURITY</div><div style="font-weight:650;margin-top:8px">Credentials are sent to your FastAPI authentication endpoint.</div><div class="ql-caption">QuantLab stores the returned access token only in this Streamlit session. Logging out clears the local session.</div></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="ql-panel">', unsafe_allow_html=True)
        st.markdown("### " + ("Create your account" if is_signup else "Sign in"))
        st.caption("Use your registered email address and password.")
        with st.form(f"auth_{mode}_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="e.g. vikash_baghel", help="Required for a new account.") if is_signup else None
            email = st.text_input("Email address", placeholder="you@example.com", autocomplete="email")
            password = st.text_input("Password", type="password", autocomplete="new-password" if is_signup else "current-password")
            confirm = st.text_input("Confirm password", type="password", autocomplete="new-password") if is_signup else None
            submit_label = "Create account" if is_signup else "Sign in to QuantLab"
            submitted = st.form_submit_button(submit_label, type="primary", use_container_width=True)
        if submitted:
            clean_email = email.strip().lower()
            if not clean_email or "@" not in clean_email:
                st.error("Enter a valid email address.")
            elif not password:
                st.error("Enter your password.")
            elif is_signup and (not username or len(username.strip()) < 3):
                st.error("Choose a username with at least 3 characters.")
            elif is_signup and password != confirm:
                st.error("The passwords do not match.")
            elif is_signup and len(password) < 8:
                st.error("Use a password with at least 8 characters.")
            else:
                try:
                    with st.spinner("Creating your account…" if is_signup else "Signing you in…"):
                        if is_signup:
                            register_response = requests.post(
                                f"{AUTH_URL}/register",
                                json={"username": username.strip(), "email": clean_email, "password": password},
                                timeout=20,
                            )
                            if not register_response.ok:
                                st.error(_api_error_message(register_response))
                                return
                            login_response = requests.post(
                                f"{AUTH_URL}/login", json={"email": clean_email, "password": password}, timeout=20
                            )
                            if not login_response.ok:
                                st.success("Account created successfully. Please sign in with your new credentials.")
                                st.session_state.public_nav = "Login"
                                st.rerun()
                            token = login_response.json().get("access_token")
                        else:
                            login_response = requests.post(
                                f"{AUTH_URL}/login", json={"email": clean_email, "password": password}, timeout=20
                            )
                            if not login_response.ok:
                                st.error(_api_error_message(login_response))
                                return
                            token = login_response.json().get("access_token")
                        if not token:
                            st.error("The authentication API did not return an access token. Check TokenResponse.")
                        else:
                            _save_authenticated_session(token)
                            st.success("You're signed in. Opening your workspace…")
                            st.rerun()
                except requests.ConnectionError:
                    st.error(f"Cannot reach the authentication API at {AUTH_URL}. Start FastAPI and try again.")
                except requests.Timeout:
                    st.error("The request timed out. Check that the API is running, then try again.")
                except requests.RequestException as exc:
                    st.error(f"Authentication request failed: {exc}")
                except (ValueError, KeyError) as exc:
                    st.error(str(exc))
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")
        if is_signup:
            st.caption("Already have an account?")
            if st.button("Go to sign in", key="switch_to_login", use_container_width=True):
                st.session_state.public_nav = "Login"
                st.rerun()
        else:
            st.caption("New to QuantLab?")
            if st.button("Create an account", key="switch_to_signup", use_container_width=True):
                st.session_state.public_nav = "Sign up"
                st.rerun()

def app_workspace():
    # Workspace entry requires a real API-issued token and a verified /me response.
    token = st.session_state.get("ql_access_token")
    user = st.session_state.get("ql_user")
    if not token or not user:
        st.markdown('<div class="ql-kicker">PRIVATE WORKSPACE</div>', unsafe_allow_html=True)
        st.title("Your research workspace")
        st.markdown("Sign in to access your strategy experiments, backtest results, and research history.")
        if st.button("Sign in to continue", type="primary", use_container_width=True):
            st.session_state.public_nav = "Login"
            st.rerun()
        st.caption("Workspace access is verified by the FastAPI authentication service.")
        return

    # Revalidate the token when the user enters or interacts with the workspace.
    try:
        verified_user = _load_current_user(token)
        if verified_user is None:
            clear_auth_session()
            st.warning("Your session has expired. Please sign in again.")
            st.session_state.public_nav = "Login"
            if st.button("Return to sign in", type="primary"):
                st.rerun()
            return
        st.session_state.ql_user = verified_user
    except requests.RequestException:
        st.warning("Could not verify your session because the API is temporarily unreachable. Some workspace actions may fail until the connection returns.")

    with st.sidebar:
        st.markdown('<div class="ql-brand"><span class="ql-brand-mark">Q</span>QUANTLAB</div>', unsafe_allow_html=True)
        st.caption("SYSTEMATIC RESEARCH")
        st.markdown("---")
        workspace_page = st.radio(
            "Workspace",
            ["Overview", "Strategy Builder", "Backtest Results", "Trade History", "Sentiment Analysis", "Forecasting", "Profile & Settings"],
        )
        st.markdown("---")
        st.caption(f"Theme: {st.session_state.ql_theme}")
        if st.button("Switch theme", use_container_width=True):
            st.session_state.ql_theme = "Light" if st.session_state.ql_theme == "Dark" else "Dark"
            st.rerun()
        if st.button("Log out", use_container_width=True):
            clear_auth_session()
            st.rerun()

    st.markdown(
        '<div style="display:flex;justify-content:space-between;align-items:center">'
        '<div><div class="ql-kicker">PRIVATE RESEARCH TERMINAL</div><h1 style="margin:4px 0">Workspace</h1></div>'
        '<span class="ql-pill">AUTHENTICATED SESSION</span></div>',
        unsafe_allow_html=True,
    )
    current_user = st.session_state.get("ql_user", {})
    st.caption(f"Signed in as {current_user.get('username') or current_user.get('email') or 'QuantLab user'} · Research only — no live orders are placed.")

    if workspace_page == "Overview":
        st.markdown("### Run a backtest")
        l, r = st.columns([1, 1.4], gap="large")
        with l:
            symbol = st.selectbox("Instrument", ["RELIANCE.NS", "TCS.NS", "INFY.NS", "AAPL"], key="ws_symbol")
            strategy_name = st.selectbox("Strategy", list(STRATEGIES.keys()), key="ws_strategy")
            d1, d2 = st.columns(2)
            with d1:
                start = st.date_input("Start date", value=pd.Timestamp("2026-01-01").date(), key="ws_start")
            with d2:
                end = st.date_input("End date", value=pd.Timestamp("2026-09-05").date(), key="ws_end")
            capital = st.number_input("Initial capital (₹)", min_value=1000.0, value=100000.0, step=10000.0, key="ws_capital")
            run = st.button("Execute backtest", type="primary", use_container_width=True)
            if run:
                if start >= end:
                    st.error("End date must be later than start date.")
                else:
                    try:
                        with st.spinner("Running the selected model..."):
                            response = requests.post(
                                f"{API_URL}/backtests/run",
                                json={
                                    "symbol": symbol,
                                    "start_date": start.isoformat(),
                                    "end_date": end.isoformat(),
                                    "initial_capital": float(capital),
                                    "strategy": STRATEGIES[strategy_name],
                                },
                                headers={"Authorization": f"Bearer {st.session_state.get('ql_access_token', '')}"},
                                timeout=900,
                            )
                        if response.ok:
                            payload = response.json()
                            payload["initial_capital"] = float(capital)
                            payload["selected_strategy_name"] = strategy_name
                            st.session_state.backtest_result = payload
                            st.success("Backtest completed.")
                            st.rerun()
                        else:
                            st.error(f"API error {response.status_code}: {response.text[:800]}")
                    except requests.RequestException as exc:
                        st.error(f"Cannot connect to FastAPI at {API_URL}: {exc}")
        with r:
            result = st.session_state.get("backtest_result")
            if not result:
                st.markdown('<div class="ql-panel"><div class="ql-label">PORTFOLIO OVERVIEW</div><h3>No run selected</h3><div class="ql-caption">Execute a backtest to display real metrics and the equity curve here.</div></div>', unsafe_allow_html=True)
            else:
                metrics = result.get("metrics", {})
                initial = result.get("initial_capital", 100000)
                final = metrics.get("final_value")
                ret = metrics.get("total_return")
                sharpe = metrics.get("sharpe_ratio")
                dd = metrics.get("max_drawdown")
                m1, m2 = st.columns(2)
                with m1:
                    panel_metric("Portfolio value", f"₹{float(final):,.2f}" if final is not None else "N/A", "Final simulated value")
                with m2:
                    panel_metric("Total return", f"{float(ret):.2f}%" if ret is not None else "N/A", f"Initial ₹{initial:,.0f}", "green" if ret is not None and ret >= 0 else "red")
                m3, m4 = st.columns(2)
                with m3:
                    panel_metric("Sharpe ratio", f"{float(sharpe):.3f}" if sharpe is not None else "N/A", "Annualized, as returned by API")
                with m4:
                    panel_metric("Max drawdown", f"{float(dd):.2f}%" if dd is not None else "N/A", "Peak-to-trough decline", "red")
                curve = pd.DataFrame(result.get("equity_curve", []))
                if not curve.empty and "date" in curve and "portfolio_value" in curve:
                    curve["date"] = pd.to_datetime(curve["date"], errors="coerce")
                    curve["portfolio_value"] = pd.to_numeric(curve["portfolio_value"], errors="coerce")
                    curve = curve.dropna(subset=["date", "portfolio_value"])
                    fig = go.Figure(go.Scatter(x=curve["date"], y=curve["portfolio_value"], mode="lines", line=dict(color="#4cd7f6", width=2), name="Equity"))
                    fig.update_layout(template="plotly_dark" if st.session_state.ql_theme == "Dark" else "plotly_white", height=300, margin=dict(l=5,r=5,t=15,b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
    else:
        result = st.session_state.get("backtest_result", {})
        if workspace_page == "Strategy Builder":
            st.markdown("### Strategy Builder")
            st.markdown("Choose among strategies currently supported by the backend. Strategy parameter editing can be added once those parameters are exposed by the API.")
            st.write(list(STRATEGIES.keys()))
        elif workspace_page == "Backtest Results":
            st.markdown("### Backtest Results")
            if result:
                st.json(result.get("metrics", {}))
            else:
                st.info("Run a backtest from Overview first.")
        elif workspace_page == "Trade History":
            st.markdown("### Trade History")
            trades = pd.DataFrame(result.get("trades", [])) if result else pd.DataFrame()
            if trades.empty:
                st.info("No trade history available yet.")
            else:
                st.dataframe(trades, use_container_width=True, hide_index=True)
        elif workspace_page == "Sentiment Analysis":
            st.markdown("### Sentiment Analysis")
            st.markdown("FinBERT sentiment results will appear here when the API returns article-level or daily sentiment payloads.")
            st.info("This page does not invent headline sentiment or scores.")
        elif workspace_page == "Forecasting":
            st.markdown("### Forecasting")
            st.markdown("ARIMA and LSTM outputs can be displayed here when forecast series and accuracy metrics are exposed by the backend.")
            st.info("Forecast metrics are not inferred from the portfolio return.")
        elif workspace_page == "Profile & Settings":
            st.markdown("### Profile & Settings")
            user = st.session_state.get("ql_user", {})
            st.text_input("Username", value=str(user.get("username", "—")), disabled=True)
            st.text_input("Email", value=str(user.get("email", "—")), disabled=True)
            st.text_input("Account ID", value=str(user.get("id", "—")), disabled=True)
            st.caption("Profile details are read from GET /api/v1/auth/me. Profile editing is not exposed by the current API.")

# Routing
route = st.session_state.get("public_nav", "Home")
if route in ["Login", "Sign up"]:
    auth_screen(route)
    footer()
elif route == "Workspace":
    app_workspace()
    footer()
else:
    if route == "Home":
        public_home()
    elif route == "Products":
        public_products()
    elif route == "About":
        public_about()
    elif route == "Contact":
        public_contact()
    footer()

# Clear end-of-page call to action without bypassing authentication.
if not st.session_state.get("ql_access_token"):
    st.markdown('<div style="margin-top:14px;text-align:center" class="ql-caption">Ready to evaluate a strategy with your own settings?</div>', unsafe_allow_html=True)
    if st.button("Sign in to open the workspace", key="open_workspace_footer", type="primary"):
        st.session_state.public_nav = "Login"
        st.rerun()
