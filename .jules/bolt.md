## 2023-10-27 - [Hidden Animations CPU Burn]
**Learning:** `requestAnimationFrame` is not inherently throttled by the browser when the element has `display: none`. This caused the hidden `#starCanvas` element to burn CPU constantly.
**Action:** Used `IntersectionObserver` to actively pause the animation loop and cancel the animation frame when the element is hidden or not intersecting.