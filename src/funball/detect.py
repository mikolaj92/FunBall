from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Detection:
    x: float
    y: float
    conf: float = 1.0
    track_id: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Detection":
        track_id = data.get("track_id")
        return cls(
            x=float(data["x"]),
            y=float(data["y"]),
            conf=float(data.get("conf", 1.0)),
            track_id=None if track_id is None else int(track_id),
        )


def detections_from_dict(items: list[dict[str, Any]] | None) -> list[Detection]:
    return [Detection.from_dict(item) for item in items or []]


def detection_from_box(
    xyxy: list[float],
    *,
    conf: float,
    scale: float = 1.0,
    track_id: int | None = None,
) -> Detection:
    x0, y0, x1, y1 = xyxy
    return Detection(
        x=((x0 + x1) / 2.0) / scale,
        y=((y0 + y1) / 2.0) / scale,
        conf=conf,
        track_id=track_id,
    )


def plausible_ball(
    xyxy: list[float],
    frame_size: tuple[int, int],
    *,
    min_px: float = 3.0,
    max_frac: float = 0.35,
) -> bool:
    x0, y0, x1, y1 = xyxy
    width = x1 - x0
    height = y1 - y0
    if width < min_px or height < min_px:
        return False
    limit = max_frac * min(frame_size)
    if width > limit or height > limit:
        return False
    ratio = width / height
    return 0.45 <= ratio <= 2.2


def is_projectile(name: str) -> bool:
    """One object: a ball or a puck. Sport does not matter."""
    lowered = name.lower().replace("_", " ").replace("-", " ")
    return "ball" in lowered or "puck" in lowered


class YoloDetector:
    """Adapter around a local Ultralytics weight. Optional extra `yolo`."""

    def __init__(self, weights: str, *, conf: float = 0.25) -> None:
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError(
                "YOLO adapter needs ultralytics: uv sync --extra yolo"
            ) from exc
        self.model = YOLO(weights)
        self.conf = conf

    def detect(self, frame: Any) -> list[Detection]:
        results = self.model.predict(frame, conf=self.conf, verbose=False)
        if not results:
            return []
        result = results[0]
        boxes = result.boxes
        if boxes is None:
            return []
        height, width = frame.shape[:2]
        names = {int(k): str(v).lower() for k, v in (result.names or {}).items()}
        dedicated = not any(is_projectile(name) for name in names.values())
        detections: list[Detection] = []
        for box in boxes:
            cls_id = int(box.cls[0]) if box.cls is not None else -1
            name = names.get(cls_id, "")
            if name and not dedicated and not is_projectile(name):
                continue
            xyxy = box.xyxy[0].tolist()
            if not plausible_ball(xyxy, (width, height)):
                continue
            track_id = int(box.id[0]) if box.id is not None else None
            detections.append(
                detection_from_box(
                    xyxy,
                    conf=float(box.conf[0]) if box.conf is not None else 0.0,
                    track_id=track_id,
                )
            )
        return detections
