import unittest

import numpy as np

from ai_surveillance.motion import MotionDetector


class MotionDetectorTests(unittest.TestCase):
    def test_first_frame_establishes_baseline(self) -> None:
        detector = MotionDetector(min_area=100)
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        self.assertFalse(detector.analyze(frame).detected)

    def test_large_change_is_motion(self) -> None:
        detector = MotionDetector(min_area=500)
        baseline = np.zeros((240, 320, 3), dtype=np.uint8)
        changed = baseline.copy()
        changed[50:150, 80:220] = 255
        detector.analyze(baseline)
        result = detector.analyze(changed)
        self.assertTrue(result.detected)
        self.assertGreater(result.changed_area, 500)
        self.assertTrue(result.boxes)

    def test_small_change_is_ignored(self) -> None:
        detector = MotionDetector(min_area=2000)
        baseline = np.zeros((240, 320, 3), dtype=np.uint8)
        changed = baseline.copy()
        changed[10:15, 10:15] = 255
        detector.analyze(baseline)
        self.assertFalse(detector.analyze(changed).detected)


if __name__ == "__main__":
    unittest.main()
