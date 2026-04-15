## 2026-04-15 - Canvas CPU Burn
**Learning:** requestAnimationFrame is not automatically throttled by browsers for elements hidden via display: none if the tab is active, which causes unnecessary CPU burn.
**Action:** Use IntersectionObserver to explicitly pause animations for hidden canvas elements.
