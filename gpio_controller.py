import threading
import time
from typing import Optional

import RPi.GPIO as GPIO


class GPIOController:
    def __init__(self, pin: int, short_press_seconds: float = 0.5, long_press_seconds: float = 5.0) -> None:
        self.pin = pin
        self.short_press_seconds = short_press_seconds
        self.long_press_seconds = long_press_seconds
        self._lock = threading.Lock()
        self._initialized = False

    def initialize(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        self._initialized = True

    def pulse(self, seconds: float) -> None:
        if not self._initialized:
            raise RuntimeError("GPIO controller is not initialized")

        with self._lock:
            GPIO.output(self.pin, GPIO.HIGH)
            try:
                time.sleep(seconds)
            finally:
                GPIO.output(self.pin, GPIO.LOW)

    def power_on(self) -> None:
        self.pulse(self.short_press_seconds)

    def power_off(self) -> None:
        self.pulse(self.long_press_seconds)

    def cleanup(self) -> None:
        if not self._initialized:
            return

        with self._lock:
            GPIO.output(self.pin, GPIO.LOW)
            GPIO.cleanup(self.pin)
            self._initialized = False
