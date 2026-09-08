from __future__ import annotations

from math import hypot


# Slow → fast: blue → green → yellow → red. No purple, no magenta.
_THERMO = (
    (0.00, (255, 0, 0)),
    (0.33, (0, 255, 0)),
    (0.66, (0, 255, 255)),
    (1.00, (0, 0, 255)),
)


def speed_px_s(
    x0: float, y0: float, x1: float, y1: float, dt: float
) -> float:
    if dt <= 0:
        return 0.0
    return hypot(x1 - x0, y1 - y0) / dt


def speed_to_bgr(
    speed: float, vmin: float = 0.0, vmax: float = 800.0
) -> tuple[int, int, int]:
    """Map px/s: blue (slow) → green → yellow → red (fast)."""
    span = vmax - vmin
    t = 0.0 if span <= 0 else (speed - vmin) / span
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    for (t0, c0), (t1, c1) in zip(_THERMO, _THERMO[1:]):
        if t <= t1:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return (
                int(round(c0[0] + (c1[0] - c0[0]) * u)),
                int(round(c0[1] + (c1[1] - c0[1]) * u)),
                int(round(c0[2] + (c1[2] - c0[2]) * u)),
            )
    return _THERMO[-1][1]
