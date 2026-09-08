# FunBall

**One indicated object. One marker. A speed-colored trail.**

FunBall is an experimental streaming video overlay for a ball, puck, or eventually another indicated object. It is not a camera director. The trail runs **blue → green → yellow → red** using image-plane speed (pixels/second), not calibrated physical speed.

## Status: working overlay, tracking still research

The renderer, bounded trail, synthetic fixtures, and optional YOLO adapter work. **Reliable real-ball tracking has not yet been demonstrated.** Earlier detector experiments produced many false candidates; more boxes and longer locks were not improvements in accuracy.

The current lock is a spatial association heuristic, not an appearance-based tracker. A [synthetic replay through real Splot and the committed renderer](examples/dual-channel/README.md) now works. SAM inference, the live dual-channel host, and compiled inference workers remain **planned, not shipped**.

## Quick start

Python 3.11+ and [uv](https://docs.astral.sh/uv/):

```sh
uv sync --locked
uv run python -m unittest discover -s tests
uv run funball overlay --input examples/frames/rally.json --out overlay_out.png
```

Without weights, the video path decodes and re-encodes frames without an object overlay (not a byte-for-byte file copy):

```sh
uv run funball overlay --video match.mp4 --out match.funball.mp4
```

Optional experimental YOLO adapter:

```sh
uv sync --extra yolo
uv run funball overlay --video match.mp4 --weights yolov8n.pt \
  --click 640,360 --out match.funball.mp4
```

`--click` supplies a coordinate; there is no interactive click UI. Without it, initial acquisition requires exactly one usable candidate. Neither rule proves that a candidate is the intended object. Video is processed incrementally. The current writer does not preserve audio.

## Direction

```text
                       slow, continuously searching SAM channel
                      /
video → bounded host                                             → Splot → FunBall
                      \                                        /
                       fast, stateful tracking channel
```

- **SAM-first POC:** establish whether SAM 3.1 finds the intended object, with honest timing and accuracy measurements.
- **Parallel tracker:** initialize from accepted SAM observations; keep SAM running on fresh sampled frames.
- **Splot:** fuse eligible observations and stabilize selection. No stale positions presented as current observations.
- **Fala:** host the session lifecycle. Small resident programs exchange JSONL and bounded frame references.
- **Runtime independence:** PyTorch is a reference implementation, not a mandatory production dependency. Evaluate TensorRT, Core ML, ONNX Runtime, and MAX where a verified deployment path exists.

[Splot](https://github.com/mikolaj92/Splot) and [Fala](https://github.com/mikolaj92/Fala) remain separate products. FunBall does not implement a second fusion engine.

## Public development

- [Issues and experiments](https://github.com/mikolaj92/FunBall/issues)
- [Roadmap](docs/ROADMAP.md)
- [Current architecture](docs/ARCHITECTURE.md)
- [Dual-channel design](docs/DUAL_CHANNEL.md)
- [Model experiments and limitations](docs/MODELS.md)
- [Research starting points](docs/RESEARCH.md)
- [Contributing](CONTRIBUTING.md)

Development happens on `main`. Publish reproducible failures as well as successes. Do not equate model confidence, throughput, or lock occupancy with tracking correctness.

## License

Original FunBall code is [MIT](LICENSE). External models, datasets, optional dependencies, and runtime SDKs retain their own licenses. No model weights or video datasets are distributed here. Installing the optional Ultralytics adapter requires reviewing its licensing separately.
