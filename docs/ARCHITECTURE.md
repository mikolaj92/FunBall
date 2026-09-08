# Current architecture

This document describes shipped code; [DUAL_CHANNEL.md](DUAL_CHANNEL.md) describes the proposed system.

```text
frame → optional YOLO/fixture detections → BallLock → bounded trail → overlay
```

- `detect.py`: coordinates/confidence/optional ID, experimental YOLO prediction and size filtering.
- `lock.py`: confidence filtering and spatial association. With a click, acquire the nearest usable candidate; without a click, acquire only a sole usable candidate. Follow a supplied ID or nearest candidate within the jump limit.
- `geometry.py`: image-plane distance/speed and blue → green → yellow → red LUT.
- `trail.py`: bounded sample history.
- `overlay.py`: drawing on BGR frames.
- `pipeline.py`: existing combined lock/trail/render tick.
- `stream.py`: incremental decode/render/write; CFR-derived timestamps, no audio preservation.
- `cli.py`: video and synthetic JSON entry points.

A miss returns no new detection. The lock can remain held briefly, and the existing trail can remain visible until reset. No new trail sample is added on a miss. After loss, acquisition may happen again; instance preservation is not guaranteed. YOLO `predict()` does not provide appearance-based tracking.

```json
{"x":640.0,"y":360.0,"conf":0.87,"track_id":3}
```

This minimal detection contract is suitable for current fixtures. The planned observation protocol adds time, identity, provenance, and explicit missing states. An externally committed observation must eventually bypass BallLock to avoid selecting the target twice. No Splot/Fala/SAM integration is currently shipped.
