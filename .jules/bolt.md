## 2024-03-26 - Hidden Canvas Animation Loop Anti-Pattern
**Learning:** Browsers do not throttle `requestAnimationFrame` for elements hidden via `display: none` or off-screen if the tab is active. The codebase had an unthrottled `#starCanvas` animation loop that was permanently hidden, wasting CPU.
**Action:** Use an `IntersectionObserver` to wrap `requestAnimationFrame` loops on canvas elements. Only call `requestAnimationFrame` when the element is actually intersecting/visible to the user, and ensure you `cancelAnimationFrame` when it leaves the viewport or becomes hidden via CSS.
