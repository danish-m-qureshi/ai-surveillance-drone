"""Picamera2 lifecycle helpers."""

from __future__ import annotations

from contextlib import contextmanager
from time import sleep
from typing import Iterator

from picamera2 import Picamera2


def available_cameras() -> list[dict]:
    """Return Picamera2's description of attached cameras."""
    return Picamera2.global_camera_info()


@contextmanager
def open_camera(
    width: int = 640,
    height: int = 480,
    warmup_seconds: float = 1.5,
) -> Iterator[Picamera2]:
    """Configure and start a camera, always releasing it on exit."""
    camera = Picamera2()
    try:
        config = camera.create_video_configuration(
            main={"size": (width, height), "format": "RGB888"},
            buffer_count=4,
        )
        camera.configure(config)

        try:
            from libcamera import controls

            camera.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        except (ImportError, RuntimeError):
            # Autofocus support depends on the attached camera and libcamera build.
            pass

        camera.start()
        sleep(max(0.0, warmup_seconds))
        yield camera
    finally:
        try:
            camera.stop()
        except RuntimeError:
            pass
        camera.close()
