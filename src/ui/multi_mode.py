"""
Multiple Mode Interface
Gallery view for all saved visualizations from all users
"""

import pygame
import pygame_gui
import sys
import threading
import time
import os
from typing import Dict, List, Optional, Any, Tuple
from ..storage import DataStorage, AudioRecord
from ..visualization import VisualizationEngine, RealtimeAudioVisualizer
from ..audio import AudioAnalyzer


class MultiModeInterface:
    """Multiple user gallery interface for viewing all visualizations"""
    
    def __init__(self, width: int = 1600, height: int = 1000, data_dir: str = "data"):
        """
        Initialize multiple mode interface
        
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
        pygame.display.set_caption("Audio Perception - Gallery Mode")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # UI Manager
        self.ui_manager = pygame_gui.UIManager((width, height))
        
        # Components
        self.data_storage = DataStorage(data_dir)
        self.visualization_engine = None
        
        # State
        self.recordings: List[AudioRecord] = []
        self.selected_recording: Optional[AudioRecord] = None
        self.current_playback_data: Optional[Tuple[AudioRecord, List]] = None
        self.playback_index = 0
        self.is_playing = False
        self.playback_speed = 1.0
        
        # UI Elements
        self.ui_elements = {}
        self.recording_buttons = []
        self.setup_ui()
        
        # Load recordings
        self.refresh_recordings()
        
    def setup_ui(self):
        """Setup the user interface elements"""
        # Left Panel for Recording List
        list_width = 350
        self.ui_elements['list_panel'] = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, 10, list_width, self.height - 20),
            manager=self.ui_manager
        )
        
        # Title
        self.ui_elements['title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 20, list_width - 20, 30),
            text='Audio Perception Gallery',
            manager=self.ui_manager
        )
        
        # Statistics
        self.ui_elements['stats'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 60, list_width - 20, 40),
            text='Loading statistics...',
            manager=self.ui_manager
        )
        
        # Refresh Button
        self.ui_elements['refresh_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 110, 100, 30),
            text='Refresh',
            manager=self.ui_manager
        )
        
        # Delete Button
        self.ui_elements['delete_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(130, 110, 100, 30),
            text='Delete',
            manager=self.ui_manager
        )
        self.ui_elements['delete_btn'].disable()
        
        # Recordings List (Scrollable)
        self.ui_elements['recordings_list'] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(20, 150, list_width - 20, self.height - 200),
            manager=self.ui_manager
        )
        
        # Right Panel for Visualization and Controls
        viz_x = list_width + 30
        viz_width = self.width - viz_x - 300
        
        self.ui_elements['viz_panel'] = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(viz_x, 10, viz_width, self.height - 120),
            starting_layer_height=0,
            manager=self.ui_manager
        )
        
        # Control Panel
        control_y = self.height - 100
        self.ui_elements['control_panel'] = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(viz_x, control_y, viz_width, 90),
            starting_layer_height=0,
            manager=self.ui_manager
        )
        
        # Playback Controls
        self.ui_elements['play_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(viz_x + 10, control_y + 10, 80, 30),
            text='Play',
            manager=self.ui_manager
        )
        self.ui_elements['play_btn'].disable()
        
        self.ui_elements['pause_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(viz_x + 100, control_y + 10, 80, 30),
            text='Pause',
            manager=self.ui_manager
        )
        self.ui_elements['pause_btn'].disable()
        
        self.ui_elements['stop_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(viz_x + 190, control_y + 10, 80, 30),
            text='Stop',
            manager=self.ui_manager
        )
        self.ui_elements['stop_btn'].disable()
        
        # Speed Control
        self.ui_elements['speed_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(viz_x + 290, control_y + 10, 50, 30),
            text='Speed:',
            manager=self.ui_manager
        )
        
        self.ui_elements['speed_slider'] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(viz_x + 350, control_y + 15, 150, 20),
            start_value=1.0,
            value_range=(0.1, 3.0),
            manager=self.ui_manager
        )
        
        # Progress Bar
        self.ui_elements['progress_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(viz_x + 10, control_y + 50, 100, 20),
            text='Progress:',
            manager=self.ui_manager
        )
        
        self.ui_elements['progress_bar'] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(viz_x + 120, control_y + 50, viz_width - 140, 20),
            start_value=0.0,
            value_range=(0.0, 1.0),
            manager=self.ui_manager
        )
        
        # Info Panel
        info_x = self.width - 280
        self.ui_elements['info_panel'] = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(info_x, 10, 270, self.height - 20),
            starting_layer_height=0,
            manager=self.ui_manager
        )
        
        # Recording Info
        self.ui_elements['info_title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(info_x + 10, 30, 250, 25),
            text='Recording Info',
            manager=self.ui_manager
        )
        
        self.ui_elements['info_content'] = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(info_x + 10, 65, 250, 400),
            html_text='Select a recording to view details',
            manager=self.ui_manager
        )
        
    def refresh_recordings(self):
        """Refresh the list of recordings"""
        self.recordings = self.data_storage.get_all_recordings()
        self.update_recordings_list()
        self.update_statistics()
        
    def update_recordings_list(self):
        """Update the recordings list UI"""
        # Clear existing buttons
        for button in self.recording_buttons:
            button.kill()
        self.recording_buttons.clear()
        
        # Create new buttons
        y_offset = 10
        for i, recording in enumerate(self.recordings):
            # Format recording info
            duration_str = f"{recording.duration:.1f}s"
            title = recording.title or f"Recording {i+1}"
            button_text = f"{title}\n{recording.user_name} - {duration_str}"
            
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, y_offset, 300, 50),
                text=button_text,
                manager=self.ui_manager,
                container=self.ui_elements['recordings_list']
            )
            
            # Store recording reference
            button.recording = recording
            self.recording_buttons.append(button)
            y_offset += 60
            
    def update_statistics(self):
        """Update statistics display"""
        stats = self.data_storage.get_recording_statistics()
        stats_text = (
            f"Total Recordings: {stats['total_recordings']}\n"
            f"Total Duration: {stats['total_duration']:.1f}s\n"
            f"Unique Users: {stats['unique_users']}\n"
            f"Most Active: {stats['most_active_user']}"
        )
        self.ui_elements['stats'].set_text(stats_text)
        
    def select_recording(self, recording: AudioRecord):
        """
        Select a recording for viewing
        
        Args:
            recording: AudioRecord to select
        """
        self.selected_recording = recording
        self.ui_elements['delete_btn'].enable()
        self.ui_elements['play_btn'].enable()
        
        # Update info panel
        info_html = f"""
        <b>Title:</b> {recording.title or 'Untitled'}<br>
        <b>User:</b> {recording.user_name}<br>
        <b>Duration:</b> {recording.duration:.1f}s<br>
        <b>Date:</b> {recording.timestamp[:19]}<br>
        <b>Sample Rate:</b> {recording.sample_rate} Hz<br>
        <br>
        <b>Visualization Settings:</b><br>
        """
        
        for key, value in recording.visualization_settings.items():
            info_html += f"{key}: {value}<br>"
            
        if recording.tags:
            info_html += f"<br><b>Tags:</b> {', '.join(recording.tags)}"
            
        self.ui_elements['info_content'].set_text(info_html)
        
        # Load recording data
        self.load_recording_data(recording.id)
        
    def load_recording_data(self, record_id: str):
        """
        Load recording data for playback
        
        Args:
            record_id: ID of recording to load
        """
        data = self.data_storage.load_recording(record_id)
        if data:
            self.current_playback_data = data
            record, audio_data = data
            
            # Initialize visualization engine with recording settings
            if self.visualization_engine:
                self.visualization_engine.cleanup()
                
            viz_width = self.width - 650  # Account for panels
            viz_height = self.height - 130
            self.visualization_engine = VisualizationEngine(viz_width, viz_height)
            self.visualization_engine.update_settings(record.visualization_settings)
            
            print(f"Loaded recording: {len(audio_data)} audio chunks")
        else:
            print(f"Failed to load recording: {record_id}")
            
    def start_playback(self):
        """Start playback of selected recording"""
        if not self.current_playback_data:
            return
            
        self.is_playing = True
        self.playback_index = 0
        
        self.ui_elements['play_btn'].disable()
        self.ui_elements['pause_btn'].enable()
        self.ui_elements['stop_btn'].enable()
        
        # Start playback thread
        self.playback_thread = threading.Thread(target=self._playback_loop)
        self.playback_thread.daemon = True
        self.playback_thread.start()
        
    def pause_playback(self):
        """Pause playback"""
        self.is_playing = False
        self.ui_elements['play_btn'].enable()
        self.ui_elements['pause_btn'].disable()
        
    def stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        self.playback_index = 0
        
        self.ui_elements['play_btn'].enable()
        self.ui_elements['pause_btn'].disable()
        self.ui_elements['stop_btn'].disable()
        
        self.ui_elements['progress_bar'].set_current_value(0.0)
        
    def _playback_loop(self):
        """Playback loop running in separate thread"""
        if not self.current_playback_data:
            return
            
        record, audio_data = self.current_playback_data
        
        while self.is_playing and self.playback_index < len(record.audio_metrics.get('amplitude', [])):
            # Get current metrics
            current_metrics = {}
            for metric_name, values in record.audio_metrics.items():
                if self.playback_index < len(values):
                    current_metrics[metric_name] = values[self.playback_index]
                    
            # Create normalized metrics for visualization
            normalized_metrics = self._normalize_playback_metrics(current_metrics)
            
            # Update visualization
            if self.visualization_engine:
                self.visualization_engine.update_from_audio(normalized_metrics)
                
            # Update progress
            progress = self.playback_index / len(record.audio_metrics.get('amplitude', []))
            self.ui_elements['progress_bar'].set_current_value(progress)
            
            # Sleep based on playback speed
            time.sleep(0.05 / self.playback_speed)  # ~20 FPS base rate
            
            self.playback_index += 1
            
        # Playback finished
        if self.is_playing:
            self.stop_playback()
            
    def _normalize_playback_metrics(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """Normalize metrics for playback visualization"""
        normalized = {}
        
        # Basic normalization similar to AudioAnalyzer
        amplitude = metrics.get('amplitude', 0.0)
        rms = metrics.get('rms', 0.0)
        peak = metrics.get('peak', 0.0)
        db = metrics.get('db', -60.0)
        frequency = metrics.get('frequency', 0.0)
        
        normalized['amplitude_norm'] = min(amplitude / 5000.0, 1.0)
        normalized['rms_norm'] = min(rms / 5000.0, 1.0)
        normalized['peak_norm'] = min(peak / 32767.0, 1.0)
        normalized['db_norm'] = max((db + 60.0) / 60.0, 0.0)
        normalized['frequency_norm'] = min(frequency / 22050.0, 1.0)
        
        return normalized
        
    def delete_selected_recording(self):
        """Delete the selected recording"""
        if self.selected_recording:
            # Confirm deletion (in a real app, you'd want a proper dialog)
            print(f"Deleting recording: {self.selected_recording.id}")
            
            success = self.data_storage.delete_recording(self.selected_recording.id)
            if success:
                print("Recording deleted successfully")
                self.selected_recording = None
                self.current_playback_data = None
                self.refresh_recordings()
                self.ui_elements['delete_btn'].disable()
                self.ui_elements['play_btn'].disable()
                self.ui_elements['info_content'].set_text('Select a recording to view details')
            else:
                print("Failed to delete recording")
                
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Handle UI events
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    self.handle_button_press(event.ui_element)
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    self.handle_slider_change(event.ui_element)
                    
            self.ui_manager.process_events(event)
            
    def handle_button_press(self, button):
        """Handle button press events"""
        if button == self.ui_elements['refresh_btn']:
            self.refresh_recordings()
        elif button == self.ui_elements['delete_btn']:
            self.delete_selected_recording()
        elif button == self.ui_elements['play_btn']:
            self.start_playback()
        elif button == self.ui_elements['pause_btn']:
            self.pause_playback()
        elif button == self.ui_elements['stop_btn']:
            self.stop_playback()
        elif button in self.recording_buttons:
            self.select_recording(button.recording)
            
    def handle_slider_change(self, slider):
        """Handle slider change events"""
        if slider == self.ui_elements['speed_slider']:
            self.playback_speed = slider.get_current_value()
        elif slider == self.ui_elements['progress_bar']:
            # Allow seeking during playback
            if self.current_playback_data and not self.is_playing:
                record, _ = self.current_playback_data
                total_frames = len(record.audio_metrics.get('amplitude', []))
                self.playback_index = int(slider.get_current_value() * total_frames)
                
    def run(self):
        """Main application loop"""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update UI
            self.ui_manager.update(time_delta)
            
            # Clear screen
            self.screen.fill((15, 15, 25))
            
            # Render visualization if available
            if self.visualization_engine:
                viz_x = 380
                viz_width = self.width - viz_x - 300
                viz_height = self.height - 130
                
                vis_surface = pygame.Surface((viz_width, viz_height))
                self.visualization_engine.render(vis_surface)
                self.screen.blit(vis_surface, (viz_x + 10, 20))
            
            # Render UI
            self.ui_manager.draw_ui(self.screen)
            
            # Update display
            pygame.display.flip()
            
        # Cleanup
        self.cleanup()
        
    def cleanup(self):
        """Cleanup resources"""
        self.is_playing = False
        
        if self.visualization_engine:
            self.visualization_engine.cleanup()
            
        pygame.quit()


if __name__ == "__main__":
    app = MultiModeInterface()
    app.run()
