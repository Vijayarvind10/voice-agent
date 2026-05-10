## 2026-05-10 - [Hoisting Typed Arrays from Animation Loops]
**Learning:** Instantiating objects like `Uint8Array` inside high-frequency animation loops (like `requestAnimationFrame`) causes unnecessary garbage collection pressure and micro-stutters.
**Action:** Always declare TypedArray buffers or other heavily reused objects globally or at the module scope, initialize them once, and reuse the memory buffer inside the animation loop.
