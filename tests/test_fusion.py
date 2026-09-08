import importlib.util
import unittest
from pathlib import Path

from funball.fusion import Fusion
from funball.observation import Observation


@unittest.skipUnless(importlib.util.find_spec("splot"), "requires optional Splot Mojo binding")
class FusionTests(unittest.TestCase):
    def test_real_splot_switches_and_rejects_stale_candidates(self):
        fusion = Fusion(Path(__file__).resolve().parents[1] / "examples/dual-channel/tracking.profile.toml")
        def obs(channel, i, uncertainty, shot=0):
            return Observation(1, "run", f"{channel}-{i}", channel, i, i*100,
                               shot, "ball", "observed", (10, 20), uncertainty)
        def choose(i, items, shot=0):
            return fusion.choose(items, run_id="run", frame_id=i, pts_ns=i*100,
                                 shot_id=shot, target_id="ball")
        self.assertEqual(choose(0, [obs("sam", 0, .2)]).channel, "sam")
        self.assertEqual(choose(1, [obs("sam", 1, .3), obs("tracker", 1, .1)]).channel, "tracker")
        self.assertEqual(choose(2, [obs("sam", 2, .09), obs("tracker", 2, .1)]).channel, "tracker")
        self.assertEqual(choose(3, [obs("sam", 3, .5), obs("tracker", 2, .01)]).channel, "sam")
        self.assertIsNone(choose(4, [obs("sam", 3, .01)]))
        self.assertIsNone(choose(5, [obs("tracker", 5, .01)], shot=1))
        self.assertEqual(choose(6, [obs("sam", 6, .2, shot=1)], shot=1).channel, "sam")
