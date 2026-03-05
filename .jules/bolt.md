## 2026-03-05 - Avoid Object Allocation in Animation Loops
**Learning:** In JavaScript, constantly creating objects or arrays (like `Uint8Array`) inside a `requestAnimationFrame` loop (60+ times per second) creates significant garbage collection (GC) pressure, which manifests as micro-stutters during animations (e.g., the microphone visualizer).
**Action:** Always allocate buffers, objects, and arrays outside the tight animation loop and reuse them inside the loop, reallocating only if size requirements change.
