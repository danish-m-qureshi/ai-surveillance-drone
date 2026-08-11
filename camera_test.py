#!/usr/bin/env python3
"""Compatibility smoke test: capture a frame through the new pipeline."""

from argparse import Namespace

from surveillance import capture


if __name__ == "__main__":
    raise SystemExit(
        capture(
            Namespace(
                output="artifacts/camera_test.jpg",
                width=640,
                height=480,
                warmup=1.5,
            )
        )
    )
