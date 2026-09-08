"""Replay synthetic JSONL rounds through real Splot and the committed renderer.

This validates integration, not model inference or live tracking quality.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from .committed import CommittedRenderer
from .fusion import Fusion
from .observation import Observation
from .stream import FrameWriter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
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
    writer = FrameWriter(args.out / "output.avi", fps=10)
    try:
        with args.input.open() as source, (args.out / "decisions.jsonl").open("w") as journal:
            for line in source:
                item = json.loads(line)
                observations = [Observation.from_dict(value) for value in item["observations"]]
                selected = fusion.choose(observations, **item["frame"])
                frame = np.zeros((args.height, args.width, 3), dtype=np.uint8)
                writer(renderer.tick(frame, selected, **item["frame"]))
                journal.write(json.dumps({"frame": item["frame"],
                                          "selected": selected.to_dict() if selected else None,
                                          "decision": fusion.last_envelope["decision"]},
                                         allow_nan=False, sort_keys=True) + "\n")
                count += 1
    finally:
        writer.close()
    (args.out / "result.json").write_text(json.dumps({"frames": count, "mode": "synthetic-replay"}) + "\n")


if __name__ == "__main__":
    main()
