## 2026-04-10 - Cached Uint8Array in drawVis
**Learning:** The `drawVis` function in `index.html` instantiated a new `Uint8Array` every frame during its animation loop, causing unnecessary garbage collection pressure.
**Action:** Hoisted the allocation out of the render loop by introducing a cached array (`visDataArray`) that is initialized once and reused across frames to improve animation smoothness.
