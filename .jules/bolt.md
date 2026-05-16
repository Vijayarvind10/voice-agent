## 2024-05-16 - Prevent GC pressure in Canvas Animation Loops
**Learning:** In `index.html` canvas animation loops (e.g., `drawStars`), using dynamic string interpolation for colors (like `rgba()`) or instantiating new `Uint8Array` arrays inside the loop causes high Garbage Collection pressure.
**Action:** Use constant `fillStyle` strings and mutate `globalAlpha` instead to optimize rendering performance, and hoist array instantiations out of the loop and reuse the same buffer.
