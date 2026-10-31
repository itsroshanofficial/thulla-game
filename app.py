"""Thulla — Streamlit entry point.   Run:  streamlit run app.py"""
from pathlib import Path

import streamlit as st

from thulla.auth.service import AuthService
from thulla.ui import auth_pages, offline_page, online_page
from thulla.ui.common import init_state, voice_settings_ui
from thulla.ui.styles import CSS

st.set_page_config(
    page_title="Thulla 🃏",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)
init_state()


@st.cache_resource
def get_auth() -> AuthService:
    return AuthService()


def mode_card(icon: str, title: str, text: str, badge: str, warm: bool = False) -> str:
    """Return the HTML for one glass feature card (styles live in styles.py)."""
    warm_cls = " warm" if warm else ""
    return (
        f'<div class="glass-card">'
        f'<div class="icon{warm_cls}">{icon}</div>'
        f"<h3>{title}</h3>"
        f"<p>{text}</p>"
        f'<span class="badge">{badge}</span>'
        f"</div>"
    )


def render_home() -> None:
    st.markdown(
        """
        <div class="hero">
          <h1>Thulla</h1>
          <p>Oye hoye! Pattay khelo, Thulla se bacho. Apna mode chuno aur khel shuru karo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2, gap="large")
    c1.markdown(
        mode_card("🤖", "Offline", "Play vs AI bots — no internet needed.", "SOLO"),
        unsafe_allow_html=True,
    )
    c2.markdown(
        mode_card(
            "🌐", "Online",
            "Private rooms with friends (needs the game server and an account).",
            "MULTIPLAYER", warm=True,
        ),
        unsafe_allow_html=True,
    )

    user = st.session_state.user
    if user:
        st.write("")
        st.success(f"Welcome back, {user['nickname']}!")


auth = get_auth()
PAGES = ["🏠 Home", "🤖 Offline", "🌐 Online", "👤 Account", "📖 Rules"]

with st.sidebar:
    st.markdown("## 🃏 Thulla")
    st.caption("Card game dashboard")
    page = st.radio("Menu", PAGES, key="page", label_visibility="collapsed")
    st.divider()
    voice_settings_ui()

if page == PAGES[0]:
    render_home()
elif page == PAGES[1]:
    offline_page.render(auth)
elif page == PAGES[2]:
    online_page.render(auth)
elif page == PAGES[3]:
    auth_pages.render(auth)
else:
    rules = Path("docs/RULES_CONFIRMATION.md")
    st.markdown(rules.read_text(encoding="utf-8"))
