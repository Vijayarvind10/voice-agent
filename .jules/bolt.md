## 2024-05-18 - [Extract Regex Initialization from High-Frequency Functions]
**Learning:** Frequent initialization of Regular Expressions directly within high-frequency event handlers, like the `classify` function triggered on keystrokes and speech intervals, leads to unnecessary garbage collection pressure and could contribute to micro-stutters.
**Action:** Always declare fixed/constant regular expressions in the outer scope, rather than instantiating them within the high-frequency functions themselves.
