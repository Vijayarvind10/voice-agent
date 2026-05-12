## 2024-05-24 - Hoisting arrays out of animation loops
**Learning:** Creating new instances of typed arrays (like `new Uint8Array()`) inside high-frequency animation loops (`requestAnimationFrame`, e.g., `drawVis()`) in this codebase causes unnecessary garbage collection pressure and leads to micro-stutters during visualizer execution.
**Action:** Always hoist array and object instantiations out of animation loops. Initialize them once globally or at the component level and reuse the same buffer/reference inside the loop to ensure smooth ~60fps rendering without GC spikes.
