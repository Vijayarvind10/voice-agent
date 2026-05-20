## 2026-05-20 - [Optimize animation loops in index.html]
**Learning:** In canvas animation loops like `drawVis` and `drawStars`, string interpolation for colors and creating new `Uint8Array` inside the loop causes huge Garbage Collection pressure leading to micro-stutters.
**Action:** Pre-allocate arrays (`visDataArray`) and colors array (`visColors`) outside of the animation loop, and reuse them. Also, use `sCtx.globalAlpha` instead of string interpolation for fading effects.
