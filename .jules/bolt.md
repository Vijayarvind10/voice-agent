## 2026-04-21 - Prevent GC pressure in audio visualizer loop
**Learning:** Instantiating a new Uint8Array inside requestAnimationFrame creates massive GC pressure and micro-stutters.
**Action:** Hoist the array declaration out of the drawVis loop and reuse a single buffer initialized once in startAudioVis.
