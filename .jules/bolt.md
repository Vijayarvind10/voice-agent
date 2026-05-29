## 2025-05-29 - Canvas Animation Garbage Collection Bottleneck
**Learning:** In `index.html`'s `requestAnimationFrame` loops (`drawStars` and `drawVis`), constructing string literals like \`rgba(...)\` and instantiating `new Uint8Array(...)` on every frame creates significant garbage collection pressure, leading to micro-stutters.
**Action:** Hoist array instantiations out of render loops and reuse them. Replace dynamic RGBA string generation in loops with constant `fillStyle` and mutating `globalAlpha`, or pre-calculate color arrays at the module scope.
