## 2025-02-12 - Prevent background animation CPU burn
**Learning:** Browsers do not throttle `requestAnimationFrame` for elements hidden via `display: none` or off-screen if the tab is active. The `#starCanvas` element continuously runs its `drawStars` loop even when hidden, causing unnecessary CPU consumption.
**Action:** Use an `IntersectionObserver` or explicit start/stop methods with `cancelAnimationFrame` to control animation loops for hidden or off-screen elements.
