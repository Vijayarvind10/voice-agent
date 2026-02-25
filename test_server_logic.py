import sys
import unittest
from unittest.mock import MagicMock

# Mock fastapi and uvicorn before importing server
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

# Also mock WebSocket and WebSocketDisconnect inside fastapi
sys.modules["fastapi"].WebSocket = MagicMock()
sys.modules["fastapi"].WebSocketDisconnect = MagicMock()

try:
    from server import classify
except ImportError as e:
    print(f"Failed to import server.py: {e}")
    sys.exit(1)

class TestClassify(unittest.TestCase):
    def test_set_timer(self):
        # Duration
        res = classify("set timer for 10 minutes")
        self.assertEqual(res["intent"], "SET_TIMER")
        self.assertEqual(res["params"]["seconds"], 600)
        self.assertEqual(res["confidence"], 0.96)

        # Numeric (requires state)
        res = classify("10", session_state={"awaiting_slot": "timer_duration"})
        self.assertEqual(res["intent"], "SET_TIMER")
        self.assertEqual(res["params"]["seconds"], 600)

    def test_music(self):
        res = classify("play jazz")
        self.assertEqual(res["intent"], "PLAY_MUSIC")
        self.assertEqual(res["params"]["query"], "jazz")

    def test_weather(self):
        res = classify("weather in London")
        self.assertEqual(res["intent"], "GET_WEATHER")
        self.assertEqual(res["params"]["location"], "london")

    def test_screenshot(self):
        res = classify("take a screenshot")
        self.assertEqual(res["intent"], "TAKE_SCREENSHOT")

    def test_clipboard(self):
        res = classify("show clipboard")
        self.assertEqual(res["intent"], "CLIPBOARD")

    def test_system_info(self):
        res = classify("battery status")
        self.assertEqual(res["intent"], "SYSTEM_INFO")

    def test_volume(self):
        res = classify("set volume to 50")
        self.assertEqual(res["intent"], "VOLUME_CONTROL")
        self.assertEqual(res["params"]["level"], 50)

        res = classify("mute volume")
        self.assertEqual(res["intent"], "VOLUME_CONTROL")
        self.assertTrue(res["params"]["mute"])

    def test_notes(self):
        res = classify("create a note saying hello world")
        self.assertEqual(res["intent"], "CREATE_NOTE")
        self.assertEqual(res["params"]["body"], "hello world")

    def test_reminders(self):
        res = classify("remind me to buy milk")
        self.assertEqual(res["intent"], "CREATE_REMINDER")
        self.assertEqual(res["params"]["body"], "buy milk")

    def test_finder(self):
        res = classify("open downloads folder")
        self.assertEqual(res["intent"], "OPEN_FINDER")
        self.assertEqual(res["params"]["folder"], "downloads")

    def test_followup(self):
        res = classify("follow up on that message")
        self.assertEqual(res["intent"], "FOLLOWUP_FROM_MESSAGE")

    def test_web_search(self):
        res = classify("search for python")
        self.assertEqual(res["intent"], "WEB_SEARCH")
        self.assertEqual(res["params"]["query"], "python")

    def test_maps(self):
        res = classify("navigate to paris")
        self.assertEqual(res["intent"], "OPEN_MAPS")
        self.assertEqual(res["params"]["query"], "paris")

    def test_send_message(self):
        res = classify("send a message")
        self.assertEqual(res["intent"], "SEND_MESSAGE")

    def test_create_event(self):
        res = classify("create a meeting")
        self.assertEqual(res["intent"], "CREATE_EVENT")

    def test_open_app(self):
        res = classify("open safari")
        self.assertEqual(res["intent"], "OPEN_APP")
        self.assertEqual(res["params"]["app"], "safari")

    def test_date_time(self):
        res = classify("what time is it")
        self.assertEqual(res["intent"], "GET_DATE_TIME")

    def test_calculate(self):
        res = classify("calculate 5 plus 5")
        self.assertEqual(res["intent"], "CALCULATE")
        self.assertEqual(res["params"]["expression"], "calculate 5 plus 5")

    def test_joke(self):
        res = classify("tell me a joke")
        self.assertEqual(res["intent"], "TELL_JOKE")

    def test_quote(self):
        res = classify("inspire me")
        self.assertEqual(res["intent"], "GET_QUOTE")

    def test_flip_coin(self):
        res = classify("flip a coin")
        self.assertEqual(res["intent"], "FLIP_COIN")

    def test_roll_die(self):
        res = classify("roll a die")
        self.assertEqual(res["intent"], "ROLL_DIE")

    def test_define(self):
        res = classify("define recursion")
        self.assertEqual(res["intent"], "DEFINE_WORD")
        self.assertEqual(res["params"]["word"], "recursion")

    def test_currency(self):
        res = classify("convert 10 usd to eur")
        self.assertEqual(res["intent"], "CONVERT_CURRENCY")

    def test_ip(self):
        res = classify("what is my ip")
        self.assertEqual(res["intent"], "GET_IP")

    def test_uptime(self):
        res = classify("uptime")
        self.assertEqual(res["intent"], "GET_UPTIME")

    def test_unsupported(self):
        res = classify("make me a sandwich")
        self.assertEqual(res["intent"], "UNSUPPORTED")

if __name__ == '__main__':
    unittest.main()
