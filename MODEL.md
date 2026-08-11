# Object detection model

- Model: Ultralytics YOLO26n detection, COCO pretrained
- Runtime: ONNX Runtime CPUExecutionProvider
- Input: 640×640 RGB, aspect-ratio-preserving letterbox
- Output: end-to-end rows (`x1`, `y1`, `x2`, `y2`, confidence, class ID)
- Enabled classes: person, car, motorcycle, bus, truck

The model binary is stored as `models/yolo26n.onnx` and ignored by Git. Its
checksum is recorded in `models/yolo26n.onnx.sha256` after deployment.

Ultralytics code and pretrained models use AGPL-3.0 by default. A proprietary or
commercial deployment requires appropriate licensing or a differently licensed
model. See <https://www.ultralytics.com/license>.
