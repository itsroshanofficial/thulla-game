"""Pure-Python Thulla game engine (no UI / network / DB imports)."""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Optional

from .cards import ACE_OF_SPADES, Card, shuffled_deck, sort_hand
from .rules import DEFAULT_RULES, RulesConfig


class IllegalMove(Exception):
    """Raised when a move violates the rules."""


@dataclass
class Event:
    """Game event; the voice system maps `kind` to reaction categories."""
    kind: str  # game_start|card_played|thulla|pile_pickup|trick_clear|player_out|game_over
    player: Optional[int] = None
    data: dict = field(default_factory=dict)


class ThullaGame:
    def __init__(self, num_players: int, rules: RulesConfig = DEFAULT_RULES,
                 rng: random.Random | None = None, deck: list[Card] | None = None):
        if not (rules.min_players <= num_players <= rules.max_players):
            raise ValueError(f"Players must be {rules.min_players}-{rules.max_players}")
        self.rules = rules
        self.n = num_players
        self.hands: list[list[Card]] = [[] for _ in range(self.n)]
        self.trick: list[tuple[int, Card]] = []        # cards on table, in play order
        self.trick_players: list[int] = []            # seats that must play this trick
        self.discarded: list[Card] = []
        self.finished: list[int] = []                 # seats out, in order (winners first)
        self.loser: Optional[int] = None
        self.first_trick = True
        self.turn: int = 0
        self.events: list[Event] = []
        self._deal(deck if deck is not None else shuffled_deck(rng))
        self._start_trick(self._starter())
        self.events.append(Event("game_start", self.turn))

    # ---------------------------------------------------------------- setup
    def _deal(self, deck: list[Card]) -> None:
        for i, card in enumerate(deck):
            self.hands[i % self.n].append(card)
        self.hands = [sort_hand(h) for h in self.hands]

    def _starter(self) -> int:
        if self.rules.starter_is_ace_of_spades:
            for seat, hand in enumerate(self.hands):
                if ACE_OF_SPADES in hand:
                    return seat
        return 0

    def _in_play(self) -> list[int]:
        return [s for s in range(self.n) if s not in self.finished]

    def _next_seat(self, seat: int, among: list[int]) -> int:
        step = 1 if self.rules.clockwise else -1
        for k in range(1, self.n + 1):
            cand = (seat + step * k) % self.n
            if cand in among:
                return cand
        return seat

    def _start_trick(self, leader: int) -> None:
        self.trick = []
        self.trick_players = self._in_play()
        self.turn = leader

    # ---------------------------------------------------------------- queries
    @property
    def over(self) -> bool:
        return self.loser is not None

    @property
    def lead_suit(self) -> Optional[str]:
        return self.trick[0][1].suit if self.trick else None

    def legal_moves(self, seat: int) -> list[Card]:
        if self.over or seat != self.turn:
            return []
        hand = self.hands[seat]
        if not self.trick:
            if self.first_trick and self.rules.first_card_must_be_ace_spades \
                    and ACE_OF_SPADES in hand:
                return [ACE_OF_SPADES]
            return list(hand)
        if self.rules.must_follow_suit:
            same = [c for c in hand if c.suit == self.lead_suit]
            if same:
                return same
        return list(hand)

    def current_winner(self) -> Optional[int]:
        """Seat holding the highest lead-suit card on the table."""
        if not self.trick:
            return None
        ls = self.lead_suit
        return max((p for p in self.trick if p[1].suit == ls), key=lambda p: p[1].rank)[0]

    # ---------------------------------------------------------------- moves
    def play(self, seat: int, card: Card) -> list[Event]:
        if self.over:
            raise IllegalMove("Game is over")
        if seat != self.turn:
            raise IllegalMove("Not your turn")
        if card not in self.hands[seat]:
            raise IllegalMove("You do not hold that card")
        if card not in self.legal_moves(seat):
            raise IllegalMove("Illegal card: you must follow the lead suit / start card")

        new: list[Event] = []
        self.hands[seat].remove(card)
        self.trick.append((seat, card))
        self.first_trick = False
        new.append(Event("card_played", seat, {"card": card.code}))

        off_suit = len(self.trick) > 1 and card.suit != self.lead_suit
        if off_suit and self.rules.thulla_ends_trick_immediately:
            winner = self.current_winner()
            new.append(Event("thulla", seat, {"victim": winner}))
            self._pickup(winner, new)
        else:
            played = {p for p, _ in self.trick}
            if all(p in played for p in self.trick_players):
                # everyone followed suit -> pile is discarded
                winner = self.current_winner()
                self.discarded.extend(c for _, c in self.trick)
                new.append(Event("trick_clear", winner))
                self._finish_trick(winner, new)
            else:
                self.turn = self._next_seat(
                    seat, [p for p in self.trick_players if p not in played])
        self.events.extend(new)
        return new

    def _pickup(self, winner: int, new: list[Event]) -> None:
        pile = [c for _, c in self.trick]
        self.hands[winner] = sort_hand(self.hands[winner] + pile)
        new.append(Event("pile_pickup", winner, {"count": len(pile)}))
        self._finish_trick(winner, new)

    def _finish_trick(self, next_leader: int, new: list[Event]) -> None:
        for s in range(self.n):
            if s not in self.finished and not self.hands[s]:
                self.finished.append(s)
                new.append(Event("player_out", s, {"place": len(self.finished)}))
        remaining = self._in_play()
        if len(remaining) <= 1:
            self.loser = remaining[0] if remaining else self.finished.pop()
            if self.loser in self.finished:
                self.finished.remove(self.loser)
            new.append(Event("game_over", self.loser))
            self.trick, self.trick_players = [], []
            return
        leader = next_leader if next_leader in remaining else self._next_seat(next_leader, remaining)
        self._start_trick(leader)

    # ---------------------------------------------------------------- views
    def view_for(self, seat: int) -> dict:
        """State visible to one seat. Never includes other players' cards."""
        return {
            "n": self.n,
            "your_seat": seat,
            "your_hand": [c.code for c in self.hands[seat]],
            "legal": [c.code for c in self.legal_moves(seat)],
            "hand_counts": [len(h) for h in self.hands],
            "trick": [(p, c.code) for p, c in self.trick],
            "lead_suit": self.lead_suit,
            "turn": self.turn,
            "finished": list(self.finished),
            "loser": self.loser,
            "over": self.over,
        }
