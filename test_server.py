import sys
from unittest.mock import MagicMock
import unittest

# Mock external dependencies
fastapi_mock = MagicMock()
app_mock = MagicMock()
fastapi_mock.FastAPI.return_value = app_mock
sys.modules["fastapi"] = fastapi_mock
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

# Import the module to be tested
from server import classify

class TestClassify(unittest.TestCase):
    def test_timer(self):
        # Awaiting slot scenario
        state = {"awaiting_slot": "timer_duration"}
        result = classify("10 minutes", state)
        self.assertEqual(result["intent"], "SET_TIMER")
        self.assertEqual(result["params"]["seconds"], 600)

        # Direct command
        result = classify("set timer for 10 minutes")
        self.assertEqual(result["intent"], "SET_TIMER")
        self.assertEqual(result["params"]["seconds"], 600)

        result = classify("timer 5 min")
        self.assertEqual(result["intent"], "SET_TIMER")
        self.assertEqual(result["params"]["seconds"], 300)

        # Missing slot
        result = classify("set a timer")
        self.assertEqual(result["intent"], "MISSING_SLOT")
        self.assertEqual(result["params"]["slot"], "timer_duration")

    def test_repeat_history(self):
        result = classify("repeat that")
        self.assertEqual(result["intent"], "REPEAT_LAST")

        result = classify("what did i just say")
        self.assertEqual(result["intent"], "RECALL_HISTORY")

    def test_music(self):
        result = classify("play jazz on youtube music")
        self.assertEqual(result["intent"], "PLAY_MUSIC")
        self.assertEqual(result["params"]["query"], "jazz")

    def test_weather(self):
        result = classify("weather in London")
        self.assertEqual(result["intent"], "GET_WEATHER")
        self.assertEqual(result["params"]["location"], "london")

    def test_screenshot(self):
        result = classify("take a screenshot")
        self.assertEqual(result["intent"], "TAKE_SCREENSHOT")

    def test_clipboard(self):
        result = classify("show clipboard")
        self.assertEqual(result["intent"], "CLIPBOARD")

    def test_system_info(self):
        result = classify("battery status")
        self.assertEqual(result["intent"], "SYSTEM_INFO")

    def test_volume(self):
        result = classify("set volume to 50")
        self.assertEqual(result["intent"], "VOLUME_CONTROL")
        self.assertEqual(result["params"]["level"], 50)

        result = classify("mute volume")
        self.assertEqual(result["intent"], "VOLUME_CONTROL")
        self.assertTrue(result["params"]["mute"])

    def test_notes(self):
        result = classify("create a note buy milk")
        self.assertEqual(result["intent"], "CREATE_NOTE")
        self.assertEqual(result["params"]["body"], "buy milk")

    def test_reminders(self):
        result = classify("remind me to call mom")
        self.assertEqual(result["intent"], "CREATE_REMINDER")
        self.assertEqual(result["params"]["body"], "call mom")

    def test_finder(self):
        result = classify("open downloads folder")
        self.assertEqual(result["intent"], "OPEN_FINDER")
        self.assertEqual(result["params"]["folder"], "downloads")

    def test_messages_followup(self):
        result = classify("message follow-up")
        self.assertEqual(result["intent"], "FOLLOWUP_FROM_MESSAGE")

    def test_web_search(self):
        result = classify("search for python")
        self.assertEqual(result["intent"], "WEB_SEARCH")
        self.assertEqual(result["params"]["query"], "python")

    def test_maps(self):
        result = classify("navigate to home")
        self.assertEqual(result["intent"], "OPEN_MAPS")
        self.assertEqual(result["params"]["query"], "home")

    def test_send_message(self):
        result = classify("send message")
        self.assertEqual(result["intent"], "SEND_MESSAGE")

    def test_create_event(self):
        result = classify("create event")
        self.assertEqual(result["intent"], "CREATE_EVENT")

    def test_open_app(self):
        result = classify("open calculator")
        self.assertEqual(result["intent"], "OPEN_APP")
        self.assertEqual(result["params"]["app"], "calculator")

    def test_date_time(self):
        result = classify("what time is it")
        self.assertEqual(result["intent"], "GET_DATE_TIME")

    def test_calculate(self):
        result = classify("calculate 5 plus 5")
        self.assertEqual(result["intent"], "CALCULATE")
        self.assertEqual(result["params"]["expression"], "calculate 5 plus 5")

    def test_jokes_quotes(self):
        result = classify("tell me a joke")
        self.assertEqual(result["intent"], "TELL_JOKE")

        result = classify("give me a quote")
        self.assertEqual(result["intent"], "GET_QUOTE")

    def test_random(self):
        result = classify("flip a coin")
        self.assertEqual(result["intent"], "FLIP_COIN")

        result = classify("roll a die")
        self.assertEqual(result["intent"], "ROLL_DIE")

    def test_dictionary(self):
        result = classify("define recursion")
        self.assertEqual(result["intent"], "DEFINE_WORD")
        self.assertEqual(result["params"]["word"], "recursion")

    def test_currency(self):
        result = classify("convert 10 usd to eur")
        self.assertEqual(result["intent"], "CONVERT_CURRENCY")

    def test_ip_uptime(self):
        result = classify("what is my ip")
        self.assertEqual(result["intent"], "GET_IP")

        result = classify("system uptime")
        self.assertEqual(result["intent"], "GET_UPTIME")

    def test_unsupported(self):
        result = classify("something completely random 12345")
        self.assertEqual(result["intent"], "UNSUPPORTED")

if __name__ == "__main__":
    unittest.main()
