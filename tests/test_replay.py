import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(importlib.util.find_spec("splot"), "requires optional Splot Mojo binding")
class ReplayTests(unittest.TestCase):
    def test_video_replay_preserves_actual_background(self):
        import cv2
        import numpy as np
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            video = directory / "source.avi"
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10, (64, 64))
            writer.write(np.full((64, 64, 3), (40, 120, 60), dtype=np.uint8))
            writer.release()
            rounds = directory / "rounds.jsonl"
            rounds.write_text(json.dumps(dict(frame=dict(run_id="v", frame_id=0, pts_ns=0,
                shot_id=0, target_id="ball"), observations=[]))+"\n")
            output = directory / "out"
            process = subprocess.run([sys.executable, "-m", "funball.replay", "--input", str(rounds),
                "--video", str(video), "--profile", str(root/"examples/dual-channel/tracking.profile.toml"),
                "--out", str(output)], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            capture = cv2.VideoCapture(str(output/"output.avi"))
            ok, frame = capture.read()
            capture.release()
            self.assertTrue(ok)
            self.assertGreater(frame[:, :, 1].mean(), 100)
            self.assertEqual(json.loads((output/"result.json").read_text())["mode"], "video-replay")
            for name, frame_id, pts_ns in [("wrong-frame", 1, 0), ("wrong-time", 0, 900000000)]:
                rounds.write_text(json.dumps(dict(frame=dict(run_id="v", frame_id=frame_id,
                    pts_ns=pts_ns, shot_id=0, target_id="ball"), observations=[]))+"\n")
                invalid = directory / name
                process = subprocess.run([sys.executable, "-m", "funball.replay", "--input", str(rounds),
                    "--video", str(video), "--profile", str(root/"examples/dual-channel/tracking.profile.toml"),
                    "--out", str(invalid)], capture_output=True, text=True)
                self.assertNotEqual(process.returncode, 0)
                self.assertFalse((invalid/"result.json").exists())

    def test_jsonl_replay_uses_real_fusion_and_emits_evidence(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "rounds.jsonl"
            frames = []
            for i in range(3):
                frame = dict(run_id="demo", frame_id=i, pts_ns=i*100000000,
                             shot_id=0, target_id="ball")
                observations = [dict(v=1, request_id=str(i), channel="sam", **frame,
                                     status="observed", center_px=[20+i, 20], uncertainty=.2)] if i < 2 else []
                frames.append(dict(frame=frame, observations=observations))
            source.write_text("".join(json.dumps(item)+"\n" for item in frames))
            def run(out):
                subprocess.run([sys.executable, "-m", "funball.replay", "--input", str(source),
                                "--profile", str(root/"examples/dual-channel/tracking.profile.toml"),
                                "--out", str(out), "--width", "64", "--height", "64"], check=True,
                               capture_output=True, text=True)
            first = Path(directory)/"first"
            second = Path(directory)/"second"
            run(first)
            run(second)
            self.assertEqual((first/"decisions.jsonl").read_bytes(), (second/"decisions.jsonl").read_bytes())
            decisions = [json.loads(line) for line in (first/"decisions.jsonl").read_text().splitlines()]
            self.assertEqual(decisions[0]["selected"]["channel"], "sam")
            self.assertIsNone(decisions[2]["selected"])
            self.assertTrue((first/"output.avi").is_file())
            self.assertEqual(json.loads((first/"result.json").read_text())["frames"], 3)
