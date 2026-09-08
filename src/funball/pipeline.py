from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detect import Detection
from .geometry import speed_px_s
from .lock import BallLock
from .overlay import draw
from .trail import Sample, Trail


@dataclass
class TickResult:
    frame: np.ndarray
    locked: Detection | None
    speed: float


class Pipeline:
    def __init__(
        self,
        *,
        lock: BallLock | None = None,
        trail: Trail | None = None,
        vmin: float = 0.0,
        vmax: float = 800.0,
    ) -> None:
        self.lock = lock or BallLock()
        self.trail = trail or Trail()
        self.vmin = vmin
        self.vmax = vmax
        self._prev: Sample | None = None

    def tick(
        self,
        frame: np.ndarray,
        detections: list[Detection],
        t: float,
        *,
        click: tuple[float, float] | None = None,
    ) -> TickResult:
        chosen = self.lock.update(detections, click=click)
        speed = 0.0
        if chosen is None:
            if not self.lock.held:
                self.trail.clear()
                self._prev = None
        else:
            if self._prev is not None:
                speed = speed_px_s(
                    self._prev.x, self._prev.y, chosen.x, chosen.y, t - self._prev.t
                )
            self._prev = self.trail.push(chosen.x, chosen.y, speed, t)
        return TickResult(
            frame=draw(
                frame, chosen, self.trail, vmin=self.vmin, vmax=self.vmax
            ),
            locked=chosen,
            speed=speed,
        )
