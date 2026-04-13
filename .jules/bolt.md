## 2024-05-18 - requestAnimationFrame for Hidden Elements
**Learning:** Browsers do not throttle `requestAnimationFrame` for elements hidden via `display: none` or off-screen if the tab is active. An `IntersectionObserver` or `MutationObserver` should be used to explicitly cancel animations for hidden elements, such as `<canvas>`, to prevent CPU burn.

## 2024-05-18 - Garbage Collection in Animation Loops
**Learning:** Instantiating objects like `Uint8Array` inside a `requestAnimationFrame` loop creates massive garbage collection pressure, causing micro-stutters. Arrays should be cached and reused across frames.
