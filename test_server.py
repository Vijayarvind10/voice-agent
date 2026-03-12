import unittest
import sys
from unittest.mock import MagicMock

# Mock fastapi and other dependencies that might not be present
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

from server import normalise, wake_score

class TestServer(unittest.TestCase):
    def test_normalise_whitespace(self):
        self.assertEqual(normalise("  multiple   spaces  "), "multiple spaces")
        self.assertEqual(normalise("\t\n leading and trailing \r\n"), "leading and trailing")

    def test_normalise_empty(self):
        self.assertEqual(normalise(""), "")
        self.assertEqual(normalise("   "), "")

    def test_normalise_casing(self):
        # Should preserve original casing
        self.assertEqual(normalise("Hello"), "Hello")
        self.assertEqual(normalise("HELLO"), "HELLO")
        self.assertEqual(normalise("Play Music"), "Play Music")
        self.assertEqual(normalise("a"), "a")
        self.assertEqual(normalise("A"), "A")

    def test_wake_score(self):
        self.assertAlmostEqual(wake_score(""), 0.91)
        self.assertAlmostEqual(wake_score("a"), 0.92)
        self.assertAlmostEqual(wake_score("ab"), 0.93)
        self.assertAlmostEqual(wake_score("abc"), 0.94)
        self.assertAlmostEqual(wake_score("abcd"), 0.95)
        self.assertAlmostEqual(wake_score("abcde"), 0.91)
        # Test a longer string
        self.assertAlmostEqual(wake_score("123456789"), 0.95) # 9 % 5 = 4

if __name__ == '__main__':
    unittest.main()
