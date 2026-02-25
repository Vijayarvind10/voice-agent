import sys
from unittest.mock import MagicMock
import asyncio
import time
import os

# Mock dependencies
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

# Now import server
import server

async def heartbeat():
    """Prints a dot every 0.1s to show event loop is running."""
    print("Heartbeat started")
    for _ in range(15):
        print(".", end="", flush=True)
        await asyncio.sleep(0.1)
    print("\nHeartbeat stopped")

async def test_run_osascript():
    print(f"\nTesting run_osascript (blocking check)...")
    start_time = time.time()

    # Start heartbeat task
    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        if asyncio.iscoroutinefunction(server.run_osascript):
            print("Function is async, awaiting...")
            res = await server.run_osascript('tell app "Finder" to beep')
        else:
            print("Function is sync, calling directly...")
            res = server.run_osascript('tell app "Finder" to beep')
    except Exception as e:
        print(f"Error calling function: {e}")
        res = "error"

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nFunction returned: {res}")
    print(f"Duration: {duration:.4f}s")

    await heartbeat_task

async def test_run_cmd():
    print(f"\nTesting run_cmd (blocking check)...")
    start_time = time.time()

    # Start heartbeat task
    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        # We use 'sleep 1' via bash to simulate a slow command
        # Since run_cmd takes a list
        if asyncio.iscoroutinefunction(server.run_cmd):
            print("Function is async, awaiting...")
            res = await server.run_cmd(["sleep", "1"])
        else:
            print("Function is sync, calling directly...")
            res = server.run_cmd(["sleep", "1"])
    except Exception as e:
        print(f"Error calling function: {e}")
        res = "error"

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nFunction returned: {res}")
    print(f"Duration: {duration:.4f}s")

    await heartbeat_task

async def main():
    # Setup PATH to include current directory so 'osascript' command works (points to our mock)
    os.environ["PATH"] = os.getcwd() + os.pathsep + os.environ["PATH"]

    # Ensure our mock exists
    if not os.path.exists("osascript"):
        if os.path.exists("osascript_mock"):
             os.symlink("osascript_mock", "osascript")
        else:
             print("Error: osascript_mock not found")
             return

    await test_run_osascript()
    await test_run_cmd()

    # Clean up
    if os.path.islink("osascript"):
        os.remove("osascript")

if __name__ == "__main__":
    asyncio.run(main())
