"""
Selfie segmentation wrapper using MediaPipe
Provides a small, safe API around MediaPipe SelfieSegmentation
"""

import cv2
import numpy as np

try:
    import mediapipe as mp
except Exception:
    mp = None


class SelfieSegmenter:
    """Wraps MediaPipe SelfieSegmentation for easy integration."""

    def __init__(self, model_selection: int = 1, segmentation_threshold: float = 0.1):
        if mp is None:
            raise RuntimeError("mediapipe is not installed. Install with 'pip install mediapipe' or use the requirements-ml.txt")
        self._mp = mp
        self.seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=model_selection)
        self.threshold = segmentation_threshold

    def apply(self, frame: np.ndarray, background, threshold: float = None) -> np.ndarray:
        """
        Apply segmentation to a BGR frame and composite it over the provided background.

        frame: HxWx3 BGR uint8
        background: color tuple (B,G,R) or HxWx3 array
        returns: composited BGR frame
        """
        if threshold is None:
            threshold = self.threshold

        h, w = frame.shape[:2]

        # Prepare background
        if isinstance(background, (tuple, list)):
            bg = np.full((h, w, 3), background, dtype=np.uint8)
        else:
            try:
                bg = cv2.resize(background, (w, h)) if background.shape[:2] != (h, w) else background
            except Exception:
                bg = np.full((h, w, 3), (0, 128, 255), dtype=np.uint8)

        # Convert to RGB for mediapipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.seg.process(rgb)

        if results is None or results.segmentation_mask is None:
            return frame

        mask = results.segmentation_mask
        condition = np.stack((mask,) * 3, axis=-1) > threshold
        out = np.where(condition, frame, bg)
        return out

    def close(self):
        try:
            self.seg.close()
        except Exception:
            pass
