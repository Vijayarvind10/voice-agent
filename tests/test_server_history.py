
import unittest
import asyncio
import collections
from datetime import datetime
import sys
import os
from unittest.mock import MagicMock

# Add parent dir to path so we can import server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies that might be missing
mock_fastapi = MagicMock()
sys.modules['fastapi'] = mock_fastapi
sys.modules['fastapi.middleware.cors'] = MagicMock()
sys.modules['fastapi.staticfiles'] = MagicMock()
sys.modules['fastapi.responses'] = MagicMock()
sys.modules['uvicorn'] = MagicMock()

# Setup FastAPI mock to pass through decorated functions
def identity_decorator(*args, **kwargs):
    def wrapper(func):
        return func
    return wrapper

mock_app = MagicMock()
mock_app.get.side_effect = identity_decorator
mock_app.websocket.side_effect = identity_decorator
mock_app.mount = MagicMock()
mock_app.add_middleware = MagicMock()

mock_fastapi.FastAPI.return_value = mock_app

# Now import server
import server

class TestServerHistory(unittest.TestCase):
    def setUp(self):
        # Reset history before each test
        # We need to handle both list (current) and deque (future) to avoid crash during transition if tested
        if isinstance(server.conversation_history, list):
            server.conversation_history = []
        else:
            server.conversation_history.clear()

    def test_history_type(self):
        # This test is expected to fail before changes, pass after
        self.assertIsInstance(server.conversation_history, collections.deque, "conversation_history should be a deque")
        self.assertEqual(server.conversation_history.maxlen, server.MAX_HISTORY, "maxlen should be set")

    def test_get_history_endpoint(self):
        # Populate history
        for i in range(25):
            server.conversation_history.append({
                "turn": i,
                "command": f"cmd_{i}",
                "intent": "TEST",
                "response": "resp",
                "timestamp": datetime.now().isoformat()
            })
            # If still using list logic in server.py (pop(0)), this manual append won't trigger pop
            # So we must manually trim if it's a list to simulate server behavior,
            # OR we rely on the fact that we are testing the endpoint's slicing capability.
            if isinstance(server.conversation_history, list) and len(server.conversation_history) > server.MAX_HISTORY:
                server.conversation_history.pop(0)

        # Test /history endpoint logic
        # server.get_history() returns conversation_history[-10:]
        if asyncio.iscoroutinefunction(server.get_history):
            result = asyncio.run(server.get_history())
        else:
            result = server.get_history()

        # Should return last 10
        self.assertEqual(len(result), 10)
        # Last item should be i=24
        self.assertEqual(result[-1]["turn"], 24)
        # First item of result should be i=15
        self.assertEqual(result[0]["turn"], 15)

        # Verify it returns a list (JSON serializable)
        self.assertIsInstance(result, list)

    def test_recall_history_intent(self):
        # Populate history
        for i in range(5):
             server.conversation_history.append({
                "turn": i,
                "command": f"cmd_{i}",
                "intent": f"INTENT_{i}",
                "response": f"resp_{i}",
                "timestamp": datetime.now().isoformat()
            })

        # server.execute({"intent": "RECALL_HISTORY", ...})
        # Logic: recent = conversation_history[-3:] -> summary = " -> ".join([h["intent"]...])

        plan = {"intent": "RECALL_HISTORY", "params": {}}
        result = server.execute(plan)

        # Expected summary: INTENT_2 -> INTENT_3 -> INTENT_4
        self.assertIn("INTENT_2 → INTENT_3 → INTENT_4", result["response"])

    def test_max_history_enforcement(self):
        # This tests if the deque automatically handles maxlen
        # We can't easily test the 'websocket_endpoint' logic directly as it's async and loops,
        # but we can verify that the data structure itself enforces the limit if we are using deque.

        if isinstance(server.conversation_history, list):
            print("Skipping max_history_enforcement test for list type")
            return

        for i in range(server.MAX_HISTORY + 10):
            server.conversation_history.append(i)

        self.assertEqual(len(server.conversation_history), server.MAX_HISTORY)
        self.assertEqual(server.conversation_history[-1], server.MAX_HISTORY + 9)
        self.assertEqual(server.conversation_history[0], 10)

if __name__ == '__main__':
    unittest.main()
