## 2026-05-23 - GC Pressure from Animation Loops
**Learning:** High Garbage Collection pressure occurs when dynamic string interpolation (`rgba()`) and array instantiations (like `new Uint8Array()`) are used inside `requestAnimationFrame` loops (e.g. `drawStars` and `drawVis`). This causes micro-stutters and drops frames.
**Action:** Always hoist array and string creation out of `requestAnimationFrame` loops. Use constant `fillStyle` strings and mutate `globalAlpha` for transparency, and pre-calculate color arrays instead of regenerating strings on every frame.
