"""
Single Mode Interface
Real-time audio visualization interface for individual users
"""

import pygame
import pygame_gui
import sys
import threading
import time
from typing import Dict, Optional, Any
from ..audio import AudioAnalyzer
from ..visualization import VisualizationEngine, ColorPalette
from ..storage import DataStorage


class SingleModeInterface:
    """Single user real-time audio visualization interface"""
    
    def __init__(self, width: int = 1400, height: int = 900, data_dir: str = "data"):
        """
        Initialize single mode interface
        
        Args:
            width: Window width
            height: Window height
            data_dir: Directory for data storage
        """
        pygame.init()
        
        self.width = width
        self.height = height
        
        # Create main window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Audio Perception - Single Mode")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # UI Manager
        self.ui_manager = pygame_gui.UIManager((width, height))
        
        # Components
        self.audio_analyzer = None
        self.visualization_engine = VisualizationEngine(width - 300, height - 50)
        self.data_storage = DataStorage(data_dir)
        
        # State
        self.is_recording = False
        self.is_playing_back = False
        self.current_user = "Anonymous"
        self.current_title = ""
        
        # UI Elements
        self.ui_elements = {}
        self.setup_ui()
        
        # Recording
        self.recording_session_active = False
        
    def setup_ui(self):
        """Setup the user interface elements"""
        panel_x = self.width - 290
        
        # Control Panel Background
        self.ui_elements['control_panel'] = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, 10, 280, self.height - 20),
            starting_layer_height=0,
            manager=self.ui_manager
        )
        
        y_pos = 30
        
        # User Info
        self.ui_elements['user_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 25),
            text='User Name:',
            manager=self.ui_manager
        )
        
        y_pos += 30
        self.ui_elements['user_input'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 25),
            manager=self.ui_manager
        )
        self.ui_elements['user_input'].set_text("Anonymous")
        
        y_pos += 40
        self.ui_elements['title_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 25),
            text='Recording Title:',
            manager=self.ui_manager
        )
        
        y_pos += 30
        self.ui_elements['title_input'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 25),
            manager=self.ui_manager
        )
        
        # Recording Controls
        y_pos += 50
        self.ui_elements['start_recording'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 120, 35),
            text='Start Recording',
            manager=self.ui_manager
        )
        
        self.ui_elements['stop_recording'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x + 140, y_pos, 120, 35),
            text='Stop Recording',
            manager=self.ui_manager
        )
        self.ui_elements['stop_recording'].disable()
        
        # Audio Controls
        y_pos += 50
        self.ui_elements['start_audio'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 120, 35),
            text='Start Audio',
            manager=self.ui_manager
        )
        
        self.ui_elements['stop_audio'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x + 140, y_pos, 120, 35),
            text='Stop Audio',
            manager=self.ui_manager
        )
        self.ui_elements['stop_audio'].disable()
        
        # Visualization Settings
        y_pos += 60
        self.ui_elements['settings_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 25),
            text='Visualization Settings:',
            manager=self.ui_manager
        )
        
        # Color Palette
        y_pos += 35
        self.ui_elements['palette_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 100, 25),
            text='Palette:',
            manager=self.ui_manager
        )
        
        self.ui_elements['palette_dropdown'] = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(panel_x + 120, y_pos, 150, 25),
            options_list=list(ColorPalette.PALETTES.keys()),
            starting_option='rainbow',
            manager=self.ui_manager
        )
        
        # Element Count
        y_pos += 35
        self.ui_elements['elements_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 100, 25),
            text='Elements:',
            manager=self.ui_manager
        )
        
        self.ui_elements['elements_slider'] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x + 120, y_pos, 150, 25),
            start_value=50,
            value_range=(10, 200),
            manager=self.ui_manager
        )
        
        # Size Multiplier
        y_pos += 35
        self.ui_elements['size_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 100, 25),
            text='Size:',
            manager=self.ui_manager
        )
        
        self.ui_elements['size_slider'] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x + 120, y_pos, 150, 25),
            start_value=1.0,
            value_range=(0.1, 3.0),
            manager=self.ui_manager
        )
        
        # Speed Multiplier
        y_pos += 35
        self.ui_elements['speed_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 100, 25),
            text='Speed:',
            manager=self.ui_manager
        )
        
        self.ui_elements['speed_slider'] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x + 120, y_pos, 150, 25),
            start_value=1.0,
            value_range=(0.1, 3.0),
            manager=self.ui_manager
        )
        
        # Visual Effects Toggles
        y_pos += 50
        self.ui_elements['effects_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 25),
            text='Visual Effects:',
            manager=self.ui_manager
        )
        
        y_pos += 30
        self.ui_elements['particles_check'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 80, 25),
            text='Particles',
            manager=self.ui_manager
        )
        
        self.ui_elements['wave_check'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x + 100, y_pos, 80, 25),
            text='Wave',
            manager=self.ui_manager
        )
        
        self.ui_elements['symmetry_check'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x + 190, y_pos, 80, 25),
            text='Symmetry',
            manager=self.ui_manager
        )
        
        # Audio Metrics Display
        y_pos += 60
        self.ui_elements['metrics_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 25),
            text='Audio Metrics:',
            manager=self.ui_manager
        )
        
        y_pos += 30
        self.ui_elements['amplitude_display'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 20),
            text='Amplitude: 0.00',
            manager=self.ui_manager
        )
        
        y_pos += 25
        self.ui_elements['rms_display'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 20),
            text='RMS: 0.00',
            manager=self.ui_manager
        )
        
        y_pos += 25
        self.ui_elements['peak_display'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 20),
            text='Peak: 0.00',
            manager=self.ui_manager
        )
        
        y_pos += 25
        self.ui_elements['db_display'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 20),
            text='dB: -60.0',
            manager=self.ui_manager
        )
        
        y_pos += 25
        self.ui_elements['freq_display'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x + 10, y_pos, 260, 20),
            text='Frequency: 0 Hz',
            manager=self.ui_manager
        )
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Handle UI events
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    self.handle_button_press(event.ui_element)
                elif event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    self.handle_dropdown_change(event.ui_element)
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    self.handle_slider_change(event.ui_element)
                    
            self.ui_manager.process_events(event)
            
    def handle_button_press(self, button):
        """Handle button press events"""
        if button == self.ui_elements['start_audio']:
            self.start_audio()
        elif button == self.ui_elements['stop_audio']:
            self.stop_audio()
        elif button == self.ui_elements['start_recording']:
            self.start_recording()
        elif button == self.ui_elements['stop_recording']:
            self.stop_recording()
        elif button == self.ui_elements['particles_check']:
            self.toggle_particles()
        elif button == self.ui_elements['wave_check']:
            self.toggle_wave()
        elif button == self.ui_elements['symmetry_check']:
            self.toggle_symmetry()
            
    def handle_dropdown_change(self, dropdown):
        """Handle dropdown change events"""
        if dropdown == self.ui_elements['palette_dropdown']:
            palette = dropdown.selected_option
            self.visualization_engine.update_settings({'palette': palette})
            
    def handle_slider_change(self, slider):
        """Handle slider change events"""
        if slider == self.ui_elements['elements_slider']:
            count = int(slider.get_current_value())
            self.visualization_engine.update_settings({'base_element_count': count})
        elif slider == self.ui_elements['size_slider']:
            size = slider.get_current_value()
            self.visualization_engine.update_settings({'size_multiplier': size})
        elif slider == self.ui_elements['speed_slider']:
            speed = slider.get_current_value()
            self.visualization_engine.update_settings({'speed_multiplier': speed})
            
    def start_audio(self):
        """Start audio capture"""
        try:
            self.audio_analyzer = AudioAnalyzer(callback=self.audio_callback)
            self.audio_analyzer.start_recording()
            
            self.ui_elements['start_audio'].disable()
            self.ui_elements['stop_audio'].enable()
            
            print("Audio capture started")
            
        except Exception as e:
            print(f"Error starting audio: {e}")
            
    def stop_audio(self):
        """Stop audio capture"""
        if self.audio_analyzer:
            self.audio_analyzer.stop_recording()
            self.audio_analyzer = None
            
        self.ui_elements['start_audio'].enable()
        self.ui_elements['stop_audio'].disable()
        
        print("Audio capture stopped")
        
    def start_recording(self):
        """Start recording session"""
        user_name = self.ui_elements['user_input'].get_text() or "Anonymous"
        title = self.ui_elements['title_input'].get_text() or ""
        
        self.data_storage.start_recording_session(user_name, title)
        self.recording_session_active = True
        
        self.ui_elements['start_recording'].disable()
        self.ui_elements['stop_recording'].enable()
        
        print("Recording session started")
        
    def stop_recording(self):
        """Stop recording session"""
        if self.recording_session_active:
            settings = self.visualization_engine.get_settings()
            record_id = self.data_storage.stop_recording_session(
                visualization_settings=settings,
                tags=[]
            )
            
            if record_id:
                print(f"Recording saved with ID: {record_id}")
            else:
                print("Failed to save recording")
                
        self.recording_session_active = False
        
        self.ui_elements['start_recording'].enable()
        self.ui_elements['stop_recording'].disable()
        
    def toggle_particles(self):
        """Toggle particle effects"""
        current = self.visualization_engine.settings.get('particle_mode', True)
        self.visualization_engine.update_settings({'particle_mode': not current})
        
    def toggle_wave(self):
        """Toggle wave mode"""
        current = self.visualization_engine.settings.get('wave_mode', False)
        self.visualization_engine.update_settings({'wave_mode': not current})
        
    def toggle_symmetry(self):
        """Toggle symmetry mode"""
        current = self.visualization_engine.settings.get('symmetry_mode', False)
        self.visualization_engine.update_settings({'symmetry_mode': not current})
        
    def audio_callback(self, metrics: Dict[str, float]):
        """
        Callback function for audio data
        
        Args:
            metrics: Audio metrics from analyzer
        """
        # Update visualization
        normalized_metrics = self.audio_analyzer.get_normalized_metrics()
        self.visualization_engine.update_from_audio(normalized_metrics)
        
        # Update UI displays
        self.update_metrics_display(metrics)
        
        # Add to recording if active
        if self.recording_session_active and self.audio_analyzer:
            audio_data = self.audio_analyzer.get_audio_data()
            if audio_data:
                latest_chunk = audio_data[-1]
                self.data_storage.add_audio_data(latest_chunk, metrics)
                
    def update_metrics_display(self, metrics: Dict[str, float]):
        """Update the audio metrics display"""
        self.ui_elements['amplitude_display'].set_text(
            f"Amplitude: {metrics.get('amplitude', 0):.2f}"
        )
        self.ui_elements['rms_display'].set_text(
            f"RMS: {metrics.get('rms', 0):.2f}"
        )
        self.ui_elements['peak_display'].set_text(
            f"Peak: {metrics.get('peak', 0):.2f}"
        )
        self.ui_elements['db_display'].set_text(
            f"dB: {metrics.get('db', -60):.1f}"
        )
        self.ui_elements['freq_display'].set_text(
            f"Frequency: {metrics.get('frequency', 0):.0f} Hz"
        )
        
    def run(self):
        """Main application loop"""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update UI
            self.ui_manager.update(time_delta)
            
            # Clear screen
            self.screen.fill((20, 20, 20))
            
            # Render visualization
            vis_surface = pygame.Surface((self.width - 300, self.height))
            self.visualization_engine.render(vis_surface)
            self.screen.blit(vis_surface, (0, 0))
            
            # Add visual frame to recording if active
            if self.recording_session_active:
                self.data_storage.add_visual_frame(vis_surface)
            
            # Render UI
            self.ui_manager.draw_ui(self.screen)
            
            # Update display
            pygame.display.flip()
            
        # Cleanup
        self.cleanup()
        
    def cleanup(self):
        """Cleanup resources"""
        if self.audio_analyzer:
            self.audio_analyzer.stop_recording()
            
        if self.recording_session_active:
            self.stop_recording()
            
        self.visualization_engine.cleanup()
        pygame.quit()


if __name__ == "__main__":
    app = SingleModeInterface()
    app.run()
