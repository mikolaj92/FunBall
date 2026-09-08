import unittest

from funball.geometry import speed_px_s, speed_to_bgr


class GeometryTests(unittest.TestCase):
    def test_speed_is_distance_over_dt(self):
        self.assertAlmostEqual(speed_px_s(0, 0, 30, 40, 0.1), 500.0)

    def test_zero_dt_is_zero_speed(self):
        self.assertEqual(speed_px_s(0, 0, 10, 10, 0), 0.0)

    def test_slow_is_blue_then_green_yellow_red(self):
        slow = speed_to_bgr(0, 0, 100)
        green = speed_to_bgr(33, 0, 100)
        yellow = speed_to_bgr(66, 0, 100)
        fast = speed_to_bgr(100, 0, 100)
        self.assertGreater(slow[0], slow[1])
        self.assertGreater(slow[0], slow[2])
        self.assertGreater(green[1], green[0])
        self.assertGreater(green[1], green[2])
        self.assertGreater(yellow[1], 180)
        self.assertGreater(yellow[2], 180)
        self.assertGreater(fast[2], fast[0])
        self.assertGreater(fast[2], fast[1])


if __name__ == "__main__":
    unittest.main()
