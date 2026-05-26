## 2026-05-26 - Prevent GC pressure in Canvas Animation Loops
**Learning:** Re-allocating Typed Arrays (`new Uint8Array`) and using string interpolation (`rgba(${r}, ${g}, ${b}, ${a})`) inside `requestAnimationFrame` loops like `drawVis` and `drawStars` creates high Garbage Collection pressure, leading to micro-stutters.
**Action:** Always precalculate and cache color strings or use `globalAlpha` for fading elements. Hoist typed array creation outside the animation loop entirely.
