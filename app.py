import argparse
import atexit
import logging
import os
from flask import Flask, jsonify, redirect, render_template, url_for

from gpio_controller import GPIOController

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = int(os.getenv("PORT", "5000"))


def create_app(controller: GPIOController) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/on")
    def power_on():
        controller.power_on()
        return jsonify({"status": "ok", "action": "power_on", "pulse_seconds": controller.short_press_seconds})

    @app.post("/off")
    def power_off():
        controller.power_off()
        return jsonify({"status": "ok", "action": "power_off", "pulse_seconds": controller.long_press_seconds})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/on/ui")
    def on_ui():
        controller.power_on()
        return redirect(url_for("index"))

    @app.post("/off/ui")
    def off_ui():
        controller.power_off()
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
    controller = GPIOController(pin=17, short_press_seconds=0.5, long_press_seconds=5.0)
    controller.initialize()
    atexit.register(controller.cleanup)

    app = create_app(controller)
    LOGGER.info("Starting GPIO Server Power Controller on %s:%s", args.host, args.port)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
