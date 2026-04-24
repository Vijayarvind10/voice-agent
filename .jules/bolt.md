## 2024-05-24 - Animation Loop GC Anti-Pattern
**Learning:** Instantiating objects (like `new Uint8Array`) inside a `requestAnimationFrame` loop creates severe garbage collection pressure, leading to micro-stutters during visual updates. This is particularly impactful for audio visualizers running at 60fps.
**Action:** Always hoist array and object instantiations outside of animation loops, allocating memory once and reusing the buffer across frames.
