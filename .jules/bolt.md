## 2026-04-08 - [Reuse Uint8Array in animation loop]
**Learning:** Instantiating new objects inside a `requestAnimationFrame` loop creates unnecessary garbage collection pressure and can lead to micro-stutters during high-frequency animations (like the microphone visualizer).
**Action:** Cache the typed array (e.g., `Uint8Array`) outside the loop during initialization and reuse it via `analyser.getByteFrequencyData(visDataArray)` across frames.
