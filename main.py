"""
Main Application Entry Point
Audio Perception - Dynamic Audio Visualization System

This application captures audio using PyAudio and creates real-time visualizations
that respond to audio metrics like amplitude, RMS, peak, and dB levels.

Features:
- Real-time audio capture and analysis
- Dynamic visualizations with customizable parameters
- Single mode: Individual user interface
- Multiple mode: Gallery of all user visualizations
- Data storage for recordings and visual outputs
"""

import pygame
import pygame_gui
import sys
import os
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui import SingleModeInterface, MultiModeInterface


class AudioPerceptionLauncher:
    """Main launcher for the Audio Perception application"""
    
    def __init__(self):
        """Initialize the launcher"""
        pygame.init()
        
        self.width = 800
        self.height = 600
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Audio Perception - Welcome")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # UI Manager
        self.ui_manager = pygame_gui.UIManager((self.width, self.height))
        
        # UI Elements
        self.ui_elements = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the launcher UI"""
        # Background panel
        self.ui_elements['main_panel'] = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(50, 50, self.width - 100, self.height - 100),
            starting_layer_height=0,
            manager=self.ui_manager
        )
        
        # Title
        self.ui_elements['title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(100, 100, self.width - 200, 60),
            text='Audio Perception',
            manager=self.ui_manager
        )
        
        # Subtitle
        self.ui_elements['subtitle'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(100, 170, self.width - 200, 40),
            text='Dynamic Audio Visualization System',
            manager=self.ui_manager
        )
        
        # Description
        description_text = (
            "Transform sound into stunning visual experiences!\n\n"
            "• Real-time audio analysis and visualization\n"
            "• Customizable visual effects and parameters\n"
            "• Record and share your audio-visual creations\n"
            "• Explore visualizations from other users"
        )
        
        self.ui_elements['description'] = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(100, 230, self.width - 200, 150),
            html_text=description_text.replace('\n', '<br>'),
            manager=self.ui_manager
        )
        
        # Mode Selection Buttons
        button_width = 200
        button_height = 50
        button_y = 400
        
        # Single Mode Button
        single_x = (self.width // 2) - button_width - 20
        self.ui_elements['single_mode_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(single_x, button_y, button_width, button_height),
            text='Single Mode\n(Individual Recording)',
            manager=self.ui_manager
        )
        
        # Multiple Mode Button
        multi_x = (self.width // 2) + 20
        self.ui_elements['multi_mode_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(multi_x, button_y, button_width, button_height),
            text='Gallery Mode\n(View All Recordings)',
            manager=self.ui_manager
        )
        
        # Exit Button
        self.ui_elements['exit_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.width // 2) - 75, 480, 150, 40),
            text='Exit',
            manager=self.ui_manager
        )
        
        # Instructions
        instructions = (
            "Single Mode: Create your own audio visualizations with real-time feedback\n"
            "Gallery Mode: View and playback visualizations from all users"
        )
        
        self.ui_elements['instructions'] = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(100, 540, self.width - 200, 50),
            html_text=instructions.replace('\n', '<br>'),
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
                    
            self.ui_manager.process_events(event)
            
    def handle_button_press(self, button):
        """Handle button press events"""
        if button == self.ui_elements['single_mode_btn']:
            self.launch_single_mode()
        elif button == self.ui_elements['multi_mode_btn']:
            self.launch_multi_mode()
        elif button == self.ui_elements['exit_btn']:
            self.running = False
            
    def launch_single_mode(self):
        """Launch single mode interface"""
        print("Launching Single Mode...")
        pygame.quit()
        
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            
            app = SingleModeInterface(data_dir=data_dir)
            app.run()
        except Exception as e:
            print(f"Error launching Single Mode: {e}")
            print("Make sure all required packages are installed:")
            print("pip install pygame pygame-gui pyaudio numpy")
        finally:
            # Return to launcher
            self.__init__()
            
    def launch_multi_mode(self):
        """Launch multiple mode interface"""
        print("Launching Gallery Mode...")
        pygame.quit()
        
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            
            app = MultiModeInterface(data_dir=data_dir)
            app.run()
        except Exception as e:
            print(f"Error launching Gallery Mode: {e}")
            print("Make sure all required packages are installed:")
            print("pip install pygame pygame-gui pyaudio numpy")
        finally:
            # Return to launcher
            self.__init__()
            
    def run(self):
        """Main launcher loop"""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update UI
            self.ui_manager.update(time_delta)
            
            # Clear screen with gradient background
            self.draw_gradient_background()
            
            # Render UI
            self.ui_manager.draw_ui(self.screen)
            
            # Update display
            pygame.display.flip()
            
        # Cleanup
        pygame.quit()
        
    def draw_gradient_background(self):
        """Draw a gradient background"""
        for y in range(self.height):
            # Create a color gradient from dark blue to dark purple
            ratio = y / self.height
            r = int(20 + (40 - 20) * ratio)
            g = int(20 + (20 - 20) * ratio)
            b = int(40 + (60 - 40) * ratio)
            
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))


def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import pygame
    except ImportError:
        missing_deps.append("pygame")
        
    try:
        import pygame_gui
    except ImportError:
        missing_deps.append("pygame-gui")
        
    try:
        import pyaudio
    except ImportError:
        missing_deps.append("pyaudio")
        
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
        
    if missing_deps:
        print("Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install missing dependencies with:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
        
    return True


def main():
    """Main entry point"""
    print("Audio Perception - Dynamic Audio Visualization System")
    print("=" * 55)
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
        
    # Create data directory
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'recordings'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'visualizations'), exist_ok=True)
    
    print("Data directory created at:", data_dir)
    print("Starting launcher...")
    
    try:
        launcher = AudioPerceptionLauncher()
        launcher.run()
    except Exception as e:
        print(f"Error running launcher: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
