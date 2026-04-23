## 2026-04-23 - Prevent GC pressure in audio visualizer
**Learning:** Instantiating new arrays (e.g., `new Uint8Array()`) inside high-frequency animation loops like `requestAnimationFrame` creates unnecessary garbage collection pressure, leading to micro-stutters and increased memory usage over time.
**Action:** Always hoist array instantiations outside the animation loop, caching the buffer globally or at the component level, and reuse it each frame.
