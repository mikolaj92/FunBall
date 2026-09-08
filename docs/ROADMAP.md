# Public roadmap

Status: experimental. Existing overlay tests pass; reliable real-object tracking is unresolved. The order below is intentional: **SAM-first**, then a parallel tracker, then measured deployment optimization.

1. Ground-truth fixtures and honest accuracy metrics.
2. Resident observation protocol and bounded frame transport.
3. SAM 3.1 reference POC: verify acquisition, timing and license/access requirements.
4. Splot profile and committed-observation renderer path.
5. Fast tracker initialized from accepted SAM observations; keep SAM running.
6. Time alignment, camera cuts, uncertainty calibration and recovery.
7. Runtime parity and speed/footprint comparison: optimized PyTorch, TensorRT, Core ML/ONNX Runtime, MAX where supported.
8. Fala lifecycle integration and reproducible resident-process sessions.

See the [issue backlog](https://github.com/mikolaj92/FunBall/issues) for acceptance criteria and dependencies. Architecture is described in [DUAL_CHANNEL.md](DUAL_CHANNEL.md).

No release date or realtime accuracy guarantee is implied. Checkpoint selection remains experimental. Model weights and media stay outside the repository.
