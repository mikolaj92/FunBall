"""Single-owner bounded frame files. A lease expiry invalidates worker results."""
import io
import os
from pathlib import Path
import tempfile
import time

import numpy as np


class FrameBuffer:
    def __init__(self, directory, *, max_bytes, max_frames, lease_seconds=10.0, clock=time.monotonic):
        if max_bytes <= 0 or max_frames <= 0 or not 0 < lease_seconds < float("inf"):
            raise ValueError("positive finite buffer limits required")
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        self.max_frames = max_frames
        self.lease_seconds = lease_seconds
        self.clock = clock
        self._entries = {}
        self._last_id = -1
        self.bytes_used = 0

    def publish(self, frame_id, frame):
        if type(frame_id) is not int or frame_id <= self._last_id:
            raise ValueError("frame IDs must increase; never reuse a leased path")
        if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[2] != 3 or not frame.size:
            raise ValueError("expected nonempty uint8 BGR frame")
        self.expire()
        if len(self._entries) >= self.max_frames or frame.nbytes > self.max_bytes - self.bytes_used:
            raise BufferError("frame buffer full")
        payload = io.BytesIO()
        np.save(payload, frame, allow_pickle=False)
        size = payload.tell()
        if size > self.max_bytes - self.bytes_used:
            raise BufferError("frame including NPY header exceeds budget")
        destination = self.directory / f"{frame_id:012d}.npy"
        fd, temporary = tempfile.mkstemp(dir=self.directory, prefix=".frame-")
        try:
            with os.fdopen(fd, "wb") as output:
                output.write(payload.getbuffer())
            # Atomic publication without overwriting an existing frame.
            os.link(temporary, destination)
        finally:
            os.unlink(temporary)
        self._entries[frame_id] = (destination, size, self.clock() + self.lease_seconds)
        self.bytes_used += size
        self._last_id = frame_id
        return destination

    def release(self, frame_id):
        entry = self._entries.get(frame_id)
        if entry is not None:
            path, size, _ = entry
            path.unlink(missing_ok=True)
            del self._entries[frame_id]
            self.bytes_used -= size

    def expire(self):
        now = self.clock()
        expired = [key for key, (_, _, deadline) in self._entries.items() if deadline <= now]
        for key in expired:
            self.release(key)
        return expired
