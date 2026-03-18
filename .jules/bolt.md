## 2024-05-24 - [CPU Burn from Hidden Animations]
**Learning:** Browsers do not throttle `requestAnimationFrame` for elements hidden via `display: none` or off-screen if the tab is active. The `#starCanvas` element was running its animation loop continuously even when hidden, causing unnecessary CPU usage.
**Action:** Use `IntersectionObserver` to explicitly cancel animations for hidden elements, such as `<canvas>`, to prevent CPU burn.
