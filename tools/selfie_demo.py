"""
Simple demo to run selfie segmentation from the project camera
Falls back to an informative message if mediapipe is not installed
"""

import sys
import os
import cv2
import numpy as np
import time

# Ensure repo root is on sys.path so imports like `core` work when running this script directly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.vision.selfie_segmentation import SelfieSegmenter

def setup_camera_fallback(camera_index=0):
    """Simple fallback to openCV VideoCapture if no camera_utils module is available."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {camera_index}")
    return cap, camera_index


def main():
    print("Selfie segmentation demo")
    try:
        # prefer a project-specific camera_utils.setup_camera if present
        try:
            from camera_utils import setup_camera
            cap, cam_id = setup_camera()
        except Exception:
            cap, cam_id = setup_camera_fallback()
    except Exception as e:
        print(f"Failed to open camera: {e}")
        return

    try:
        seg = SelfieSegmenter()
    except RuntimeError as e:
        print(e)
        print("Install mediapipe in the venv or use requirements-ml.txt")
        cap.release()
        return

    backgrounds = {
        'blue': (255, 0, 0),
        'green': (0, 255, 0),
        'checker': None
    }
    bg_keys = list(backgrounds.keys())
    idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        if bg_keys[idx] == 'checker':
            bg_img = np.zeros(frame.shape, dtype=np.uint8)
            # make checker
            for i in range(0, frame.shape[0], 40):
                for j in range(0, frame.shape[1], 40):
                    c = (255,255,255) if ((i//40 + j//40) % 2 == 0) else (0,0,0)
                    bg_img[i:i+40, j:j+40] = c
            out = seg.apply(frame, bg_img)
        else:
            out = seg.apply(frame, backgrounds[bg_keys[idx]])

        cv2.imshow('Selfie Demo', out)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        if k == ord('b'):
            idx = (idx + 1) % len(bg_keys)

    seg.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
