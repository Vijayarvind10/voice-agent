## 2024-05-27 - Eliminate animation loop GC overhead in canvas drawing
**Learning:** In this codebase, creating objects (`new Uint8Array`) and using dynamic string interpolation (`rgba(...)`) inside `requestAnimationFrame` canvas loops (`drawVis` and `drawStars`) caused massive Garbage Collection (GC) overhead and micro-stutters.
**Action:** Always preallocate buffers globally and initialize them once. For dynamic opacity, set a static color outside the loop and mutate `globalAlpha` per-iteration, or pre-calculate color string arrays, instead of generating strings inside the loop.
