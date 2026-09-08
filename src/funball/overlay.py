from __future__ import annotations

import cv2
import numpy as np

from .detect import Detection
from .geometry import speed_to_bgr
from .trail import Trail


def draw(
    frame: np.ndarray,
    locked: Detection | None,
    trail: Trail,
    *,
    radius: int = 8,
    vmin: float = 0.0,
    vmax: float = 800.0,
) -> np.ndarray:
    out = frame.copy()
    points = list(trail)
    for prev, curr in zip(points, points[1:]):
        color = speed_to_bgr(curr.speed, vmin, vmax)
        cv2.line(
            out,
            (int(prev.x), int(prev.y)),
            (int(curr.x), int(curr.y)),
            color,
            3,
            cv2.LINE_AA,
        )
    if locked is not None:
        speed = points[-1].speed if points else 0.0
        color = speed_to_bgr(speed, vmin, vmax)
        center = (int(locked.x), int(locked.y))
        cv2.circle(out, center, radius, color, 2, cv2.LINE_AA)
        cv2.circle(out, center, 2, color, -1, cv2.LINE_AA)
    return out
