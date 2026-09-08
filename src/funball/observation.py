"""Versioned single-object observations, independent of inference runtime."""
from dataclasses import asdict, dataclass
from math import isfinite


@dataclass(frozen=True)
class Observation:
    v: int
    run_id: str
    request_id: str
    channel: str
    frame_id: int
    pts_ns: int
    shot_id: int
    target_id: str
    status: str
    center_px: tuple[float, float] | None
    uncertainty: float

    def __post_init__(self):
        if type(self.v) is not int or self.v != 1:
            raise ValueError("unsupported observation version")
        for value in (self.frame_id, self.pts_ns, self.shot_id):
            if type(value) is not int or value < 0:
                raise ValueError("frame, PTS and shot must be nonnegative integers")
        for value in (self.run_id, self.request_id, self.channel, self.target_id):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("identifiers must be nonempty strings")
        if self.status not in {"observed", "lost", "occluded", "uncertain"}:
            raise ValueError("unsupported observation status")
        if (type(self.uncertainty) not in (int, float)
                or not isfinite(self.uncertainty) or not 0 <= self.uncertainty <= 1):
            raise ValueError("uncertainty must be finite and in [0,1]")
        if self.status == "observed":
            point = self.center_px
            if (not isinstance(point, tuple) or len(point) != 2
                    or any(type(v) not in (int, float) or not isfinite(v) or v < 0 for v in point)):
                raise ValueError("observed requires two finite nonnegative coordinates")
        elif self.center_px is not None:
            raise ValueError("non-observations cannot carry a drawable position")

    @classmethod
    def from_dict(cls, message):
        fields = dict(message)
        if fields.get("center_px") is not None:
            fields["center_px"] = tuple(fields["center_px"])
        return cls(**fields)

    def to_dict(self):
        result = asdict(self)
        if self.center_px is not None:
            result["center_px"] = list(self.center_px)
        return result

    def eligible(self, *, run_id, frame_id, pts_ns, shot_id, target_id):
        return self.status == "observed" and (
            self.run_id, self.frame_id, self.pts_ns, self.shot_id, self.target_id
        ) == (run_id, frame_id, pts_ns, shot_id, target_id)
