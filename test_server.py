
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock fastapi and uvicorn modules BEFORE importing server
mock_fastapi = MagicMock()
sys.modules["fastapi"] = mock_fastapi
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

# Configure the mock app instance
mock_app_instance = MagicMock()
mock_fastapi.FastAPI.return_value = mock_app_instance

# Decorators need to return the function they decorate
def mock_decorator(*args, **kwargs):
    def decorator(f):
        return f
    return decorator

mock_app_instance.websocket.side_effect = mock_decorator
mock_app_instance.get.side_effect = mock_decorator

# Now we can import server
try:
    import server
except ImportError as e:
    print(f"Failed to import server despite mocking: {e}")
    sys.exit(1)

class TestServerHelpers(unittest.TestCase):

    def test_normalise(self):
        self.assertEqual(server.normalise("  Hello   World  "), "hello World")
        self.assertEqual(server.normalise("Test"), "test")
        self.assertEqual(server.normalise(""), "")
        self.assertEqual(server.normalise("UPPERCASE"), "uPPERCASE")

    def test_wake_score(self):
        # wake_score(cmd) = min(0.98, 0.91 + (len(cmd) % 5) * 0.01)
        # len("hi") = 2. 2%5 = 2. 0.91 + 0.02 = 0.93
        self.assertAlmostEqual(server.wake_score("hi"), 0.93)
        # len("hello") = 5. 5%5 = 0. 0.91 + 0 = 0.91
        self.assertAlmostEqual(server.wake_score("hello"), 0.91)
        # len("longcommand") = 11. 11%5 = 1. 0.91 + 0.01 = 0.92
        self.assertAlmostEqual(server.wake_score("longcommand"), 0.92)

    def test_split_commands(self):
        text = "open safari and then check mail"
        cmds = server.split_commands(text)
        self.assertEqual(cmds, ["open safari", "check mail"])

        text = "do x and also do y"
        cmds = server.split_commands(text)
        self.assertEqual(cmds, ["do x", "do y"])

        text = "single command"
        cmds = server.split_commands(text)
        self.assertEqual(cmds, ["single command"])

        text = "first then second also third"
        cmds = server.split_commands(text)
        self.assertEqual(cmds, ["first", "second", "third"])

class TestClassification(unittest.TestCase):

    def test_classify_timer(self):
        # Timer with duration
        res = server.classify("set a timer for 10 minutes")
        self.assertEqual(res["intent"], "SET_TIMER")
        self.assertEqual(res["params"]["seconds"], 600)
        self.assertEqual(res["params"]["duration"], "10 minutes")

        # Timer missing duration
        res = server.classify("set a timer")
        self.assertEqual(res["intent"], "MISSING_SLOT")
        self.assertEqual(res["params"]["slot"], "timer_duration")

        # Timer slot filling
        res = server.classify("10 minutes", session_state={"awaiting_slot": "timer_duration"})
        self.assertEqual(res["intent"], "SET_TIMER")
        self.assertEqual(res["params"]["seconds"], 600)

        # Timer slot filling just number
        res = server.classify("10", session_state={"awaiting_slot": "timer_duration"})
        self.assertEqual(res["intent"], "SET_TIMER")
        self.assertEqual(res["params"]["seconds"], 600)

    def test_classify_music(self):
        res = server.classify("play jazz")
        self.assertEqual(res["intent"], "PLAY_MUSIC")
        self.assertEqual(res["params"]["query"], "jazz")

        res = server.classify("play something on youtube music")
        self.assertEqual(res["intent"], "PLAY_MUSIC")

    def test_classify_weather(self):
        res = server.classify("weather in London")
        self.assertEqual(res["intent"], "GET_WEATHER")
        self.assertEqual(res["params"]["location"], "london")

        res = server.classify("what is the weather")
        self.assertEqual(res["intent"], "GET_WEATHER")

    def test_classify_system(self):
        self.assertEqual(server.classify("take a screenshot")["intent"], "TAKE_SCREENSHOT")
        self.assertEqual(server.classify("what is on my clipboard")["intent"], "CLIPBOARD")
        self.assertEqual(server.classify("system info")["intent"], "SYSTEM_INFO")

    def test_classify_volume(self):
        res = server.classify("set volume to 50")
        self.assertEqual(res["intent"], "VOLUME_CONTROL")
        self.assertEqual(res["params"]["level"], 50)

        res = server.classify("mute")
        self.assertEqual(res["intent"], "VOLUME_CONTROL")
        self.assertTrue(res["params"]["mute"])

        res = server.classify("unmute")
        self.assertEqual(res["intent"], "VOLUME_CONTROL")
        self.assertTrue(res["params"]["unmute"])

    def test_classify_notes_reminders(self):
        res = server.classify("create a note buy milk")
        self.assertEqual(res["intent"], "CREATE_NOTE")
        self.assertEqual(res["params"]["body"], "buy milk")

        res = server.classify("remind me to call mom")
        self.assertEqual(res["intent"], "CREATE_REMINDER")
        self.assertEqual(res["params"]["body"], "call mom")

    def test_classify_finder(self):
        res = server.classify("open downloads folder")
        self.assertEqual(res["intent"], "OPEN_FINDER")
        self.assertEqual(res["params"]["folder"], "downloads")

    def test_classify_followup(self):
        res = server.classify("send a message and schedule a meeting")
        self.assertEqual(res["intent"], "FOLLOWUP_FROM_MESSAGE")

    def test_classify_web_maps(self):
        res = server.classify("search for python")
        self.assertEqual(res["intent"], "WEB_SEARCH")
        self.assertEqual(res["params"]["query"], "python")

        res = server.classify("navigate to home")
        self.assertEqual(res["intent"], "OPEN_MAPS")
        self.assertEqual(res["params"]["query"], "home")

    def test_classify_send_message(self):
        self.assertEqual(server.classify("send a message")["intent"], "SEND_MESSAGE")

    def test_classify_create_event(self):
        self.assertEqual(server.classify("create an event")["intent"], "CREATE_EVENT")

    def test_classify_open_app(self):
        res = server.classify("open safari")
        self.assertEqual(res["intent"], "OPEN_APP")
        self.assertEqual(res["params"]["app"], "safari")

    def test_classify_utilities(self):
        self.assertEqual(server.classify("what time is it")["intent"], "GET_DATE_TIME")
        self.assertEqual(server.classify("calculate 5 plus 3")["intent"], "CALCULATE")
        self.assertEqual(server.classify("what is my ip")["intent"], "GET_IP")
        self.assertEqual(server.classify("uptime")["intent"], "GET_UPTIME")

    def test_classify_fun(self):
        self.assertEqual(server.classify("tell me a joke")["intent"], "TELL_JOKE")
        self.assertEqual(server.classify("inspire me")["intent"], "GET_QUOTE") # "inspire" is in regex
        self.assertEqual(server.classify("flip a coin")["intent"], "FLIP_COIN")
        self.assertEqual(server.classify("roll a die")["intent"], "ROLL_DIE")

    def test_classify_definitions_conversions(self):
        res = server.classify("define algorithm")
        self.assertEqual(res["intent"], "DEFINE_WORD")
        self.assertEqual(res["params"]["word"], "algorithm")

        res = server.classify("convert 10 usd to eur")
        self.assertEqual(res["intent"], "CONVERT_CURRENCY")

    def test_unsupported(self):
        res = server.classify("make me a sandwich")
        self.assertEqual(res["intent"], "UNSUPPORTED")

class TestPrivacyAndRouting(unittest.TestCase):

    def test_privacy_check(self):
        plan_remote = {"privacyClass": "external_search", "routeType": "remote"}
        plan_local = {"privacyClass": "local_safe", "routeType": "local"}

        # Privacy ON, Remote Search -> Blocked
        res = server.privacy_check(plan_remote, "ON")
        self.assertFalse(res["approved"])
        self.assertIn("BLOCKED", res["label"])

        # Privacy OFF, Remote Search -> Allowed
        res = server.privacy_check(plan_remote, "OFF")
        self.assertTrue(res["approved"])
        self.assertIn("approved", res["label"])

        # Privacy ON, Local -> Allowed
        res = server.privacy_check(plan_local, "ON")
        self.assertTrue(res["approved"])

    def test_route_check(self):
        plan_remote = {"routeType": "remote", "servers": ["remote.server"]}
        plan_local = {"routeType": "local", "servers": ["local.server"]}

        # Offline, Remote Route -> Blocked
        res = server.route_check(plan_remote, "OFFLINE")
        self.assertFalse(res["ok"])
        self.assertIn("unavailable", res["label"])

        # Online, Remote Route -> OK
        res = server.route_check(plan_remote, "ONLINE")
        self.assertTrue(res["ok"])

        # Offline, Local Route -> OK
        res = server.route_check(plan_local, "OFFLINE")
        self.assertTrue(res["ok"])


class TestExecution(unittest.TestCase):

    @patch('server.run_osascript')
    @patch('server.run_cmd')
    @patch('server.run_open')
    @patch('server.subprocess')
    def test_execute_timer(self, mock_subprocess, mock_open, mock_cmd, mock_osascript):
        plan = {"intent": "SET_TIMER", "params": {"seconds": 60, "duration": "1 minute"}}
        res = server.execute(plan)

        self.assertEqual(res["entityId"][:6], "timer_")
        # Should call notification and sleep loop
        mock_osascript.assert_called()
        mock_subprocess.Popen.assert_called()

    @patch('server.run_open')
    def test_execute_music(self, mock_open):
        plan = {"intent": "PLAY_MUSIC", "params": {"query": "jazz"}}
        res = server.execute(plan)
        mock_open.assert_called_with("https://music.youtube.com/search?q=jazz")
        self.assertIn("Opening YouTube Music", res["response"])

    @patch('server.subprocess.run')
    def test_execute_weather(self, mock_run):
        mock_run.return_value.stdout = "20 C"
        plan = {"intent": "GET_WEATHER", "params": {"location": "London"}}
        res = server.execute(plan)
        self.assertEqual(res["response"], "20 C")

    @patch('server.run_cmd')
    def test_execute_screenshot(self, mock_cmd):
        plan = {"intent": "TAKE_SCREENSHOT", "params": {}}
        res = server.execute(plan)
        mock_cmd.assert_called()
        self.assertIn("Screenshot saved", res["response"])

    @patch('server.run_cmd')
    def test_execute_clipboard(self, mock_cmd):
        mock_cmd.return_value = "clipboard content"
        plan = {"intent": "CLIPBOARD", "params": {}}
        res = server.execute(plan)
        self.assertEqual(res["response"], "Clipboard: clipboard content")

    @patch('server.run_cmd')
    def test_execute_system_info(self, mock_cmd):
        # mock_cmd is called multiple times. We can use side_effect to return different values
        mock_cmd.side_effect = [
            "100%", # battery
            "17179869184", # mem (16GB)
            "Intel Core i7", # cpu
            "50%", # disk
        ]
        plan = {"intent": "SYSTEM_INFO", "params": {}}
        res = server.execute(plan)
        self.assertIn("Battery: 100%", res["response"])
        self.assertIn("RAM: 16GB", res["response"])

    @patch('server.run_osascript')
    def test_execute_volume(self, mock_osascript):
        plan = {"intent": "VOLUME_CONTROL", "params": {"level": 50}}
        server.execute(plan)
        mock_osascript.assert_called_with('set volume output volume 50')

    @patch('server.run_osascript')
    def test_execute_note(self, mock_osascript):
        plan = {"intent": "CREATE_NOTE", "params": {"body": "hello"}}
        server.execute(plan)
        # Check if osascript was called with something containing "hello"
        args, _ = mock_osascript.call_args
        self.assertIn("hello", args[0])

    @patch('server.run_open')
    def test_execute_finder(self, mock_open):
        plan = {"intent": "OPEN_FINDER", "params": {"folder": "downloads"}}
        server.execute(plan)
        # expanduser is called, so we can't match exact path easily without mocking expanduser,
        # but we can assume it calls run_open with something ending in Downloads
        args, _ = mock_open.call_args
        self.assertTrue(args[0].endswith("Downloads"))

    @patch('server.run_open')
    def test_execute_web_search(self, mock_open):
        plan = {"intent": "WEB_SEARCH", "params": {"query": "python"}}
        server.execute(plan)
        mock_open.assert_called_with("https://www.google.com/search?q=python")

    def test_execute_calculate(self):
        plan = {"intent": "CALCULATE", "params": {"expression": "5 plus 5"}}
        res = server.execute(plan)
        self.assertEqual(res["response"], "The answer is 10")

        # Test error handling
        plan = {"intent": "CALCULATE", "params": {"expression": "invalid"}}
        res = server.execute(plan)
        self.assertIn("I couldn't calculate that", res["response"])

    def test_execute_joke(self):
        plan = {"intent": "TELL_JOKE", "params": {}}
        res = server.execute(plan)
        self.assertIsInstance(res["response"], str)
        self.assertTrue(len(res["response"]) > 0)

    @patch('server.run_cmd')
    def test_execute_ip(self, mock_cmd):
        mock_cmd.return_value = "inet 192.168.1.5"
        plan = {"intent": "GET_IP", "params": {}}
        res = server.execute(plan)
        self.assertEqual(res["response"], "Your IP address is 192.168.1.5")

if __name__ == "__main__":
    unittest.main()
