import unittest
import sys
from unittest.mock import MagicMock

# Mock fastapi modules to allow importing server.py
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

# Import the module to test
import server

class TestEscapeOsascript(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(server.escape_osascript(""), "")

    def test_simple_string(self):
        self.assertEqual(server.escape_osascript("hello world"), "hello world")

    def test_backslash(self):
        # Input: C:\Windows\System32
        # Expected: C:\\Windows\\System32
        self.assertEqual(server.escape_osascript("C:\\Windows\\System32"), "C:\\\\Windows\\\\System32")

    def test_double_quote(self):
        # Input: Say "Hello"
        # Expected: Say \"Hello\"
        self.assertEqual(server.escape_osascript('Say "Hello"'), 'Say \\"Hello\\"')

    def test_single_quote(self):
        # Input: It's me
        # Expected: It\'s me
        self.assertEqual(server.escape_osascript("It's me"), "It\\'s me")

    def test_mixed(self):
        # Input: I said "Don't do that\"
        # Expected: I said \"Don\'t do that\\\"
        self.assertEqual(server.escape_osascript("I said \"Don't do that\\\""), "I said \\\"Don\\'t do that\\\\\\\"")

if __name__ == '__main__':
    unittest.main()
