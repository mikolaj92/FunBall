import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import cv2
import numpy as np

from funball.detect import Detection
from funball.pipeline import Pipeline
from funball.stream import overlay_stream, read_video, write_video


def _tiny_video(path: Path, n: int = 5, size: tuple[int, int] = (160, 120), fps: float = 10.0) -> None:
    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"MJPG"), fps, size
    )
    assert writer.isOpened(), path
    for i in range(n):
        frame = np.full((size[1], size[0], 3), (i * 20, 40, 80), dtype=np.uint8)
        writer.write(frame)
    writer.release()


class StreamTests(unittest.TestCase):
    def test_overlay_stream_writes_each_frame_before_reading_the_next(self):
        writes: list[int] = []
        seen: list[int] = []

        def frames():
            for i in range(4):
                seen.append(len(writes))
                frame = np.zeros((32, 32, 3), dtype=np.uint8)
                yield frame, i * 0.1, [Detection(float(i * 4), 10.0, track_id=1)]

        def write(frame: np.ndarray) -> None:
            writes.append(int(frame[0, 0, 0]))

        stats = overlay_stream(frames(), write, Pipeline(), click=(0, 10))
        self.assertEqual(stats["frames"], 4)
        self.assertEqual(stats["locked"], 4)
        self.assertEqual(seen, [0, 1, 2, 3])

    def test_read_write_video_is_a_frame_filter(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "in.avi"
            dest = Path(tmp) / "out.avi"
            _tiny_video(src, n=5)
            stats = overlay_stream(
                read_video(src),
                write_video(dest, fps=10, size=(160, 120)),
                Pipeline(),
            )
            self.assertEqual(stats["frames"], 5)
            capture = cv2.VideoCapture(str(dest))
            count = 0
            while True:
                ok, _frame = capture.read()
                if not ok:
                    break
                count += 1
            capture.release()
            self.assertEqual(count, 5)


if __name__ == "__main__":
    unittest.main()
