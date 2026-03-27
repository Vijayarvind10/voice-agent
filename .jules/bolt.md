## 2026-03-27 - [Avoid Object Allocation in Animation Loops]
**Learning:** Instantiating `new Uint8Array` inside a 60fps `requestAnimationFrame` loop (like `drawVis`) causes significant garbage collection pressure, leading to micro-stutters and increased CPU usage.
**Action:** Declare and reuse a persistent `Uint8Array` outside the `requestAnimationFrame` loop.