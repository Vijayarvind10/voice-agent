## 2024-05-25 - Canvas Animation GC Pressure Optimization
**Learning:** In heavily animated UI components using `requestAnimationFrame` (like `drawStars` and `drawVis`), continuously creating object instances (like `new Uint8Array`) or using dynamic string interpolation (`rgba(${r},${g},${b})`) places severe pressure on the Garbage Collector. This leads to noticeable micro-stutters.
**Action:** Always hoist object and array instantiation outside of animation loops, and use static fill styles with `globalAlpha` manipulation instead of dynamic string construction where possible.
