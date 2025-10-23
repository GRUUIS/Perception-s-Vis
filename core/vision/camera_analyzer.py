"""
Camera Vision Analysis Module
Real-time camera processing for visual effects generation
"""

import cv2
import numpy as np
import threading
import time
from typing import Dict, List, Tuple, Optional, Callable


class CameraAnalyzer:
    """Advanced camera analysis for multi-modal visual effects"""
    
    def __init__(self, 
                 camera_id: int = 0,
                 resolution: Tuple[int, int] = (640, 480),
                 fps: int = 30,
                 callback: Optional[Callable] = None,
                 enable_segmentation: bool = False,
                 segmentation_background=None):
        """
        Initialize camera analyzer
        
        Args:
            camera_id: Camera device ID
            resolution: Camera resolution (width, height)
            fps: Target frames per second
            callback: Callback function for processed data
        """
        self.camera_id = camera_id
        self.resolution = resolution
        self.fps = fps
        self.callback = callback
        
        # Camera setup
        self.cap = None
        self.is_active = False
        
        # Analysis components
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True, varThreshold=50
        )
        
        # Analysis data
        self.current_frame = None
        self.motion_intensity = 0.0
        self.dominant_colors = []
        self.motion_centers = []
        self.visual_energy = 0.0
        
        # Processing threads
        self.capture_thread = None
        self.analysis_thread = None
        self.running = False

        # Optional selfie segmentation
        self.enable_segmentation = enable_segmentation
        self.segmentation_background = segmentation_background
        self.segmenter = None
        if self.enable_segmentation:
            try:
                from core.vision.selfie_segmentation import SelfieSegmenter
                self.segmenter = SelfieSegmenter()
                print("🪄 Selfie segmentation enabled")
            except Exception as e:
                print(f"⚠️ Selfie segmentation unavailable: {e}")
                self.segmenter = None
                self.enable_segmentation = False
        
    def start(self) -> bool:
        """Start camera capture and analysis"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                raise Exception(f"Cannot access camera {self.camera_id}")
            
            # Configure camera
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.is_active = True
            self.running = True
            
            # Start processing threads
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
            
            self.capture_thread.start()
            self.analysis_thread.start()
            
            print("🎥 Camera analyzer started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            return False
    
    def stop(self):
        """Stop camera capture and analysis"""
        self.running = False
        self.is_active = False
        
        # Wait for threads to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=1.0)
        
        # Release camera
        if self.cap:
            self.cap.release()
            
        print("🎥 Camera analyzer stopped")
    
    def _capture_loop(self):
        """Continuous frame capture loop"""
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Mirror effect for natural interaction
                self.current_frame = cv2.flip(frame, 1)
            time.sleep(1.0 / self.fps)
    
    def _analysis_loop(self):
        """Continuous analysis loop"""
        while self.running:
            if self.current_frame is not None:
                try:
                    self._analyze_motion()
                    self._analyze_colors()
                    self._calculate_energy()
                    
                    # Send data to callback
                    if self.callback:
                        data = self.get_analysis_data()
                        self.callback(data)
                        
                except Exception as e:
                    print(f"Analysis error: {e}")
            
            time.sleep(1.0 / 30)  # 30 FPS analysis
    
    def _analyze_motion(self):
        """Analyze motion in current frame"""
        if self.current_frame is None:
            return
        
        # Background subtraction for motion detection
        motion_mask = self.background_subtractor.apply(self.current_frame)
        
        # Calculate motion intensity
        motion_pixels = np.sum(motion_mask > 0)
        total_pixels = motion_mask.shape[0] * motion_mask.shape[1]
        self.motion_intensity = motion_pixels / total_pixels
        
        # Find motion centers
        contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        self.motion_centers = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 200:  # Filter noise
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    self.motion_centers.append((cx, cy, area))
    
    def _analyze_colors(self):
        """Extract dominant colors from frame"""
        if self.current_frame is None:
            return
        
        # Convert to RGB for color analysis
        rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        
        # Reshape for k-means
        data = rgb_frame.reshape((-1, 3))
        data = np.float32(data)
        
        try:
            # K-means clustering for dominant colors
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            k = 5
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Calculate color weights
            unique_labels, counts = np.unique(labels, return_counts=True)
            total_pixels = len(labels)
            
            self.dominant_colors = []
            for i, center in enumerate(centers):
                if i in unique_labels:
                    weight = counts[np.where(unique_labels == i)[0][0]] / total_pixels
                    color = tuple(map(int, center))
                    self.dominant_colors.append({
                        'color': color,
                        'weight': weight
                    })
            
            # Sort by weight
            self.dominant_colors.sort(key=lambda x: x['weight'], reverse=True)
            
        except Exception:
            # Fallback to average color
            mean_color = np.mean(rgb_frame.reshape((-1, 3)), axis=0)
            self.dominant_colors = [{
                'color': tuple(map(int, mean_color)),
                'weight': 1.0
            }]
    
    def _calculate_energy(self):
        """Calculate overall visual energy"""
        motion_component = self.motion_intensity
        color_diversity = len(self.dominant_colors) / 5.0
        movement_count = len(self.motion_centers) / 10.0
        
        self.visual_energy = (
            motion_component * 0.5 + 
            color_diversity * 0.3 + 
            movement_count * 0.2
        )
    
    def get_analysis_data(self) -> Dict:
        """Get current analysis results"""
        return {
            'motion_intensity': self.motion_intensity,
            'visual_energy': self.visual_energy,
            'dominant_colors': self.dominant_colors,
            'motion_centers': self.motion_centers,
            'frame_available': self.current_frame is not None,
            'timestamp': time.time()
        }
    
    def get_current_frame(self):
        """Get current camera frame"""
        return self.current_frame.copy() if self.current_frame is not None else None
    
    def is_motion_detected(self, threshold: float = 0.01) -> bool:
        """Check if significant motion is detected"""
        return self.motion_intensity > threshold
    
    def get_primary_color(self) -> Tuple[int, int, int]:
        """Get most dominant color"""
        if self.dominant_colors:
            return self.dominant_colors[0]['color']
        return (255, 255, 255)
    
    def start_visual_mode(self, effects_engine=None):
        """Start camera-only visual mode with basic display"""
        import pygame
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Camera Vision Mode")
        clock = pygame.time.Clock()
        
        # Start camera
        if not self.start():
            print("❌ Failed to start camera")
            return
        
        print("📸 Camera active - Press 'Q' or ESC to quit")
        running = True
        
        # Initialize visual effects background surface if segmentation enabled
        effects_surface = None
        if self.enable_segmentation and effects_engine:
            effects_surface = pygame.Surface((640, 480))
            effects_surface.fill((0, 20, 40))  # Dark blue base
        
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_q, pygame.K_ESCAPE):
                            running = False
                
                # Clear screen
                screen.fill((0, 0, 0))
                
                # Update visual effects for segmentation background
                if self.enable_segmentation and effects_engine and effects_surface:
                    try:
                        # Get current analysis data to drive effects
                        analysis_data = self.get_analysis_data()
                        
                        # Update effects engine with motion data using correct signature
                        if effects_engine:
                            # Convert motion centers from (x, y, area) to (x, y) format
                            motion_centers = [(center[0], center[1]) for center in analysis_data.get('motion_centers', [])]
                            
                            effects_engine.update(
                                dt=1.0/30.0,  # 30 FPS delta time
                                motion_centers=motion_centers,
                                audio_data={
                                    'amplitude': analysis_data.get('visual_energy', 0.0) * 1000,
                                    'beat_detected': analysis_data.get('motion_intensity', 0.0) > 0.05
                                }
                            )
                            
                            # Render effects to background surface
                            effects_surface.fill((0, 20, 40))  # Clear with dark base
                            effects_engine.render(effects_surface)
                    except Exception as e:
                        print(f"Effects update error: {e}")
                
                # Get camera frame
                frame = self.get_current_frame()
                if frame is not None:
                    # Optionally apply segmentation with visual effects background
                    display_frame = frame
                    if self.enable_segmentation and self.segmenter is not None and effects_surface:
                        try:
                            # Convert pygame surface to OpenCV format for segmentation
                            bg_array = pygame.surfarray.array3d(effects_surface)
                            bg_bgr = cv2.cvtColor(bg_array.swapaxes(0, 1), cv2.COLOR_RGB2BGR)
                            display_frame = self.segmenter.apply(frame, bg_bgr)
                        except Exception as e:
                            print(f"Segmentation error: {e}")
                            display_frame = frame

                    # Convert OpenCV frame to pygame surface
                    frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    frame_resized = cv2.resize(frame_rgb, (640, 480))
                    frame_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))
                    screen.blit(frame_surface, (80, 60))
                    
                    # Display analysis data
                    font = pygame.font.Font(None, 24)
                    data = self.get_analysis_data()
                    
                    y_offset = 20
                    for key, value in data.items():
                        if isinstance(value, float):
                            text = f"{key}: {value:.3f}"
                        else:
                            text = f"{key}: {value}"
                        text_surface = font.render(text, True, (255, 255, 255))
                        screen.blit(text_surface, (10, y_offset))
                        y_offset += 25
                
                pygame.display.flip()
                clock.tick(30)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            pygame.quit()
            print("📸 Camera mode stopped")