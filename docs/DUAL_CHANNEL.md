# Dual-channel design — proposal

## Goal

Begin with a SAM 3.1 proof of concept, then add a fast tracker alongside the continuously operating SAM channel. Splot selects trustworthy observations; FunBall renders them. Neither SAM accuracy nor a realtime deployment has been established.

## Small programs and boundaries

| Component | Runtime | Responsibility |
| --- | --- | --- |
| Fala | Existing Mojo engine | Session lifecycle, manifest, result, journal |
| Session host | Python initially | Resident workers, frame clock, bounded queues and feedback |
| SAM channel | Reference PyTorch initially | Global acquisition and repeated search on fresh frames |
| Tracking channel | Selected model/runtime | Follow an accepted seed through subsequent images |
| Fusion channel | Existing Splot Mojo through its thin binding | Eligibility, ranking, hysteresis, one commitment |
| Painting channel | FunBall | Render committed coordinates without another selection step |

Fala's sequential process driver is not a per-frame parallel scheduler. Host a resident session as one subprocess effector; that session owns concurrent workers. Splot does not decode video or manage queues.

Workers load once and use JSONL on stdin/stdout, with diagnostics on stderr. No model reload or new subprocess per frame. Avoid a blocking `tee` that couples slow and fast consumers.

## Files and transport

Proposed layout, not existing commands:

```text
examples/dual-channel/
  session.toml
  target.json
  tracking.profile.toml
  fala-package.toml
  run-session.py
  sam-channel.py
  track-channel.py
  fuse-channel.py
  paint-channel.py

runs/<id>/
  session.toml
  versions.json
  frames/                  # bounded .npy frame buffer
  observations.jsonl
  decisions.jsonl
  events.jsonl
  state.json
  output.mp4
  result.json
```

Frame bytes stay outside JSON. Frame references identify immutable, atomically published files. One owner cleans up after consumer acknowledgement, with time, byte and count limits and bounded leases. Rotate logs. Move pixels to mmap only if measured I/O warrants it.

The SAM queue has one active inference and at most one replaceable pending frame. It continues searching while tracking works, but does not accumulate every skipped frame.

## Observation contract

Proposed fields: protocol version, run/request/channel IDs, frame ID, PTS, shot ID, target ID, status, native-image coordinates, optional bbox/mask reference, raw model score and inference duration. Example values are not measurements:

```json
{"v":1,"type":"observation","run_id":"demo","request_id":"sam-42","channel":"sam","frame_id":123,"pts_ns":4100000000,"shot_id":2,"target_id":"target-1","status":"observed","center_px":[201.0,88.0],"raw_score":0.83}
```

Missing, occluded, uncertain and predicted states must not masquerade as current observations. Model scores are not interchangeable probabilities; `1-confidence` is not automatically Shannon entropy. Supply versioned, validated uncertainty signals to Splot and keep raw scores for inspection.

## Time alignment and feedback

- Paint a result on its own frame, not whichever frame is current when inference completes.
- Offline throughput and live latency are separate measurements. Slow offline generation can still produce smooth playback.
- Live output has a bounded delay/deadline. On missing evidence, emit the frame without a new marker.
- A historical SAM result may be accepted as a tracker seed through a separate seed decision. Replay a bounded history to catch up; reject if its deadline or shot is invalid.
- Keep seed-selection and output-selection state separate.
- A cut increments shot ID, invalidates previous spatial state and breaks the trail. A confident stale tracker does not override that invalidation.
- Hysteresis only applies among eligible candidates. If both are invalid, emit no observation.
- Do not average incompatible positions or count SAM and its seeded tracker as independent evidence.

## Inference is a replaceable worker

Separate the model workshop from deployment:

```text
Python/PyTorch reference → export or compilation → parity tests → runtime artifact
```

Evaluate optimized PyTorch and TensorRT on NVIDIA, Core ML/ONNX Runtime where suitable on Apple hardware, and MAX where a verified model/backend path exists. This is a shortlist, not a support matrix or speed claim. Exporting an image encoder does not export a complete stateful video tracker. Validate multi-frame masks/positions/visibility, memory updates and error handling after conversion or precision changes.

The worker protocol stays the same if its implementation changes from Python to a native executable. FunBall and Splot should not inherit the training environment's dependencies. First test on one machine; a remote worker later needs actual image transport, not a local filesystem path.

## Milestones

1. Evidence fixtures and SAM-first reference POC through Splot to the renderer.
2. Parallel tracker, bounded catch-up, cut/loss handling and uncertainty calibration.
3. Runtime benchmark/parity results, resident-process hardening and Fala lifecycle integration.

Measure target precision/recall, center error, false-lock duration, recovery, end-to-end p50/p95 latency, cold start, memory and artifact footprint. More boxes, longer locks or smoother invented trajectories are not success criteria.
