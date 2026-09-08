import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(importlib.util.find_spec("splot"), "requires optional Splot Mojo binding")
class ReplayTests(unittest.TestCase):
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
