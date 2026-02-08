# GPIO Server Power Controller

A lightweight Flask app for Raspberry Pi Zero 2 W that triggers server power switch pulses through GPIO17.

## Features

- `POST /on`: 0.5s short pulse (power on)
- `POST /off`: 5s long pulse (force power off)
- Web UI at `/`
- Serialized GPIO access to prevent overlapping pulses
- GPIO forced LOW after each action and during cleanup

## Run

```bash
sudo python3 app.py
```

Optional flags:

```bash
sudo python3 app.py --host 0.0.0.0 --port 5000
```

## Wiring (BC548 low-side switch)

- Raspberry Pi GPIO17 -> 1kΩ resistor -> BC548 base
- Raspberry Pi GND -> BC548 emitter and motherboard GND
- BC548 collector across motherboard `PWR_SW` header pins

> Do not connect Raspberry Pi GPIO directly to motherboard header.


## systemd auto-start (optional)

1. Copy the project to your Pi (example path):

```bash
sudo mkdir -p /opt/gpio-server-power-controller
sudo cp -r . /opt/gpio-server-power-controller/
```

2. Install the included service unit:

```bash
sudo cp deploy/gpio-server-power-controller.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gpio-server-power-controller.service
```

3. Check status/logs:

```bash
sudo systemctl status gpio-server-power-controller.service
sudo journalctl -u gpio-server-power-controller.service -f
```

> If your deployment path or user differs, edit `WorkingDirectory`, `ExecStart`, `User`, and `Group` in the unit file.
