## 2024-03-07 - Preventing GC micro-stutters in Web Audio visualizations
**Learning:** Typed arrays (`Uint8Array`) created inside a `requestAnimationFrame` loop (like in `drawVis`) cause massive garbage collection pressure, leading to measurable rendering micro-stutters as the browser scrambles to clean up the allocations 60 times a second.
**Action:** Always allocate typed arrays or objects used in hot render loops outside the loop, re-assigning or re-creating them only when their required dimensions change (e.g., when `frequencyBinCount` changes).
