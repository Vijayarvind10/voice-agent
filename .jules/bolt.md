## 2024-05-22 - Fix Garbage Collection Pressure in requestAnimationFrame
**Learning:** Dynamic string interpolation (like `rgba(...)`) and array instantiations (like `new Uint8Array()`) inside `requestAnimationFrame` loops cause high garbage collection pressure, leading to micro-stutters.
**Action:** Use constant `fillStyle` strings, precalculate color arrays, mutate `globalAlpha`, and hoist array instantiations out of the loop and reuse the buffer globally or at the component level.
