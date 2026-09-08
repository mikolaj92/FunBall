# Runtime experiment protocol

Status: protocol defined; **no SAM or tracker runtime benchmark recorded yet**.

## Keep the question falsifiable

Compare identical model revisions, preprocessing, frame sequence, target initialization and temporal state. First verify the PyTorch reference actually follows the target. A faster wrong model is not a useful deployment result.

| Candidate | First question | Record even if blocked |
| --- | --- | --- |
| Optimized PyTorch | Does the complete stateful path run correctly? | Version, graph breaks, compilation and warmup |
| TensorRT / NVIDIA | Can required components export on the target Arm/GB10 environment? | Unsupported operators, shapes, plugins, memory-state boundary |
| Core ML / Apple | Can the complete loop execute with correct state? | CPU/GPU/ANE placement, fallback and conversion gaps |
| ONNX Runtime | Which execution provider covers the graph? | Provider partitions, fallback, transfer overhead |
| MAX | Is there a supported architecture/export path? | Required porting effort; do not claim automatic PyTorch import |

These rows are research candidates, not promises to implement every backend.

## Required record

- Model/checkpoint hash, code revision, weights license/access, runtime/build revisions.
- Hardware, OS, input resolution, dtype, batch size (start at 1), thread settings.
- Prompt/bbox convention, crop/resize transform, color order and normalization.
- Temporal window, lookahead, recurrent-state layout/reset behavior.
- Cold startup, warmup policy, synchronized accelerator timing method.
- End-to-end and inference-only latency samples, p50/p95, throughput, peak RAM/device memory.
- Installation size and artifact size separately; unavoidable platform runtime dependencies listed.
- Position/mask/visibility divergence from reference per frame, including cuts and occlusions.
- Seed and input provenance. No private paths, credentials, gated weights or private footage in public artifacts.

GPU work is asynchronous: CPU enqueue time is not GPU completion latency. Measure with appropriate device events or synchronization. Test a sustained sequence; a single image cannot validate memory updates or drift. Quantization requires fresh accuracy/parity checks.

## Publication gate

Use the same worker protocol for reference and candidate. Mark each result `measured`, `unsupported`, or `not tested`. Publish failed conversions. Do not infer target-device speed from another GPU's FPS or from changing Python to a native host language.

See [issue #7](https://github.com/mikolaj92/FunBall/issues/7). Acquisition must be established in [#3](https://github.com/mikolaj92/FunBall/issues/3) before an honest SAM runtime comparison exists.
