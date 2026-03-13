## 2024-05-24 - Unconditional requestAnimationFrame on Hidden Elements
**Learning:** The `#starCanvas` element unconditionally runs a `requestAnimationFrame(drawStars)` loop even when it's hidden (`display: none`). This wastes CPU cycles continuously calculating and rendering 120 stars at 60fps in the background, which is a significant unaddressed performance bottleneck.
**Action:** Always check element visibility (e.g., `canvas.offsetWidth > 0` or using `IntersectionObserver`) before executing expensive render loops to prevent unnecessary processing and battery drain.
