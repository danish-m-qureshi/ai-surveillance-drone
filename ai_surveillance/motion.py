"""Small OpenCV motion detector suitable for learning and prototyping."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class MotionResult:
    detected: bool
    changed_area: float
    boxes: tuple[tuple[int, int, int, int], ...]


class MotionDetector:
    """Detect changed regions relative to the previous video frame."""

    def __init__(self, min_area: float = 1200.0, threshold: int = 25) -> None:
        self.min_area = min_area
        self.threshold = threshold
        self._previous: np.ndarray | None = None

    @staticmethod
    def _prepare(frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        return cv2.GaussianBlur(gray, (21, 21), 0)

    def analyze(self, frame: np.ndarray) -> MotionResult:
        current = self._prepare(frame)
        if self._previous is None:
            self._previous = current
            return MotionResult(False, 0.0, ())

        difference = cv2.absdiff(self._previous, current)
        self._previous = current
        mask = cv2.threshold(difference, self.threshold, 255, cv2.THRESH_BINARY)[1]
        mask = cv2.dilate(mask, None, iterations=2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        areas_and_boxes = [
            (cv2.contourArea(contour), cv2.boundingRect(contour))
            for contour in contours
        ]
        significant = [item for item in areas_and_boxes if item[0] >= self.min_area]
        significant.sort(key=lambda item: item[0], reverse=True)
        return MotionResult(
            detected=bool(significant),
            changed_area=sum(area for area, _ in significant),
            boxes=tuple(box for _, box in significant),
        )


def annotate(frame: np.ndarray, result: MotionResult) -> np.ndarray:
    """Return a BGR image with motion boxes and a status label."""
    image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    color = (0, 0, 255) if result.detected else (0, 180, 0)
    label = "MOTION" if result.detected else "CLEAR"
    cv2.putText(image, label, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    for x, y, width, height in result.boxes:
        cv2.rectangle(image, (x, y), (x + width, y + height), color, 2)
    return image
