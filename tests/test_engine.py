import random
import unittest

from thulla.ai import choose_card
from thulla.engine.cards import Card, full_deck, ACE_OF_SPADES
from thulla.engine.game import IllegalMove, ThullaGame


def rigged(hands):
    """Build a deck so seat i receives hands[i] (round-robin deal)."""
    n = len(hands)
    longest = max(len(h) for h in hands)
    deck = []
    for k in range(longest):
        for i in range(n):
            if k < len(hands[i]):
                deck.append(Card.from_code(hands[i][k]))
    return deck


class EngineTests(unittest.TestCase):
    def test_deck(self):
        d = full_deck()
        self.assertEqual(len(set(d)), 52)

    def test_deal_all_cards_any_player_count(self):
        for n in range(2, 9):
            g = ThullaGame(n, rng=random.Random(n))
            self.assertEqual(sum(len(h) for h in g.hands), 52)
            self.assertLessEqual(max(map(len, g.hands)) - min(map(len, g.hands)), 1)

    def test_ace_of_spades_starts_and_is_forced(self):
        g = ThullaGame(4, rng=random.Random(1))
        self.assertIn(ACE_OF_SPADES, g.hands[g.turn])
        self.assertEqual(g.legal_moves(g.turn), [ACE_OF_SPADES])
        with self.assertRaises(IllegalMove):
            other = next(c for c in g.hands[g.turn] if c != ACE_OF_SPADES)
            g.play(g.turn, other)

    def test_wrong_turn_and_unowned_card(self):
        g = ThullaGame(3, rng=random.Random(2))
        other = (g.turn + 1) % 3
        with self.assertRaises(IllegalMove):
            g.play(other, g.hands[other][0])
        with self.assertRaises(IllegalMove):
            g.play(g.turn, g.hands[other][0])

    def test_must_follow_suit(self):
        deck = rigged([["AS", "2H"], ["3S", "4H"], ["5C", "6D"]])
        g = ThullaGame(3, deck=deck)
        g.play(0, Card.from_code("AS"))
        self.assertEqual(g.legal_moves(1), [Card.from_code("3S")])

    def test_thulla_highest_lead_suit_collects_pile(self):
        # seat0 leads AS; seat1 follows 3S; seat2 has no spade -> thulla (5C)
        deck = rigged([["AS", "2H"], ["3S", "4H"], ["5C", "6D"]])
        g = ThullaGame(3, deck=deck)
        g.play(0, Card.from_code("AS"))
        g.play(1, Card.from_code("3S"))
        ev = g.play(2, Card.from_code("5C"))
        kinds = [e.kind for e in ev]
        self.assertIn("thulla", kinds)
        self.assertIn("pile_pickup", kinds)
        # seat 0 holds AS (highest spade) -> collects 3 cards and leads next
        self.assertEqual(len(g.hands[0]), 1 + 3)
        self.assertEqual(g.turn, 0)

    def test_clean_trick_discards_and_highest_leads(self):
        deck = rigged([["AS", "2H"], ["3S", "4H"]])
        g = ThullaGame(2, deck=deck)
        g.play(0, Card.from_code("AS"))
        ev = g.play(1, Card.from_code("3S"))
        self.assertIn("trick_clear", [e.kind for e in ev])
        self.assertEqual(len(g.discarded), 2)
        self.assertEqual(g.turn, 0)

    def test_game_ends_with_one_loser(self):
        g = ThullaGame(2, rng=random.Random(0))
        g.hands = [[Card.from_code("AS")], [Card.from_code("3S"), Card.from_code("4H")]]
        g._start_trick(g._starter())
        g.play(0, Card.from_code("AS"))
        g.play(1, Card.from_code("3S"))
        self.assertTrue(g.over)
        self.assertEqual(g.finished, [0])
        self.assertEqual(g.loser, 1)

    def test_view_hides_other_hands(self):
        g = ThullaGame(4, rng=random.Random(5))
        v = g.view_for(0)
        self.assertEqual(v["your_hand"], [c.code for c in g.hands[0]])
        self.assertNotIn("hands", v)
        flat = str(v)
        for c in g.hands[1]:
            if c not in g.hands[0]:
                self.assertNotIn(f"'{c.code}'", flat)

    def test_ai_fuzz_always_terminates_and_conserves_cards(self):
        for seed in range(500):
            rng = random.Random(seed)
            n = rng.randint(2, 8)
            g = ThullaGame(n, rng=rng)
            for _ in range(5000):
                if g.over:
                    break
                g.play(g.turn, choose_card(g, g.turn, rng))
            self.assertTrue(g.over, f"seed {seed} did not finish")
            total = sum(len(h) for h in g.hands) + len(g.discarded) + len(g.trick)
            self.assertEqual(total, 52)
            self.assertEqual(len(g.finished) + 1, n)


if __name__ == "__main__":
    unittest.main()
