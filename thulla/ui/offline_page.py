from __future__ import annotations
import streamlit as st

from ..engine.game import IllegalMove
from ..offline import HUMAN, OfflineSession
from .common import render_hand, render_reaction_and_voice, render_seats, render_table


def render(auth) -> None:
    ss = st.session_state
    sess: OfflineSession | None = ss.get("offline")
    if sess is None:
        st.subheader("🤖 Play offline vs AI")
        default = ss.user["nickname"] if ss.user else "You"
        nick = st.text_input("Your name", value=default, max_chars=20)
        n_ai = st.slider("Number of AI opponents", 1, 7, 3)
        if st.button("Deal the cards", type="primary"):
            ss.offline = OfflineSession(nick, n_ai)
            ss.offline_recorded = False
            ss.offline_pending = ss.offline.take_events()
            st.rerun()
        return

    g = sess.game
    pending = ss.pop("offline_pending", [])
    if pending:
        render_reaction_and_voice(pending, HUMAN)
    render_seats(sess.names, [len(h) for h in g.hands], g.turn, g.finished, g.loser)
    render_table(g.trick, sess.names)

    if g.over:
        won = HUMAN != g.loser
        (st.success if won else st.error)("🎉 You are safe!" if won else "😅 You are the Thulla!")
        if ss.user and not ss.get("offline_recorded"):
            auth.record_result(ss.user["id"], won=won, was_thulla=not won)
            ss.offline_recorded = True
        if st.button("Play again", type="primary"):
            ss.pop("offline"); st.rerun()
    else:
        st.write("**Your turn** 👇" if g.turn == HUMAN else "Waiting…")
        hand = [c.code for c in g.hands[HUMAN]]
        legal = [c.code for c in g.legal_moves(HUMAN)]
        clicked = render_hand(hand, legal, "off", can_act=g.turn == HUMAN)
        if clicked:
            try:
                ss.offline_pending = sess.play_human(clicked)
            except IllegalMove as e:
                st.error(str(e))
            else:
                st.rerun()
    with st.expander("Game log"):
        for line in reversed(sess.log[-12:]):
            st.write(line)
    if st.button("Quit game"):
        ss.pop("offline", None); st.rerun()
