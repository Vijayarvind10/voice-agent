## 2024-03-24 - [Fixing CPU burn in hidden elements]
**Learning:** Browsers do not throttle `requestAnimationFrame` for elements hidden via `display: none` or off-screen if the tab is active. An `IntersectionObserver` or `MutationObserver` should be used to explicitly cancel animations for hidden elements, such as `<canvas>`, to prevent CPU burn.
**Action:** When creating continuous animations, explicitly pause them using `cancelAnimationFrame` or checking `isVisible` if the element isn't currently displayed.
