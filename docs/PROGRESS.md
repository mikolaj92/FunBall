# Progress — 2026-09-09

## Verified implementation

- Real-video replay now accepts `--video` and preserves decoded source pixels rather than generating black backgrounds. It requires one round per source frame, contiguous zero-based IDs and CFR-compatible PTS. Mismatches fail without a success result. Audio/VFR/live support is not claimed.
- Downloaded the original 408×358 Leão source and passed all 113 frames through Splot and the renderer with **empty observations**. This validates media plumbing only, not ball tracking. No made-up coordinates were placed on the match.
- Added single-owner bounded NPY frame storage: count and byte limits including file headers, atomic no-overwrite publication, release, lease expiry, monotonic IDs. It is not yet a full multi-consumer worker scheduler. Expired leases invalidate outstanding work; late results must be rejected by the eventual host.

## Actual SAM blocker

An authenticated checkpoint dry-run returned **Access denied; repository requires approval** for `facebook/sam3.1/sam3.1_multiplex.pt`. No SAM 3.1 weights were downloaded or executed. Access must be granted through the official model page; do not work around the gate using mirrors.

The intended CUDA machine also needs a verified SSH endpoint/host key before remote execution. No host-key bypass or changes to existing services were made. These access details belong in local configuration, not public issues.

## Remaining issue work

- #1: real annotations and temporal accuracy metrics, beyond current evaluation API.
- #2: worker lifecycle, acknowledgement routing and latest-only dispatch around bounded storage.
- #3: blocked on official checkpoint access and verified CUDA execution environment.
- #4: real-model observations and uncertainty calibration, beyond working Mojo fusion.
- #5: fast tracker after SAM-first correctness, not substituted as a workaround.
- #6: bounded catch-up and image-based cut detection, beyond timestamp/shot rejection.
- #7: runtime measurement protocol exists; no inference speed claims before execution.
- #8: actual Fala lifecycle wrapper remains, separate from working deterministic replay.
