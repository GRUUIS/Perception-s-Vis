"""
Visualization Engine
Creates dynamic visual effects based on audio data
Uses pygame for real-time rendering
"""

import pygame
import numpy as np
import math
import random
from typing import Dict, List, Tuple, Optional
import colorsys
from dataclasses import dataclass


@dataclass
class VisualElement:
    """Represents a single visual element"""
    x: float
    y: float
    size: float
    color: Tuple[int, int, int, int]  # RGBA
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    rotation: float = 0.0
    rotation_speed: float = 0.0
    life: float = 1.0
    shape: str = "circle"  # circle, square, triangle, star


class ColorPalette:
    """Manages color palettes for visualizations"""
    
    PALETTES = {
        'fire': [(255, 0, 0), (255, 165, 0), (255, 255, 0)],
        'ocean': [(0, 119, 190), (0, 180, 216), (144, 224, 239)],
        'forest': [(34, 139, 34), (0, 128, 0), (173, 255, 47)],
        'sunset': [(255, 94, 77), (255, 154, 0), (255, 206, 84)],
        'neon': [(57, 255, 20), (255, 20, 147), (0, 191, 255)],
        'purple': [(138, 43, 226), (186, 85, 211), (221, 160, 221)],
        'rainbow': [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 128, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]
    }
    
    @staticmethod
    def get_color(palette_name: str, intensity: float, saturation: float = 1.0, alpha: int = 255) -> Tuple[int, int, int, int]:
        """
        Get color from palette based on intensity
        
        Args:
            palette_name: Name of the color palette
            intensity: Value from 0.0 to 1.0
            saturation: Color saturation from 0.0 to 1.0
            alpha: Alpha value from 0 to 255
            
        Returns:
            RGBA color tuple
        """
        if palette_name not in ColorPalette.PALETTES:
            palette_name = 'rainbow'
            
        palette = ColorPalette.PALETTES[palette_name]
        
        # Interpolate between colors in palette
        intensity = max(0.0, min(1.0, intensity))
        index = intensity * (len(palette) - 1)
        idx1 = int(index)
        idx2 = min(idx1 + 1, len(palette) - 1)
        
        blend_factor = index - idx1
        
        color1 = palette[idx1]
        color2 = palette[idx2]
        
        # Interpolate RGB values
        r = int(color1[0] + (color2[0] - color1[0]) * blend_factor)
        g = int(color1[1] + (color2[1] - color1[1]) * blend_factor)
        b = int(color1[2] + (color2[2] - color1[2]) * blend_factor)
        
        # Apply saturation
        h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        s *= saturation
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        
        return (int(r * 255), int(g * 255), int(b * 255), alpha)


class VisualizationEngine:
    """Main visualization engine that creates dynamic visual effects"""
    
    def __init__(self, width: int = 1200, height: int = 800):
        """
        Initialize the visualization engine
        
        Args:
            width: Screen width
            height: Screen height
        """
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Audio Perception Visualizer")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Visual elements
        self.elements: List[VisualElement] = []
        self.particles: List[VisualElement] = []
        
        # Visualization settings
        self.settings = {
            'palette': 'rainbow',
            'base_element_count': 50,
            'max_element_count': 200,
            'background_color': (0, 0, 0),
            'fade_speed': 0.02,
            'size_multiplier': 1.0,
            'speed_multiplier': 1.0,
            'shape_variety': True,
            'particle_mode': True,
            'wave_mode': False,
            'symmetry_mode': False
        }
        
        # Animation state
        self.time = 0.0
        self.last_audio_metrics = {}
        
        # Create initial elements
        self._initialize_elements()
        
    def _initialize_elements(self):
        """Initialize base visual elements"""
        self.elements.clear()
        
        for i in range(self.settings['base_element_count']):
            element = VisualElement(
                x=random.uniform(0, self.width),
                y=random.uniform(0, self.height),
                size=random.uniform(5, 20),
                color=(255, 255, 255, 100),
                velocity_x=random.uniform(-2, 2),
                velocity_y=random.uniform(-2, 2),
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-5, 5),
                shape=random.choice(['circle', 'square', 'triangle', 'star'])
            )
            self.elements.append(element)
            
    def update_from_audio(self, audio_metrics: Dict[str, float]):
        """
        Update visualization based on audio metrics
        
        Args:
            audio_metrics: Audio analysis data
        """
        self.last_audio_metrics = audio_metrics
        
        # Get normalized values
        amplitude = audio_metrics.get('amplitude_norm', 0.0)
        rms = audio_metrics.get('rms_norm', 0.0)
        peak = audio_metrics.get('peak_norm', 0.0)
        db = audio_metrics.get('db_norm', 0.0)
        frequency = audio_metrics.get('frequency_norm', 0.0)
        
        # Adjust element count based on amplitude
        target_count = int(self.settings['base_element_count'] + 
                          amplitude * (self.settings['max_element_count'] - self.settings['base_element_count']))
        
        # Add or remove elements
        while len(self.elements) < target_count:
            self._add_element(amplitude, frequency)
            
        while len(self.elements) > target_count:
            if self.elements:
                self.elements.pop()
        
        # Update existing elements
        for element in self.elements:
            self._update_element(element, amplitude, rms, peak, db, frequency)
            
        # Add particles for high amplitude sounds
        if amplitude > 0.3 and self.settings['particle_mode']:
            self._add_particles(amplitude, frequency)
            
        # Update particles
        self._update_particles()
        
    def _add_element(self, amplitude: float, frequency: float):
        """Add a new visual element"""
        # Position based on frequency
        if self.settings['wave_mode']:
            x = (frequency * self.width) % self.width
            y = self.height / 2 + math.sin(frequency * 10) * amplitude * 100
        else:
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            
        # Size based on amplitude
        size = (5 + amplitude * 50) * self.settings['size_multiplier']
        
        # Color based on frequency and amplitude
        color = ColorPalette.get_color(
            self.settings['palette'], 
            frequency, 
            saturation=amplitude,
            alpha=int(100 + amplitude * 155)
        )
        
        # Shape based on frequency ranges
        if self.settings['shape_variety']:
            if frequency < 0.2:
                shape = 'circle'
            elif frequency < 0.4:
                shape = 'square'
            elif frequency < 0.6:
                shape = 'triangle'
            else:
                shape = 'star'
        else:
            shape = 'circle'
            
        element = VisualElement(
            x=x, y=y, size=size, color=color, shape=shape,
            velocity_x=random.uniform(-3, 3) * self.settings['speed_multiplier'],
            velocity_y=random.uniform(-3, 3) * self.settings['speed_multiplier'],
            rotation=random.uniform(0, 360),
            rotation_speed=random.uniform(-10, 10) * amplitude
        )
        
        self.elements.append(element)
        
    def _update_element(self, element: VisualElement, amplitude: float, rms: float, 
                       peak: float, db: float, frequency: float):
        """Update a single visual element"""
        # Update position
        element.x += element.velocity_x * self.settings['speed_multiplier']
        element.y += element.velocity_y * self.settings['speed_multiplier']
        
        # Bounce off edges
        if element.x < 0 or element.x > self.width:
            element.velocity_x *= -1
        if element.y < 0 or element.y > self.height:
            element.velocity_y *= -1
            
        # Keep in bounds
        element.x = max(0, min(self.width, element.x))
        element.y = max(0, min(self.height, element.y))
        
        # Update rotation
        element.rotation += element.rotation_speed
        
        # Update size based on RMS
        base_size = 5 + rms * 30
        element.size = base_size * self.settings['size_multiplier']
        
        # Update color based on current audio
        element.color = ColorPalette.get_color(
            self.settings['palette'],
            frequency,
            saturation=amplitude,
            alpha=int(50 + db * 200)
        )
        
        # Add some wave motion
        if self.settings['wave_mode']:
            wave_offset = math.sin(self.time * 2 + element.x * 0.01) * amplitude * 20
            element.y += wave_offset * 0.1
            
    def _add_particles(self, amplitude: float, frequency: float):
        """Add particle effects for high-energy audio"""
        particle_count = int(amplitude * 20)
        
        for _ in range(particle_count):
            particle = VisualElement(
                x=random.uniform(0, self.width),
                y=random.uniform(0, self.height),
                size=random.uniform(1, 5),
                color=ColorPalette.get_color(
                    self.settings['palette'], 
                    random.random(), 
                    amplitude,
                    int(amplitude * 255)
                ),
                velocity_x=random.uniform(-10, 10),
                velocity_y=random.uniform(-10, 10),
                life=1.0,
                shape='circle'
            )
            self.particles.append(particle)
            
    def _update_particles(self):
        """Update particle system"""
        for particle in self.particles[:]:
            particle.x += particle.velocity_x
            particle.y += particle.velocity_y
            particle.life -= 0.02
            
            # Update alpha based on life
            r, g, b, _ = particle.color
            particle.color = (r, g, b, int(particle.life * 255))
            
            # Remove dead particles
            if particle.life <= 0:
                self.particles.remove(particle)
                
    def render(self, screen: Optional[pygame.Surface] = None):
        """
        Render the visualization
        
        Args:
            screen: Optional pygame surface to render to
        """
        if screen is None:
            screen = self.screen
            
        # Clear screen with fade effect
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.set_alpha(int(self.settings['fade_speed'] * 255))
        fade_surface.fill(self.settings['background_color'])
        screen.blit(fade_surface, (0, 0))
        
        # Render elements
        for element in self.elements:
            self._render_element(screen, element)
            
        # Render particles
        for particle in self.particles:
            self._render_element(screen, particle)
            
        # Add symmetry effect if enabled
        if self.settings['symmetry_mode']:
            self._apply_symmetry(screen)
            
        self.time += 0.016  # Approximately 60 FPS
        
    def _render_element(self, screen: pygame.Surface, element: VisualElement):
        """Render a single visual element"""
        x, y = int(element.x), int(element.y)
        size = int(element.size)
        color = element.color[:3]  # RGB only for pygame
        
        if element.shape == 'circle':
            if size > 0:
                pygame.draw.circle(screen, color, (x, y), size)
                
        elif element.shape == 'square':
            if size > 0:
                rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
                pygame.draw.rect(screen, color, rect)
                
        elif element.shape == 'triangle':
            if size > 0:
                points = [
                    (x, y - size),
                    (x - size, y + size),
                    (x + size, y + size)
                ]
                pygame.draw.polygon(screen, color, points)
                
        elif element.shape == 'star':
            if size > 0:
                self._draw_star(screen, x, y, size, color, element.rotation)
                
    def _draw_star(self, screen: pygame.Surface, x: int, y: int, size: int, 
                   color: Tuple[int, int, int], rotation: float = 0):
        """Draw a star shape"""
        points = []
        for i in range(10):  # 5-pointed star = 10 points
            angle = (i * math.pi / 5) + math.radians(rotation)
            if i % 2 == 0:
                # Outer point
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
            else:
                # Inner point
                px = x + (size * 0.5) * math.cos(angle)
                py = y + (size * 0.5) * math.sin(angle)
            points.append((px, py))
            
        if len(points) > 2:
            pygame.draw.polygon(screen, color, points)
            
    def _apply_symmetry(self, screen: pygame.Surface):
        """Apply symmetry effect to the visualization"""
        # Create a copy of the current screen
        temp_surface = screen.copy()
        
        # Flip horizontally and blend
        flipped = pygame.transform.flip(temp_surface, True, False)
        flipped.set_alpha(128)
        screen.blit(flipped, (0, 0), special_flags=pygame.BLEND_ADD)
        
    def update_settings(self, new_settings: Dict):
        """Update visualization settings"""
        self.settings.update(new_settings)
        
    def get_settings(self) -> Dict:
        """Get current visualization settings"""
        return self.settings.copy()
        
    def save_frame(self, filename: str):
        """Save current frame as image"""
        pygame.image.save(self.screen, filename)
        
    def cleanup(self):
        """Cleanup pygame resources"""
        pygame.quit()
