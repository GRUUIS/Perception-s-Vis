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
        """Initialize the launcher with modern design"""
        pygame.init()
        
        # Modern app dimensions - larger for better user experience
        self.width = 1200
        self.height = 800
        
        # Create main window with modern styling
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Audio Perception Studio - Professional Audio Visualization Platform")
        
        # Set window icon (if available)
        try:
            icon = pygame.Surface((32, 32))
            icon.fill((74, 144, 226))
            pygame.display.set_icon(icon)
        except:
            pass
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Modern color scheme
        self.colors = {
            'primary': (74, 144, 226),      # Modern blue
            'secondary': (108, 92, 231),    # Purple accent
            'success': (16, 185, 129),      # Green
            'warning': (245, 158, 11),      # Orange
            'danger': (239, 68, 68),        # Red
            'dark': (17, 24, 39),           # Dark gray
            'light': (243, 244, 246),       # Light gray
            'white': (255, 255, 255),
            'text_primary': (17, 24, 39),
            'text_secondary': (107, 114, 128),
            'gradient_start': (74, 144, 226),
            'gradient_end': (108, 92, 231)
        }
        
        # UI Manager
        self.ui_manager = pygame_gui.UIManager((self.width, self.height))
        
        # UI Elements
        self.ui_elements = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup minimal launcher UI with just two main buttons"""
        # App title - clean and centered
        self.ui_elements['title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 150, self.width, 80),
            text='Audio Perception Studio',
            manager=self.ui_manager
        )
        
        # Main action buttons - large and prominent
        button_width = 400
        button_height = 120
        button_spacing = 80
        button_y = 350
        
        # Calculate button positions for perfect centering
        total_width = 2 * button_width + button_spacing
        start_x = (self.width - total_width) // 2
        
        # Studio Mode Button - Create and visualize
        self.ui_elements['single_mode_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x, button_y, button_width, button_height),
            text='STUDIO',
            manager=self.ui_manager
        )
        
        # Gallery Mode Button - Explore and view
        self.ui_elements['multi_mode_btn'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height),
            text='GALLERY',
            manager=self.ui_manager
        )
        
        # Instructions
        instructions = (
            "Single Mode: Create your own audio visualizations with real-time feedback\n"
            "Gallery Mode: View and playback visualizations from all users"
        )
        
        self.ui_elements['instructions'] = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(100, 540, self.width - 200, 200),
            html_text=instructions.replace('\n', '<br>'),
            manager=self.ui_manager
        )
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Handle UI events
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                self.handle_button_press(event.ui_element)
                    
            self.ui_manager.process_events(event)
            
    def handle_button_press(self, button):
        """Handle button press events"""
        if button == self.ui_elements['single_mode_btn']:
            self.launch_single_mode()
        elif button == self.ui_elements['multi_mode_btn']:
            self.launch_multi_mode()
    
    def show_help(self):
        """Show help and settings dialog"""
        # TODO: Implement help/settings dialog
        print("Help & Settings - Coming soon!")
        print("For now, here are the basics:")
        print("- Studio Mode: Real-time audio visualization creation")
        print("- Gallery Mode: Browse saved recordings")
        print("- Make noise into your microphone to see visualizations!")
        
    def draw_modern_background(self):
        """Draw a clean, minimal background"""
        # Simple gradient background
        for y in range(self.height):
            ratio = y / self.height
            # Deep blue to dark purple gradient
            r = int(20 * (1 - ratio) + 40 * ratio)
            g = int(25 * (1 - ratio) + 20 * ratio)
            b = int(60 * (1 - ratio) + 80 * ratio)
            
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
            
    def launch_single_mode(self):
        """Launch creative studio mode"""
        print("Launching Creative Studio...")
        pygame.quit()
        
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            from src.ui.creative_studio import CreativeStudioInterface
            # Launch creative studio with full-screen experience
            app = CreativeStudioInterface(width=1600, height=1000)
            app.run()
        except Exception as e:
            print(f"Error launching Creative Studio: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Reinitialize after studio closes
            pygame.init()
            self.__init__()
            
    def launch_multi_mode(self):
        """Launch creative gallery mode"""
        print("Launching Creative Gallery...")
        
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Close current pygame instance properly
            pygame.quit()
            
            # Import and run creative gallery
            from src.ui.creative_gallery import CreativeGalleryInterface
            app = CreativeGalleryInterface(width=1600, height=1000, data_dir=data_dir)
            app.run()
            
            # After gallery closes, restart the main menu
            pygame.init()
            self.__init__()
            
        except Exception as e:
            print(f"Error launching Creative Gallery: {e}")
            import traceback
            traceback.print_exc()
            # Ensure pygame is reinitialized if there was an error
            pygame.init()
            self.__init__()
            
    def run(self):
        """Main launcher loop"""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update UI
            self.ui_manager.update(time_delta)
            
            # Clear screen with modern gradient background
            self.draw_modern_background()
            
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
