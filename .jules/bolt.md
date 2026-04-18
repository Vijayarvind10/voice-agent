## 2024-05-24 - Pre-allocating Arrays in requestAnimationFrame
**Learning:** Instantiating `new Uint8Array(analyser.frequencyBinCount)` inside `drawVis` (which is called via `requestAnimationFrame` ~60 times a second) causes massive garbage collection pressure. This creates micro-stutters and burns CPU cycles unnecessarily.
**Action:** Always hoist array instantiations out of render/animation loops. Allocate `visDataArray` globally or at the component level once, and reuse the same buffer on each frame.
