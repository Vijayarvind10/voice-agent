## 2024-05-24 - Inline RegEx Recompilation Overhead in Hot Paths
**Learning:** In highly interactive front-end event handlers (like the `classify` function running on every keystroke during typing), compiling regular expressions inline causes unnecessary CPU cycle usage and creates garbage collection pressure, negatively impacting performance and creating jank.
**Action:** Extract static regular expression literals to module-level scope so they are compiled only once, particularly for functions bound to frequent events like `input` or `scroll`.
