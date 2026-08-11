"""ONNX object detection with a small, replaceable runtime boundary."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
import os
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np


TARGET_CLASSES = {
    0: "person",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


@contextmanager
def suppress_native_stderr():
    """Temporarily silence native-library diagnostics without hiding exceptions."""
    saved_stderr = os.dup(2)
    try:
        with open(os.devnull, "w", encoding="utf-8") as sink:
            os.dup2(sink.fileno(), 2)
            yield
    finally:
        os.dup2(saved_stderr, 2)
        os.close(saved_stderr)


@dataclass(frozen=True)
class Detection:
    class_id: int
    label: str
    confidence: float
    box: tuple[int, int, int, int]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DetectionResult:
    detections: tuple[Detection, ...]
    inference_ms: float


def letterbox(frame: np.ndarray, size: int) -> tuple[np.ndarray, float, tuple[int, int]]:
    """Resize an RGB frame to a square while preserving its aspect ratio."""
    height, width = frame.shape[:2]
    scale = min(size / width, size / height)
    resized_width = round(width * scale)
    resized_height = round(height * scale)
    resized = cv2.resize(frame, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)
    pad_x = (size - resized_width) // 2
    pad_y = (size - resized_height) // 2
    canvas = np.full((size, size, 3), 114, dtype=np.uint8)
    canvas[pad_y : pad_y + resized_height, pad_x : pad_x + resized_width] = resized
    tensor = canvas.transpose(2, 0, 1)[None].astype(np.float32) / 255.0
    return np.ascontiguousarray(tensor), scale, (pad_x, pad_y)


def parse_end_to_end(
    output: np.ndarray,
    original_shape: tuple[int, int],
    scale: float,
    padding: tuple[int, int],
    confidence: float,
    class_names: dict[int, str] | None = None,
) -> tuple[Detection, ...]:
    """Convert YOLO26 end-to-end rows (x1, y1, x2, y2, score, class) to detections."""
    names = class_names or TARGET_CLASSES
    rows = output[0] if output.ndim == 3 else output
    if rows.ndim != 2 or rows.shape[1] != 6:
        raise ValueError(f"Expected YOLO26 end-to-end output shaped [N, 6], got {output.shape}")

    height, width = original_shape
    pad_x, pad_y = padding
    detections: list[Detection] = []
    for x1, y1, x2, y2, score, raw_class_id in rows:
        class_id = int(raw_class_id)
        if float(score) < confidence or class_id not in names:
            continue
        left = int(np.clip((x1 - pad_x) / scale, 0, width - 1))
        top = int(np.clip((y1 - pad_y) / scale, 0, height - 1))
        right = int(np.clip((x2 - pad_x) / scale, 0, width - 1))
        bottom = int(np.clip((y2 - pad_y) / scale, 0, height - 1))
        if right <= left or bottom <= top:
            continue
        detections.append(
            Detection(
                class_id=class_id,
                label=names[class_id],
                confidence=round(float(score), 4),
                box=(left, top, right, bottom),
            )
        )
    detections.sort(key=lambda item: item.confidence, reverse=True)
    return tuple(detections)


class OnnxObjectDetector:
    """Run a YOLO26 end-to-end ONNX model through ONNX Runtime."""

    def __init__(
        self,
        model_path: str | Path,
        confidence: float = 0.50,
        threads: int = 4,
    ) -> None:
        # Debian's ONNX Runtime package can emit duplicate schema-registration
        # diagnostics while importing even though the runtime is healthy. Keep
        # native stderr quiet only for the import; Python exceptions still raise.
        with suppress_native_stderr():
            import onnxruntime as ort

        path = Path(model_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Object detection model not found: {path}")
        options = ort.SessionOptions()
        options.intra_op_num_threads = max(1, threads)
        options.inter_op_num_threads = 1
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        with suppress_native_stderr():
            self.session = ort.InferenceSession(
                str(path),
                sess_options=options,
                providers=["CPUExecutionProvider"],
            )
        model_input = self.session.get_inputs()[0]
        if len(model_input.shape) != 4 or not isinstance(model_input.shape[-1], int):
            raise ValueError(f"Expected a fixed square image input, got {model_input.shape}")
        self.input_name = model_input.name
        self.input_size = int(model_input.shape[-1])
        self.confidence = confidence

    def detect(self, frame: np.ndarray) -> DetectionResult:
        tensor, scale, padding = letterbox(frame, self.input_size)
        started = perf_counter()
        output = self.session.run(None, {self.input_name: tensor})[0]
        inference_ms = (perf_counter() - started) * 1000
        detections = parse_end_to_end(
            output,
            frame.shape[:2],
            scale,
            padding,
            self.confidence,
        )
        return DetectionResult(detections, round(inference_ms, 2))


def annotate_detections(frame: np.ndarray, result: DetectionResult) -> np.ndarray:
    """Return a BGR image annotated with class names and confidence scores."""
    image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    for detection in result.detections:
        left, top, right, bottom = detection.box
        color = (0, 210, 255) if detection.label == "person" else (255, 170, 0)
        cv2.rectangle(image, (left, top), (right, bottom), color, 2)
        label = f"{detection.label} {detection.confidence:.2f}"
        cv2.putText(
            image,
            label,
            (left, max(20, top - 7)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            color,
            2,
        )
    return image
