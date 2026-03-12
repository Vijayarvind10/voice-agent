import unittest
import sys
from unittest.mock import MagicMock

# ─── Mock dependencies to allow importing server.py ───────────────────
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

# Now import the function to test
from server import wake_score

class TestWakeScore(unittest.TestCase):
    def test_wake_score_basic(self):
        """Test wake_score with various string lengths."""
        # Formula: min(0.98, 0.91 + (len(cmd) % 5) * 0.01)

        # Length 0 -> 0 % 5 = 0 -> 0.91 + 0 = 0.91
        self.assertAlmostEqual(wake_score(""), 0.91)

        # Length 1 -> 1 % 5 = 1 -> 0.91 + 0.01 = 0.92
        self.assertAlmostEqual(wake_score("a"), 0.92)

        # Length 2 -> 2 % 5 = 2 -> 0.91 + 0.02 = 0.93
        self.assertAlmostEqual(wake_score("ab"), 0.93)

        # Length 3 -> 3 % 5 = 3 -> 0.91 + 0.03 = 0.94
        self.assertAlmostEqual(wake_score("abc"), 0.94)

        # Length 4 -> 4 % 5 = 4 -> 0.91 + 0.04 = 0.95
        self.assertAlmostEqual(wake_score("abcd"), 0.95)

        # Length 5 -> 5 % 5 = 0 -> 0.91 + 0 = 0.91
        self.assertAlmostEqual(wake_score("abcde"), 0.91)

        # Length 6 -> 6 % 5 = 1 -> 0.91 + 0.01 = 0.92
        self.assertAlmostEqual(wake_score("abcdef"), 0.92)

    def test_wake_score_cap(self):
        """
        Verify that wake_score is capped at 0.98.
        Note: The current formula (len % 5) * 0.01 only adds up to 0.04.
        So max value is 0.91 + 0.04 = 0.95.
        The cap at 0.98 is theoretically unreachable with the current logic,
        but we test that it doesn't exceed 0.98 regardless.
        """
        for i in range(100):
            cmd = "a" * i
            score = wake_score(cmd)
            self.assertLessEqual(score, 0.98)
            self.assertGreaterEqual(score, 0.91)

if __name__ == "__main__":
    unittest.main()
