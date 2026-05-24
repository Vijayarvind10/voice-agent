## 2024-05-24 - [Garbage Collection Pressure in Animation Loops]
**Learning:** Found that dynamic string interpolation for `fillStyle` (e.g., `rgba()`) in `requestAnimationFrame` loops (like `drawStars` and `drawVis`) creates significant Garbage Collection pressure, leading to micro-stutters.
**Action:** Use constant `fillStyle` strings or mutate `globalAlpha` instead to optimize rendering performance without creating new strings on every frame.
