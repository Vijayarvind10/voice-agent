## 2024-05-15 - [Initial Setup]
**Learning:** Initial Setup
**Action:** Use as a starting point.

## 2024-05-15 - [Audio Visualizer GC Optimization]
**Learning:** Instantiating `Uint8Array` directly within a `requestAnimationFrame` loop (e.g., `const data = new Uint8Array(analyser.frequencyBinCount);` inside `drawVis`) creates significant garbage collection pressure due to constant allocation at 60fps.
**Action:** Always hoist fixed-size array allocations out of `requestAnimationFrame` loops and re-use a persistent typed array for per-frame updates.
