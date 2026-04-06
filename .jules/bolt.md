## $(date '+%Y-%m-%d') - [Optimize animation loop GC pressure]
**Learning:** Reusing a persistent `Uint8Array` for audio frequency data avoids redundant per-frame memory allocations and reduces garbage collection pressure in animation loops like `drawVis`.
**Action:** When working with continuous streams of data like audio visualization or any `requestAnimationFrame` loop, declare arrays once and reuse them instead of allocating new instances every frame.
