"""Voice director: maps game events to reactions.

* One VoiceDirector (and one VoiceSettings) per player/session, so one player's
  settings never affect another's.
* Cooldown, no-immediate-repeat, and at most ONE line per batch of events.
"""
from __future__ import annotations
import random
import time
from dataclasses import dataclass, field
from typing import Iterable, Optional

from .lines import CATEGORIES, LINES


@dataclass
class VoiceSettings:
    enabled: bool = True
    volume: float = 0.8                          # 0.0 - 1.0
    languages: set = field(default_factory=lambda: {"pa", "ur", "en"})
    categories: set = field(default_factory=lambda: set(CATEGORIES))

    def clamp(self) -> "VoiceSettings":
        self.volume = max(0.0, min(1.0, float(self.volume)))
        return self


# event kind -> (category choices for self/other, priority, probability)
# priority: higher wins when several events arrive in one batch.
EVENT_MAP = {
    "thulla":      (("thulla",), 5, 1.0),
    "game_over":   (None, 6, 1.0),             # victory/defeat chosen from outcome
    "player_out":  (("victory",), 4, 0.9),
    "pile_pickup": (("surprise", "teasing"), 3, 0.7),
    "trick_clear": (("commentary", "random"), 1, 0.25),
    "game_start":  (("commentary",), 2, 1.0),
    "card_played": (("commentary", "random"), 0, 0.08),
}
HIGH_PRIORITY = 4


class VoiceDirector:
    def __init__(self, settings: VoiceSettings | None = None,
                 cooldown: float = 4.0, urgent_cooldown: float = 1.5,
                 rng: random.Random | None = None, clock=time.monotonic):
        self.settings = settings or VoiceSettings()
        self.cooldown = cooldown
        self.urgent_cooldown = urgent_cooldown
        self.rng = rng or random.Random()
        self.clock = clock
        self._last_time = -1e9
        self._recent: list[str] = []

    def _eligible(self, category: str) -> list[dict]:
        s = self.settings
        return [l for l in LINES.get(category, [])
                if l["lang"] in s.languages and l["id"] not in self._recent]

    def pick_for_events(self, events: Iterable, my_seat: Optional[int] = None) -> Optional[dict]:
        """Return at most one line for a batch of engine events, or None."""
        s = self.settings
        if not s.enabled or s.volume <= 0:
            return None
        best = None
        for ev in events:
            spec = EVENT_MAP.get(ev.kind)
            if not spec:
                continue
            cats, prio, prob = spec
            if ev.kind == "game_over":
                cats = ("victory",) if ev.player != my_seat else ("defeat",)
            if best is None or prio > best[1]:
                best = (cats, prio, prob)
        if best is None:
            return None
        cats, prio, prob = best
        now = self.clock()
        wait = self.urgent_cooldown if prio >= HIGH_PRIORITY else self.cooldown
        if now - self._last_time < wait:
            return None
        if self.rng.random() > prob:
            return None
        order = [c for c in cats if c in s.categories]
        self.rng.shuffle(order)
        for cat in order:
            pool = self._eligible(cat)
            if pool:
                line = self.rng.choice(pool)
                self._last_time = now
                self._recent = (self._recent + [line["id"]])[-4:]
                return line
        return None
