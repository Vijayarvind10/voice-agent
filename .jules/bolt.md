## 2024-03-XX - Unnecessary allocations inside requestAnimationFrame loop
**Learning:** Found an anti-pattern in `drawVis` allocating `new Uint8Array(analyser.frequencyBinCount)` ~60 times a second inside `requestAnimationFrame`. This adds massive GC pressure causing micro-stutters during rendering logic.
**Action:** When working with rendering loops like `requestAnimationFrame`, always allocate arrays and objects outside the loop and reuse them. Clean up memory allocations in stop/cleanup functions.
