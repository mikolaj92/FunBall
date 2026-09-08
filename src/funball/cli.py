from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy as np

from .detect import Detection, YoloDetector, detections_from_dict
from .pipeline import Pipeline
from .stream import FrameTick, overlay_stream, read_video, write_video


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="funball")
    sub = parser.add_subparsers(dest="command", required=True)
    overlay = sub.add_parser("overlay", help="draw lock + speed trail on any video")
    overlay.add_argument("--input", help="JSON rally of detections")
    overlay.add_argument("--video", help="any video file")
    overlay.add_argument(
        "--weights",
        help="Ultralytics weight or HF id; yolov8n.pt is the generic any-ball default",
    )
    overlay.add_argument("--click", help="lock click as x,y")
    overlay.add_argument("--out", required=True)
    overlay.add_argument("--vmin", type=float, default=0.0)
    overlay.add_argument("--vmax", type=float, default=800.0)
    args = parser.parse_args(argv)
    try:
        if args.command == "overlay":
            return _overlay(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def _overlay(args: argparse.Namespace) -> int:
    if bool(args.input) == bool(args.video):
        raise ValueError("pass exactly one of --input or --video")
    click = _parse_click(args.click)
    pipeline = Pipeline(vmin=args.vmin, vmax=args.vmax)
    dest = Path(args.out)
    if args.input:
        return _overlay_json(Path(args.input), dest, pipeline, click)
    return _overlay_video(Path(args.video), dest, pipeline, click, args.weights)


def _overlay_json(
    source: Path,
    dest: Path,
    pipeline: Pipeline,
    click: tuple[float, float] | None,
) -> int:
    payload = json.loads(source.read_text(encoding="utf-8"))
    fps = float(payload.get("fps", 30))
    if click is None and payload.get("click"):
        click = (float(payload["click"][0]), float(payload["click"][1]))
    stats = overlay_stream(
        _json_frames(payload),
        _sink(dest, fps),
        pipeline,
        click=click,
    )
    if stats["frames"] == 0:
        raise ValueError("rally has no frames")
    print(f"wrote {dest} frames={stats['frames']} locked={stats['locked']}")
    return 0


def _overlay_video(
    source: Path,
    dest: Path,
    pipeline: Pipeline,
    click: tuple[float, float] | None,
    weights: str | None,
) -> int:
    video = read_video(source)
    detect = YoloDetector(weights).detect if weights else None
    stats = overlay_stream(
        video,
        _sink(dest, video.fps, video.size),
        pipeline,
        click=click,
        detect=detect,
    )
    if stats["frames"] == 0:
        raise ValueError("video has no frames")
    print(f"wrote {dest} frames={stats['frames']} locked={stats['locked']}")
    return 0


def _json_frames(payload: dict) -> Iterator[FrameTick]:
    width = int(payload.get("width", 960))
    height = int(payload.get("height", 540))
    for item in payload.get("frames") or []:
        frame = np.full((height, width, 3), (32, 28, 24), dtype=np.uint8)
        detections: list[Detection] = detections_from_dict(item.get("detections"))
        yield frame, float(item.get("t", 0.0)), detections


def _sink(
    dest: Path,
    fps: float,
    size: tuple[int, int] | None = None,
):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        return LastFrame(dest)
    return write_video(dest, fps=fps, size=size)


class LastFrame:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.frame: np.ndarray | None = None

    def __call__(self, frame: np.ndarray) -> None:
        self.frame = frame

    def close(self) -> None:
        if self.frame is None:
            raise ValueError(f"no frame to write {self.path}")
        cv2.imwrite(str(self.path), self.frame)


def _parse_click(value: str | None) -> tuple[float, float] | None:
    if not value:
        return None
    x_text, y_text = value.split(",", 1)
    return float(x_text), float(y_text)


if __name__ == "__main__":
    raise SystemExit(main())
