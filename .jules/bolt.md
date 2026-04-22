## 2024-05-24 - Canvas CPU Burn
**Learning:** Hidden canvases (like `#starCanvas` which has `display: none`) still trigger `requestAnimationFrame` loops at 60fps in the background if the tab is active, burning CPU unnecessarily. Browsers do not throttle `display: none` elements.
**Action:** Use an `IntersectionObserver` or `MutationObserver` on canvas elements to explicitly call `cancelAnimationFrame` when they are not visible, and resume the loop only when they become visible.
