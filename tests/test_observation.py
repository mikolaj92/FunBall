import unittest

from funball.observation import Observation


class ObservationTests(unittest.TestCase):
    def test_invalid_messages_fail_closed(self):
        base = dict(v=1, run_id="r", request_id="s", channel="sam", frame_id=0,
                    pts_ns=0, shot_id=0, target_id="ball", status="observed",
                    center_px=[1, 2], uncertainty=0.2)
        for change in [dict(v=2), dict(pts_ns=-1), dict(frame_id=True),
                       dict(channel=""), dict(status="predicted"),
                       dict(center_px=None), dict(center_px=[float("nan"), 2]),
                       dict(center_px=[-1, 2]), dict(uncertainty=2),
                       dict(uncertainty=float("nan")), dict(status="lost")]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                Observation.from_dict(base | change)
        lost = Observation.from_dict(base | dict(status="lost", center_px=None, uncertainty=1.0))
        self.assertFalse(lost.eligible(run_id="r", frame_id=0, pts_ns=0, shot_id=0, target_id="ball"))

    def test_roundtrip_and_exact_frame_eligibility(self):
        message = dict(v=1, run_id="run", request_id="sam-1", channel="sam",
                       frame_id=10, pts_ns=100, shot_id=0, target_id="ball",
                       status="observed", center_px=[20, 30], uncertainty=0.2)
        observation = Observation.from_dict(message)
        self.assertEqual(observation.to_dict(), message)
        self.assertTrue(observation.eligible(run_id="run", frame_id=10, pts_ns=100, shot_id=0, target_id="ball"))
        self.assertFalse(observation.eligible(run_id="run", frame_id=11, pts_ns=110, shot_id=0, target_id="ball"))
        self.assertFalse(observation.eligible(run_id="run", frame_id=10, pts_ns=100, shot_id=1, target_id="ball"))
