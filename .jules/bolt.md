## 2024-05-24 - `requestAnimationFrame` continues for `display: none`
**Learning:** Browsers do not automatically throttle `requestAnimationFrame` loops for elements hidden via `display: none` (like `#starCanvas` in `index.html`). This causes continuous CPU usage in the background even when the element is completely invisible.
**Action:** Always wrap continuous animation loops (like canvas renders) with an `IntersectionObserver` or `MutationObserver` to explicitly pause execution (`cancelAnimationFrame` or early return) when the target element is no longer visible in the DOM.
