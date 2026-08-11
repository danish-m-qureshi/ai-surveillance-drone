import unittest

import numpy as np

from ai_surveillance.detection import letterbox, parse_end_to_end


class DetectionTests(unittest.TestCase):
    def test_letterbox_preserves_frame_and_reports_padding(self) -> None:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tensor, scale, padding = letterbox(frame, 640)
        self.assertEqual(tensor.shape, (1, 3, 640, 640))
        self.assertEqual(scale, 1.0)
        self.assertEqual(padding, (0, 80))

    def test_parser_filters_classes_and_confidence(self) -> None:
        output = np.array(
            [[[10, 90, 110, 190, 0.90, 0], [20, 100, 120, 200, 0.20, 2], [0, 0, 20, 20, 0.99, 15]]],
            dtype=np.float32,
        )
        detections = parse_end_to_end(output, (480, 640), 1.0, (0, 80), 0.35)
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0].label, "person")
        self.assertEqual(detections[0].box, (10, 10, 110, 110))

    def test_parser_rejects_unknown_output_shape(self) -> None:
        with self.assertRaises(ValueError):
            parse_end_to_end(np.zeros((1, 84, 8400)), (480, 640), 1.0, (0, 80), 0.35)


if __name__ == "__main__":
    unittest.main()
