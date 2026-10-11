import random
import unittest

from thulla.engine.game import Event
from thulla.voice.lines import CATEGORIES, LINES
from thulla.voice.manager import VoiceDirector, VoiceSettings


class Clock:
    def __init__(self): self.t = 1000.0
    def __call__(self): return self.t


class VoiceTests(unittest.TestCase):
    def mk(self, **kw):
        clk = Clock()
        d = VoiceDirector(VoiceSettings(**kw), rng=random.Random(1), clock=clk)
        return d, clk

    def test_all_categories_have_lines_in_every_language(self):
        for c in CATEGORIES:
            langs = {l["lang"] for l in LINES[c]}
            self.assertEqual(langs, {"pa", "ur", "en"}, c)

    def test_thulla_triggers_thulla_line(self):
        d, _ = self.mk()
        line = d.pick_for_events([Event("thulla", 1)])
        self.assertEqual(line["category"], "thulla")

    def test_muted_player_gets_nothing(self):
        d, _ = self.mk(enabled=False)
        self.assertIsNone(d.pick_for_events([Event("thulla", 1)]))
        d2, _ = self.mk(volume=0.0)
        self.assertIsNone(d2.pick_for_events([Event("thulla", 1)]))

    def test_cooldown_blocks_spam_then_allows(self):
        d, clk = self.mk()
        self.assertIsNotNone(d.pick_for_events([Event("thulla", 1)]))
        self.assertIsNone(d.pick_for_events([Event("thulla", 1)]))
        clk.t += 2
        self.assertIsNotNone(d.pick_for_events([Event("thulla", 1)]))

    def test_one_line_per_batch_highest_priority(self):
        d, _ = self.mk()
        line = d.pick_for_events([Event("card_played", 0), Event("thulla", 1),
                                  Event("pile_pickup", 0)])
        self.assertEqual(line["category"], "thulla")

    def test_language_filter(self):
        d, clk = self.mk(languages={"pa"})
        for _ in range(20):
            clk.t += 10
            line = d.pick_for_events([Event("thulla", 1)])
            self.assertEqual(line["lang"], "pa")

    def test_category_filter(self):
        d, _ = self.mk(categories={"victory"})
        self.assertIsNone(d.pick_for_events([Event("thulla", 1)]))

    def test_no_immediate_repeat(self):
        d, clk = self.mk()
        ids = []
        for _ in range(4):
            clk.t += 10
            ids.append(d.pick_for_events([Event("thulla", 1)])["id"])
        self.assertEqual(len(set(ids)), 4)

    def test_game_over_winner_vs_loser(self):
        d, _ = self.mk()
        self.assertEqual(d.pick_for_events([Event("game_over", 2)], my_seat=2)["category"], "defeat")
        d2, _ = self.mk()
        self.assertEqual(d2.pick_for_events([Event("game_over", 2)], my_seat=0)["category"], "victory")

    def test_settings_are_independent(self):
        a, b = VoiceSettings(), VoiceSettings()
        a.enabled = False; a.languages.discard("pa")
        self.assertTrue(b.enabled); self.assertIn("pa", b.languages)


if __name__ == "__main__":
    unittest.main()
