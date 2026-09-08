# Model experiments

## Current result

**No reliable real-ball tracker has been demonstrated yet.** The overlay works; finding and maintaining the correct instance remains unresolved.

The optional YOLO adapter accepts a local weight path understood by Ultralytics. Download external weights separately; arbitrary Hugging Face repository IDs are not a FunBall download API. Without weights, the CLI runs without detection.

## Early soccer experiment

Source: [Goal by Rafael Leao](https://commons.wikimedia.org/wiki/File:Goal_by_Rafael_Leao.webm), 408×358, 113 decoded frames. Consult the source page for media licensing. No video is bundled.

Raw predictions at confidence threshold 0.15, default inference size, without the FunBall lock or size filter:

| Weight | Frames containing ball-labelled candidates | Boxes |
| --- | ---: | ---: |
| COCO YOLOv8n | 50/113 | 69 |
| martinjolif/yolo-football-ball-detection | 113/113 | 930 |
| uisikdag/yolo-v8-football-players-detection | 105/113 | 196 |
| asahwells/yolo26n-football-detection | 113/113 | 380 |
| acatorcini/yolov9-soccer-ball | 0/113 | 0 |

These are historical diagnostic counts, **not precision, recall, or verified detections of the real ball**. Visual review rejected the rendered results as false tracking. Confidence thresholds alone did not solve this. A separately downloaded higher-resolution clip was unrelated and is excluded as a comparison.

An experimental WASB run used simplified resize/argmax rather than faithfully reproducing the upstream affine preprocessing and connected-component postprocessing. Its unstable output does not justify rejecting the model family. A faithful retest remains an open experiment.

## Next experiments

1. Annotate visible, absent, and unresolvable target states.
2. Run a SAM 3.1 reference POC; verify actual object identity and timing.
3. Add one initialized tracker while SAM keeps searching independently.
4. Compare reference and deployment runtimes on the same inputs.

Keep raw scores, calibrated or explicitly heuristic uncertainty, latency, and correctness separate. Do not distribute checkpoints without reviewing their licenses. See [research links](RESEARCH.md) and the [roadmap](ROADMAP.md).
