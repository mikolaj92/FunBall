from __future__ import annotations

from math import hypot

from .detect import Detection


class BallLock:
    """Hold one indicated ball. Lost → wait. Never hop to another id."""

    def __init__(
        self,
        *,
        max_jump_px: float = 96.0,
        lost_frames: int = 12,
        min_conf: float = 0.25,
    ) -> None:
        self.max_jump_px = max_jump_px
        self.lost_frames = lost_frames
        self.min_conf = min_conf
        self.track_id: int | None = None
        self.x: float | None = None
        self.y: float | None = None
        self.lost_for = 0

    @property
    def held(self) -> bool:
        return self.x is not None

    def reset(self) -> None:
        self.track_id = None
        self.x = None
        self.y = None
        self.lost_for = 0

    def update(
        self,
        detections: list[Detection],
        *,
        click: tuple[float, float] | None = None,
    ) -> Detection | None:
        usable = [item for item in detections if item.conf >= self.min_conf]
        if not self.held:
            chosen = self._acquire(usable, click)
            if chosen is None:
                return None
            self._set(chosen)
            return chosen

        chosen = self._follow(usable)
        if chosen is None:
            self.lost_for += 1
            if self.lost_for >= self.lost_frames:
                self.reset()
            return None
        self._set(chosen)
        return chosen

    def _acquire(
        self,
        usable: list[Detection],
        click: tuple[float, float] | None,
    ) -> Detection | None:
        if not usable:
            return None
        if click is not None:
            return min(
                usable,
                key=lambda item: hypot(item.x - click[0], item.y - click[1]),
            )
        if len(usable) != 1:
            return None
        return usable[0]

    def _follow(self, usable: list[Detection]) -> Detection | None:
        if self.track_id is not None:
            same = [item for item in usable if item.track_id == self.track_id]
            return max(same, key=lambda item: item.conf) if same else None
        if not usable or self.x is None or self.y is None:
            return None
        nearest = min(
            usable,
            key=lambda item: hypot(item.x - self.x, item.y - self.y),  # type: ignore[operator]
        )
        if hypot(nearest.x - self.x, nearest.y - self.y) > self.max_jump_px:
            return None
        return nearest

    def _set(self, detection: Detection) -> None:
        if detection.track_id is not None:
            self.track_id = detection.track_id
        self.x = detection.x
        self.y = detection.y
        self.lost_for = 0
