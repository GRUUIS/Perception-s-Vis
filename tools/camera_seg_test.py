"""
Quick smoke test to start CameraAnalyzer in visual mode with segmentation enabled for 8 seconds
"""
import sys
import os

# Ensure repo root is on sys.path so imports like `core` work when running this script directly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.vision.camera_analyzer import CameraAnalyzer

def main():
    cam = CameraAnalyzer(enable_segmentation=True)
    try:
        cam.start_visual_mode()
    except Exception as e:
        print(f"Error running visual mode: {e}")

if __name__ == '__main__':
    main()
