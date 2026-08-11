#!/usr/bin/env python3
"""Command-line interface for the camera learning project."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic, sleep

import cv2
import numpy as np
from picamera2 import Picamera2

from ai_surveillance.camera import available_cameras, open_camera
from ai_surveillance.motion import MotionDetector, annotate


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def doctor(_: argparse.Namespace) -> int:
    cameras = available_cameras()
    report = {
        "status": "ready" if cameras else "no-camera",
        "picamera2": getattr(__import__("picamera2"), "__version__", "unknown"),
        "opencv": cv2.__version__,
        "numpy": np.__version__,
        "cameras": cameras,
    }
    print(json.dumps(report, indent=2, default=str))
    return 0 if cameras else 1


def capture(args: argparse.Namespace) -> int:
    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    with open_camera(args.width, args.height, args.warmup) as camera:
        frame = camera.capture_array("main")
    if not cv2.imwrite(str(output), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)):
        raise RuntimeError(f"OpenCV could not write {output}")
    print(json.dumps({"status": "captured", "path": str(output.resolve()), "shape": frame.shape}))
    return 0


def monitor(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    detector = MotionDetector(min_area=args.min_area, threshold=args.threshold)
    started = monotonic()
    last_event = float("-inf")
    frames = 0
    events = 0
    latest = None

    with open_camera(args.width, args.height, args.warmup) as camera:
        while monotonic() - started < args.seconds:
            frame = camera.capture_array("main")
            result = detector.analyze(frame)
            latest = annotate(frame, result)
            frames += 1

            now = monotonic()
            if result.detected and now - last_event >= args.cooldown:
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
                cv2.imwrite(str(output_dir / f"motion-{timestamp}.jpg"), latest)
                last_event = now
                events += 1

            if args.fps > 0:
                sleep(1.0 / args.fps)

    if latest is None:
        raise RuntimeError("No frames were captured")
    latest_path = output_dir / "latest.jpg"
    cv2.imwrite(str(latest_path), latest)
    elapsed = monotonic() - started
    summary = {
        "status": "complete",
        "frames": frames,
        "motion_events": events,
        "elapsed_seconds": round(elapsed, 2),
        "effective_fps": round(frames / elapsed, 2),
        "latest_frame": str(latest_path.resolve()),
    }
    print(json.dumps(summary, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subcommands.add_parser("doctor", help="check dependencies and camera discovery")
    doctor_parser.set_defaults(func=doctor)

    capture_parser = subcommands.add_parser("capture", help="capture one image")
    capture_parser.add_argument("--output", default="artifacts/capture.jpg")
    add_camera_options(capture_parser)
    capture_parser.set_defaults(func=capture)

    monitor_parser = subcommands.add_parser("monitor", help="run headless motion detection")
    monitor_parser.add_argument("--seconds", type=positive_int, default=10)
    monitor_parser.add_argument("--fps", type=float, default=8.0)
    monitor_parser.add_argument("--min-area", type=float, default=1200.0)
    monitor_parser.add_argument("--threshold", type=int, default=25)
    monitor_parser.add_argument("--cooldown", type=float, default=2.0)
    monitor_parser.add_argument("--output-dir", default="artifacts/monitor")
    add_camera_options(monitor_parser)
    monitor_parser.set_defaults(func=monitor)
    return parser


def add_camera_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--width", type=positive_int, default=640)
    parser.add_argument("--height", type=positive_int, default=480)
    parser.add_argument("--warmup", type=float, default=1.5)


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    raise SystemExit(arguments.func(arguments))
