"""
Creative Audio Visualization Studio
A completely reimagined approach to audio-visual art creation
"""

import pygame
import pygame_gui
import numpy as np
import math
import random
import time
from typing import Dict, List, Tuple, Optional
import colorsys
from dataclasses import dataclass
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.audio import AudioAnalyzer


@dataclass
class Particle:
    """A single visual particle in the creative space"""
    x: float
    y: float
    z: float  # depth for 3D-like effects
    vx: float  # velocity x
    vy: float  # velocity y
    vz: float  # velocity z
    size: float
    color: Tuple[int, int, int, int]  # RGBA
    life: float  # 0.0 to 1.0
    birth_time: float
    particle_type: str  # 'spark', 'wave', 'flow', 'burst'
    frequency_bin: int  # which frequency bin this particle represents


class CreativeVisualizationEngine:
    """Advanced creative visualization engine with dynamic particle systems"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Particle systems
        self.particles: List[Particle] = []
        self.max_particles = 2000
        
        # Audio data
        self.fft_data = np.zeros(128)
        self.audio_history = []
        self.max_history = 60  # 1 second at 60fps
        
        # Creative parameters
        self.time = 0.0
        self.energy_level = 0.0
        self.dominant_frequency = 0.0
        self.beat_detected = False
        self.last_beat_time = 0.0
        
        # Visual themes
        self.current_theme = 'cosmic'
        self.themes = {
            'cosmic': {
                'bg_color': (5, 5, 20),
                'particle_colors': [(138, 43, 226), (75, 0, 130), (148, 0, 211), (255, 20, 147)],
                'trail_alpha': 20
            },
            'fire': {
                'bg_color': (20, 5, 0),
                'particle_colors': [(255, 0, 0), (255, 165, 0), (255, 255, 0), (255, 69, 0)],
                'trail_alpha': 30
            },
            'ocean': {
                'bg_color': (0, 10, 25),
                'particle_colors': [(0, 119, 190), (0, 180, 216), (144, 224, 239), (64, 224, 208)],
                'trail_alpha': 25
            },
            'forest': {
                'bg_color': (5, 15, 5),
                'particle_colors': [(34, 139, 34), (0, 128, 0), (173, 255, 47), (50, 205, 50)],
                'trail_alpha': 22
            },
            'neon': {
                'bg_color': (10, 0, 10),
                'particle_colors': [(57, 255, 20), (255, 20, 147), (0, 191, 255), (255, 0, 255)],
                'trail_alpha': 35
            }
        }
        
        # Background surface for trails
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Initialize pygame and fonts
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        
    def cycle_theme(self):
        """Cycle to the next visual theme"""
        theme_names = list(self.themes.keys())
        current_index = theme_names.index(self.current_theme)
        self.current_theme = theme_names[(current_index + 1) % len(theme_names)]
        
    def detect_beat(self, audio_data: np.ndarray) -> bool:
        """Simple beat detection based on energy spikes"""
        if len(audio_data) < 1024:
            return False
            
        # Calculate energy in bass range
        fft = np.abs(np.fft.rfft(audio_data))
        bass_energy = np.sum(fft[1:8])  # Low frequency bins
        
        # Simple threshold-based beat detection
        if bass_energy > self.energy_level * 2.5 and time.time() - self.last_beat_time > 0.3:
            self.last_beat_time = time.time()
            return True
        return False
        
    def update_audio_analysis(self, audio_data: np.ndarray):
        """Analyze audio and update visualization parameters"""
        if len(audio_data) < 512:
            return
            
        # FFT analysis
        windowed = audio_data[:1024] * np.hanning(min(len(audio_data), 1024))
        fft = np.abs(np.fft.rfft(windowed))
        
        # Resize to our FFT bins
        if len(fft) > len(self.fft_data):
            # Downsample
            factor = len(fft) // len(self.fft_data)
            self.fft_data = np.array([np.mean(fft[i:i+factor]) for i in range(0, len(fft), factor)])[:len(self.fft_data)]
        else:
            self.fft_data = np.pad(fft, (0, len(self.fft_data) - len(fft)), 'constant')
        
        # Normalize
        self.fft_data = self.fft_data / (np.max(self.fft_data) + 1e-6)
        
        # Overall energy
        self.energy_level = np.mean(self.fft_data) * 0.9 + self.energy_level * 0.1
        
        # Dominant frequency
        peak_bin = np.argmax(self.fft_data)
        self.dominant_frequency = peak_bin / len(self.fft_data)
        
        # Beat detection
        self.beat_detected = self.detect_beat(audio_data)
        
        # Store history
        self.audio_history.append(self.fft_data.copy())
        if len(self.audio_history) > self.max_history:
            self.audio_history.pop(0)
    
    def spawn_particles(self):
        """Spawn new particles based on audio data"""
        theme = self.themes[self.current_theme]
        
        # Spawn rate based on energy
        spawn_rate = int(self.energy_level * 50 + 5)
        
        for _ in range(min(spawn_rate, self.max_particles - len(self.particles))):
            # Choose particle type based on audio characteristics
            if self.beat_detected:
                particle_type = 'burst'
            elif self.dominant_frequency > 0.7:
                particle_type = 'spark'
            elif self.dominant_frequency > 0.3:
                particle_type = 'flow'
            else:
                particle_type = 'wave'
            
            # Choose frequency bin
            freq_bin = random.randint(0, len(self.fft_data) - 1)
            intensity = self.fft_data[freq_bin]
            
            if intensity > 0.1:  # Only spawn if there's activity in this frequency
                # Position based on particle type
                if particle_type == 'burst':
                    x = self.width // 2 + random.uniform(-100, 100)
                    y = self.height // 2 + random.uniform(-100, 100)
                elif particle_type == 'spark':
                    x = random.uniform(0, self.width)
                    y = self.height - 50
                elif particle_type == 'flow':
                    x = random.uniform(0, self.width)
                    y = random.uniform(0, self.height)
                else:  # wave
                    x = freq_bin * (self.width / len(self.fft_data))
                    y = self.height - intensity * self.height
                
                # Velocity based on type and intensity
                if particle_type == 'burst':
                    angle = random.uniform(0, 2 * math.pi)
                    speed = intensity * 300 + 50
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                elif particle_type == 'spark':
                    vx = random.uniform(-100, 100)
                    vy = -intensity * 400 - 100
                elif particle_type == 'flow':
                    vx = math.sin(self.time + freq_bin) * 150
                    vy = math.cos(self.time + freq_bin) * 150
                else:  # wave
                    vx = random.uniform(-50, 50)
                    vy = -intensity * 200
                
                # Color from theme
                base_color = random.choice(theme['particle_colors'])
                # Modify color based on frequency
                hue_shift = freq_bin / len(self.fft_data) * 0.3
                r, g, b = base_color
                h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                h = (h + hue_shift) % 1.0
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                color = (int(r*255), int(g*255), int(b*255), int(intensity * 255))
                
                particle = Particle(
                    x=x, y=y, z=random.uniform(0, 100),
                    vx=vx, vy=vy, vz=random.uniform(-50, 50),
                    size=intensity * 8 + 2,
                    color=color,
                    life=1.0,
                    birth_time=self.time,
                    particle_type=particle_type,
                    frequency_bin=freq_bin
                )
                
                self.particles.append(particle)
    
    def update_particles(self, dt: float):
        """Update all particles"""
        self.time += dt
        
        # Update existing particles
        particles_to_remove = []
        
        for i, particle in enumerate(self.particles):
            # Age and life decay
            age = self.time - particle.birth_time
            
            if particle.particle_type == 'burst':
                particle.life = max(0, 1.0 - age * 2.0)
            elif particle.particle_type == 'spark':
                particle.life = max(0, 1.0 - age * 1.5)
            elif particle.particle_type == 'flow':
                particle.life = max(0, 1.0 - age * 0.8)
            else:  # wave
                particle.life = max(0, 1.0 - age * 1.2)
            
            if particle.life <= 0:
                particles_to_remove.append(i)
                continue
            
            # Physics update
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.z += particle.vz * dt
            
            # Apply forces based on type
            if particle.particle_type == 'flow':
                # Flowing motion influenced by audio
                if particle.frequency_bin < len(self.fft_data):
                    force = self.fft_data[particle.frequency_bin] * 200
                    particle.vx += math.sin(self.time * 2 + particle.frequency_bin) * force * dt
                    particle.vy += math.cos(self.time * 2 + particle.frequency_bin) * force * dt
            elif particle.particle_type == 'wave':
                # Wave-like motion
                particle.vy += 100 * dt  # gravity
                particle.vx *= 0.98  # air resistance
            elif particle.particle_type == 'spark':
                # Spark physics
                particle.vy += 200 * dt  # gravity
                particle.vx *= 0.95
            
            # Boundary handling
            if particle.x < 0 or particle.x > self.width or particle.y > self.height:
                if particle.particle_type == 'flow':
                    # Wrap around for flow particles
                    particle.x = particle.x % self.width
                    if particle.y > self.height:
                        particle.y = 0
                else:
                    particles_to_remove.append(i)
            
            # Update color alpha based on life
            r, g, b, _ = particle.color
            particle.color = (r, g, b, int(particle.life * 255))
        
        # Remove dead particles
        for i in reversed(particles_to_remove):
            self.particles.pop(i)
    
    def render(self, surface: pygame.Surface):
        """Render the creative visualization"""
        theme = self.themes[self.current_theme]
        
        # Clear with background color
        surface.fill(theme['bg_color'])
        
        # Add trail effect
        trail_alpha = theme['trail_alpha']
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.fill(theme['bg_color'])
        fade_surface.set_alpha(trail_alpha)
        self.trail_surface.blit(fade_surface, (0, 0))
        
        # Draw particles to trail surface
        for particle in self.particles:
            if particle.life > 0:
                # 3D perspective effect
                z_factor = 1.0 + particle.z / 500
                screen_x = int(particle.x)
                screen_y = int(particle.y)
                size = max(1, int(particle.size * z_factor * particle.life))
                
                # Draw particle with glow effect
                if size > 2:
                    # Outer glow
                    glow_color = (*particle.color[:3], max(20, particle.color[3] // 4))
                    pygame.draw.circle(self.trail_surface, glow_color, 
                                     (screen_x, screen_y), size + 2)
                
                # Main particle
                pygame.draw.circle(self.trail_surface, particle.color, 
                                 (screen_x, screen_y), size)
        
        # Blit trail surface to main surface
        surface.blit(self.trail_surface, (0, 0))
        
        # Draw frequency visualization at bottom
        if len(self.fft_data) > 0:
            bar_width = self.width // len(self.fft_data)
            for i, magnitude in enumerate(self.fft_data):
                bar_height = int(magnitude * 100)
                if bar_height > 0:
                    color = theme['particle_colors'][i % len(theme['particle_colors'])]
                    alpha_color = (*color, int(magnitude * 255))
                    bar_surface = pygame.Surface((bar_width - 1, bar_height), pygame.SRCALPHA)
                    bar_surface.fill(alpha_color)
                    surface.blit(bar_surface, (i * bar_width, self.height - bar_height))
        
        # Draw theme name
        theme_text = self.font.render(f"Theme: {self.current_theme.title()}", True, (255, 255, 255, 200))
        surface.blit(theme_text, (10, 10))
        
        # Draw instructions
        instructions = "Press SPACE to change theme • ESC to exit"
        inst_text = self.font.render(instructions, True, (255, 255, 255, 150))
        surface.blit(inst_text, (10, self.height - 30))


class CreativeStudioInterface:
    """Completely reimagined creative studio interface"""
    
    def __init__(self, width: int = 1600, height: int = 1000):
        pygame.init()
        
        self.width = width
        self.height = height
        
        # Create fullscreen-like window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Audio Perception Studio - Creative Mode")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Creative visualization engine
        self.vis_engine = CreativeVisualizationEngine(width, height)
        
        # Audio system
        self.audio_analyzer = None
        self.setup_audio()
        
    def setup_audio(self):
        """Setup audio capture system"""
        try:
            self.audio_analyzer = AudioAnalyzer(callback=self.audio_callback)
            self.audio_analyzer.start_recording()
            print("🎤 Creative audio capture started!")
        except Exception as e:
            print(f"Audio setup failed: {e}")
    
    def audio_callback(self, metrics: Dict[str, float]):
        """Process audio data for creative visualization"""
        if self.audio_analyzer:
            audio_chunks = self.audio_analyzer.get_audio_data()
            if audio_chunks and len(audio_chunks) > 0:
                latest_chunk = audio_chunks[-1]
                self.vis_engine.update_audio_analysis(latest_chunk)
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.vis_engine.cycle_theme()
                elif event.key == pygame.K_r:
                    # Reset particles
                    self.vis_engine.particles.clear()
    
    def run(self):
        """Main creative studio loop"""
        print("🎨 Creative Studio Mode Started!")
        print("Make some noise and watch the magic happen!")
        print("Controls:")
        print("  SPACE - Change visual theme")
        print("  R - Reset particles")
        print("  ESC - Exit")
        
        try:
            while self.running:
                dt = self.clock.tick(60) / 1000.0  # 60 FPS
                
                # Handle events
                self.handle_events()
                
                # Update visualization
                self.vis_engine.spawn_particles()
                self.vis_engine.update_particles(dt)
                
                # Render
                self.vis_engine.render(self.screen)
                
                pygame.display.flip()
                
        except KeyboardInterrupt:
            print("\nCreative session interrupted by user")
        
        finally:
            # Cleanup
            if self.audio_analyzer:
                self.audio_analyzer.stop_recording()
            pygame.quit()
            print("🎨 Creative Studio session ended")


if __name__ == "__main__":
    app = CreativeStudioInterface()
    app.run()