import unittest

from funball.detect import Detection, is_projectile


class ProjectileTests(unittest.TestCase):
    def test_any_ball_or_puck_is_the_same_object(self):
        names = [
            "sports ball",
            "ball",
            "tennis ball",
            "soccer ball",
            "football",
            "basketball",
            "volleyball",
            "puck",
            "hockey puck",
        ]
        for name in names:
            self.assertTrue(is_projectile(name), name)

    def test_people_and_goals_are_not_projectiles(self):
        for name in ("person", "player", "goal", "net", "stick", "racket"):
            self.assertFalse(is_projectile(name), name)

    def test_detection_contract_has_no_sport(self):
        item = Detection.from_dict({"x": 1, "y": 2, "conf": 0.4, "track_id": 7})
        self.assertEqual((item.x, item.y, item.conf, item.track_id), (1.0, 2.0, 0.4, 7))

    def test_dedicated_ball_model_keeps_unnamed_class(self):
        names = {0: "object", 1: "target"}
        dedicated = not any(is_projectile(name) for name in names.values())
        self.assertTrue(dedicated)
        coco = {0: "person", 32: "sports ball"}
        self.assertFalse(not any(is_projectile(name) for name in coco.values()))

    def test_upscaled_box_maps_back_to_original_frame(self):
        from funball.detect import detection_from_box

        item = detection_from_box([200, 80, 240, 120], conf=0.9, scale=2.0)
        self.assertEqual((item.x, item.y), (110.0, 50.0))

    def test_implausible_boxes_are_not_balls(self):
        from funball.detect import plausible_ball

        self.assertTrue(plausible_ball([200, 180, 214, 194], (408, 358)))
        self.assertTrue(plausible_ball([200, 180, 204, 184], (408, 358)))
        self.assertFalse(plausible_ball([0, 0, 300, 300], (408, 358)))


if __name__ == "__main__":
    unittest.main()
