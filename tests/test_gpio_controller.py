import importlib
import sys
import threading
import time
import types
import unittest


class FakeGPIO:
    BCM = "BCM"
    OUT = "OUT"
    LOW = 0
    HIGH = 1

    def __init__(self):
        self.output_calls = []
        self.setup_calls = []
        self.cleanup_calls = []

    def setwarnings(self, _flag):
        return None

    def setmode(self, _mode):
        return None

    def setup(self, pin, mode, initial=None):
        self.setup_calls.append((pin, mode, initial))

    def output(self, pin, value):
        self.output_calls.append((pin, value))

    def cleanup(self, pin):
        self.cleanup_calls.append(pin)


class GPIOControllerTests(unittest.TestCase):
    def setUp(self):
        self.fake_gpio = FakeGPIO()
        sys.modules["RPi"] = types.SimpleNamespace(GPIO=self.fake_gpio)
        sys.modules["RPi.GPIO"] = self.fake_gpio
        module = importlib.import_module("gpio_controller")
        module = importlib.reload(module)
        self.GPIOController = module.GPIOController

    def tearDown(self):
        sys.modules.pop("RPi", None)
        sys.modules.pop("RPi.GPIO", None)

    def test_pulse_resets_pin_low(self):
        controller = self.GPIOController(pin=17, short_press_seconds=0.01)
        controller.initialize()
        controller.power_on()
        self.assertEqual(self.fake_gpio.output_calls[-2:], [(17, 1), (17, 0)])

    def test_cleanup_forces_low(self):
        controller = self.GPIOController(pin=17)
        controller.initialize()
        controller.cleanup()
        self.assertEqual(self.fake_gpio.output_calls[-1], (17, 0))
        self.assertEqual(self.fake_gpio.cleanup_calls, [17])

    def test_lock_serializes_pulses(self):
        controller = self.GPIOController(pin=17, short_press_seconds=0.02)
        controller.initialize()

        t1 = threading.Thread(target=controller.power_on)
        t2 = threading.Thread(target=controller.power_on)
        start = time.perf_counter()
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        elapsed = time.perf_counter() - start

        self.assertGreaterEqual(elapsed, 0.035)


if __name__ == "__main__":
    unittest.main()
