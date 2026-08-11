# AI Surveillance Camera Lab

A small, headless learning project for Raspberry Pi Camera Module 3, Picamera2,
and OpenCV. It is intentionally local-first: frames stay on the Pi unless you
explicitly copy them elsewhere.

## What is included

- Camera and dependency diagnostics
- Still-image capture with autofocus
- A live OpenCV frame pipeline
- Simple motion detection and annotated evidence frames
- Unit tests that do not require camera hardware
- Clean shutdown so the camera is released after every run

## Quick start

```bash
cd ~/ai-surveillance
python3 surveillance.py doctor
python3 surveillance.py capture --output artifacts/capture.jpg
python3 surveillance.py monitor --seconds 10 --output-dir artifacts/monitor
python3 -m unittest discover -s tests -v
```

The monitor is headless, so it works over SSH. It prints a JSON summary and
writes `latest.jpg`, plus timestamped `motion-*.jpg` images when motion crosses
the configured threshold.

## Useful options

```bash
python3 surveillance.py --help
python3 surveillance.py capture --width 1280 --height 720
python3 surveillance.py monitor --seconds 30 --min-area 1800 --cooldown 2
```

`--min-area` controls how large a changed region must be before it counts as
motion. Increase it to reduce false positives; decrease it to make detection
more sensitive.

## Camera ownership

Only one program can own the Raspberry Pi camera at a time. The previous
`pi-camera-stream.service` was disabled during setup because it held the camera
continuously. To inspect camera users:

```bash
fuser -v /dev/media0 /dev/media1
```

## Project layout

```text
ai_surveillance/   reusable camera and motion-detection code
tests/             hardware-independent unit tests
artifacts/         generated captures (ignored by Git)
surveillance.py    command-line entry point
```

## Responsible use

Use this only where you have permission to record. Avoid identifying people or
uploading footage by default; this starter project performs only local motion
detection and does not include face recognition.
