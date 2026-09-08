from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Sample:
    x: float
    y: float
    speed: float
    t: float


class Trail:
    def __init__(self, maxlen: int = 48) -> None:
        self._points: deque[Sample] = deque(maxlen=maxlen)

    def push(self, x: float, y: float, speed: float, t: float) -> Sample:
        sample = Sample(x=x, y=y, speed=speed, t=t)
        self._points.append(sample)
        return sample

    def clear(self) -> None:
        self._points.clear()

    def __len__(self) -> int:
        return len(self._points)

    def __iter__(self) -> Iterator[Sample]:
        return iter(self._points)
