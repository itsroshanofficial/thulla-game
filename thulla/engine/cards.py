"""Cards and deck helpers."""
from __future__ import annotations
import random
from dataclasses import dataclass

SUITS = ("S", "H", "D", "C")
SUIT_SYMBOL = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}
RANK_LABEL = {11: "J", 12: "Q", 13: "K", 14: "A"}


@dataclass(frozen=True, order=True)
class Card:
    rank: int  # 2..14 (14 = Ace)
    suit: str  # one of SUITS

    def __post_init__(self):
        if not (2 <= self.rank <= 14) or self.suit not in SUITS:
            raise ValueError(f"Invalid card: {self.rank}{self.suit}")

    @property
    def code(self) -> str:
        """Stable string id, e.g. 'AS', '10H'."""
        return f"{RANK_LABEL.get(self.rank, str(self.rank))}{self.suit}"

    @property
    def label(self) -> str:
        return f"{RANK_LABEL.get(self.rank, str(self.rank))}{SUIT_SYMBOL[self.suit]}"

    @staticmethod
    def from_code(code: str | "Card") -> "Card":
        if isinstance(code, Card):
            return code
        suit, r = code[-1], code[:-1]
        inv = {v: k for k, v in RANK_LABEL.items()}
        rank = inv[r] if r in inv else int(r)
        return Card(rank, suit)

    def __str__(self) -> str:
        return self.label


ACE_OF_SPADES = Card(14, "S")


def full_deck() -> list[Card]:
    return [Card(r, s) for s in SUITS for r in range(2, 15)]


def shuffled_deck(rng: random.Random | None = None) -> list[Card]:
    deck = full_deck()
    (rng or random).shuffle(deck)
    return deck


def sort_hand(cards) -> list[Card]:
    order = {s: i for i, s in enumerate(SUITS)}
    return sorted(cards, key=lambda c: (order[c.suit], c.rank))