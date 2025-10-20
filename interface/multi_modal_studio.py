"""
Multi-Modal Creative Studio
Advanced interface supporting camera, audio, and AI integration
"""

import pygame
import pygame_gui
import sys
import os
import time
from typing import Dict, List, Optional, Any
import threading

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.vision import CameraAnalyzer
from core.audio import AudioAnalyzer
from core.ai import AIStyleProcessor
from core.effects import VisualEffectsEngine


class MultiModalStudio:
    """Main application interface for multi-modal creative visualization"""
    
    def __init__(self, width: int = 1400, height: int = 900):
        """
        Initialize Multi-Modal Creative Studio
        
        Args:
            width: Window width (increased for side panels)
            height: Window height (increased for better layout)
        """
        self.width = width
        self.height = height
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Multi-Modal Creative Studio v2.0")
        self.clock = pygame.time.Clock()
        
        # GUI Manager
        self.gui_manager = pygame_gui.UIManager((width, height))
        
        # Layout configuration
        self.main_area_width = width - 320  # Reserve 320px for side panels
        self.main_area_height = height - 150  # Reserve 150px for controls
        self.side_panel_width = 300
        
        # Core components
        self.camera_analyzer = None
        self.audio_analyzer = None
        # Allow environment overrides for AI URL/model
        lm_url = os.environ.get('LM_STUDIO_URL', 'http://localhost:1234')
        model_name = os.environ.get('AI_MODEL_NAME', 'gpt-oss-20b')
        self.ai_processor = AIStyleProcessor(lm_studio_url=lm_url, model_name=model_name)
        self.visual_engine = VisualEffectsEngine((self.main_area_width, self.main_area_height))
        
        # Display surfaces for real-time data
        self.camera_surface = None
        self.audio_surface = None
        self.camera_display_rect = pygame.Rect(width - 310, 10, 300, 225)  # Top right
        self.audio_display_rect = pygame.Rect(width - 310, 245, 300, 200)  # Below camera
        
        # Application state
        self.running = True
        self.camera_active = False
        self.audio_active = False
        self.ai_connected = False
        
        # Input handling
        self.text_input = ""
        self.text_input_active = False
        self.last_style_update = 0
        
        # Performance tracking
        self.fps = 60
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0
        
        # Setup UI
        self._setup_ui()
        
        # Initialize components
        self._initialize_components()
    
    def _setup_ui(self):
        """Setup user interface elements"""
        # Control panel area
        panel_y = self.height - 140
        
        # Mode buttons
        self.camera_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, panel_y, 120, 30),
            text='Camera: OFF',
            manager=self.gui_manager
        )
        
        self.audio_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(140, panel_y, 120, 30),
            text='Audio: OFF',
            manager=self.gui_manager
        )
        
        # Removed manual AI connect button; auto-connect on startup
        
        # Real-time display labels
        self.camera_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.width - 310, 460, 300, 25),
            text='📸 Real-time Camera Feed',
            manager=self.gui_manager
        )
        
        self.audio_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.width - 310, 690, 300, 25),
            text='🎵 Real-time Audio Analysis',
            manager=self.gui_manager
        )
        
        # Text input for AI commands
        self.text_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, panel_y + 40, 400, 30),
            manager=self.gui_manager,
            placeholder_text='Enter style description for AI processing...'
        )
        
        self.process_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(420, panel_y + 40, 80, 30),
            text='Apply Style',
            manager=self.gui_manager
        )
        
        # Reset button
        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(510, panel_y + 40, 60, 30),
            text='Reset',
            manager=self.gui_manager
        )
        
        # Status labels
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, panel_y + 80, 600, 25),
            text='Status: Ready',
            manager=self.gui_manager
        )
        
        # Performance info
        self.perf_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, panel_y + 105, 600, 25),
            text='FPS: 0 | Particles: 0',
            manager=self.gui_manager
        )
    
    def _initialize_components(self):
        """Initialize core components"""
        print("🚀 Initializing Multi-Modal Creative Studio...")
        
        # Auto-connect to AI silently on startup
        try:
            self.ai_connected = self.ai_processor.connect()
            if self.ai_connected:
                print("✅ AI processor connected")
            else:
                print("🤖 AI not available (LM Studio offline?) — using smart fallbacks")
        except Exception:
            self.ai_connected = False
        
        print("✅ Studio initialized successfully")
    
    def toggle_camera(self):
        """Toggle camera input"""
        if not self.camera_active:
            # Start camera
            self.camera_analyzer = CameraAnalyzer(
                camera_id=0,
                resolution=(640, 480),
                callback=self._handle_vision_data
            )
            
            if self.camera_analyzer.start():
                self.camera_active = True
                self.camera_button.set_text('Camera: ON')
                self.status_label.set_text('Status: Camera activated')
            else:
                self.camera_analyzer = None
                self.status_label.set_text('Status: Camera failed to start')
        else:
            # Stop camera
            if self.camera_analyzer:
                self.camera_analyzer.stop()
                self.camera_analyzer = None
            self.camera_active = False
            self.camera_button.set_text('Camera: OFF')
            self.status_label.set_text('Status: Camera deactivated')
    
    def toggle_audio(self):
        """Toggle audio input"""
        if not self.audio_active:
            # Start audio
            self.audio_analyzer = AudioAnalyzer(
                chunk_size=1024,
                callback=self._handle_audio_data
            )
            
            if self.audio_analyzer.start_recording():
                self.audio_active = True
                self.audio_button.set_text('Audio: ON')
                self.status_label.set_text('Status: Audio activated')
            else:
                self.audio_analyzer = None
                self.status_label.set_text('Status: Audio failed to start')
        else:
            # Stop audio
            if self.audio_analyzer:
                self.audio_analyzer.stop_recording()
                self.audio_analyzer = None
            self.audio_active = False
            self.audio_button.set_text('Audio: OFF')
            self.status_label.set_text('Status: Audio deactivated')
    
    def process_ai_input(self):
        """Process AI text input"""
        text = self.text_entry.get_text()
        if not text.strip():
            self.status_label.set_text('Status: Please enter text for AI processing')
            return
        
        try:
            # Get current context from active inputs
            context = {}
            
            if self.camera_active and self.camera_analyzer:
                vision_data = self.camera_analyzer.get_analysis_data()
                context.update(vision_data)
            
            if self.audio_active and self.audio_analyzer:
                audio_data = self.audio_analyzer.get_current_metrics()
                context.update(audio_data)
            
            # Process with AI
            style_config = self.ai_processor.process_text_input(text, context)
            
            # Apply to visual engine
            self.visual_engine.apply_style(style_config)
            
            self.status_label.set_text(f'Status: Applied style "{text}"')
            self.text_entry.set_text('')  # Clear input
            
        except Exception as e:
            self.status_label.set_text(f'Status: AI processing failed - {e}')
    
    def reset_effects(self):
        """Reset all visual effects"""
        self.visual_engine.particle_system.clear()
        self.visual_engine.apply_style({
            'colors': [(100, 100, 255), (150, 150, 255)],
            'motion': 'gentle',
            'intensity': 0.3,
            'particles': {'count': 50, 'size': 2, 'speed': 1.0, 'life': 3.0}
        })
        self.status_label.set_text('Status: Effects reset')
    
    def _handle_vision_data(self, vision_data: Dict):
        """Handle camera vision data"""
        # Extract motion centers for particle spawning
        motion_centers = []
        for center_data in vision_data.get('motion_centers', []):
            if len(center_data) >= 2:
                # Scale to screen coordinates
                x = int(center_data[0] * (self.width / 640))
                y = int(center_data[1] * ((self.height - 150) / 480))
                motion_centers.append((x, y))
        
        # Update visual engine with motion data
        self.visual_engine.update(
            dt=1.0/self.fps,
            motion_centers=motion_centers
        )
    
    def _handle_audio_data(self, audio_data: Dict):
        """Handle audio analysis data"""
        # Update visual engine with audio data
        self.visual_engine.update(
            dt=1.0/self.fps,
            audio_data=audio_data
        )
    
    def _handle_events(self):
        """Handle Pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle GUI events
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.camera_button:
                        self.toggle_camera()
                    elif event.ui_element == self.audio_button:
                        self.toggle_audio()
                    # Removed manual AI connect button
                    elif event.ui_element == self.process_button:
                        self.process_ai_input()
                    elif event.ui_element == self.reset_button:
                        self.reset_effects()
                
                elif event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self.text_entry:
                        self.process_ai_input()
            
            # Handle keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_c and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.toggle_camera()
                elif event.key == pygame.K_a and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.toggle_audio()
                elif event.key == pygame.K_RETURN and not self.text_entry.is_focused:
                    self.text_entry.focus()
            
            # Pass event to GUI manager
            self.gui_manager.process_events(event)
    
    def _render_real_time_displays(self):
        """Render real-time camera and audio displays"""
        import cv2
        import numpy as np
        
        # Camera display
        if self.camera_analyzer and self.camera_active:
            frame = self.camera_analyzer.get_current_frame()
            if frame is not None:
                # Resize frame to fit display area
                display_frame = cv2.resize(frame, (self.camera_display_rect.width, 
                                                  self.camera_display_rect.height - 25))
                
                # Convert BGR to RGB for pygame
                display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                
                # Create pygame surface
                camera_surface = pygame.surfarray.make_surface(display_frame.swapaxes(0, 1))
                
                # Draw camera feed
                self.screen.blit(camera_surface, (self.camera_display_rect.x, 
                                                self.camera_display_rect.y + 25))
                
                # Draw border
                pygame.draw.rect(self.screen, (100, 100, 100), 
                               (self.camera_display_rect.x, self.camera_display_rect.y + 25,
                                self.camera_display_rect.width, self.camera_display_rect.height - 25), 2)
        else:
            # Draw placeholder
            pygame.draw.rect(self.screen, (30, 30, 40), 
                           (self.camera_display_rect.x, self.camera_display_rect.y + 25,
                            self.camera_display_rect.width, self.camera_display_rect.height - 25))
            
            font = pygame.font.Font(None, 24)
            text = font.render("Camera Offline", True, (100, 100, 100))
            text_rect = text.get_rect(center=(self.camera_display_rect.centerx, 
                                             self.camera_display_rect.centery))
            self.screen.blit(text, text_rect)
        
        # Audio display
        if self.audio_analyzer and self.audio_active:
            self._render_audio_visualization()
        else:
            # Draw placeholder
            pygame.draw.rect(self.screen, (30, 30, 40), 
                           (self.audio_display_rect.x, self.audio_display_rect.y + 25,
                            self.audio_display_rect.width, self.audio_display_rect.height - 25))
            
            font = pygame.font.Font(None, 24)
            text = font.render("Audio Offline", True, (100, 100, 100))
            text_rect = text.get_rect(center=(self.audio_display_rect.centerx, 
                                             self.audio_display_rect.centery + 12))
            self.screen.blit(text, text_rect)
    
    def _render_audio_visualization(self):
        """Render beautiful audio visualization"""
        import numpy as np
        
        # Get audio data and metrics
        if not self.audio_analyzer:
            return
            
        metrics = self.audio_analyzer.get_current_metrics()
        audio_data = self.audio_analyzer.get_audio_data()
        
        # Audio display area
        display_x = self.audio_display_rect.x
        display_y = self.audio_display_rect.y + 25
        display_w = self.audio_display_rect.width
        display_h = self.audio_display_rect.height - 25
        
        # Clear area with dark background
        pygame.draw.rect(self.screen, (15, 15, 25), (display_x, display_y, display_w, display_h))
        
        # Draw waveform if we have recent audio data
        if len(audio_data) > 0:
            # audio_data is a list of numpy arrays; flatten safely
            try:
                buffers = audio_data[-4:]  # last few buffers
                flat = np.concatenate([np.asarray(b).astype(np.float32) for b in buffers])
                # Normalize
                max_abs = np.max(np.abs(flat)) if flat.size else 0.0
                if max_abs > 0:
                    data_normalized = flat / max_abs
                else:
                    data_normalized = flat
                # Use up to N points for drawing
                N = min(512, data_normalized.size)
                if N > 10:
                    segment = data_normalized[-N:]
                    center_y = display_y + display_h // 2
                    step = display_w / N
                    # Build points as number pairs (x, y)
                    points = [(display_x + i * step, center_y - float(sample) * (display_h // 3))
                              for i, sample in enumerate(segment)]
                    if len(points) > 1:
                        volume = metrics.get('amplitude', 0.0)
                        color_intensity = min(255, int(volume * 5000))
                        color = (
                            min(255, color_intensity + 50),
                            min(255, color_intensity // 2 + 100),
                            255 - color_intensity // 3
                        )
                        pygame.draw.lines(self.screen, color, False, points, 2)
            except Exception:
                # If anything goes wrong, just skip this frame's waveform
                pass
        
        # Draw frequency spectrum bars
        # Frequency spectrum bars (use concatenated recent samples)
        if len(audio_data) > 0:
            try:
                buffers = audio_data[-4:]
                flat = np.concatenate([np.asarray(b).astype(np.float32) for b in buffers])
                if flat.size >= 256:
                    segment = flat[-512:] if flat.size >= 512 else flat
                    # Windowed FFT
                    window = np.hanning(segment.size)
                    fft = np.fft.rfft(segment * window)
                    freqs = np.abs(fft)
                    if freqs.size > 1 and np.max(freqs) > 0:
                        freqs_norm = freqs / np.max(freqs)
                        draw_bins = min(64, freqs_norm.size)
                        bar_width = display_w / draw_bins
                        for i, freq_level in enumerate(freqs_norm[:draw_bins]):
                            bar_height = float(freq_level) * (display_h // 3)
                            bar_x = display_x + i * bar_width
                            bar_y = display_y + display_h - bar_height
                            hue = (i / draw_bins) * 360
                            color = self._hsv_to_rgb(hue, 0.8, float(freq_level) * 0.8 + 0.2)
                            pygame.draw.rect(self.screen, color,
                                             (bar_x, bar_y, max(1, bar_width - 1), bar_height))
            except Exception:
                pass
        
        # Draw audio level meter
        level = metrics.get('amplitude', 0.0) * 5000  # Scale for visibility
        level_width = int(min(display_w - 20, level * display_w))
        
        # Level bar background
        pygame.draw.rect(self.screen, (40, 40, 50), 
                       (display_x + 10, display_y + 10, display_w - 20, 8))
        
        # Level bar foreground
        if level_width > 0:
            level_color = (
                min(255, int(level * 500)),
                max(50, 255 - int(level * 300)),
                100
            )
            pygame.draw.rect(self.screen, level_color, 
                           (display_x + 10, display_y + 10, level_width, 8))
        
        # Beat indicator
        if metrics.get('beat_detected', False):
            pygame.draw.circle(self.screen, (255, 255, 100), 
                             (display_x + display_w - 30, display_y + 30), 8)
        else:
            pygame.draw.circle(self.screen, (80, 80, 80), 
                             (display_x + display_w - 30, display_y + 30), 8, 2)
        
        # Draw border
        pygame.draw.rect(self.screen, (100, 100, 100), 
                       (display_x, display_y, display_w, display_h), 2)
    
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h/360.0, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        current_time = time.time()
        self.frame_count += 1
        
        if current_time - self.last_fps_update > 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
            
            # Update performance label
            stats = self.visual_engine.get_stats()
            self.perf_label.set_text(
                f"FPS: {self.current_fps} | "
                f"Particles: {stats['particle_count']} | "
                f"Pattern: {stats['motion_pattern']} | "
                f"Intensity: {stats['intensity']:.2f}"
            )
    
    def run(self):
        """Main application loop"""
        print("🎮 Starting Multi-Modal Creative Studio...")
        
        try:
            while self.running:
                dt = self.clock.tick(self.fps) / 1000.0
                
                # Handle events
                self._handle_events()
                
                # Update visual effects (if no input data, use default update)
                if not self.camera_active and not self.audio_active:
                    self.visual_engine.update(dt)
                
                # Update GUI
                self.gui_manager.update(dt)
                
                # Render
                self.visual_engine.render(self.screen)
                
                # Render real-time camera and audio displays
                self._render_real_time_displays()
                
                # Render GUI on top
                self.gui_manager.draw_ui(self.screen)
                
                # Update display
                pygame.display.flip()
                
                # Update performance stats
                self._update_performance_stats()
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        except Exception as e:
            print(f"❌ Application error: {e}")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")
        
        # Stop camera
        if self.camera_analyzer:
            self.camera_analyzer.stop()
        
        # Stop audio
        if self.audio_analyzer:
            self.audio_analyzer.stop_recording()
        
        pygame.quit()
        print("✅ Cleanup complete")


def main():
    """Main entry point"""
    try:
        studio = MultiModalStudio(1200, 800)
        studio.run()
    except Exception as e:
        print(f"❌ Failed to start studio: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())