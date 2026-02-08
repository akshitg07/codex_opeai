import argparse
import atexit
import logging
import os
from flask import Flask, jsonify, redirect, render_template, url_for

from gpio_controller import GPIOController

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = int(os.getenv("PORT", "5000"))
WINDOWS_GPIO_PIN = int(os.getenv("WINDOWS_GPIO_PIN", "17"))
LINUX_GPIO_PIN = int(os.getenv("LINUX_GPIO_PIN", "27"))


def create_app(windows_controller: GPIOController, linux_controller: GPIOController) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template(
            "index.html",
            windows_pin=windows_controller.pin,
            linux_pin=linux_controller.pin,
            short_press=windows_controller.short_press_seconds,
            long_press=windows_controller.long_press_seconds,
        )

    @app.post("/on")
    def windows_power_on():
        windows_controller.power_on()
        return jsonify({"status": "ok", "host": "windows", "action": "power_on", "pulse_seconds": windows_controller.short_press_seconds})

    @app.post("/off")
    def windows_power_off():
        windows_controller.power_off()
        return jsonify({"status": "ok", "host": "windows", "action": "power_off", "pulse_seconds": windows_controller.long_press_seconds})

    @app.post("/linux/on")
    def linux_power_on():
        linux_controller.power_on()
        return jsonify({"status": "ok", "host": "linux", "action": "power_on", "pulse_seconds": linux_controller.short_press_seconds})

    @app.post("/linux/off")
    def linux_power_off():
        linux_controller.power_off()
        return jsonify({"status": "ok", "host": "linux", "action": "power_off", "pulse_seconds": linux_controller.long_press_seconds})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/on/ui")
    def windows_on_ui():
        windows_controller.power_on()
        return redirect(url_for("index"))

    @app.post("/off/ui")
    def windows_off_ui():
        windows_controller.power_off()
        return redirect(url_for("index"))

    @app.post("/linux/on/ui")
    def linux_on_ui():
        linux_controller.power_on()
        return redirect(url_for("index"))

    @app.post("/linux/off/ui")
    def linux_off_ui():
        linux_controller.power_off()
        return redirect(url_for("index"))

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GPIO Server Power Controller")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Bind port (default: {DEFAULT_PORT})")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    windows_controller = GPIOController(pin=WINDOWS_GPIO_PIN, short_press_seconds=0.5, long_press_seconds=5.0)
    linux_controller = GPIOController(pin=LINUX_GPIO_PIN, short_press_seconds=0.5, long_press_seconds=5.0)

    windows_controller.initialize()
    linux_controller.initialize()
    atexit.register(windows_controller.cleanup)
    atexit.register(linux_controller.cleanup)

    app = create_app(windows_controller, linux_controller)
    LOGGER.info("Starting GPIO Server Power Controller on %s:%s", args.host, args.port)
    LOGGER.info("Windows host pin: GPIO%s, Linux host pin: GPIO%s", WINDOWS_GPIO_PIN, LINUX_GPIO_PIN)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
