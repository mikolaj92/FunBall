import unittest

import numpy as np

from funball.detect import Detection
from funball.pipeline import Pipeline


class PipelineTests(unittest.TestCase):
    def test_tick_paints_trail_and_reports_speed(self):
        pipeline = Pipeline()
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        first = pipeline.tick(frame, [Detection(10, 10, track_id=1)], 0.0, click=(10, 10))
        second = pipeline.tick(frame, [Detection(40, 50, track_id=1)], 0.1)
        self.assertIsNotNone(first.locked)
        self.assertAlmostEqual(second.speed, 500.0)
        self.assertEqual(len(pipeline.trail), 2)
        self.assertFalse(np.array_equal(second.frame, frame))

    def test_lost_lock_clears_trail(self):
        pipeline = Pipeline()
        pipeline.lock.lost_frames = 1
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        pipeline.tick(frame, [Detection(10, 10, track_id=1)], 0.0, click=(10, 10))
        lost = pipeline.tick(frame, [], 0.1)
        self.assertIsNone(lost.locked)
        self.assertEqual(len(pipeline.trail), 0)


if __name__ == "__main__":
    unittest.main()
