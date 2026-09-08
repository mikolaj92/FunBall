"""Render a host-committed observation without running BallLock again."""
from .detect import Detection
from .geometry import speed_px_s
from .overlay import draw
from .trail import Trail


class CommittedRenderer:
    def __init__(self):
        self.trail = Trail()
        self._context = None

    def tick(self, frame, observation, *, run_id, frame_id, pts_ns, shot_id, target_id):
        context = (run_id, shot_id, target_id)
        if context != self._context:
            self.trail.clear()
            self._context = context
        if observation is None or not observation.eligible(
            run_id=run_id, frame_id=frame_id, pts_ns=pts_ns,
            shot_id=shot_id, target_id=target_id,
        ):
            self.trail.clear()
            return frame.copy()
        x, y = observation.center_px
        t = pts_ns / 1e9
        if x >= frame.shape[1] or y >= frame.shape[0]:
            self.trail.clear()
            return frame.copy()
        previous = list(self.trail)
        speed = 0.0
        if previous:
            prev = previous[-1]
            if t <= prev.t:
                self.trail.clear()
                return frame.copy()
            speed = speed_px_s(prev.x, prev.y, x, y, t - prev.t)
        self.trail.push(x, y, speed, t)
        return draw(frame, Detection(x, y), self.trail)
