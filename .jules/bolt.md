## 2024-05-18 - Caching Typed Arrays in requestAnimationFrame
**Learning:** Instantiating new typed arrays like `Uint8Array` inside high-frequency `requestAnimationFrame` loops (like an audio visualizer) causes unnecessary memory allocation and garbage collection pressure, leading to micro-stutters.
**Action:** Declare the array outside the loop scope once, and reuse it inside the animation frame by passing it to data-gathering methods like `analyser.getByteFrequencyData()`. Clean it up when the animation stops.
