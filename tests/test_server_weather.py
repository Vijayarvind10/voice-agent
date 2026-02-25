import unittest
import sys
from unittest.mock import MagicMock, patch

# Mock dependencies before importing server
# This is crucial because fastapi, uvicorn, etc. are not installed in the environment
# but are imported by server.py at module level.
mock_fastapi = MagicMock()
sys.modules["fastapi"] = mock_fastapi
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()
sys.modules["websockets"] = MagicMock()

# Now import the server module
import server

class TestWeather(unittest.TestCase):
    @patch("server.subprocess.run")
    def test_weather_success(self, mock_run):
        # Arrange
        mock_result = MagicMock()
        mock_result.stdout = "Sunny, 25C"
        mock_run.return_value = mock_result

        plan = {
            "intent": "GET_WEATHER",
            "params": {"location": "London"}
        }

        # Act
        result = server.execute(plan)

        # Assert
        self.assertEqual(result["response"], "Sunny, 25C")
        mock_run.assert_called_with(
            ["curl", "-s", "https://wttr.in/London?format=3"],
            capture_output=True, text=True, timeout=5
        )

    @patch("server.subprocess.run")
    def test_weather_failure(self, mock_run):
        # Arrange
        mock_run.side_effect = Exception("Connection error")

        plan = {
            "intent": "GET_WEATHER",
            "params": {"location": "London"}
        }

        # Act
        result = server.execute(plan)

        # Assert
        self.assertEqual(result["response"], "Could not fetch weather")

if __name__ == "__main__":
    unittest.main()
