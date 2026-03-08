## 2026-03-08 - Caching Typed Arrays in rAF Loops
**Learning:** Instantiating `Uint8Array` directly inside a `requestAnimationFrame` loop (running ~60fps) creates significant garbage collection pressure, leading to micro-stutters in UI rendering. This is especially true for audio visualizers that constantly pull frequency data.
**Action:** Always allocate arrays and objects used in high-frequency rendering loops externally and reuse them. Check size/length before reusing, and ensure they are cleaned up when the rendering loop terminates to prevent memory leaks.
