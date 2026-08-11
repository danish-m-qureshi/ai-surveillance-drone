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
from ai_surveillance.detection import OnnxObjectDetector, annotate_detections
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


def detect_image(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser()
    output_path = Path(args.output).expanduser()
    image = cv2.imread(str(input_path))
    if image is None:
        raise FileNotFoundError(f"Could not read input image: {input_path}")
    frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    detector = OnnxObjectDetector(args.model, args.confidence, args.threads)
    result = detector.detect(frame)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), annotate_detections(frame, result))
    report = {
        "status": "complete",
        "input": str(input_path.resolve()),
        "output": str(output_path.resolve()),
        "inference_ms": result.inference_ms,
        "detections": [detection.to_dict() for detection in result.detections],
    }
    print(json.dumps(report, indent=2))
    return 0


def detect_live(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    events_path = output_dir / "events.jsonl"
    detector = OnnxObjectDetector(args.model, args.confidence, args.threads)
    started = monotonic()
    last_event = float("-inf")
    frames = 0
    total_detections = 0
    event_images = 0
    inference_times: list[float] = []
    latest = None

    with events_path.open("a", encoding="utf-8") as event_file:
        with open_camera(args.width, args.height, args.warmup) as camera:
            while monotonic() - started < args.seconds:
                frame = camera.capture_array("main")
                result = detector.detect(frame)
                latest = annotate_detections(frame, result)
                frames += 1
                total_detections += len(result.detections)
                inference_times.append(result.inference_ms)

                if result.detections and monotonic() - last_event >= args.cooldown:
                    captured_at = datetime.now(timezone.utc)
                    timestamp = captured_at.strftime("%Y%m%dT%H%M%S.%fZ")
                    image_path = output_dir / f"detection-{timestamp}.jpg"
                    cv2.imwrite(str(image_path), latest)
                    event = {
                        "captured_at": captured_at.isoformat(),
                        "image": str(image_path.resolve()),
                        "detections": [item.to_dict() for item in result.detections],
                    }
                    event_file.write(json.dumps(event) + "\n")
                    event_file.flush()
                    last_event = monotonic()
                    event_images += 1

    if latest is None:
        raise RuntimeError("No frames were captured")
    latest_path = output_dir / "latest.jpg"
    cv2.imwrite(str(latest_path), latest)
    elapsed = monotonic() - started
    report = {
        "status": "complete",
        "frames": frames,
        "detections": total_detections,
        "event_images": event_images,
        "mean_inference_ms": round(sum(inference_times) / len(inference_times), 2),
        "effective_fps": round(frames / elapsed, 2),
        "events": str(events_path.resolve()),
        "latest_frame": str(latest_path.resolve()),
    }
    print(json.dumps(report, indent=2))
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

    image_parser = subcommands.add_parser("detect-image", help="run AI detection on an image")
    image_parser.add_argument("--input", required=True)
    image_parser.add_argument("--output", default="artifacts/detected-image.jpg")
    add_detection_options(image_parser)
    image_parser.set_defaults(func=detect_image)

    detection_parser = subcommands.add_parser("detect", help="run live AI object detection")
    detection_parser.add_argument("--seconds", type=positive_int, default=10)
    detection_parser.add_argument("--cooldown", type=float, default=2.0)
    detection_parser.add_argument("--output-dir", default="artifacts/detections")
    add_camera_options(detection_parser)
    add_detection_options(detection_parser)
    detection_parser.set_defaults(func=detect_live)
    return parser


def add_camera_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--width", type=positive_int, default=640)
    parser.add_argument("--height", type=positive_int, default=480)
    parser.add_argument("--warmup", type=float, default=1.5)


def add_detection_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model", default="models/yolo26n.onnx")
    parser.add_argument("--confidence", type=float, default=0.50)
    parser.add_argument("--threads", type=positive_int, default=4)


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    raise SystemExit(arguments.func(arguments))
