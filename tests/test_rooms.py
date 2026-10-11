import random
import unittest

from thulla.online.rooms import DISCONNECT_AFTER, RoomError, RoomManager


class Clock:
    def __init__(self): self.t = 100.0
    def __call__(self): return self.t


class RoomTests(unittest.TestCase):
    def setUp(self):
        self.clk = Clock()
        self.m = RoomManager(clock=self.clk, rng=random.Random(4))
        self.code = self.m.create(1, "Ali")
        self.m.join(self.code, 2, "Sara")

    def test_code_format_and_join_case_insensitive(self):
        self.assertEqual(len(self.code), 6)
        self.assertEqual(self.m.join(self.code.lower(), 3, "Zed"), self.code)

    def test_unknown_room_and_full_room(self):
        with self.assertRaises(RoomError): self.m.join("ZZZZZZ", 9, "x")
        for i in range(3, 9): self.m.join(self.code, i, f"p{i}")
        with self.assertRaises(RoomError): self.m.join(self.code, 99, "late")

    def test_only_host_starts_and_needs_two(self):
        with self.assertRaises(RoomError): self.m.start(self.code, 2)
        solo = self.m.create(10, "Solo")
        with self.assertRaises(RoomError): self.m.start(solo, 10)
        self.m.add_bot(solo, 10); self.m.start(solo, 10)

    def test_no_join_after_start_but_reconnect_ok(self):
        self.m.start(self.code, 1)
        with self.assertRaises(RoomError): self.m.join(self.code, 5, "new")
        self.assertEqual(self.m.join(self.code, 2, "Sara"), self.code)   # reconnect

    def test_state_never_leaks_opponent_cards(self):
        self.m.start(self.code, 1)
        room = self.m.rooms[self.code]
        s1, s2 = self.m.state(self.code, 1), self.m.state(self.code, 2)
        for s, other_seat in ((s1, s2["game"]["your_seat"]), (s2, s1["game"]["your_seat"])):
            blob = str(s)
            other_hand = room.game.hands[other_seat]
            mine = set(s["game"]["your_hand"])
            for c in other_hand:
                if c.code not in mine:
                    self.assertNotIn(f"'{c.code}'", blob.replace(str(s["game"]["trick"]), ""))

    def test_server_rejects_invalid_moves(self):
        self.m.start(self.code, 1)
        room = self.m.rooms[self.code]
        turn_uid = next(x.user_id for x in room.members if x.seat == room.game.turn)
        other_uid = 2 if turn_uid == 1 else 1
        with self.assertRaises(RoomError): self.m.play(self.code, other_uid, "AS")   # not your turn
        with self.assertRaises(RoomError): self.m.play(self.code, turn_uid, "garbage")
        with self.assertRaises(RoomError): self.m.play(self.code, 77, "AS")          # not a member

    def test_disconnected_player_is_auto_played_and_can_reconnect(self):
        self.m.start(self.code, 1)
        room = self.m.rooms[self.code]
        away = next(x for x in room.members if x.seat == room.game.turn)
        other = 2 if away.user_id == 1 else 1
        self.clk.t += DISCONNECT_AFTER + 1
        st = self.m.state(self.code, other)               # other player polls
        self.assertTrue(st["game"]["over"] or room.game.turn != away.seat)
        away_view = next(x for x in st["members"] if x["seat"] == away.seat)
        self.assertFalse(away_view["connected"])
        self.m.join(self.code, away.user_id, "x")         # reconnect keeps seat
        self.assertEqual(self.m.state(self.code, away.user_id)["game"]["your_seat"], away.seat)

    def test_leave_in_game_turns_seat_into_bot(self):
        self.m.start(self.code, 1)
        self.m.leave(self.code, 2)
        room = self.m.rooms[self.code]
        self.assertTrue(any(x.bot for x in room.members))

    def test_event_cursor(self):
        self.m.start(self.code, 1)
        s = self.m.state(self.code, 1, since=0)
        self.assertTrue(s["events"])
        self.assertEqual(self.m.state(self.code, 1, since=s["seq"])["events"], [])


if __name__ == "__main__":
    unittest.main()
