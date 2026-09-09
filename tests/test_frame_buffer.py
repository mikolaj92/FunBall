import tempfile
import unittest
from pathlib import Path

import numpy as np
from funball.frame_buffer import FrameBuffer


class FrameBufferTests(unittest.TestCase):
    def test_limits_pin_and_release_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            store = FrameBuffer(Path(directory), max_bytes=140, max_frames=1)
            frame = np.zeros((2, 2, 3), dtype=np.uint8)
            first = store.publish(0, frame)
            self.assertEqual(np.load(first, allow_pickle=False).shape, frame.shape)
            with self.assertRaises(BufferError):
                store.publish(1, frame)
            with self.assertRaises(ValueError):
                store.publish(0, frame)
            store.release(0)
            self.assertFalse(first.exists())
            second = store.publish(1, frame)
            self.assertTrue(second.exists())
            self.assertLessEqual(store.bytes_used, 140)

    def test_expired_lease_removes_frame_and_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            now = [0.0]
            store = FrameBuffer(Path(directory), max_bytes=1000, max_frames=2,
                                lease_seconds=1, clock=lambda: now[0])
            path = store.publish(0, np.zeros((2, 2, 3), dtype=np.uint8))
            now[0] = 2
            self.assertEqual(store.expire(), [0])
            self.assertFalse(path.exists())
            self.assertEqual(store.bytes_used, 0)
