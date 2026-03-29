## 2026-03-29 - [Canvas GC Pressure]
**Learning:** Allocating a new `Uint8Array` every frame inside a `requestAnimationFrame` loop (`drawVis`) causes unnecessary garbage collection pressure.
**Action:** Allocate `Uint8Array` once when the stream starts and reuse it across frames to improve animation smoothness.
