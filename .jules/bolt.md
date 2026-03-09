## 2026-03-09 - Pre-compile inline regular expressions
**Learning:** Compiling regex patterns repeatedly inside high-frequency functions (like event handlers running on keystrokes or audio frames) causes unnecessary garbage collection and main thread block time in this JavaScript frontend context.
**Action:** Extract and pre-compile regular expressions as constant declarations outside the loop or function body where possible.
