## 2024-05-24 - Animation Loop GC Pressure
**Learning:** Instantiating `Uint8Array` inside a `requestAnimationFrame` loop creates significant garbage collection pressure, leading to micro-stutters during voice recording visualizations.
**Action:** Always hoist typed array instantiations out of animation loops and reuse the same buffer when calling Web Audio API methods like `getByteFrequencyData()`.
