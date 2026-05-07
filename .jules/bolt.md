## 2026-05-07 - Animation Loop GC Pressure
**Learning:** In Web Audio API visualizers, creating new `Uint8Array` buffers on every `requestAnimationFrame` creates unnecessary garbage collection pressure and micro-stutters.
**Action:** Always allocate the buffer once (e.g. `new Uint8Array(analyser.frequencyBinCount)`) when initializing the `AnalyserNode`, and reuse it using `analyser.getByteFrequencyData(buffer)`. Be sure to nullify the reference during teardown.
