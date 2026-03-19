## 2024-05-24 - [Avoid blocking subprocess calls in FastAPI]
**Learning:** Found a synchronous `subprocess.getoutput` inside an async FastAPI route handler. This blocks the main event loop, causing latency spikes for all concurrent connections (especially WebSockets).
**Action:** Always use asynchronous subprocess alternatives like `asyncio.create_subprocess_exec` (wrapped in `run_cmd` here) to prevent blocking the event loop when making shell calls within async functions.
