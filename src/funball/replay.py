"""Replay synthetic JSONL rounds through real Splot and the committed renderer.

This validates integration, not model inference or live tracking quality.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from .committed import CommittedRenderer
from .fusion import Fusion
from .observation import Observation
from .stream import FrameWriter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--video", type=Path, help="CFR video matching every round by frame index")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--width", type=int, default=408)
    parser.add_argument("--height", type=int, default=358)
    args = parser.parse_args()
    if not 1 <= args.width <= 8192 or not 1 <= args.height <= 8192:
        parser.error("dimensions must be within 1..8192")
    fusion = Fusion(args.profile)
    renderer = CommittedRenderer()
    args.out.mkdir(parents=True, exist_ok=False)
    count = 0
    capture = cv2.VideoCapture(str(args.video)) if args.video else None
    if capture is not None and not capture.isOpened():
        capture.release()
        raise ValueError("cannot open source video")
    fps = capture.get(cv2.CAP_PROP_FPS) if capture is not None else 10
    if not 0 < fps < float("inf"):
        if capture is not None:
            capture.release()
        raise ValueError("source requires valid CFR frame rate")
    writer = FrameWriter(args.out / "output.avi", fps=fps)
    try:
        with args.input.open() as source, (args.out / "decisions.jsonl").open("w") as journal:
            for line in source:
                item = json.loads(line)
                observations = [Observation.from_dict(value) for value in item["observations"]]
                selected = fusion.choose(observations, **item["frame"])
                if capture is None:
                    frame = np.zeros((args.height, args.width, 3), dtype=np.uint8)
                else:
                    if item["frame"]["frame_id"] != count:
                        raise ValueError("video replay requires contiguous zero-based frame IDs")
                    if abs(item["frame"]["pts_ns"] - round(count * 1e9 / fps)) > 1_000_000:
                        raise ValueError("observation PTS does not match CFR source")
                    ok, frame = capture.read()
                    if not ok:
                        raise ValueError("observations exceed source video length")
                writer(renderer.tick(frame, selected, **item["frame"]))
                journal.write(json.dumps({"frame": item["frame"],
                                          "selected": selected.to_dict() if selected else None,
                                          "decision": fusion.last_envelope["decision"]},
                                         allow_nan=False, sort_keys=True) + "\n")
                count += 1
        if capture is not None and capture.read()[0]:
            raise ValueError("source video has frames without observation rounds")
    finally:
        writer.close()
        if capture is not None:
            capture.release()
    mode = "video-replay" if args.video else "synthetic-replay"
    (args.out / "result.json").write_text(json.dumps({"frames": count, "mode": mode}) + "\n")


if __name__ == "__main__":
    main()
