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
