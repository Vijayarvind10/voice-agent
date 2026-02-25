
import sys
import unittest
from unittest.mock import MagicMock

# --- Mocking dependencies ---
sys.modules['fastapi'] = MagicMock()
sys.modules['fastapi.middleware'] = MagicMock()
sys.modules['fastapi.middleware.cors'] = MagicMock()
sys.modules['fastapi.staticfiles'] = MagicMock()
sys.modules['fastapi.responses'] = MagicMock()
sys.modules['uvicorn'] = MagicMock()

# Now import server which uses these mocks
import server

class TestSplitCommands(unittest.TestCase):
    """
    Test suite for split_commands function in server.py.
    """

    def test_basic_split_and_then(self):
        """Test 'and then' separator."""
        text = "open music and then play jazz"
        result = server.split_commands(text)
        expected = ["open music", "play jazz"]
        self.assertEqual(result, expected)

    def test_basic_split_and_also(self):
        """Test 'and also' separator."""
        text = "open music and also play jazz"
        result = server.split_commands(text)
        expected = ["open music", "play jazz"]
        self.assertEqual(result, expected)

    def test_basic_split_and(self):
        """Test 'and' separator."""
        text = "open music and play jazz"
        result = server.split_commands(text)
        expected = ["open music", "play jazz"]
        self.assertEqual(result, expected)

    def test_basic_split_then(self):
        """Test 'then' separator."""
        text = "open music then play jazz"
        result = server.split_commands(text)
        expected = ["open music", "play jazz"]
        self.assertEqual(result, expected)

    def test_basic_split_also(self):
        """Test 'also' separator."""
        text = "open music also play jazz"
        result = server.split_commands(text)
        expected = ["open music", "play jazz"]
        self.assertEqual(result, expected)

    def test_case_insensitivity(self):
        """Test case insensitivity of separators."""
        text = "open music AND THEN play jazz"
        result = server.split_commands(text)
        expected = ["open music", "play jazz"]
        self.assertEqual(result, expected)

        text = "open music And Also play jazz"
        result = server.split_commands(text)
        self.assertEqual(result, expected)

    def test_whitespace_handling(self):
        """Test extra whitespace handling around separators."""
        text = "open music    and then    play jazz"
        result = server.split_commands(text)
        expected = ["open music", "play jazz"]
        self.assertEqual(result, expected)

        text = "  open music   and then   play jazz  "
        result = server.split_commands(text)
        self.assertEqual(result, expected)

    def test_newline_tab_handling(self):
        """Test newline and tab handling as whitespace."""
        text = "open music\nand then\tplay jazz"
        result = server.split_commands(text)
        expected = ["open music", "play jazz"]
        self.assertEqual(result, expected)

    def test_no_separator(self):
        """Test string with no separator."""
        text = "just one command"
        result = server.split_commands(text)
        expected = ["just one command"]
        self.assertEqual(result, expected)

    def test_empty_string(self):
        """Test empty string."""
        text = ""
        result = server.split_commands(text)
        expected = []
        self.assertEqual(result, expected)

    def test_whitespace_only(self):
        """Test whitespace only string."""
        text = "   "
        result = server.split_commands(text)
        expected = []
        self.assertEqual(result, expected)

    def test_consecutive_separators(self):
        """Test consecutive separators behavior."""
        text = "command1 and then and then command2"
        result = server.split_commands(text)
        # Current implementation consumes whitespace, leaving 'and' as a command part
        # "command1[ and then ]and then command2" -> "command1", "and then command2"
        # "and then command2" -> splits at " then " -> "and", "command2"
        expected = ["command1", "and", "command2"]
        self.assertEqual(result, expected)

    def test_mixed_separators(self):
        """Test multiple different separators in one string."""
        text = "command1 and then command2 and also command3 then command4"
        result = server.split_commands(text)
        expected = ["command1", "command2", "command3", "command4"]
        self.assertEqual(result, expected)

    def test_separator_at_ends(self):
        """Test separators at the start or end of string."""
        # Current implementation does not strip leading/trailing separators if they don't match the full regex (surrounded by space)
        text = "and then command1"
        result = server.split_commands(text)
        # "and then command1" -> splits at " then " -> "and", "command1"
        expected = ["and", "command1"]
        self.assertEqual(result, expected)

        text = "command1 and then"
        result = server.split_commands(text)
        # "command1 and then" -> matches " and " -> "command1", "then"
        expected = ["command1", "then"]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
