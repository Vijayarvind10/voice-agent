## 2024-05-24 - Web Audio API Buffer Allocation in Animation Loops
**Learning:** Instantiating new objects (like `new Uint8Array`) inside a `requestAnimationFrame` callback at 60fps causes rapid memory allocation and frequent garbage collection, leading to micro-stutters.
**Action:** Declare and initialize the typed array or buffer once when setting up the audio context (`startAudioVis`), and reuse the persistent buffer inside the animation loop (`drawVis`).
