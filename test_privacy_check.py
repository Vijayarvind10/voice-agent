
import unittest
import sys
from unittest.mock import MagicMock

# Mock fastapi and uvicorn modules before importing server
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

# Import the function to be tested
from server import privacy_check

class TestPrivacyCheck(unittest.TestCase):
    def test_privacy_mode_on_external_search(self):
        plan = {"privacyClass": "external_search", "routeType": "remote"}
        privacy_mode = "ON"
        result = privacy_check(plan, privacy_mode)
        self.assertEqual(result, {"approved": False, "label": "BLOCKED · privacy mode ON"})

    def test_local_route(self):
        plan = {"privacyClass": "local_safe", "routeType": "local"}
        privacy_mode = "ON"
        result = privacy_check(plan, privacy_mode)
        self.assertEqual(result, {"approved": True, "label": "LOCAL · approved"})

    def test_pcc_route(self):
        plan = {"privacyClass": "cross_context_local", "routeType": "pcc"}
        privacy_mode = "ON"
        result = privacy_check(plan, privacy_mode)
        self.assertEqual(result, {"approved": True, "label": "PCC · approved"})

    def test_remote_route(self):
        plan = {"privacyClass": "remote_data", "routeType": "remote"}
        privacy_mode = "ON"
        result = privacy_check(plan, privacy_mode)
        self.assertEqual(result, {"approved": True, "label": "REMOTE · approved"})

    def test_privacy_mode_off_external_search(self):
        plan = {"privacyClass": "external_search", "routeType": "remote"}
        privacy_mode = "OFF"
        result = privacy_check(plan, privacy_mode)
        self.assertEqual(result, {"approved": True, "label": "REMOTE · approved"})

    def test_unsupported_route(self):
        plan = {"privacyClass": "unknown", "routeType": "unknown"}
        privacy_mode = "ON"
        result = privacy_check(plan, privacy_mode)
        self.assertEqual(result, {"approved": False, "label": "BLOCKED · unsupported"})

if __name__ == "__main__":
    unittest.main()
