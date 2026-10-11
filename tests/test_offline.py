import random
import unittest

from thulla.engine.game import IllegalMove
from thulla.offline import HUMAN, OfflineSession


class OfflineTests(unittest.TestCase):
    def test_full_game_with_random_legal_human(self):
        for seed in range(100):
            rng = random.Random(seed)
            s = OfflineSession("Me", rng.randint(1, 7), rng)
            for _ in range(3000):
                if s.game.over: break
                self.assertEqual(s.game.turn, HUMAN)          # bots always hand control back
                s.play_human(rng.choice(s.game.legal_moves(HUMAN)).code)
            self.assertTrue(s.game.over)

    def test_illegal_human_move_rejected(self):
        s = OfflineSession("Me", 3, random.Random(3))
        illegal = next((c for c in s.game.hands[HUMAN] if c not in s.game.legal_moves(HUMAN)), None)
        if illegal:
            with self.assertRaises(IllegalMove): s.play_human(illegal.code)

if __name__ == "__main__":
    unittest.main()
