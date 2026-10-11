from __future__ import annotations
import os
import streamlit as st

from ..engine.game import Event
from ..online.client import OnlineClient, OnlineError
from .common import render_hand, render_reaction_and_voice, render_seats, render_table

SERVER_URL = os.environ.get("THULLA_SERVER_URL", "http://127.0.0.1:8000")


def render(auth) -> None:
    ss = st.session_state
    if not ss.user:
        st.info("Please sign in (Account page) to play online.")
        return
    client = OnlineClient(SERVER_URL, ss.token)
    code = ss.get("room_code")
    if not code:
        st.subheader("🌐 Online rooms")
        c1, c2 = st.columns(2)
        if c1.button("Create private room", type="primary", use_container_width=True):
            try:
                ss.room_code, ss.room_seq = client.create_room(), 0
                st.rerun()
            except OnlineError as e:
                st.error(str(e))
        with c2.form("join"):
            c = st.text_input("Room code", max_chars=6)
            if st.form_submit_button("Join room"):
                try:
                    ss.room_code, ss.room_seq = client.join(c), 0
                    st.rerun()
                except OnlineError as e:
                    st.error(str(e))
        st.caption(f"Server: {SERVER_URL}")
        return
    _room(client, code)


@st.fragment(run_every=2)
def _room(client: OnlineClient, code: str) -> None:
    ss = st.session_state
    try:
        s = client.state(code, since=ss.get("room_seq", 0))
    except OnlineError as e:
        st.error(str(e))
        if st.button("Back"):
            ss.pop("room_code", None); st.rerun()
        return
    ss.room_seq = s["seq"]
    st.subheader(f"Room code: `{s['code']}`")
    names = [m["nickname"] + ("" if m["connected"] else " (away)") for m in
             sorted(s["members"], key=lambda m: (m["seat"] is None, m["seat"] or 0))]

    if s["status"] == "lobby":
        st.write("**Players:** " + ", ".join(m["nickname"] + (" 🤖" if m["bot"] else "") for m in s["members"]))
        st.caption("Share the code with friends. Up to 8 players.")
        if s["host"]:
            a, b = st.columns(2)
            if a.button("Add bot 🤖"):
                _try(client.add_bot, code)
            if b.button("Start game ▶", type="primary"):
                _try(client.start, code)
    else:
        g = s["game"]
        events = [Event(e["kind"], e["seat"], e["data"]) for e in s["events"]]
        if events:
            render_reaction_and_voice(events, g["your_seat"])
        render_seats(names, g["hand_counts"], g["turn"], g["finished"], g["loser"])
        render_table([(p, c) for p, c in g["trick"]], names)
        if g["over"]:
            st.error("😅 You are the Thulla!") if g["loser"] == g["your_seat"] else st.success("🎉 You are safe!")
        else:
            mine = g["turn"] == g["your_seat"]
            st.write("**Your turn** 👇" if mine else f"Waiting for {names[g['turn']]}…")
            clicked = render_hand(g["your_hand"], set(g["legal"]), "on", can_act=mine)
            if clicked:
                _try(client.play, code, clicked)
    if st.button("Leave room"):
        _try(client.leave, code)
        ss.pop("room_code", None); st.rerun()


def _try(fn, *a):
    try:
        fn(*a); st.rerun()
    except OnlineError as e:
        st.error(str(e))
