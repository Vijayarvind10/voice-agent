## 2026-04-11 - [Hidden Canvas Animations]
**Learning:** requestAnimationFrame runs continuously for elements hidden with display: none, causing CPU burn.
**Action:** Always use an IntersectionObserver or MutationObserver to explicitly cancel animation frames for hidden canvases.
