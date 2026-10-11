"""Server-side room logic (framework-independent so it can be unit-tested).

All moves are validated by the engine on the server; clients only ever receive
`ThullaGame.view_for(seat)`, which never contains other players' cards.
"""
from __future__ import annotations
import random
import secrets
import time
from dataclasses import dataclass, field
from typing import Optional

from ..ai import choose_card
from ..engine.cards import Card
from ..engine.game import IllegalMove, ThullaGame

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # no 0/O/1/I
MAX_PLAYERS = 8
DISCONNECT_AFTER = 45.0     # seconds without contact -> bot plays for that seat


class RoomError(Exception):
    """Safe-to-display error."""


@dataclass
class Member:
    user_id: Optional[int]       # None for bots
    nickname: str
    last_seen: float
    bot: bool = False
    seat: Optional[int] = None


@dataclass
class Room:
    code: str
    host: int
    members: list = field(default_factory=list)
    game: Optional[ThullaGame] = None
    status: str = "lobby"        # lobby | playing | over
    event_log: list = field(default_factory=list)   # (seq, kind, seat, text)
    seq: int = 0


class RoomManager:
    def __init__(self, clock=time.monotonic, rng: random.Random | None = None):
        self.clock = clock
        self.rng = rng or random.Random()
        self.rooms: dict[str, Room] = {}

    # ------------------------------------------------------------ helpers
    def _room(self, code: str) -> Room:
        r = self.rooms.get(code.strip().upper())
        if not r:
            raise RoomError("Room not found.")
        return r

    def _member(self, room: Room, uid: int) -> Member:
        for m in room.members:
            if m.user_id == uid and not m.bot:
                return m
        raise RoomError("You are not in this room.")

    def _log(self, room: Room, events) -> None:
        for e in events:
            room.seq += 1
            room.event_log.append((room.seq, e.kind, e.player, e.data))
        room.event_log = room.event_log[-100:]

    # ------------------------------------------------------------ lobby
    def create(self, uid: int, nickname: str) -> str:
        for _ in range(20):
            code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(6))
            if code not in self.rooms:
                break
        room = Room(code=code, host=uid)
        room.members.append(Member(uid, nickname, self.clock()))
        self.rooms[code] = room
        return code

    def join(self, code: str, uid: int, nickname: str) -> str:
        room = self._room(code)
        for m in room.members:
            if m.user_id == uid and not m.bot:       # reconnect / duplicate join
                m.last_seen = self.clock()
                return room.code
        if room.status != "lobby":
            raise RoomError("Game already started.")
        if len(room.members) >= MAX_PLAYERS:
            raise RoomError("Room is full.")
        room.members.append(Member(uid, nickname, self.clock()))
        return room.code

    def add_bot(self, code: str, uid: int) -> None:
        room = self._room(code)
        if uid != room.host:
            raise RoomError("Only the host can add bots.")
        if room.status != "lobby":
            raise RoomError("Game already started.")
        if len(room.members) >= MAX_PLAYERS:
            raise RoomError("Room is full.")
        n = sum(m.bot for m in room.members) + 1
        room.members.append(Member(None, f"Bot {n}", self.clock(), bot=True))

    def leave(self, code: str, uid: int) -> None:
        room = self._room(code)
        m = self._member(room, uid)
        if room.status == "lobby":
            room.members.remove(m)
            humans = [x for x in room.members if not x.bot]
            if not humans:
                del self.rooms[room.code]
            elif room.host == uid:
                room.host = humans[0].user_id
        else:
            m.bot = True              # a bot takes over the seat
            self._advance_bots(room)

    def start(self, code: str, uid: int) -> None:
        room = self._room(code)
        if uid != room.host:
            raise RoomError("Only the host can start the game.")
        if room.status != "lobby":
            raise RoomError("Game already started.")
        if len(room.members) < 2:
            raise RoomError("Need at least 2 players (add a bot to play alone).")
        self.rng.shuffle(room.members)
        for i, m in enumerate(room.members):
            m.seat = i
        room.game = ThullaGame(len(room.members), rng=self.rng)
        room.status = "playing"
        self._log(room, room.game.events)
        self._advance_bots(room)

    # ------------------------------------------------------------ play
    def play(self, code: str, uid: int, card_code: str) -> None:
        room = self._room(code)
        m = self._member(room, uid)
        m.last_seen = self.clock()
        if room.status != "playing":
            raise RoomError("Game is not in progress.")
        try:
            card = Card.from_code(card_code)
            events = room.game.play(m.seat, card)
        except (IllegalMove, ValueError, KeyError) as e:
            raise RoomError(str(e) if isinstance(e, IllegalMove) else "Invalid card.")
        self._log(room, events)
        self._advance_bots(room)

    def _advance_bots(self, room: Room) -> None:
        """Let bots (and long-disconnected humans) play until a connected human is up."""
        now = self.clock()
        g = room.game
        while g and not g.over:
            m = next(x for x in room.members if x.seat == g.turn)
            away = (not m.bot) and now - m.last_seen > DISCONNECT_AFTER
            if not (m.bot or away):
                break
            self._log(room, g.play(g.turn, choose_card(g, g.turn, self.rng)))
        if g and g.over:
            room.status = "over"

    # ------------------------------------------------------------ state
    def state(self, code: str, uid: int, since: int = 0) -> dict:
        room = self._room(code)
        me = self._member(room, uid)
        me.last_seen = self.clock()
        if room.status == "playing":
            self._advance_bots(room)       # handles disconnect takeover lazily
        now = self.clock()
        out = {
            "code": room.code, "status": room.status, "host": room.host == uid,
            "members": [{"nickname": m.nickname, "bot": m.bot, "seat": m.seat,
                         "connected": m.bot or now - m.last_seen <= DISCONNECT_AFTER}
                        for m in room.members],
            "seq": room.seq,
            "events": [{"seq": s, "kind": k, "seat": p, "data": d}
                       for s, k, p, d in room.event_log if s > since],
            "game": None,
        }
        if room.game:
            out["game"] = room.game.view_for(me.seat)
        return out
