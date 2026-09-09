# First integration slice: deterministic synthetic replay

Implemented: versioned observations, exact-frame eligibility, a real Splot Mojo profile, a committed renderer bypassing BallLock, and JSONL replay with decision evidence. This is **not SAM inference**, a live host, or a tracking-quality demonstration.

Prerequisites: a sibling Splot checkout with its supported Mojo environment and EmberJson dependency. Install the thin Splot binding following its README, or expose its Python directory as below. Use a Splot revision containing the blocked/absent-candidate hysteresis fix.

```sh
export SPLOT_HOME="$(cd ../Splot && pwd)"
export PYTHONPATH="$SPLOT_HOME/python${PYTHONPATH:+:$PYTHONPATH}"
uv run python -m unittest discover -s tests
uv run python -m funball.replay \
  --input examples/dual-channel/rounds.jsonl \
  --profile examples/dual-channel/tracking.profile.toml \
  --out runs/replay-01
```

The output directory must not exist. Output: synthetic black video with selected markers, `decisions.jsonl`, and `result.json`. This diagnostic uses 10 FPS playback; PTS values govern sample speed. It does not claim to reconstruct arbitrary video timing. Every line is one round; only a bounded trail is kept. The offline diagnostic journal grows with input length; production log rotation is not implemented yet.

The fixture contains invented observations under `sam`/`tracker` channel names: SAM selection, tracker selection, then a cut rejecting an old-shot tracker. No model is invoked. Replaying identical input/profile yields identical decisions.

## Evaluation API

`funball.evaluation.evaluate(annotations, predictions)` accepts a **single clip/target** with unique frame IDs. Visible annotations require a center and positive radius; the hit tolerance is that radius. Absent/occluded states must not show a marker; unresolvable frames are excluded. Wrong visible markers count as both false positives and false negatives. Undefined precision/recall is `None`, not a misleading perfect score.

The API currently reports counts, precision/recall and center errors. It does not yet compute false-lock durations or recovery, and no human-annotated real-video dataset is bundled.

## Replay on an actual video

Add `--video match.avi` to the replay command to render on decoded source frames. The observation file must have one round per frame, zero-based contiguous frame IDs and PTS matching the source CFR rate (1 ms tolerance). Missing detections are explicit empty observation lists, not omitted frames. Mismatched or truncated inputs fail; no success result is written. Audio is not preserved and VFR is not supported by this diagnostic.

A real video with empty observations is only a media-path check, not a tracking demo. Synthetic fixture coordinates must never be presented as model detections on a match.

## Remaining work

Bounded media transport/lifecycle, actual SAM checkpoint execution, native runtime benchmarks, a fast tracker, confidence calibration, catch-up and Fala hosting remain open issues. Default CI skips real Splot integration unless the optional binding is available; run the explicit command above to validate the Mojo path.
