## 2023-10-27 - Hidden Canvas Animation Loops
**Learning:** `requestAnimationFrame` loops continue to fire and consume CPU at 60fps even when the target element (like a `<canvas>`) is hidden via `display: none` or is off-screen. Browsers do not throttle these if the tab itself is active.
**Action:** Always use an `IntersectionObserver` or `MutationObserver` to explicitly pause animations using `cancelAnimationFrame` when the element is not visible or intersecting to prevent CPU burn.
