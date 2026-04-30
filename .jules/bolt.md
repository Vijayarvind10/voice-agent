## 2024-04-30 - Prevent GC Stutters in Animation Loops
**Learning:** In frontend environments (especially 60fps `requestAnimationFrame` loops like the audio visualizer in this codebase), instantiating arrays (e.g., `new Uint8Array()`) on every frame creates significant garbage collection pressure, leading to micro-stutters and frame drops.
**Action:** Always hoist array instantiations out of high-frequency loops (e.g., into the initialization function like `startAudioVis`) and reuse the same buffer across frames. Nullify the reference when the animation stops to ensure proper memory cleanup.
