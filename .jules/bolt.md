## 2026-04-04 - [Async Handlers Subprocess Blocking]
**Learning:** Using synchronous `subprocess.run` or `subprocess.getoutput` in FastAPI's async route handlers blocks the main event loop, causing latency spikes and degraded concurrency for all connected clients.
**Action:** Always use asynchronous alternatives like `await asyncio.create_subprocess_exec` (or existing project wrappers like `await run_cmd()`) for subprocess calls within async handlers to keep the event loop non-blocking.
