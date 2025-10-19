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
    
    def __init__(self, width: int = 1200, height: int = 800):
        """
        Initialize Multi-Modal Creative Studio
        
        Args:
            width: Window width
            height: Window height
        """
        self.width = width
        self.height = height
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Multi-Modal Creative Studio")
        self.clock = pygame.time.Clock()
        
        # GUI Manager
        self.gui_manager = pygame_gui.UIManager((width, height))
        
        # Core components
        self.camera_analyzer = None
        self.audio_analyzer = None
        self.ai_processor = AIStyleProcessor()
        self.visual_engine = VisualEffectsEngine((width, height - 150))  # Leave space for controls
        
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
            relative_rect=pygame.Rect(10, panel_y, 100, 30),
            text='Camera: OFF',
            manager=self.gui_manager
        )
        
        self.audio_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(120, panel_y, 100, 30),
            text='Audio: OFF',
            manager=self.gui_manager
        )
        
        self.ai_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(230, panel_y, 100, 30),
            text='AI: Disconnected',
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
        
        # Try to connect to AI
        try:
            self.ai_connected = self.ai_processor.connect()
            if self.ai_connected:
                self.ai_button.set_text('AI: Connected')
                print("✅ AI processor connected")
            else:
                print("⚠️ AI processor not available (LM Studio not running?)")
        except Exception as e:
            print(f"❌ AI initialization failed: {e}")
        
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
                    elif event.ui_element == self.ai_button:
                        # Try to reconnect AI
                        self.ai_connected = self.ai_processor.connect()
                        self.ai_button.set_text('AI: Connected' if self.ai_connected else 'AI: Failed')
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