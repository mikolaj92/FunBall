# Public roadmap

Status: experimental. Existing overlay tests pass; reliable real-object tracking is unresolved. The order below is intentional: **SAM-first**, then a parallel tracker, then measured deployment optimization.

1. [Ground-truth fixtures and honest accuracy metrics](https://github.com/mikolaj92/FunBall/issues/1).
2. [Resident observation protocol and bounded frame transport](https://github.com/mikolaj92/FunBall/issues/2).
3. [SAM 3.1 reference POC](https://github.com/mikolaj92/FunBall/issues/3): verify acquisition, timing and license/access requirements.
4. [Splot profile and committed-observation renderer path](https://github.com/mikolaj92/FunBall/issues/4).
5. [Fast tracker alongside continuous SAM](https://github.com/mikolaj92/FunBall/issues/5).
6. [Time alignment, camera cuts and recovery](https://github.com/mikolaj92/FunBall/issues/6).
7. [Runtime parity, speed and footprint comparison](https://github.com/mikolaj92/FunBall/issues/7): optimized PyTorch, TensorRT, Core ML/ONNX Runtime, MAX where supported.
8. [Fala lifecycle integration and reproducible sessions](https://github.com/mikolaj92/FunBall/issues/8).

See the [issue backlog](https://github.com/mikolaj92/FunBall/issues) for acceptance criteria and dependencies. Architecture is described in [DUAL_CHANNEL.md](DUAL_CHANNEL.md).

No release date or realtime accuracy guarantee is implied. Checkpoint selection remains experimental. Model weights and media stay outside the repository.
