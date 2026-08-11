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

## Object detection milestone

Added 2026-08-12:

- Model: YOLO26n, COCO pretrained, 640×640 ONNX export
- Runtime: Debian `python3-onnxruntime`, CPUExecutionProvider, four threads
- Enabled classes: person, car, motorcycle, bus, truck
- Static-image inference: 133.26 ms; one person at 75.29% confidence
- Eight-second live run: 43 frames, 43 detections, four evidence events
- Mean live inference: 142.73 ms
- End-to-end live rate including camera handling: 5.10 fps
- Detection and motion unit tests: 6 passed
- Model checksum verification: passed
- Camera release after live inference: passed

The model binary is ignored by Git and documented by its SHA-256 manifest.
