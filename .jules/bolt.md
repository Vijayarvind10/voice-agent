## 2026-05-15 - [Optimize Animation Loops to Reduce GC Pressure]
**Learning:** In fast-running animation loops (like `requestAnimationFrame`), inline dynamic string interpolations (e.g. `rgba()`) and per-frame array allocations (e.g. `new Uint8Array()`) cause significant Garbage Collection pressure and can lead to micro-stutters.
**Action:** Always hoist array instantiations out of loops, re-using global buffers. Use constant strings for properties like `fillStyle` and achieve transparency via `globalAlpha` modifications where possible.
