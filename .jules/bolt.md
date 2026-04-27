## 2024-04-27 - Prevent GC Pressure in requestAnimationFrame

**Learning:** Allocating objects or typed arrays (like `new Uint8Array(...)`) inside a high-frequency `requestAnimationFrame` loop (up to 60fps) creates continuous memory allocation and garbage collection (GC) pressure. In the case of `drawVis` for the audio visualizer, this pattern could lead to micro-stutters during audio visualization playback.

**Action:** Always hoist array instantiations and object creations outside of animation loops. Initialize the buffers/arrays once and reuse them by mutating their contents (e.g., using `analyser.getByteFrequencyData(visDataArray)`). Clean up memory references by setting them to `null` when the loop is stopped.
