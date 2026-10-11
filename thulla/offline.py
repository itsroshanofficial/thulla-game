"""Offline game controller (no network, no DB). Human is always seat 0."""
from __future__ import annotations
import random

from .ai import choose_card
from .engine.cards import Card
from .engine.game import Event, IllegalMove, ThullaGame

HUMAN = 0


def describe(ev: Event, names: list[str]) -> str | None:
    n = lambda s: names[s] if s is not None else "?"
    if ev.kind == "game_start":
        return f"Game on! {n(ev.player)} has the Ace of Spades and starts."
    if ev.kind == "card_played":
        from .engine.cards import Card as C
        return f"{n(ev.player)} played {C.from_code(ev.data['card'])}"
    if ev.kind == "thulla":
        return f"🔥 THULLA by {n(ev.player)}!"
    if ev.kind == "pile_pickup":
        return f"{n(ev.player)} picks up {ev.data['count']} cards."
    if ev.kind == "trick_clear":
        return f"Pile cleared. {n(ev.player)} leads next."
    if ev.kind == "player_out":
        return f"✅ {n(ev.player)} is out (place {ev.data['place']})."
    if ev.kind == "game_over":
        return f"🏁 Game over — {n(ev.player)} is the Thulla!"
    return None


class OfflineSession:
    def __init__(self, nickname: str, num_ai: int, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.names = [nickname or "You"] + [f"Bot {i}" for i in range(1, num_ai + 1)]
        self.game = ThullaGame(len(self.names), rng=self.rng)
        self.log: list[str] = []
        self.new_events: list[Event] = []
        self._collect(self.game.events)
        self.advance_ai()

    def _collect(self, events):
        self.new_events.extend(events)
        for e in events:
            if e.kind != "card_played":
                t = describe(e, self.names)
                if t:
                    self.log.append(t)
        self.log = self.log[-30:]

    def advance_ai(self) -> None:
        g = self.game
        while not g.over and g.turn != HUMAN:
            seat = g.turn
            card = choose_card(g, seat, self.rng)
            self.log.append(f"{self.names[seat]} played {card}")
            self._collect(g.play(seat, card))

    def play_human(self, card_code: str) -> list[Event]:
        """Validate + play the human's card, then let bots respond. Returns new events."""
        self.new_events = []
        self._collect(self.game.play(HUMAN, Card.from_code(card_code)))  # may raise IllegalMove
        self.advance_ai()
        return self.new_events

    def take_events(self) -> list[Event]:
        ev, self.new_events = self.new_events, []
        return ev
