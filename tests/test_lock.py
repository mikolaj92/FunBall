import unittest

from funball.detect import Detection
from funball.lock import BallLock


class LockTests(unittest.TestCase):
    def test_click_locks_nearest_not_highest_conf(self):
        lock = BallLock()
        chosen = lock.update(
            [
                Detection(800, 80, conf=0.99, track_id=2),
                Detection(120, 400, conf=0.6, track_id=1),
            ],
            click=(125, 405),
        )
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen.track_id, 1)
        self.assertEqual(lock.track_id, 1)

    def test_holds_track_id_and_does_not_hop(self):
        lock = BallLock()
        lock.update([Detection(10, 10, track_id=1)], click=(10, 10))
        chosen = lock.update(
            [
                Detection(800, 800, conf=0.99, track_id=2),
                Detection(20, 20, conf=0.4, track_id=1),
            ]
        )
        self.assertEqual(chosen.track_id, 1)
        self.assertEqual(lock.track_id, 1)

    def test_lost_frames_drop_lock_instead_of_hopping(self):
        lock = BallLock(lost_frames=2)
        lock.update([Detection(10, 10, track_id=1)], click=(10, 10))
        self.assertIsNone(lock.update([Detection(800, 800, track_id=2)]))
        self.assertTrue(lock.held)
        self.assertIsNone(lock.update([Detection(800, 800, track_id=2)]))
        self.assertFalse(lock.held)

    def test_without_ids_rejects_jump_beyond_max(self):
        lock = BallLock(max_jump_px=30)
        lock.update([Detection(10, 10)])
        chosen = lock.update([Detection(400, 400, conf=0.99)])
        self.assertIsNone(chosen)
        self.assertTrue(lock.held)

    def test_without_click_does_not_guess_among_many(self):
        lock = BallLock()
        chosen = lock.update(
            [
                Detection(80, 80, conf=0.99),
                Detection(200, 200, conf=0.4),
            ]
        )
        self.assertIsNone(chosen)
        self.assertFalse(lock.held)

    def test_without_click_locks_the_only_detection(self):
        lock = BallLock()
        chosen = lock.update([Detection(80, 80, conf=0.6)])
        self.assertEqual((chosen.x, chosen.y), (80, 80))


if __name__ == "__main__":
    unittest.main()
