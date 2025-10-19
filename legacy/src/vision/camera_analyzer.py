"""
Vision Analysis Module
Real-time camera capture and computer vision analysis
"""

import cv2
import numpy as np
import threading
import time
from typing import Dict, List, Tuple, Optional, Callable


class VisionAnalyzer:
    """Real-time camera analyzer for visual effects generation"""
    
    def __init__(self, 
                 camera_id: int = 0,
                 resolution: Tuple[int, int] = (640, 480),
                 fps: int = 30,
                 callback: Optional[Callable] = None):
        """
        Initialize the Vision Analyzer
        
        Args:
            camera_id: Camera device ID (usually 0 for default camera)
            resolution: Camera resolution (width, height)
            fps: Target frames per second
            callback: Callback function to receive vision data
        """
        self.camera_id = camera_id
        self.resolution = resolution
        self.fps = fps
        self.callback = callback
        
        # Camera capture
        self.cap = None
        self.is_recording = False
        
        # Analysis components
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True, varThreshold=50
        )
        
        # Vision data storage
        self.current_frame = None
        self.motion_intensity = 0.0
        self.dominant_colors = []
        self.visual_energy = 0.0
        self.motion_areas = []
        
        # Analysis history for smoothing
        self.motion_history = []
        self.color_history = []
        self.max_history = 10
        
        # Threading
        self.capture_thread = None
        self.analysis_thread = None
        self.running = False
        
    def start_capture(self):
        """Start camera capture and analysis"""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                raise Exception(f"Cannot open camera {self.camera_id}")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.is_recording = True
            self.running = True
            
            # Start capture thread
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            # Start analysis thread
            self.analysis_thread = threading.Thread(target=self._analysis_loop)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            
            print("🎥 Camera capture started!")
            return True
            
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return False
    
    def stop_capture(self):
        """Stop camera capture"""
        self.running = False
        self.is_recording = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=1.0)
        
        if self.cap:
            self.cap.release()
            
        print("🎥 Camera capture stopped")
    
    def _capture_loop(self):
        """Camera capture loop (runs in separate thread)"""
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Flip frame horizontally for mirror effect
                self.current_frame = cv2.flip(frame, 1)
            
            time.sleep(1.0 / self.fps)
    
    def _analysis_loop(self):
        """Vision analysis loop (runs in separate thread)"""
        while self.running:
            if self.current_frame is not None:
                try:
                    # Perform analysis
                    self._analyze_motion()
                    self._analyze_colors()
                    self._calculate_visual_energy()
                    
                    # Call callback with metrics
                    if self.callback:
                        metrics = self.get_vision_metrics()
                        self.callback(metrics)
                        
                except Exception as e:
                    print(f"Vision analysis error: {e}")
            
            time.sleep(1.0 / 30)  # Analysis at 30 FPS
    
    def _analyze_motion(self):
        """Analyze motion in the current frame"""
        if self.current_frame is None:
            return
        
        # Create motion mask using background subtraction
        motion_mask = self.background_subtractor.apply(self.current_frame)
        
        # Calculate motion intensity (percentage of frame with motion)
        motion_pixels = np.sum(motion_mask > 0)
        total_pixels = motion_mask.shape[0] * motion_mask.shape[1]
        self.motion_intensity = motion_pixels / total_pixels
        
        # Find motion contours for particle generation
        contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        self.motion_areas = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                self.motion_areas.append({
                    'center': (center_x, center_y),
                    'area': area,
                    'bounds': (x, y, w, h)
                })
        
        # Update motion history for smoothing
        self.motion_history.append(self.motion_intensity)
        if len(self.motion_history) > self.max_history:
            self.motion_history.pop(0)
    
    def _analyze_colors(self):
        """Analyze dominant colors in the current frame"""
        if self.current_frame is None:
            return
        
        # Convert to HSV for better color analysis
        hsv_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2HSV)
        
        # Reshape for K-means clustering
        data = hsv_frame.reshape((-1, 3))
        data = np.float32(data)
        
        # Use K-means to find 5 dominant colors
        try:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            k = 5
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert back to RGB
            centers = np.uint8(centers)
            dominant_colors_hsv = centers.reshape((k, 1, 3))
            dominant_colors_rgb = cv2.cvtColor(dominant_colors_hsv, cv2.COLOR_HSV2RGB)
            
            # Calculate color weights (how much of the image each color represents)
            unique_labels, counts = np.unique(labels, return_counts=True)
            total_pixels = len(labels)
            
            self.dominant_colors = []
            for i, center in enumerate(dominant_colors_rgb.reshape((k, 3))):
                if i in unique_labels:
                    weight = counts[np.where(unique_labels == i)[0][0]] / total_pixels
                    self.dominant_colors.append({
                        'color': tuple(map(int, center)),
                        'weight': weight
                    })
            
            # Sort by weight
            self.dominant_colors.sort(key=lambda x: x['weight'], reverse=True)
            
        except Exception as e:
            # Fallback: use average color
            mean_color = np.mean(self.current_frame.reshape((-1, 3)), axis=0)
            self.dominant_colors = [{
                'color': tuple(map(int, mean_color[::-1])),  # BGR to RGB
                'weight': 1.0
            }]
        
        # Update color history
        if self.dominant_colors:
            self.color_history.append(self.dominant_colors[0]['color'])
            if len(self.color_history) > self.max_history:
                self.color_history.pop(0)
    
    def _calculate_visual_energy(self):
        """Calculate overall visual energy level"""
        # Combine motion intensity and color diversity
        motion_component = np.mean(self.motion_history) if self.motion_history else 0
        color_component = len(self.dominant_colors) / 5.0  # Normalize to 0-1
        
        self.visual_energy = (motion_component * 0.7 + color_component * 0.3)
    
    def get_vision_metrics(self) -> Dict:
        """Get current vision analysis metrics"""
        return {
            'motion_intensity': self.motion_intensity,
            'visual_energy': self.visual_energy,
            'dominant_colors': self.dominant_colors,
            'motion_areas': self.motion_areas,
            'frame_shape': self.current_frame.shape if self.current_frame is not None else None,
            'smoothed_motion': np.mean(self.motion_history) if self.motion_history else 0
        }
    
    def get_current_frame(self):
        """Get the current camera frame"""
        return self.current_frame.copy() if self.current_frame is not None else None
    
    def is_motion_detected(self, threshold: float = 0.01) -> bool:
        """Check if motion is detected above threshold"""
        return self.motion_intensity > threshold
    
    def get_motion_centers(self) -> List[Tuple[int, int]]:
        """Get centers of motion areas for particle spawning"""
        return [area['center'] for area in self.motion_areas]
    
    def get_primary_color(self) -> Tuple[int, int, int]:
        """Get the most dominant color in current frame"""
        if self.dominant_colors:
            return self.dominant_colors[0]['color']
        return (255, 255, 255)  # Default white