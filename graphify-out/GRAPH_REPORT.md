# Graph Report - .  (2026-08-12)

## Corpus Check
- Corpus is ~2,566 words - fits in a single context window. You may not need a graph.

## Summary
- 92 nodes · 155 edges · 7 communities (6 shown, 1 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Camera CLI and Capture|Camera CLI and Capture]]
- [[_COMMUNITY_Object Detection Pipeline|Object Detection Pipeline]]
- [[_COMMUNITY_Motion Detection Tests|Motion Detection Tests]]
- [[_COMMUNITY_YOLO Model Design|YOLO Model Design]]
- [[_COMMUNITY_Setup and Responsible Use|Setup and Responsible Use]]
- [[_COMMUNITY_ONNX Runtime Boundary|ONNX Runtime Boundary]]
- [[_COMMUNITY_Package Overview|Package Overview]]

## God Nodes (most connected - your core abstractions)
1. `MotionDetector` - 12 edges
2. `build_parser()` - 10 edges
3. `parse_end_to_end()` - 8 edges
4. `Ultralytics YOLO26n` - 8 edges
5. `open_camera()` - 7 edges
6. `OnnxObjectDetector` - 7 edges
7. `annotate_detections()` - 7 edges
8. `monitor()` - 7 edges
9. `detect_live()` - 7 edges
10. `letterbox()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Ultralytics YOLO26n` --semantically_similar_to--> `YOLO26n Person and Vehicle Detection`  [INFERRED] [semantically similar]
  MODEL.md → README.md
- `Model Binary Integrity` --semantically_similar_to--> `Model Checksum Verification`  [INFERRED] [semantically similar]
  MODEL.md → SETUP_REPORT.md
- `YOLO26n Person and Vehicle Detection` --semantically_similar_to--> `Object Detection Milestone`  [INFERRED] [semantically similar]
  README.md → SETUP_REPORT.md
- `Exclusive Camera Ownership` --semantically_similar_to--> `Camera-Busy Diagnosis`  [INFERRED] [semantically similar]
  README.md → SETUP_REPORT.md
- `detect_image()` --calls--> `OnnxObjectDetector`  [EXTRACTED]
  surveillance.py → ai_surveillance/detection.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Documented YOLO26n Detection Stack** — pi_project_staging_ai_surveillance_drone_model_yolo26n, pi_project_staging_ai_surveillance_drone_readme_yolo26n_person_vehicle_detection, pi_project_staging_ai_surveillance_drone_setup_report_object_detection_milestone [INFERRED 0.95]
- **Camera Resource Management Flow** — pi_project_staging_ai_surveillance_drone_readme_exclusive_camera_ownership, pi_project_staging_ai_surveillance_drone_setup_report_camera_busy_diagnosis, pi_project_staging_ai_surveillance_drone_setup_report_non_destructive_service_disablement, pi_project_staging_ai_surveillance_drone_setup_report_camera_pipeline_verification [INFERRED 0.95]
- **Local Surveillance Evidence Pipeline** — pi_project_staging_ai_surveillance_drone_readme_local_first_frame_handling, pi_project_staging_ai_surveillance_drone_readme_headless_motion_monitor, pi_project_staging_ai_surveillance_drone_readme_annotated_motion_evidence, pi_project_staging_ai_surveillance_drone_readme_detection_event_artifacts, pi_project_staging_ai_surveillance_drone_readme_responsible_surveillance_use [INFERRED 0.85]

## Communities (7 total, 1 thin omitted)

### Community 0 - "Camera CLI and Capture"
Cohesion: 0.21
Nodes (18): available_cameras(), open_camera(), Picamera2 lifecycle helpers., Return Picamera2's description of attached cameras., Configure and start a camera, always releasing it on exit., ArgumentParser, Namespace, Path (+10 more)

### Community 1 - "Object Detection Pipeline"
Cohesion: 0.19
Nodes (11): annotate_detections(), Detection, DetectionResult, letterbox(), parse_end_to_end(), ndarray, ONNX object detection with a small, replaceable runtime boundary., Return a BGR image annotated with class names and confidence scores. (+3 more)

### Community 2 - "Motion Detection Tests"
Cohesion: 0.21
Nodes (8): annotate(), MotionDetector, MotionResult, ndarray, Small OpenCV motion detector suitable for learning and prototyping., Detect changed regions relative to the previous video frame., Return a BGR image with motion boxes and a status label., MotionDetectorTests

### Community 3 - "YOLO Model Design"
Cohesion: 0.14
Nodes (15): COCO Pretraining, Enabled Detection Classes, End-to-End Detection Rows, Aspect-Ratio-Preserving Letterbox Preprocessing, Model Binary Integrity, Object Detection Model, ONNX Runtime CPUExecutionProvider, Ultralytics Licensing (+7 more)

### Community 4 - "Setup and Responsible Use"
Cohesion: 0.15
Nodes (14): AI Surveillance Camera Lab, Annotated Motion Evidence, Exclusive Camera Ownership, Headless Motion Monitor, Local-First Frame Handling, Motion Area Threshold Tuning, Raspberry Pi Camera Stack, Responsible Surveillance Use (+6 more)

### Community 5 - "ONNX Runtime Boundary"
Cohesion: 0.40
Nodes (4): OnnxObjectDetector, Run a YOLO26 end-to-end ONNX model through ONNX Runtime., Temporarily silence native-library diagnostics without hiding exceptions., suppress_native_stderr()

## Knowledge Gaps
- **9 isolated node(s):** `COCO Pretraining`, `ONNX Runtime CPUExecutionProvider`, `End-to-End Detection Rows`, `Enabled Detection Classes`, `Annotated Motion Evidence` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MotionDetector` connect `Motion Detection Tests` to `Camera CLI and Capture`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `YOLO26n Person and Vehicle Detection` connect `YOLO Model Design` to `Setup and Responsible Use`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `build_parser()` (e.g. with `capture()` and `detect_image()`) actually correct?**
  _`build_parser()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Reusable components for the AI surveillance camera lab.`, `Picamera2 lifecycle helpers.`, `Return Picamera2's description of attached cameras.` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `YOLO Model Design` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._