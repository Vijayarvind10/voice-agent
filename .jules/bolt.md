## 2025-02-12 - Prevent Garbage Collection Pressure in requestAnimationFrame

**Learning:** When using `requestAnimationFrame` for audio visualizers (e.g. `drawVis`), instantiating new typed arrays like `new Uint8Array` inside the frame loop causes significant garbage collection pressure and micro-stutters.
**Action:** Always hoist array instantiations out of animation loops. Initialize the array once (e.g. when the mic stream connects) and reuse the same buffer on every frame via `analyser.getByteFrequencyData()`. Nullify the array when stopping the visualizer to free memory.
