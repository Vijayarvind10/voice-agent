## 2026-03-12 - Background Animation Overhead
**Learning:** Found that `requestAnimationFrame(drawStars)` runs continuously unconditionally in `index.html` even when the canvas is visually hidden (`display: none` in CSS `#starCanvas { display: none }`). It's just burning CPU in the background for an element that might not even be seen (or might be toggled but currently it just has display:none with a `.visible` class supposedly being added but there's no CSS for `.visible` on it anyway!).
**Action:** Always verify if continuous animations (like `requestAnimationFrame`) are tied to elements that are actually visible or active in the DOM. Unnecessary loops should be paused or conditionally executed using `IntersectionObserver` or checking `display` status to save CPU cycles and battery.

## 2026-03-12 - Hidden Element Animation Loops
**Learning:** Found that `requestAnimationFrame` loops attached to hidden elements (like `#starCanvas`) will run unconditionally unless explicitly checked. This is an anti-pattern that burns CPU in the background. In this codebase, elements toggled via display properties or classes need animation suspension.
**Action:** When working with canvas animations or `requestAnimationFrame`, always add a conditional check like `getComputedStyle(element).display === 'none'` or verify visibility classes to prevent background execution when hidden.
