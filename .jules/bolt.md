## 2024-05-24 - Canvas GC Pressure in requestAnimationFrame
**Learning:** Instantiating typed arrays (`new Uint8Array`) and creating dynamic strings (`rgba(...)`) inside a `requestAnimationFrame` loop causes significant garbage collection pressure, leading to micro-stutters in the visualization animations specific to this app.
**Action:** Always hoist object and array instantiations out of animation loops, reusing a single buffer where possible. Replace dynamic string interpolation for colors with constant `fillStyle` strings and modify `globalAlpha` instead.
