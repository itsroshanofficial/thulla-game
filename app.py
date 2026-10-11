"""Thulla — Streamlit entry point.   Run:  streamlit run app.py"""
import streamlit as st

from thulla.auth.service import AuthService
from thulla.ui import auth_pages, offline_page, online_page
from thulla.ui.common import init_state, voice_settings_ui
from thulla.ui.styles import CSS

st.set_page_config(page_title="Thulla 🃏", page_icon="🃏", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)
init_state()


@st.cache_resource
def get_auth() -> AuthService:
    return AuthService()


auth = get_auth()
PAGES = ["🏠 Home", "🤖 Offline", "🌐 Online", "👤 Account", "📖 Rules"]
page = st.sidebar.radio("Menu", PAGES, key="page")
with st.sidebar:
    st.divider()
    voice_settings_ui()

if page == PAGES[0]:
    st.title("🃏 Thulla")
    st.write("Oye hoye! Pattay khelo, Thulla se bacho. Pick a mode from the menu.")
    c1, c2 = st.columns(2)
    c1.info("**Offline** — play vs AI bots, no internet needed.")
    c2.info("**Online** — private rooms (needs the game server and an account).")
    if st.session_state.user:
        st.success(f"Welcome back, {st.session_state.user['nickname']}!")
elif page == PAGES[1]:
    offline_page.render(auth)
elif page == PAGES[2]:
    online_page.render(auth)
elif page == PAGES[3]:
    auth_pages.render(auth)
else:
    st.markdown(open("docs/RULES_CONFIRMATION.md", encoding="utf-8").read())
