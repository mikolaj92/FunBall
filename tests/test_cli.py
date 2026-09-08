import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_overlay_writes_png_from_json_rally(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "overlay_out.png"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "funball",
                    "overlay",
                    "--input",
                    "examples/frames/rally.json",
                    "--out",
                    str(dest),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(dest.exists())
            self.assertIn("locked=", result.stdout)

    def test_overlay_accepts_any_video_without_weights(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "in.avi"
            dest = Path(tmp) / "out.avi"
            writer = cv2.VideoWriter(
                str(src), cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 120)
            )
            for i in range(4):
                writer.write(
                    np.full((120, 160, 3), (i * 10, 20, 30), dtype=np.uint8)
                )
            writer.release()
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "funball",
                    "overlay",
                    "--video",
                    str(src),
                    "--out",
                    str(dest),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("frames=4", result.stdout)
            self.assertTrue(dest.exists())

    def test_rally_fixture_has_two_balls_and_a_click(self):
        payload = json.loads(
            (ROOT / "examples/frames/rally.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["click"], [120, 400])
        self.assertEqual(len(payload["frames"][0]["detections"]), 2)


if __name__ == "__main__":
    unittest.main()
