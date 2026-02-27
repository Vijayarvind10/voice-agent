
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# Mock dependencies to allow server.py import
# Use MagicMock for things that are called synchronously at module level
sys.modules['fastapi'] = MagicMock()
sys.modules['fastapi.middleware.cors'] = MagicMock()
sys.modules['fastapi.responses'] = MagicMock()
sys.modules['fastapi.staticfiles'] = MagicMock()
sys.modules['uvicorn'] = MagicMock()
sys.modules['websockets'] = MagicMock()

import server

class TestServerAsync(unittest.TestCase):
    def test_run_osascript_calls_run_cmd(self):
        async def run_test():
            # We patch 'server.run_cmd' inside the coroutine where it will be awaited
            with patch('server.run_cmd', new_callable=AsyncMock) as mock_cmd:
                mock_cmd.return_value = "mock_output"

                # Call the function under test
                res = await server.run_osascript('beep')

                # Assertions
                self.assertEqual(res, "mock_output")
                mock_cmd.assert_awaited_once_with(["osascript", "-e", "beep"], timeout=10)

        # Run the async test in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_test())
        loop.close()

if __name__ == '__main__':
    unittest.main()
