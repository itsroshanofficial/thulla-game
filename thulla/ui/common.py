"""Shared Streamlit helpers: session state, table rendering, voice."""
from __future__ import annotations
import streamlit as st
import streamlit.components.v1 as components

from ..engine.cards import Card
from ..voice.lines import CATEGORIES, LANGUAGES
from ..voice.manager import VoiceDirector, VoiceSettings
from ..voice.player import build_playback_html


def init_state() -> None:
    ss = st.session_state
    ss.setdefault("user", None)          # {"id","username","nickname"}
    ss.setdefault("token", None)
    # Per-session (= per-player) voice settings: never shared between players.
    ss.setdefault("voice", VoiceDirector(VoiceSettings()))
    ss.setdefault("audio_html", None)


def card_html(code: str) -> str:
    c = Card.from_code(code)
    red = "red" if c.suit in "HD" else ""
    return f'<span class="pcard {red}">{c.label}</span>'


def render_reaction_and_voice(events, my_seat) -> None:
    """Show a pop animation + play at most one voice line for a batch of events."""
    kinds = [e.kind for e in events]
    if "thulla" in kinds:
        st.markdown('<div class="pop">🔥 THULLA! 🤣</div>', unsafe_allow_html=True)
    elif "game_over" in kinds:
        st.markdown('<div class="pop">🏁 Game over!</div>', unsafe_allow_html=True)
    director: VoiceDirector = st.session_state.voice
    line = director.pick_for_events(events, my_seat)
    if line:
        components.html(build_playback_html(line, director.settings.volume), height=36)
        st.caption(f"🗣️ {line['text']}")


def render_seats(names, counts, turn, finished, loser=None) -> None:
    cols = st.columns(min(4, len(names)))
    for i, name in enumerate(names):
        cls = "seat" + (" turn" if i == turn and loser is None else "") + (" out" if i in finished else "")
        badge = "▶ " if (i == turn and loser is None) else ""
        status = "🏆 out" if i in finished else ("😅 Thulla" if i == loser else f"🂠 {counts[i]}")
        cols[i % len(cols)].markdown(f'<div class="{cls}">{badge}<b>{name}</b><br>{status}</div>',
                                     unsafe_allow_html=True)


def render_table(trick, names) -> None:
    if trick:
        cards = "".join(f"<div style='display:inline-block;margin:0 .3rem'>{card_html(c)}"
                        f"<div style='font-size:.7rem'>{names[p]}</div></div>" for p, c in trick)
    else:
        cards = "<i>Table is empty — waiting for a lead card</i>"
    st.markdown(f'<div class="table">{cards}</div>', unsafe_allow_html=True)


def render_hand(hand_codes, legal_codes, key_prefix, can_act: bool):
    """Return the clicked card code (or None)."""
    clicked = None
    per_row = 6
    for start in range(0, len(hand_codes), per_row):
        row = hand_codes[start:start + per_row]
        cols = st.columns(per_row)
        for col, code in zip(cols, row):
            if col.button(Card.from_code(code).label, key=f"{key_prefix}_{code}",
                          disabled=not (can_act and code in legal_codes),
                          use_container_width=True):
                clicked = code
    return clicked


def _toggle_mute() -> None:
    st.session_state["v_enabled"] = not st.session_state.get("v_enabled", True)


def voice_settings_ui() -> None:
    d: VoiceDirector = st.session_state.voice
    s = d.settings
    st.subheader("🔊 Funny voices")
    s.enabled = st.toggle("Enable funny voices", value=s.enabled, key="v_enabled")
    s.volume = st.slider("Voice volume", 0.0, 1.0, float(s.volume), 0.05, key="v_volume")
    langs = st.multiselect("Languages", list(LANGUAGES), default=sorted(s.languages),
                           format_func=LANGUAGES.get, key="v_langs")
    s.languages = set(langs)
    cats = st.multiselect("Reaction types", list(CATEGORIES), default=sorted(s.categories), key="v_cats")
    s.categories = set(cats)
    st.button("🔇 Mute all" if s.enabled else "🔈 Unmute", key="v_mute", on_click=_toggle_mute)
    if st.button("▶ Test / unlock sound", key="v_test"):
        from ..voice.lines import LINES
        line = LINES["thulla"][0]
        components.html(build_playback_html(line, s.volume), height=36)
    st.caption("Tip: browsers only allow sound after you interact with the page. "
               "Press “Test / unlock sound” once.")
