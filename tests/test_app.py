import importlib
import importlib.util
import sys
import types
import unittest


@unittest.skipIf(importlib.util.find_spec("flask") is None, "Flask is not installed in this environment")
class AppRouteTests(unittest.TestCase):
    class StubGPIO:
        BCM = "BCM"
        OUT = "OUT"
        LOW = 0
        HIGH = 1

        def setwarnings(self, _flag):
            return None

        def setmode(self, _mode):
            return None

        def setup(self, _pin, _mode, initial=None):
            return None

        def output(self, _pin, _value):
            return None

        def cleanup(self, _pin):
            return None

    class StubController:
        short_press_seconds = 0.5
        long_press_seconds = 5.0

        def __init__(self, pin):
            self.pin = pin
            self.on_calls = 0
            self.off_calls = 0

        def power_on(self):
            self.on_calls += 1

        def power_off(self):
            self.off_calls += 1

    def setUp(self):
        gpio = self.StubGPIO()
        sys.modules["RPi"] = types.SimpleNamespace(GPIO=gpio)
        sys.modules["RPi.GPIO"] = gpio
        module = importlib.import_module("app")
        module = importlib.reload(module)

        self.windows_controller = self.StubController(pin=17)
        self.linux_controller = self.StubController(pin=27)
        self.client = module.create_app(self.windows_controller, self.linux_controller).test_client()

    def tearDown(self):
        sys.modules.pop("RPi", None)
        sys.modules.pop("RPi.GPIO", None)

    def test_root_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Windows Host", response.data)
        self.assertIn(b"Linux Host", response.data)

    def test_windows_on_endpoint(self):
        response = self.client.post("/on")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.windows_controller.on_calls, 1)

    def test_windows_off_endpoint(self):
        response = self.client.post("/off")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.windows_controller.off_calls, 1)

    def test_linux_on_endpoint(self):
        response = self.client.post("/linux/on")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.linux_controller.on_calls, 1)

    def test_linux_off_endpoint(self):
        response = self.client.post("/linux/off")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.linux_controller.off_calls, 1)


if __name__ == "__main__":
    unittest.main()
