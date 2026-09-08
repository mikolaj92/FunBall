import unittest
import numpy as np
from funball.committed import CommittedRenderer
from funball.observation import Observation


def observation(frame_id, shot_id=0, center=(20, 20)):
    return Observation(1, "run", str(frame_id), "sam", frame_id, frame_id * 100000000,
                       shot_id, "ball", "observed", center, 0.2)


class CommittedTests(unittest.TestCase):
    def test_direct_render_breaks_on_miss_and_cut(self):
        renderer = CommittedRenderer()
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        def tick(i, obs, shot=0):
            return renderer.tick(frame, obs, run_id="run", frame_id=i,
                                 pts_ns=i*100000000, shot_id=shot, target_id="ball")
        self.assertGreater(tick(0, observation(0)).sum(), 0)
        tick(1, observation(1, center=(30, 20)))
        self.assertEqual(len(renderer.trail), 2)
        self.assertEqual(tick(2, None).sum(), 0)
        self.assertEqual(len(renderer.trail), 0)
        tick(3, observation(3, center=(40, 20)))
        self.assertEqual(list(renderer.trail)[0].speed, 0)
        tick(4, observation(4, shot_id=1), shot=1)
        self.assertEqual(len(renderer.trail), 1)
        self.assertEqual(tick(5, observation(4, shot_id=1), shot=1).sum(), 0)
