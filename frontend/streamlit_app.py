import os
import math
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from streamlit_cookies_manager import EncryptedCookieManager
from theme import apply_theme, init_theme, panel_metric

API_URL = os.getenv(
    "QUANTLAB_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")
AUTH_URL = f"{API_URL}/api/v1/auth"
WORKSPACE_STATE_URL = f"{API_URL}/api/v1/workspace/state"

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
apply_theme()

# ---------------------------------------------------------
# PERSISTENT AUTHENTICATION
# ---------------------------------------------------------

def _load_current_user(token):
    response = requests.get(
        f"{AUTH_URL}/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )

    if response.status_code == 401:
        return None

    response.raise_for_status()
    return response.json()


COOKIE_PASSWORD = os.getenv("QUANTLAB_COOKIE_PASSWORD")

if not COOKIE_PASSWORD:
    st.error(
        "QUANTLAB_COOKIE_PASSWORD is missing. "
        "Add it to your .env and load the environment variables."
    )
    st.stop()

cookies = EncryptedCookieManager(
    prefix="quantlab/",
    password=COOKIE_PASSWORD,
)

if not cookies.ready():
    st.stop()


# Define workspace pages and helpers BEFORE restoring a session.
# This avoids calling load_workspace_page before it exists.
WORKSPACE_PAGES = [
    "Overview",
    "Strategy Builder",
    "Backtest Results",
    "Trade History",
    "Sentiment Analysis",
    "Forecasting",
    "Profile & Settings",
]


def load_workspace_page(token):
    response = requests.get(
        WORKSPACE_STATE_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    response.raise_for_status()

    page = response.json().get("current_page", "Overview")
    return page if page in WORKSPACE_PAGES else "Overview"


def save_workspace_page(token, page):
    if page not in WORKSPACE_PAGES:
        page = "Overview"

    response = requests.put(
        WORKSPACE_STATE_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"current_page": page},
        timeout=10,
    )
    response.raise_for_status()


def persist_workspace_navigation():
    token = st.session_state.get("ql_access_token")
    page = st.session_state.get("workspace_nav", "Overview")

    if not token or page not in WORKSPACE_PAGES:
        return

    try:
        save_workspace_page(token, page)
    except requests.RequestException:
        # Navigation still works if the state endpoint is unavailable.
        st.session_state["workspace_state_save_pending"] = True
    else:
        st.session_state["workspace_state_save_pending"] = False


# Restore the token after a browser refresh or Streamlit rerun.
if not st.session_state.get("ql_access_token"):
    saved_token = cookies.get("access_token")

    if saved_token:
        try:
            restored_user = _load_current_user(saved_token)

            if restored_user:
                st.session_state["ql_access_token"] = saved_token
                st.session_state["ql_user"] = restored_user
                st.session_state["public_nav"] = "Workspace"

                try:
                    st.session_state["workspace_nav"] = (
                        load_workspace_page(saved_token)
                    )
                except requests.RequestException:
                    st.session_state["workspace_nav"] = "Overview"
            else:
                # The API rejected the saved token.
                cookies["access_token"] = ""
                cookies.save()

        except requests.RequestException:
            st.warning(
                "Unable to verify your saved session because the API "
                "is unavailable. Please check the backend connection."
            )


# ---------------------------------------------------------
# NAVIGATION AND SESSION STATE
# ---------------------------------------------------------

if "public_nav" not in st.session_state:
    st.session_state["public_nav"] = "Home"

if "workspace_nav" not in st.session_state:
    st.session_state["workspace_nav"] = "Overview"


def navigate_to(route):
    st.session_state["public_nav"] = route


def navigate_workspace(page):
    if page not in WORKSPACE_PAGES:
        page = "Overview"

    st.session_state["workspace_nav"] = page
    st.session_state["public_nav"] = "Workspace"
    persist_workspace_navigation()


def toggle_theme():
    current = st.session_state.get("ql_theme", "Dark")
    st.session_state["ql_theme"] = (
        "Light" if current == "Dark" else "Dark"
    )


def clear_auth_session():
    """Clear both the browser cookie and Streamlit session."""
    cookies["access_token"] = ""
    cookies.save()

    for key in (
        "ql_access_token",
        "ql_user",
        "backtest_result",
        "workspace_state_save_pending",
    ):
        st.session_state.pop(key, None)

    st.session_state["public_nav"] = "Home"
    st.session_state["workspace_nav"] = "Overview"


def is_authenticated():
    return bool(
        st.session_state.get("ql_access_token")
        and st.session_state.get("ql_user")
    )


# ---------------------------------------------------------
# NAVBAR
# ---------------------------------------------------------

_authenticated = is_authenticated()
_route = st.session_state.get("public_nav", "Home")

if _authenticated and _route == "Workspace":
    nav_left, nav_mid, nav_right = st.columns(
        [2.2, 3.8, 2.4],
        vertical_alignment="center",
    )

    with nav_left:
        st.markdown(
            '<div class="ql-brand">'
            '<span class="ql-brand-mark">Q</span>QUANTLAB'
            '</div>'
            '<div class="ql-label" '
            'style="margin-left:39px;margin-top:-2px">'
            'SYSTEMATIC RESEARCH</div>',
            unsafe_allow_html=True,
        )

    with nav_mid:
        current_user = st.session_state.get("ql_user", {})

        st.markdown(
            '<div class="ql-nav-status">'
            'PRIVATE RESEARCH WORKSPACE</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "Signed in · "
            f"{current_user.get('username') or current_user.get('email') or 'User'}"
        )

    with nav_right:
        theme_col, logout_col = st.columns(
            [1, 1.6],
            vertical_alignment="center",
        )

        with theme_col:
            st.button(
                "☼ / ◐",
                key="theme_auth_top",
                help="Switch theme",
                use_container_width=True,
                on_click=toggle_theme,
            )

        with logout_col:
            st.button(
                "Log out",
                key="nav_logout_top",
                type="primary",
                use_container_width=True,
                on_click=clear_auth_session,
            )

    st.radio(
        "Workspace navigation",
        options=WORKSPACE_PAGES,
        horizontal=True,
        label_visibility="collapsed",
        key="workspace_nav",
        on_change=persist_workspace_navigation,
    )

else:
    nav_left, nav_mid, nav_right = st.columns(
        [2.0, 4.4, 3.0],
        vertical_alignment="center",
    )

    with nav_left:
        st.markdown(
            '<div class="ql-brand">'
            '<span class="ql-brand-mark">Q</span>QUANTLAB'
            '</div>'
            '<div class="ql-label" '
            'style="margin-left:39px;margin-top:-2px">'
            'SYSTEMATIC RESEARCH</div>',
            unsafe_allow_html=True,
        )

    with nav_mid:
        public_pages = ["Home", "Products", "About", "Contact"]
        nav_cols = st.columns(len(public_pages))

        for nav_col, page in zip(nav_cols, public_pages):
            with nav_col:
                st.button(
                    page,
                    key=f"nav_{page}",
                    type=(
                        "primary"
                        if st.session_state["public_nav"] == page
                        else "secondary"
                    ),
                    use_container_width=True,
                    on_click=navigate_to,
                    args=(page,),
                )

    with nav_right:
        theme_col, account_col = st.columns(
            [0.75, 2.2],
            vertical_alignment="center",
        )

        with theme_col:
            st.button(
                "☼ / ◐",
                key="theme_public_top",
                help="Switch theme",
                use_container_width=True,
                on_click=toggle_theme,
            )

        with account_col:
            if _authenticated:
                account_actions = st.columns(
                    [1.15, 1],
                    vertical_alignment="center",
                )

                with account_actions[0]:
                    st.button(
                        "Workspace",
                        key="nav_workspace_top",
                        type="primary",
                        use_container_width=True,
                        on_click=navigate_to,
                        args=("Workspace",),
                    )

                with account_actions[1]:
                    st.button(
                        "Log out",
                        key="nav_logout_top_public",
                        use_container_width=True,
                        on_click=clear_auth_session,
                    )

            else:
                account_actions = st.columns(
                    [1, 1.15],
                    vertical_alignment="center",
                )

                with account_actions[0]:
                    st.button(
                        "Log in",
                        key="nav_login",
                        use_container_width=True,
                        on_click=navigate_to,
                        args=("Login",),
                    )

                with account_actions[1]:
                    st.button(
                        "Sign up",
                        key="nav_signup",
                        type="primary",
                        use_container_width=True,
                        on_click=navigate_to,
                        args=("Sign up",),
                    )

st.markdown(
    '<div class="ql-navline"></div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

def footer():
    st.markdown(
        '<div class="ql-footer">',
        unsafe_allow_html=True,
    )

    f1, f2, f3, f4 = st.columns([2.2, 1, 1, 1])

    with f1:
        st.markdown("**QUANTLAB**")
        st.caption(
            "Research tools for systematic strategy evaluation."
        )

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
        '<div style="border-top:1px solid var(--ql-border);'
        'padding-top:12px;margin-top:10px">'
        '© 2026 QuantLab · For research and educational use. '
        'Historical backtests do not guarantee future results. '
        'This platform does not execute live trades.'
        '</div></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# PUBLIC LANDING PAGE
# ---------------------------------------------------------

def hero_visual():
    # Decorative illustration, not live market data.
    fig = go.Figure()
    x = list(range(80))
    y = [
        100
        + i * 0.22
        + 2.7 * math.sin(i / 5.0)
        + 1.2 * math.sin(i / 2.8)
        for i in x
    ]

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color="#4cd7f6", width=2),
            fill="tozeroy",
            fillcolor="rgba(76,215,246,0.08)",
            hoverinfo="skip",
            name="Illustrative curve",
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=260,
        margin=dict(l=4, r=4, t=20, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )


def public_home():
    st.markdown(
        '<div class="ql-pill">'
        'AI-ASSISTED QUANTITATIVE RESEARCH'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    left, right = st.columns(
        [1.25, 1],
        gap="large",
        vertical_alignment="center",
    )

    with left:
        st.markdown(
            '<div class="ql-hero-title">'
            'Build strategies.<br>Test assumptions.<br>'
            '<span style="color:var(--ql-cyan)">'
            'Measure what matters.</span></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p class="ql-subtitle">'
            'A focused research workspace for algorithmic backtesting, '
            'financial-news sentiment, forecasting experiments, and '
            'risk analysis — built to help you evaluate strategies '
            'with evidence.</p>',
            unsafe_allow_html=True,
        )

        a, b = st.columns([1.2, 1])

        with a:
            if st.button(
                "Explore the platform →",
                type="primary",
                use_container_width=True,
            ):
                st.session_state["public_nav"] = "Products"
                st.rerun()

        with b:
            if st.button(
                "View research workflow",
                use_container_width=True,
            ):
                st.session_state["public_nav"] = "About"
                st.rerun()

        st.write("")

        st.markdown(
            '<div class="ql-label">'
            'TECHNICAL INDICATORS · FINBERT SENTIMENT · ARIMA · LSTM'
            '</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="ql-panel">',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="display:flex;justify-content:space-between;'
            'align-items:center">'
            '<div><div class="ql-label">RESEARCH PREVIEW</div>'
            '<div style="font-weight:700;margin-top:5px">'
            'Strategy evaluation workspace</div></div>'
            '<span class="ql-pill">ILLUSTRATIVE</span></div>',
            unsafe_allow_html=True,
        )

        hero_visual()

        st.markdown(
            '<div class="ql-caption">'
            'Illustrative visual only. Actual portfolio charts and '
            'metrics appear after a backtest is run.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")

    st.markdown(
        '<div class="ql-kicker">ONE WORKSPACE, FOUR RESEARCH LENSES</div>',
        unsafe_allow_html=True,
    )
    st.markdown("## From market data to measurable decisions")

    cards = st.columns(4)

    feature_data = [
        (
            "01",
            "Strategy Backtesting",
            "Evaluate entry/exit rules on historical price data.",
        ),
        (
            "02",
            "News Sentiment",
            "Analyze financial headlines with a FinBERT model.",
        ),
        (
            "03",
            "Forecasting",
            "Experiment with ARIMA and LSTM price forecasts.",
        ),
        (
            "04",
            "Risk Analytics",
            "Review returns, drawdown, Sharpe ratio and trade outcomes.",
        ),
    ]

    for col, (num, title, desc) in zip(cards, feature_data):
        with col:
            st.markdown(
                f'<div class="ql-panel" style="height:170px">'
                f'<div class="ql-kicker">{num}</div>'
                f'<div style="font-weight:700;font-size:16px;'
                f'margin-top:17px">{title}</div>'
                f'<div class="ql-caption" '
                f'style="font-size:13px;margin-top:10px">'
                f'{desc}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")

    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        st.markdown(
            '<div class="ql-kicker">RESEARCH PRINCIPLE</div>',
            unsafe_allow_html=True,
        )
        st.markdown("### Results before claims")
        st.markdown(
            "Every strategy should be judged on the same historical "
            "period, with transparent assumptions, trade-level detail "
            "and risk metrics. A forecast score alone is not proof "
            "of a profitable strategy."
        )

    with c2:
        st.markdown(
            '<div class="ql-panel-muted">',
            unsafe_allow_html=True,
        )
        st.markdown("**Designed for experimentation**")
        st.markdown("- Compare technical and AI-assisted strategies")
        st.markdown("- Inspect trade history and signal explanations")
        st.markdown("- Keep research separate from live execution")
        st.markdown("</div>", unsafe_allow_html=True)


def public_products():
    st.markdown(
        '<div class="ql-kicker">PLATFORM</div>',
        unsafe_allow_html=True,
    )
    st.title("Research tools")
    st.markdown(
        "A practical set of tools for testing and understanding "
        "systematic strategies."
    )

    products = [
        (
            "Backtest Engine",
            "Run historical simulations using the connected FastAPI "
            "engine and inspect portfolio performance.",
        ),
        (
            "Technical Strategies",
            "Explore indicator-driven rules using moving averages, "
            "RSI, MACD and other supported indicators.",
        ),
        (
            "FinBERT Sentiment",
            "Score financial headlines and align sentiment with "
            "market dates for research.",
        ),
        (
            "ARIMA & LSTM Forecasting",
            "Experiment with statistical and sequence-based forecasts; "
            "compare prediction errors and directional accuracy.",
        ),
        (
            "Trade Journal & Risk",
            "Review completed trades, signal reasons, returns, "
            "win rate and drawdown.",
        ),
    ]

    for title, body in products:
        st.markdown(
            f'<div class="ql-panel" style="margin-bottom:12px">'
            f'<b>{title}</b><div class="ql-caption">{body}</div></div>',
            unsafe_allow_html=True,
        )


def public_about():
    st.markdown(
        '<div class="ql-kicker">ABOUT QUANTLAB</div>',
        unsafe_allow_html=True,
    )
    st.title("Research with transparency at its core")
    st.markdown(
        "QuantLab is an educational algorithmic-trading research "
        "project focused on connecting historical market data, "
        "rule-based strategies, financial-news sentiment and "
        "forecasting models in one workflow."
    )

    st.markdown("### Our principles")
    st.markdown(
        "- **Reproducibility:** compare models over consistent "
        "date ranges and assumptions."
    )
    st.markdown(
        "- **Explainability:** inspect signals and completed trades, "
        "not just headline returns."
    )
    st.markdown(
        "- **Risk awareness:** show drawdowns and negative outcomes "
        "as clearly as positive ones."
    )
    st.markdown(
        "- **Honest reporting:** no guaranteed-return claims and "
        "no invented market statistics."
    )

    st.info(
        "QuantLab is a research and educational platform, not a "
        "broker, investment adviser or live order execution system."
    )


def public_contact():
    st.markdown(
        '<div class="ql-kicker">CONTACT</div>',
        unsafe_allow_html=True,
    )
    st.title("Contact the team")
    st.markdown(
        "Send a message about the project, technical issues or collaboration."
    )

    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        topic = st.selectbox(
            "Topic",
            [
                "General enquiry",
                "Technical support",
                "Research collaboration",
                "Feedback",
            ],
        )
        message = st.text_area("Message", height=140)
        submitted = st.form_submit_button(
            "Submit enquiry",
            type="primary",
        )

    if submitted:
        if not name.strip() or not email.strip() or not message.strip():
            st.error("Please complete your name, email and message.")
        else:
            st.warning(
                f"The selected topic ({topic}) has not been sent because "
                "the contact form is not connected to a delivery endpoint."
            )
# ---------------------------------------------------------
# AUTHENTICATION HELPERS
# ---------------------------------------------------------

def _api_error_message(response):
    try:
        detail = response.json().get("detail", "")
    except (ValueError, AttributeError):
        detail = ""

    return str(
        detail or f"Request failed (HTTP {response.status_code})."
    )


def _save_authenticated_session(token):
    user = _load_current_user(token)

    if not user:
        raise ValueError("Could not verify the login session.")

    st.session_state["ql_access_token"] = token
    st.session_state["ql_user"] = user

    # Persist the token in the encrypted browser cookie so a refresh
    # does not immediately sign the user out.
    cookies["access_token"] = token
    cookies.save()

    st.session_state["public_nav"] = "Workspace"

    try:
        st.session_state["workspace_nav"] = load_workspace_page(token)
    except requests.RequestException:
        st.session_state["workspace_nav"] = "Overview"


# ---------------------------------------------------------
# LOGIN AND REGISTRATION
# ---------------------------------------------------------

def auth_screen(mode):
    is_signup = mode == "Sign up"

    left, right = st.columns(
        [1.05, 1],
        gap="large",
        vertical_alignment="center",
    )

    with left:
        st.markdown(
            '<div class="ql-kicker">QUANTLAB ACCOUNT</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="ql-hero-title" '
            'style="font-size:clamp(32px,3.5vw,46px)">'
            + (
                "Your research desk, in one place."
                if is_signup
                else "Welcome back to your research desk."
            )
            + "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p class="ql-subtitle">'
            'Sign in to run historical strategy experiments, review '
            'risk metrics, and keep your research workflow together.'
            '</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="ql-panel-muted">'
            '<div class="ql-label">ACCOUNT SECURITY</div>'
            '<div style="font-weight:650;margin-top:8px">'
            'Credentials are sent to your FastAPI authentication endpoint.'
            '</div>'
            '<div class="ql-caption">'
            'The access token is stored in an encrypted browser cookie '
            'and checked against the API. Logging out clears the session.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="ql-panel">',
            unsafe_allow_html=True,
        )

        st.markdown(
            "### " + (
                "Create your account" if is_signup else "Sign in"
            )
        )

        st.caption("Use your registered email address and password.")

        with st.form(
            f"auth_{mode}_form",
            clear_on_submit=False,
        ):
            username = (
                st.text_input(
                    "Username",
                    placeholder="e.g. vikash_baghel",
                    help="Required for a new account.",
                )
                if is_signup
                else None
            )

            email = st.text_input(
                "Email address",
                placeholder="you@example.com",
                autocomplete="email",
            )

            password = st.text_input(
                "Password",
                type="password",
                autocomplete=(
                    "new-password"
                    if is_signup
                    else "current-password"
                ),
            )

            confirm = (
                st.text_input(
                    "Confirm password",
                    type="password",
                    autocomplete="new-password",
                )
                if is_signup
                else None
            )

            submit_label = (
                "Create account"
                if is_signup
                else "Sign in to QuantLab"
            )

            submitted = st.form_submit_button(
                submit_label,
                type="primary",
                use_container_width=True,
            )

        if submitted:
            clean_email = email.strip().lower()

            if not clean_email or "@" not in clean_email:
                st.error("Enter a valid email address.")

            elif not password:
                st.error("Enter your password.")

            elif is_signup and (
                not username or len(username.strip()) < 3
            ):
                st.error("Choose a username with at least 3 characters.")

            elif is_signup and password != confirm:
                st.error("The passwords do not match.")

            elif is_signup and len(password) < 8:
                st.error("Use a password with at least 8 characters.")

            else:
                try:
                    with st.spinner(
                        "Creating your account…"
                        if is_signup
                        else "Signing you in…"
                    ):
                        if is_signup:
                            register_response = requests.post(
                                f"{AUTH_URL}/register",
                                json={
                                    "username": username.strip(),
                                    "email": clean_email,
                                    "password": password,
                                },
                                timeout=20,
                            )

                            if not register_response.ok:
                                st.error(
                                    _api_error_message(register_response)
                                )
                                return

                        login_response = requests.post(
                            f"{AUTH_URL}/login",
                            json={
                                "email": clean_email,
                                "password": password,
                            },
                            timeout=20,
                        )

                        if not login_response.ok:
                            if is_signup:
                                st.success(
                                    "Account created successfully. "
                                    "Please sign in with your new credentials."
                                )
                                st.session_state["public_nav"] = "Login"
                                st.rerun()
                            else:
                                st.error(
                                    _api_error_message(login_response)
                                )
                                return

                        token = login_response.json().get("access_token")

                        if not token:
                            st.error(
                                "The authentication API did not return "
                                "an access token. Check TokenResponse."
                            )
                        else:
                            _save_authenticated_session(token)
                            st.success(
                                "You're signed in. Opening your workspace…"
                            )
                            st.rerun()

                except requests.ConnectionError:
                    st.error(
                        f"Cannot reach the authentication API at "
                        f"{AUTH_URL}. Start FastAPI and try again."
                    )

                except requests.Timeout:
                    st.error(
                        "The request timed out. Check that the API is "
                        "running, then try again."
                    )

                except requests.RequestException as exc:
                    st.error(f"Authentication request failed: {exc}")

                except (ValueError, KeyError) as exc:
                    st.error(str(exc))

        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")

        if is_signup:
            st.caption("Already have an account?")

            if st.button(
                "Go to sign in",
                key="switch_to_login",
                use_container_width=True,
            ):
                st.session_state["public_nav"] = "Login"
                st.rerun()

        else:
            st.caption("New to QuantLab?")

            if st.button(
                "Create an account",
                key="switch_to_signup",
                use_container_width=True,
            ):
                st.session_state["public_nav"] = "Sign up"
                st.rerun()


# ---------------------------------------------------------
# AUTHENTICATED WORKSPACE
# ---------------------------------------------------------

def app_workspace():
    token = st.session_state.get("ql_access_token")
    user = st.session_state.get("ql_user")

    if not token or not user:
        st.markdown(
            '<div class="ql-kicker">PRIVATE WORKSPACE</div>',
            unsafe_allow_html=True,
        )
        st.title("Your research workspace")
        st.markdown(
            "Sign in to access your strategy experiments, "
            "backtest results, and research history."
        )

        if st.button(
            "Sign in to continue",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["public_nav"] = "Login"
            st.rerun()

        st.caption(
            "Workspace access is verified by the FastAPI authentication service."
        )
        return

    # Verify the token using the existing /me endpoint.
    try:
        verified_user = _load_current_user(token)

        if verified_user is None:
            clear_auth_session()
            st.warning("Your session has expired. Please sign in again.")
            st.session_state["public_nav"] = "Login"
            st.rerun()
            return

        st.session_state["ql_user"] = verified_user

    except requests.RequestException:
        st.warning(
            "Could not verify your session because the API is temporarily "
            "unreachable. Some workspace actions may fail until the "
            "connection returns."
        )

    # Backup logout: always available in the sidebar.
    with st.sidebar:
        st.markdown("### QuantLab")
        st.caption("Authenticated workspace")

        sidebar_user = st.session_state.get("ql_user", {})

        st.write(
            sidebar_user.get("username")
            or sidebar_user.get("email")
            or "Signed-in user"
        )

        st.divider()

        st.button(
            "Log out",
            key="sidebar_logout",
            type="primary",
            use_container_width=True,
            on_click=clear_auth_session,
        )

    workspace_page = st.session_state.get(
        "workspace_nav",
        "Overview",
    )

    st.markdown(
        '<div style="display:flex;justify-content:space-between;'
        'align-items:center">'
        '<div><div class="ql-kicker">PRIVATE RESEARCH TERMINAL</div>'
        '<h1 style="margin:4px 0">Workspace</h1></div>'
        '<span class="ql-pill">AUTHENTICATED SESSION</span></div>',
        unsafe_allow_html=True,
    )

    current_user = st.session_state.get("ql_user", {})

    st.caption(
        f"Signed in as "
        f"{current_user.get('username') or current_user.get('email') or 'QuantLab user'}"
        " · Research only — no live orders are placed."
    )

    # -----------------------------------------------------
    # OVERVIEW
    # -----------------------------------------------------

    if workspace_page == "Overview":
        st.markdown("### Run a backtest")

        left, right = st.columns(
            [1, 1.4],
            gap="large",
        )

        with left:
            symbol = st.selectbox(
                "Instrument",
                ["RELIANCE.NS", "TCS.NS", "INFY.NS", "AAPL"],
                key="ws_symbol",
            )

            strategy_name = st.selectbox(
                "Strategy",
                list(STRATEGIES.keys()),
                key="ws_strategy",
            )

            date_left, date_right = st.columns(2)

            with date_left:
                start = st.date_input(
                    "Start date",
                    value=pd.Timestamp("2026-01-01").date(),
                    key="ws_start",
                )

            with date_right:
                end = st.date_input(
                    "End date",
                    value=pd.Timestamp("2026-09-05").date(),
                    key="ws_end",
                )

            capital = st.number_input(
                "Initial capital (₹)",
                min_value=1000.0,
                value=100000.0,
                step=10000.0,
                key="ws_capital",
            )

            run = st.button(
                "Execute backtest",
                type="primary",
                use_container_width=True,
            )

            if run:
                if start >= end:
                    st.error("End date must be later than start date.")

                else:
                    try:
                        with st.spinner(
                            "Running the selected model..."
                        ):
                            response = requests.post(
                                f"{API_URL}/backtests/run",
                                json={
                                    "symbol": symbol,
                                    "start_date": start.isoformat(),
                                    "end_date": end.isoformat(),
                                    "initial_capital": float(capital),
                                    "strategy": STRATEGIES[strategy_name],
                                },
                                headers={
                                    "Authorization": (
                                        "Bearer "
                                        f"{st.session_state.get('ql_access_token', '')}"
                                    )
                                },
                                timeout=900,
                            )

                        if response.ok:
                            payload = response.json()
                            payload["initial_capital"] = float(capital)
                            payload["selected_strategy_name"] = strategy_name

                            st.session_state["backtest_result"] = payload

                            st.success("Backtest completed.")
                            st.rerun()

                        else:
                            st.error(
                                f"API error {response.status_code}: "
                                f"{response.text[:800]}"
                            )

                    except requests.RequestException as exc:
                        st.error(
                            f"Cannot connect to FastAPI at {API_URL}: {exc}"
                        )

        with right:
            result = st.session_state.get("backtest_result")

            if not result:
                st.markdown(
                    '<div class="ql-panel">'
                    '<div class="ql-label">PORTFOLIO OVERVIEW</div>'
                    '<h3>No run selected</h3>'
                    '<div class="ql-caption">'
                    'Execute a backtest to display real metrics and '
                    'the equity curve here.'
                    '</div></div>',
                    unsafe_allow_html=True,
                )

            else:
                metrics = result.get("metrics", {})
                initial = result.get("initial_capital", 100000)
                final = metrics.get("final_value")
                total_return = metrics.get("total_return")
                sharpe = metrics.get("sharpe_ratio")
                drawdown = metrics.get("max_drawdown")

                metric_left, metric_right = st.columns(2)

                with metric_left:
                    panel_metric(
                        "Portfolio value",
                        (
                            f"₹{float(final):,.2f}"
                            if final is not None
                            else "N/A"
                        ),
                        "Final simulated value",
                    )

                with metric_right:
                    panel_metric(
                        "Total return",
                        (
                            f"{float(total_return):.2f}%"
                            if total_return is not None
                            else "N/A"
                        ),
                        f"Initial ₹{initial:,.0f}",
                        (
                            "green"
                            if total_return is not None and total_return >= 0
                            else "red"
                        ),
                    )

                metric_left, metric_right = st.columns(2)

                with metric_left:
                    panel_metric(
                        "Sharpe ratio",
                        (
                            f"{float(sharpe):.3f}"
                            if sharpe is not None
                            else "N/A"
                        ),
                        "Annualized, as returned by API",
                    )

                with metric_right:
                    panel_metric(
                        "Max drawdown",
                        (
                            f"{float(drawdown):.2f}%"
                            if drawdown is not None
                            else "N/A"
                        ),
                        "Peak-to-trough decline",
                        "red",
                    )

                curve = pd.DataFrame(
                    result.get("equity_curve", [])
                )

                if (
                    not curve.empty
                    and "date" in curve
                    and "portfolio_value" in curve
                ):
                    curve["date"] = pd.to_datetime(
                        curve["date"],
                        errors="coerce",
                    )

                    curve["portfolio_value"] = pd.to_numeric(
                        curve["portfolio_value"],
                        errors="coerce",
                    )

                    curve = curve.dropna(
                        subset=["date", "portfolio_value"]
                    )

                    fig = go.Figure(
                        go.Scatter(
                            x=curve["date"],
                            y=curve["portfolio_value"],
                            mode="lines",
                            line=dict(
                                color="#4cd7f6",
                                width=2,
                            ),
                            name="Equity",
                        )
                    )

                    fig.update_layout(
                        template=(
                            "plotly_dark"
                            if st.session_state.get("ql_theme", "Dark") == "Dark"
                            else "plotly_white"
                        ),
                        height=300,
                        margin=dict(l=5, r=5, t=15, b=5),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

    # -----------------------------------------------------
    # OTHER WORKSPACE PAGES
    # -----------------------------------------------------

    else:
        result = st.session_state.get("backtest_result", {})

        if workspace_page == "Strategy Builder":
            st.markdown("### Strategy Builder")
            st.markdown(
                "Choose among strategies currently supported by the "
                "backend. Strategy parameter editing can be added once "
                "those parameters are exposed by the API."
            )

            for name, strategy_id in STRATEGIES.items():
                with st.container(border=True):
                    st.markdown(f"**{name}**")
                    st.caption(
                        f"Backend strategy identifier: {strategy_id}"
                    )

        elif workspace_page == "Backtest Results":
            st.markdown("### Backtest Results")

            if result:
                st.json(result.get("metrics", {}))
            else:
                st.info("Run a backtest from Overview first.")

        elif workspace_page == "Trade History":
            st.markdown("### Trade History")

            trades = (
                pd.DataFrame(result.get("trades", []))
                if result
                else pd.DataFrame()
            )

            if trades.empty:
                st.info("No trade history available yet.")

            else:
                st.dataframe(
                    trades,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "Download trade history CSV",
                    data=trades.to_csv(index=False).encode("utf-8"),
                    file_name="quantlab_trade_history.csv",
                    mime="text/csv",
                )

        
        elif workspace_page == "Sentiment Analysis":
            st.markdown("## Sentiment Analysis")
            st.caption(
                "Analyze financial headlines using your existing "
                "FinBERT model."
            )

            sentiment_api_url = f"{API_URL}/sentiment/analyze"

            headlines_text = st.text_area(
                "Financial news headlines",
                placeholder=(
                    "Enter one headline per line.\n"
                    "Example: The company reported record quarterly profits."
                ),
                height=180,
                key="sentiment_headlines_input",
            )

            st.caption(
                "Enter up to 50 headlines. Each non-empty line is "
                "analyzed separately."
            )

            if st.button(
                "Analyze sentiment",
                type="primary",
                key="run_sentiment_analysis",
            ):
                headlines = [
                    line.strip()
                    for line in headlines_text.splitlines()
                    if line.strip()
                ]

                if not headlines:
                    st.warning("Enter at least one news headline.")
                elif len(headlines) > 50:
                    st.warning("Please enter no more than 50 headlines.")
                else:
                    try:
                        with st.spinner("Running FinBERT analysis..."):
                            response = requests.post(
                                sentiment_api_url,
                                json={"headlines": headlines},
                                timeout=180,
                            )

                        if response.ok:
                            sentiment_result = response.json()
                            st.session_state[
                                "sentiment_analysis_result"
                            ] = sentiment_result
                        else:
                            try:
                                error_detail = response.json().get(
                                    "detail", response.text
                                )
                            except ValueError:
                                error_detail = response.text

                            st.error(
                                f"Sentiment API error "
                                f"({response.status_code}): "
                                f"{error_detail}"
                            )

                    except requests.RequestException as exc:
                        st.error(
                            "Could not connect to the sentiment API. "
                            "Check that FastAPI is running."
                        )
                        st.caption(str(exc))

            sentiment_result = st.session_state.get(
                "sentiment_analysis_result"
            )

            if sentiment_result:
                st.divider()

                average_score = float(
                    sentiment_result.get(
                        "average_sentiment_score", 0.0
                    )
                )

                distribution = sentiment_result.get(
                    "distribution", {}
                )

                positive_count = int(
                    distribution.get("positive", 0)
                )
                negative_count = int(
                    distribution.get("negative", 0)
                )
                neutral_count = int(
                    distribution.get("neutral", 0)
                )

                metric_cols = st.columns(4)

                metric_cols[0].metric(
                    "Headlines analyzed",
                    sentiment_result.get("total_headlines", 0),
                )
                metric_cols[1].metric(
                    "Average sentiment",
                    f"{average_score:+.3f}",
                )
                metric_cols[2].metric(
                    "Positive",
                    positive_count,
                )
                metric_cols[3].metric(
                    "Negative",
                    negative_count,
                )

                st.caption(
                    f"Model: {sentiment_result.get('model', 'FinBERT')}"
                )

                st.markdown("### Sentiment distribution")

                distribution_df = pd.DataFrame(
                    {
                        "Sentiment": [
                            "Positive",
                            "Neutral",
                            "Negative",
                        ],
                        "Articles": [
                            positive_count,
                            neutral_count,
                            negative_count,
                        ],
                    }
                )

                if distribution_df["Articles"].sum() > 0:
                    fig = go.Figure(
                        go.Bar(
                            x=distribution_df["Sentiment"],
                            y=distribution_df["Articles"],
                            text=distribution_df["Articles"],
                            textposition="auto",
                        )
                    )
                    fig.update_layout(
                        height=300,
                        margin=dict(l=10, r=10, t=20, b=10),
                        template=(
                            "plotly_dark"
                            if st.session_state.get("ql_theme", "Dark")
                            == "Dark"
                            else "plotly_white"
                        ),
                        showlegend=False,
                        xaxis_title=None,
                        yaxis_title="Number of headlines",
                    )
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

                st.markdown("### Article-level results")

                article_results = sentiment_result.get(
                    "results", []
                )

                if article_results:
                    sentiment_df = pd.DataFrame(article_results)

                    display_columns = [
                        column
                        for column in [
                            "text",
                            "label",
                            "confidence",
                            "sentiment_score",
                        ]
                        if column in sentiment_df.columns
                    ]

                    st.dataframe(
                        sentiment_df[display_columns],
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.download_button(
                        "Download sentiment results",
                        data=sentiment_df.to_csv(
                            index=False
                        ).encode("utf-8"),
                        file_name="sentiment_analysis.csv",
                        mime="text/csv",
                        key="download_sentiment_results",
                    )

                st.caption(
                    "Sentiment scores represent model classifications, "
                    "not guaranteed market direction."
                )

        elif workspace_page == "Forecasting":
            st.markdown("## Price Forecasting")
            st.caption(
                "Generate experimental price forecasts using your "
                "existing ARIMA or LSTM service."
            )

            with st.form("forecasting_request_form"):
                forecast_col1, forecast_col2 = st.columns(2)

                with forecast_col1:
                    forecast_symbol = st.text_input(
                        "Market symbol",
                        value="RELIANCE.NS",
                        help=(
                            "Examples: RELIANCE.NS, TCS.NS, "
                            "AAPL, MSFT"
                        ),
                    ).strip().upper()

                    forecast_model_label = st.selectbox(
                        "Forecasting model",
                        ["ARIMA", "LSTM"],
                    )

                with forecast_col2:
                    forecast_start = st.date_input(
                        "Historical data from",
                        value=pd.Timestamp("2025-01-01").date(),
                        key="forecast_start_date",
                    )

                    forecast_end = st.date_input(
                        "Historical data to",
                        value=pd.Timestamp.now().date(),
                        key="forecast_end_date",
                    )

                forecast_steps = 1

                if forecast_model_label == "ARIMA":
                    forecast_steps = st.number_input(
                        "Forecast horizon (trading steps)",
                        min_value=1,
                        max_value=10,
                        value=1,
                        step=1,
                    )
                else:
                    st.info(
                        "The current LSTM service supports one-step "
                        "forecasts only."
                    )

                run_forecast = st.form_submit_button(
                    "Generate forecast",
                    type="primary",
                    use_container_width=True,
                )

            if run_forecast:
                if not forecast_symbol:
                    st.warning("Enter a market symbol.")
                elif forecast_start >= forecast_end:
                    st.warning(
                        "The start date must be before the end date."
                    )
                else:
                    forecast_payload = {
                        "symbol": forecast_symbol,
                        "start_date": forecast_start.isoformat(),
                        "end_date": forecast_end.isoformat(),
                        "model": forecast_model_label.lower(),
                        "steps": int(forecast_steps),
                    }

                    try:
                        with st.spinner(
                            f"Running {forecast_model_label} forecast..."
                        ):
                            response = requests.post(
                                f"{API_URL}/forecasting/predict",
                                json=forecast_payload,
                                timeout=300,
                            )

                        if response.ok:
                            st.session_state[
                                "forecasting_result"
                            ] = response.json()
                        else:
                            try:
                                error_detail = response.json().get(
                                    "detail", response.text
                                )
                            except ValueError:
                                error_detail = response.text

                            st.error(
                                f"Forecasting API error "
                                f"({response.status_code}): "
                                f"{error_detail}"
                            )

                    except requests.RequestException as exc:
                        st.error(
                            "Could not connect to the forecasting API. "
                            "Check that FastAPI is running."
                        )
                        st.caption(str(exc))

            forecast_result = st.session_state.get(
                "forecasting_result"
            )

            if forecast_result:
                st.divider()

                st.markdown(
                    f"### {forecast_result.get('symbol', 'Market')} "
                    f"— {forecast_result.get('model', '').upper()}"
                )

                current_price = float(
                    forecast_result["current_price"]
                )
                predicted_price = float(
                    forecast_result["forecast_price"]
                )
                expected_return = float(
                    forecast_result["expected_return_percent"]
                )
                direction = forecast_result.get(
                    "direction", "NEUTRAL"
                )

                metric_cols = st.columns(4)

                metric_cols[0].metric(
                    "Last closing price",
                    f"{current_price:,.2f}",
                )
                metric_cols[1].metric(
                    "Forecast price",
                    f"{predicted_price:,.2f}",
                )
                metric_cols[2].metric(
                    "Expected change",
                    f"{expected_return:+.2f}%",
                )
                metric_cols[3].metric(
                    "Model direction",
                    direction,
                )

                
                forecast_prices = forecast_result.get(
                    "forecast_prices", []
                )
                historical_prices = forecast_result.get(
                    "historical_prices", []
                )

                if historical_prices:
                    historical_df = pd.DataFrame(historical_prices)
                    historical_df["date"] = pd.to_datetime(
                        historical_df["date"]
                    )
                    historical_df = historical_df.sort_values("date")

                    st.markdown("### Historical price and forecast")

                    fig = go.Figure()

                    # Actual observed market prices
                    fig.add_trace(
                        go.Scatter(
                            x=historical_df["date"],
                            y=historical_df["close"],
                            mode="lines",
                            name="Actual closing price",
                            line=dict(width=2),
                        )
                    )

                    if forecast_prices:
                        last_date = historical_df["date"].iloc[-1]
                        last_close = float(
                            historical_df["close"].iloc[-1]
                        )

                        # Use business-day labels for forecast steps.
                        # These are illustrative step labels, not
                        # confirmed exchange trading-session dates.
                        forecast_labels = [
                            last_date.strftime("%Y-%m-%d")
                        ] + [
                            f"Forecast +{step}"
                            for step in range(
                                1, len(forecast_prices) + 1
                            )
                        ]

                        forecast_values = [
                            last_close
                        ] + [
                            float(value)
                            for value in forecast_prices
                        ]

                        fig.add_trace(
                            go.Scatter(
                                x=forecast_labels,
                                y=forecast_values,
                                mode="lines+markers",
                                name="Forecast",
                                line=dict(
                                    width=3,
                                    dash="dash",
                                ),
                            )
                        )

                        fig.add_vline(
                            x=last_date.timestamp() * 1000,
                            line_dash="dot",
                            annotation_text="Forecast starts",
                        )

                    fig.update_layout(
                        height=450,
                        margin=dict(l=10, r=10, t=30, b=10),
                        template=(
                            "plotly_dark"
                            if st.session_state.get(
                                "ql_theme", "Dark"
                            ) == "Dark"
                            else "plotly_white"
                        ),
                        xaxis_title="Historical date / forecast step",
                        yaxis_title="Price",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="left",
                            x=0,
                        ),
                        hovermode="x unified",
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

                if forecast_prices:
                    forecast_df = pd.DataFrame(
                        {
                            "Forecast step": range(
                                1, len(forecast_prices) + 1
                            ),
                            "Predicted price": [
                                float(value)
                                for value in forecast_prices
                            ],
                        }
                    )

                    st.markdown("### Predicted prices")
                    st.dataframe(
                        forecast_df,
                        use_container_width=True,
                        hide_index=True,
                    )


                if forecast_prices:
                    forecast_df = pd.DataFrame(
                        {
                            "Forecast step": range(
                                1, len(forecast_prices) + 1
                            ),
                            "Predicted price": forecast_prices,
                        }
                    )

                    st.markdown("### Forecast trajectory")

                    fig = go.Figure()

                    fig.add_trace(
                        go.Scatter(
                            x=forecast_df["Forecast step"],
                            y=forecast_df["Predicted price"],
                            mode="lines+markers",
                            name="Forecast",
                        )
                    )

                    fig.add_hline(
                        y=current_price,
                        line_dash="dash",
                        annotation_text="Last closing price",
                    )

                    fig.update_layout(
                        height=360,
                        margin=dict(l=10, r=10, t=30, b=10),
                        template=(
                            "plotly_dark"
                            if st.session_state.get("ql_theme", "Dark")
                            == "Dark"
                            else "plotly_white"
                        ),
                        xaxis_title="Forecast step",
                        yaxis_title="Price",
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

                    st.dataframe(
                        forecast_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                st.caption(
                    "Historical data ends at "
                    f"{forecast_result.get('last_historical_date', 'N/A')}."
                )

                st.warning(
                    forecast_result.get(
                        "disclaimer",
                        "Forecasts are estimates and are not investment advice.",
                    )
                )
            
            st.divider()
            st.markdown("### Historical Model Evaluation")
            st.caption(
                "Evaluate ARIMA predictions against unseen historical "
                "closing prices using a chronological expanding window."
            )

            with st.form("arima_evaluation_form"):
                eval_col1, eval_col2, eval_col3 = st.columns(3)

                with eval_col1:
                    eval_symbol = st.text_input(
                        "Evaluation symbol",
                        value="RELIANCE.NS",
                        key="evaluation_symbol",
                    ).strip().upper()

                with eval_col2:
                    eval_start = st.date_input(
                        "Evaluation start date",
                        value=pd.Timestamp("2024-01-01").date(),
                        key="evaluation_start_date",
                    )

                with eval_col3:
                    eval_end = st.date_input(
                        "Evaluation end date",
                        value=pd.Timestamp.now().date(),
                        key="evaluation_end_date",
                    )

                eval_test_size = st.number_input(
                    "Test observations",
                    min_value=5,
                    max_value=30,
                    value=20,
                    step=5,
                    help=(
                        "Number of final observations reserved for "
                        "out-of-sample evaluation."
                    ),
                )

                run_evaluation = st.form_submit_button(
                    "Evaluate ARIMA",
                    type="primary",
                    use_container_width=True,
                )

            if run_evaluation:
                if not eval_symbol:
                    st.warning("Enter a market symbol.")
                elif eval_start >= eval_end:
                    st.warning(
                        "The start date must be before the end date."
                    )
                else:
                    evaluation_payload = {
                        "symbol": eval_symbol,
                        "start_date": eval_start.isoformat(),
                        "end_date": eval_end.isoformat(),
                        "test_size": int(eval_test_size),
                    }

                    try:
                        with st.spinner(
                            "Evaluating ARIMA on unseen observations..."
                        ):
                            evaluation_response = requests.post(
                                f"{API_URL}/forecasting/evaluate",
                                json=evaluation_payload,
                                timeout=300,
                            )

                        if evaluation_response.ok:
                            st.session_state[
                                "arima_evaluation_result"
                            ] = evaluation_response.json()
                        else:
                            try:
                                error_detail = (
                                    evaluation_response.json().get(
                                        "detail",
                                        evaluation_response.text,
                                    )
                                )
                            except ValueError:
                                error_detail = evaluation_response.text

                            st.error(
                                f"Evaluation failed "
                                f"({evaluation_response.status_code}): "
                                f"{error_detail}"
                            )

                    except requests.RequestException as exc:
                        st.error(
                            "Could not connect to the evaluation API. "
                            "Check that FastAPI is running."
                        )
                        st.caption(str(exc))

            evaluation_result = st.session_state.get(
                "arima_evaluation_result"
            )

            if evaluation_result:
                st.markdown("#### Evaluation metrics")

                eval_metrics = evaluation_result.get("metrics", {})

                metric_cols = st.columns(4)

                metric_cols[0].metric(
                    "MAE",
                    f"{eval_metrics.get('mae', 0):,.2f}",
                    help="Mean absolute error, in price units.",
                )

                metric_cols[1].metric(
                    "RMSE",
                    f"{eval_metrics.get('rmse', 0):,.2f}",
                    help=(
                        "Root mean squared error; larger errors "
                        "receive greater weight."
                    ),
                )

                metric_cols[2].metric(
                    "Directional accuracy",
                    f"{eval_metrics.get('directional_accuracy', 0):.1f}%",
                )

                metric_cols[3].metric(
                    "Evaluated samples",
                    str(evaluation_result.get("evaluated_samples", 0)),
                )

                st.caption(
                    f"Symbol: {evaluation_result.get('symbol', 'N/A')} · "
                    f"Method: "
                    f"{evaluation_result.get('evaluation_method', 'N/A')} · "
                    f"Training cutoff: "
                    f"{evaluation_result.get('training_cutoff_date', 'N/A')}"
                )

                predictions = evaluation_result.get("predictions", [])

                if predictions:
                    evaluation_df = pd.DataFrame(predictions)
                    evaluation_df["date"] = pd.to_datetime(
                        evaluation_df["date"]
                    )
                    evaluation_df = evaluation_df.sort_values("date")

                    st.markdown("#### Actual vs predicted prices")

                    evaluation_fig = go.Figure()

                    evaluation_fig.add_trace(
                        go.Scatter(
                            x=evaluation_df["date"],
                            y=evaluation_df["actual_price"],
                            mode="lines+markers",
                            name="Actual closing price",
                        )
                    )

                    evaluation_fig.add_trace(
                        go.Scatter(
                            x=evaluation_df["date"],
                            y=evaluation_df["predicted_price"],
                            mode="lines+markers",
                            name="ARIMA prediction",
                            line=dict(dash="dash"),
                        )
                    )

                    evaluation_fig.update_layout(
                        height=420,
                        template=(
                            "plotly_dark"
                            if st.session_state.get("ql_theme", "Dark")
                            == "Dark"
                            else "plotly_white"
                        ),
                        margin=dict(l=10, r=10, t=25, b=10),
                        xaxis_title="Evaluation date",
                        yaxis_title="Closing price",
                        hovermode="x unified",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="left",
                            x=0,
                        ),
                    )

                    st.plotly_chart(
                        evaluation_fig,
                        use_container_width=True,
                    )

                    st.markdown("#### Prediction errors")

                    display_df = evaluation_df[
                        [
                            "date",
                            "actual_price",
                            "predicted_price",
                            "absolute_error",
                        ]
                    ].copy()

                    display_df["date"] = (
                        display_df["date"].dt.strftime("%Y-%m-%d")
                    )

                    display_df = display_df.rename(
                        columns={
                            "date": "Date",
                            "actual_price": "Actual price",
                            "predicted_price": "Predicted price",
                            "absolute_error": "Absolute error",
                        }
                    )

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.download_button(
                        "Download evaluation results",
                        data=display_df.to_csv(
                            index=False
                        ).encode("utf-8"),
                        file_name="arima_evaluation.csv",
                        mime="text/csv",
                        key="download_arima_evaluation",
                    )

                st.warning(
                    evaluation_result.get(
                        "disclaimer",
                        "Historical performance does not guarantee "
                        "future forecasting accuracy.",
                    )
                )

        elif workspace_page == "Profile & Settings":
            st.markdown("### Profile & Settings")
            user = st.session_state.get("ql_user", {})

            st.text_input(
                "Username",
                value=str(user.get("username", "—")),
                disabled=True,
            )

            st.text_input(
                "Email",
                value=str(user.get("email", "—")),
                disabled=True,
            )

            st.text_input(
                "Account ID",
                value=str(user.get("id", "—")),
                disabled=True,
            )

            st.caption(
                "Profile details are read from GET /api/v1/auth/me. "
                "Profile editing is not exposed by the current API."
            )


# ---------------------------------------------------------
# APP ROUTING
# ---------------------------------------------------------

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


# Public call to action — never grants demo access.
if not st.session_state.get("ql_access_token"):
    st.markdown(
        '<div style="margin-top:14px;text-align:center" '
        'class="ql-caption">'
        'Ready to evaluate a strategy with your own settings?'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Sign in to open the workspace",
        key="open_workspace_footer",
        type="primary",
    ):
        st.session_state["public_nav"] = "Login"
        st.rerun()