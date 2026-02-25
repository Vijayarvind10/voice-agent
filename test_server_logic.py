import sys
import unittest
from unittest.mock import MagicMock

# Mock necessary modules
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()

# Import the module to test
from server import route_check

class TestRouteCheck(unittest.TestCase):
    def test_route_none(self):
        plan = {"routeType": "none", "servers": []}
        network_mode = "ONLINE"
        result = route_check(plan, network_mode)
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["routeType"], "none")
        self.assertEqual(result["label"], "no route")
        self.assertEqual(result["servers"], [])

    def test_route_remote_offline(self):
        plan = {"routeType": "remote", "servers": ["remote_server"]}
        network_mode = "OFFLINE"
        result = route_check(plan, network_mode)
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["routeType"], "remote")
        self.assertEqual(result["label"], "REMOTE · network unavailable")
        self.assertEqual(result["servers"], ["remote_server"])

    def test_route_remote_online(self):
        plan = {"routeType": "remote", "servers": ["remote_server"]}
        network_mode = "ONLINE"
        result = route_check(plan, network_mode)
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["routeType"], "remote")
        self.assertEqual(result["label"], "REMOTE route")
        self.assertEqual(result["servers"], ["remote_server"])

    def test_route_local(self):
        plan = {"routeType": "local", "servers": ["local_server"]}
        network_mode = "ONLINE"
        result = route_check(plan, network_mode)
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["routeType"], "local")
        self.assertEqual(result["label"], "LOCAL route")
        self.assertEqual(result["servers"], ["local_server"])

    def test_route_pcc(self):
        plan = {"routeType": "pcc", "servers": ["pcc_server"]}
        network_mode = "ONLINE"
        result = route_check(plan, network_mode)
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["routeType"], "pcc")
        self.assertEqual(result["label"], "PCC route")
        self.assertEqual(result["servers"], ["pcc_server"])

if __name__ == "__main__":
    unittest.main()
