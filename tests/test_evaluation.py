import unittest

from funball import evaluation


class EvaluationTests(unittest.TestCase):
    def test_unknown_visibility_is_excluded_and_absence_is_evaluated(self):
        result = evaluation.evaluate(
            [{"frame_id": 0, "status": "unresolvable"},
             {"frame_id": 1, "status": "absent"},
             {"frame_id": 2, "status": "occluded"}],
            [{"frame_id": i, "center_px": [10, 10]} for i in range(3)],
        )
        self.assertEqual(result["excluded_frames"], 1)
        self.assertEqual(result["false_positive"], 2)
        self.assertIsNone(result["recall"])

    def test_no_markers_does_not_win_recall(self):
        result = evaluation.evaluate(
            [{"frame_id": 0, "status": "visible", "center_px": [10, 10], "radius_px": 2}], []
        )
        self.assertIsNone(result["precision"])
        self.assertEqual(result["recall"], 0.0)

    def test_rejects_duplicates_unknown_frames_and_invalid_geometry(self):
        truth = {"frame_id": 0, "status": "visible", "center_px": [10, 10], "radius_px": 2}
        cases = [
            ([truth, truth], []),
            ([truth], [{"frame_id": 1, "center_px": [10, 10]}]),
            ([truth], [{"frame_id": 0, "center_px": [10, 10]}] * 2),
            ([dict(truth, radius_px=-1)], []),
            ([dict(truth, center_px=[float("nan"), 1])], []),
            ([dict(truth, status="invented")], []),
            ([truth], [{"frame_id": 0, "center_px": [1]}]),
        ]
        for annotations, predictions in cases:
            with self.subTest(annotations=annotations, predictions=predictions):
                with self.assertRaises(ValueError):
                    evaluation.evaluate(annotations, predictions)

    def test_wrong_marker_is_both_false_positive_and_missed_target(self):
        result = evaluation.evaluate(
            [{"frame_id": 0, "status": "visible", "center_px": [10, 10], "radius_px": 2}],
            [{"frame_id": 0, "center_px": [90, 90]}],
        )
        self.assertEqual(result["true_positive"], 0)
        self.assertEqual(result["false_positive"], 1)
        self.assertEqual(result["false_negative"], 1)
        self.assertEqual(result["precision"], 0.0)
        self.assertEqual(result["recall"], 0.0)
