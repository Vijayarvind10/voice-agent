## 2024-05-13 - GC pressure in animation loops
**Learning:** Instantiating new TypedArrays (like `new Uint8Array()`) inside a `requestAnimationFrame` loop (e.g., `drawVis()`) causes significant garbage collection pressure, leading to micro-stutters and frame drops at 60fps.
**Action:** Always hoist array instantiations out of high-frequency animation loops and reuse the same buffer globally or at the component level to maintain smooth performance.
