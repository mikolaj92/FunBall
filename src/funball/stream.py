from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .detect import Detection
from .pipeline import Pipeline

FrameTick = tuple[np.ndarray, float, list[Detection] | None]


def overlay_stream(
    frames: Iterator[FrameTick],
    write: Callable[[np.ndarray], Any],
    pipeline: Pipeline,
    *,
    click: tuple[float, float] | None = None,
    detect: Callable[[np.ndarray], list[Detection]] | None = None,
) -> dict[str, int]:
    """Paint one overlay frame at a time. Never buffers the whole video."""
    n = 0
    locked = 0
    try:
        for frame, t, detections in frames:
            if detections is None:
                detections = [] if detect is None else detect(frame)
            result = pipeline.tick(
                frame,
                detections,
                t,
                click=click if not pipeline.lock.held else None,
            )
            write(result.frame)
            n += 1
            if result.locked is not None:
                locked += 1
    finally:
        closer = getattr(write, "close", None)
        if closer is not None:
            closer()
    return {"frames": n, "locked": locked}


class VideoSource:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.capture = cv2.VideoCapture(str(self.path))
        if not self.capture.isOpened():
            raise ValueError(f"cannot open video {self.path}")
        self.fps = self.capture.get(cv2.CAP_PROP_FPS) or 30.0
        self.size = (
            int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

    def __iter__(self) -> Iterator[FrameTick]:
        dt = 1.0 / self.fps
        t = 0.0
        try:
            while True:
                ok, frame = self.capture.read()
                if not ok:
                    break
                yield frame, t, None
                t += dt
        finally:
            self.capture.release()


def read_video(path: str | Path) -> VideoSource:
    return VideoSource(path)


class FrameWriter:
    def __init__(
        self,
        path: str | Path,
        fps: float = 30.0,
        size: tuple[int, int] | None = None,
    ) -> None:
        self.path = Path(path)
        self.fps = fps
        self.size = size
        self.writer: cv2.VideoWriter | None = None
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if size is not None:
            self._open(size)

    def _open(self, size: tuple[int, int]) -> None:
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        if self.path.suffix.lower() in {".mp4", ".m4v", ".mov"}:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(str(self.path), fourcc, self.fps, size)
        if not self.writer.isOpened():
            raise ValueError(f"cannot write {self.path}")
        self.size = size

    def __call__(self, frame: np.ndarray) -> None:
        height, width = frame.shape[:2]
        if self.writer is None:
            self._open((width, height))
        assert self.writer is not None
        self.writer.write(frame)

    def close(self) -> None:
        if self.writer is not None:
            self.writer.release()
            self.writer = None


def write_video(
    path: str | Path, fps: float = 30.0, size: tuple[int, int] | None = None
) -> FrameWriter:
    return FrameWriter(path, fps=fps, size=size)
