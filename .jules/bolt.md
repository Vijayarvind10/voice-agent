## 2026-03-03 - [Preventing GC pressure from requestAnimationFrame]
**Learning:** `requestAnimationFrame` loops that allocate objects (like `new Uint8Array(...)`) inside the loop run ~60 times per second and create tremendous GC pressure resulting in UI micro-stutters, particularly noticeable in continuous audio visualization.
**Action:** Allocate arrays, buffers, and objects used in `requestAnimationFrame` loops outside of the function globally/in the module scope, and pass the reference or reuse the array reference on every tick to minimize object allocations.
