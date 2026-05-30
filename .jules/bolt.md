## 2023-10-24 - Animation Loop GC Optimization
**Learning:** In canvas animation loops (`drawStars` and `drawVis`), dynamically generating color strings like `rgba(255, 255, 255, ${alpha})` and instantiating `new Uint8Array()` on every frame (e.g., inside `requestAnimationFrame`) causes significant Garbage Collection (GC) pressure and micro-stutters.
**Action:** Always hoist array instantiations (like `Uint8Array` for audio visualizers) to reuse the same buffer, and avoid dynamic color strings by using constant `fillStyle` and mutating `ctx.globalAlpha`, or by pre-calculating color arrays.
