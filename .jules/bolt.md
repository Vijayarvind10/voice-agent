## 2025-02-18 - Avoiding synchronous subprocess calls in async handlers
**Learning:** In async FastAPI route handlers, synchronous subprocess calls (like `subprocess.getoutput` or `subprocess.run`) block the main event loop and cause latency spikes, which can stall concurrent tasks by up to 1s.
**Action:** Always use asynchronous alternatives like `await run_cmd` (which wraps `asyncio.create_subprocess_exec`) or `run_in_executor` for any blocking I/O in async FastAPI handlers.
