"""Rule configuration for Thulla.

IMPORTANT: Defaults below are the COMMON ("Bhabhi/Thulla") rules and are
ASSUMPTIONS until the project owner confirms them against the reference
videos (see docs/RULES_CONFIRMATION.md). Every assumption is a field here so it
can be changed without touching engine code.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class RulesConfig:
    min_players: int = 2
    max_players: int = 8
    # ASSUMPTION: standard 52-card deck, all cards dealt (some players may get
    # one extra card when 52 is not divisible by the player count).
    deck_size: int = 52
    # ASSUMPTION: holder of the Ace of Spades leads the first trick.
    starter_is_ace_of_spades: bool = True
    # ASSUMPTION: the first card played in the game must be the Ace of Spades.
    first_card_must_be_ace_spades: bool = True
    # ASSUMPTION: play goes clockwise = increasing seat index.
    clockwise: bool = True
    # ASSUMPTION: must follow lead suit if able.
    must_follow_suit: bool = True
    # ASSUMPTION: a trick ends immediately when someone cannot follow suit
    # ("thulla"); the highest lead-suit card so far collects the whole pile
    # (including the off-suit card) and leads next.
    thulla_ends_trick_immediately: bool = True
    # ASSUMPTION: last player holding cards loses (is the "Thulla").


DEFAULT_RULES = RulesConfig()
