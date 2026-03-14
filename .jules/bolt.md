## 2024-05-24 - Cache Regex Patterns in Frontend Classify
**Learning:** Inline regular expressions in high-frequency event handlers (like keystroke listeners) recompile on every call, causing unnecessary CPU cycles and garbage collection pressure.
**Action:** Extract inline regular expressions to module-level constants to cache them and improve runtime performance during typing.
