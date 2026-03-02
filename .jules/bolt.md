## 2026-03-02 - [Prevent GC Pressure in `requestAnimationFrame`]
**Learning:** Arrays and objects used within a `requestAnimationFrame` loop (such as `Uint8Array` in the audio visualizer) must be allocated externally and reused. Instantiating arrays inside the loop causes constant garbage collection pressure and rendering micro-stutters.
**Action:** Always pre-allocate arrays and reuse them inside `requestAnimationFrame` render loops.
