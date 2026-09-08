"""Live overlay for one indicated ball."""

from .detect import Detection, detections_from_dict, is_projectile
from .geometry import speed_px_s, speed_to_bgr
from .lock import BallLock
from .overlay import draw
from .pipeline import Pipeline, TickResult
from .stream import overlay_stream
from .trail import Sample, Trail

__all__ = [
    "BallLock",
    "Detection",
    "Pipeline",
    "Sample",
    "TickResult",
    "Trail",
    "detections_from_dict",
    "draw",
    "is_projectile",
    "overlay_stream",
    "speed_px_s",
    "speed_to_bgr",
]
