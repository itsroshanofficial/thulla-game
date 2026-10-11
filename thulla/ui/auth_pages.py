"""Login, registration, and security-question password recovery."""
from __future__ import annotations
import streamlit as st

from ..auth.security import make_token
from ..auth.service import AuthError, SECURITY_QUESTIONS


def _signed_in(user: dict) -> None:
    st.session_state.user = user
    st.session_state.token = make_token(user["id"])


def render(auth) -> None:
    user = st.session_state.user
    if user:
        st.success(f"Signed in as **{user['nickname']}** (@{user['username']})")
        stats = auth.get_stats(user["id"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Games", stats["games_played"]); c2.metric("Wins", stats["wins"])
        c3.metric("Times Thulla 😅", stats["thulla_count"])
        if st.button("Sign out"):
            st.session_state.user = st.session_state.token = None
            st.rerun()
        return
    tab_in, tab_up, tab_rec = st.tabs(["Sign in", "Create account", "Forgot password"])
    with tab_in:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in", type="primary"):
                try:
                    _signed_in(auth.login(u, p)); st.rerun()
                except AuthError as e:
                    st.error(str(e))
    with tab_up:
        with st.form("register"):
            u = st.text_input("Username (3-20 letters/numbers/_)")
            nick = st.text_input("Nickname (shown to other players)")
            p1 = st.text_input("Password (min 8 characters)", type="password")
            p2 = st.text_input("Confirm password", type="password")
            q = st.selectbox("Security question", SECURITY_QUESTIONS)
            a1 = st.text_input("Recovery answer", type="password")
            a2 = st.text_input("Confirm recovery answer", type="password")
            st.caption("⚠️ Security questions are weaker than verified email or authenticator-app recovery. "
                       "Choose an answer others cannot guess.")
            if st.form_submit_button("Create account", type="primary"):
                try:
                    auth.register(u, nick, p1, p2, q, a1, a2)
                    st.success("Account created! Please sign in.")
                except AuthError as e:
                    st.error(str(e))
    with tab_rec:
        _recovery(auth)


def _recovery(auth) -> None:
    ss = st.session_state
    stage = ss.get("rec_stage", 0)
    if stage == 0:
        with st.form("rec0"):
            u = st.text_input("Your username")
            if st.form_submit_button("Continue"):
                ss.rec_user, ss.rec_q, ss.rec_stage = u.strip(), auth.start_recovery(u), 1
                st.rerun()
    elif stage == 1:
        with st.form("rec1"):
            st.write(f"**Security question:** {ss.rec_q}")
            a = st.text_input("Your answer", type="password")
            if st.form_submit_button("Verify"):
                try:
                    ss.rec_token, ss.rec_stage = auth.verify_recovery(ss.rec_user, a), 2
                    st.rerun()
                except AuthError as e:
                    st.error(str(e))
        if st.button("Start over", key="rec_reset1"):
            ss.rec_stage = 0; st.rerun()
    else:
        with st.form("rec2"):
            p1 = st.text_input("New password", type="password")
            p2 = st.text_input("Confirm new password", type="password")
            if st.form_submit_button("Save new password"):
                try:
                    auth.reset_password(ss.rec_token, p1, p2)
                    for k in ("rec_stage", "rec_token", "rec_user", "rec_q"):
                        ss.pop(k, None)
                    st.success("Password updated. You can sign in now.")
                except AuthError as e:
                    st.error(str(e))
