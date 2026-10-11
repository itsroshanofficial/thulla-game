"""Simple heuristic AI. Always returns a legal move."""
from __future__ import annotations
import random
from .engine.cards import Card
from .engine.game import ThullaGame


def choose_card(game: ThullaGame, seat: int, rng: random.Random | None = None) -> Card:
    rng = rng or random
    legal = game.legal_moves(seat)
    if not legal:
        raise ValueError("No legal moves for this seat")
    if len(legal) == 1:
        return legal[0]
    if not game.trick:                       # leading: play lowest card
        low = min(c.rank for c in legal)
        return rng.choice([c for c in legal if c.rank == low])
    lead = game.lead_suit
    following = [c for c in legal if c.suit == lead]
    if following:                            # follow suit: duck under the top card if possible
        top = max(c.rank for _, c in game.trick if c.suit == lead)
        under = [c for c in following if c.rank < top]
        return max(under, key=lambda c: c.rank) if under else min(following, key=lambda c: c.rank)
    return max(legal, key=lambda c: c.rank)  # void: dump a high card (and hit the leader)
