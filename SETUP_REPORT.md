# Setup report

Date: 2026-08-11

## Raspberry Pi

- Host: `nomalice` (`192.168.0.150`)
- OS: Debian GNU/Linux 13 (trixie), arm64
- Camera: Raspberry Pi Camera Module 3, IMX708, 4608×2592 sensor
- Picamera2: system package installed and importable
- OpenCV: 4.10.0
- NumPy: 2.2.4

## Camera-busy diagnosis

The camera was held by PID 2309:

```text
/usr/bin/python3 /home/nomalice/projects/pi-camera-stream/stream.py
```

It was launched by the system service `pi-camera-stream.service`. The service
was stopped and disabled, while its source files and service definition were
left intact.

## Verification

- Picamera2 camera discovery: passed
- 1280×720 Picamera2 → NumPy → OpenCV capture: passed
- Six-second headless motion-monitor smoke test: passed
- Frames processed: 35
- Effective rate including warm-up/shutdown: 5.41 fps
- Motion events in the stationary test scene: 0
- Camera release after shutdown: passed
- Unit tests: 3 passed
- Python compilation check: passed

Generated test images are under `artifacts/` and intentionally ignored by Git.
