"""
Visual Effects Engine
Advanced particle systems and visual effects for multi-modal input
"""

import pygame
import numpy as np
import math
import random
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import time


@dataclass
class Particle:
    """Individual particle with physics"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    alpha: float = 255


class MotionPattern:
    """Base class for motion patterns"""
    
    @staticmethod
    def spiral(t: float, center: Tuple[float, float], radius: float) -> Tuple[float, float]:
        """Spiral motion pattern"""
        angle = t * 2
        x = center[0] + radius * math.cos(angle) * (1 - t)
        y = center[1] + radius * math.sin(angle) * (1 - t)
        return x, y
    
    @staticmethod
    def wave(t: float, center: Tuple[float, float], amplitude: float) -> Tuple[float, float]:
        """Wave motion pattern"""
        x = center[0] + amplitude * math.sin(t * 4)
        y = center[1] + amplitude * math.cos(t * 2) * 0.5
        return x, y
    
    @staticmethod
    def explosion(t: float, center: Tuple[float, float], speed: float) -> Tuple[float, float]:
        """Explosion motion pattern"""
        angle = random.uniform(0, 2 * math.pi)
        distance = speed * t * t
        x = center[0] + distance * math.cos(angle)
        y = center[1] + distance * math.sin(angle)
        return x, y
    
    @staticmethod
    def gentle(t: float, center: Tuple[float, float], amplitude: float) -> Tuple[float, float]:
        """Gentle floating motion"""
        x = center[0] + amplitude * math.sin(t) * 0.3
        y = center[1] + amplitude * math.cos(t * 0.7) * 0.2
        return x, y
    
    @staticmethod
    def chaotic(t: float, center: Tuple[float, float], intensity: float) -> Tuple[float, float]:
        """Chaotic motion pattern"""
        x = center[0] + intensity * (math.sin(t * 3) + math.cos(t * 7) * 0.5)
        y = center[1] + intensity * (math.cos(t * 5) + math.sin(t * 11) * 0.3)
        return x, y


class ParticleSystem:
    """Advanced particle system with multiple effects"""
    
    def __init__(self, max_particles: int = 500):
        """
        Initialize particle system
        
        Args:
            max_particles: Maximum number of particles
        """
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.motion_pattern = "gentle"
        self.base_colors = [(255, 255, 255)]
        self.intensity = 0.5
        self.spawn_rate = 10
        self.last_spawn = 0
        
        # Effect parameters
        self.particle_size = 3
        self.particle_speed = 2.0
        self.particle_life = 3.0
        self.gravity = 0.0
        self.wind = (0.0, 0.0)
        
    def update(self, dt: float, spawn_centers: List[Tuple[float, float]] = None):
        """
        Update particle system
        
        Args:
            dt: Delta time
            spawn_centers: Points where new particles should spawn
        """
        current_time = time.time()
        
        # Update existing particles
        self._update_particles(dt)
        
        # Spawn new particles
        if spawn_centers and current_time - self.last_spawn > 1.0 / self.spawn_rate:
            self._spawn_particles(spawn_centers)
            self.last_spawn = current_time
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.life > 0]
    
    def _update_particles(self, dt: float):
        """Update individual particles"""
        for particle in self.particles:
            # Update life
            particle.life -= dt
            if particle.life <= 0:
                continue
            
            # Calculate life ratio
            life_ratio = particle.life / particle.max_life
            
            # Update alpha based on life
            particle.alpha = max(0, min(255, int(255 * life_ratio)))
            
            # Apply motion pattern
            if self.motion_pattern == "spiral":
                new_x, new_y = MotionPattern.spiral(
                    1 - life_ratio, (particle.x, particle.y), 50
                )
                particle.vx = (new_x - particle.x) * 2
                particle.vy = (new_y - particle.y) * 2
            
            elif self.motion_pattern == "wave":
                wave_x, wave_y = MotionPattern.wave(
                    time.time() + particle.x * 0.01, (particle.x, particle.y), 20
                )
                particle.vx += (wave_x - particle.x) * 0.1
                particle.vy += (wave_y - particle.y) * 0.1
            
            elif self.motion_pattern == "explosion":
                # Accelerate outward
                center_x, center_y = 400, 300  # Screen center
                dx = particle.x - center_x
                dy = particle.y - center_y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    particle.vx += (dx / distance) * self.intensity * 100 * dt
                    particle.vy += (dy / distance) * self.intensity * 100 * dt
            
            elif self.motion_pattern == "chaotic":
                # Random acceleration
                particle.vx += random.uniform(-50, 50) * self.intensity * dt
                particle.vy += random.uniform(-50, 50) * self.intensity * dt
                # Damping
                particle.vx *= 0.98
                particle.vy *= 0.98
            
            # Apply physics
            particle.vx += self.wind[0] * dt
            particle.vy += self.wind[1] * dt + self.gravity * dt
            
            # Update position
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            
            # Screen wrapping
            if particle.x < 0:
                particle.x = 800
            elif particle.x > 800:
                particle.x = 0
            if particle.y < 0:
                particle.y = 600
            elif particle.y > 600:
                particle.y = 0
    
    def _spawn_particles(self, centers: List[Tuple[float, float]]):
        """Spawn new particles at given centers"""
        if len(self.particles) >= self.max_particles:
            return
        
        particles_per_center = max(1, int(self.spawn_rate * self.intensity))
        
        for center_x, center_y in centers:
            for _ in range(particles_per_center):
                if len(self.particles) >= self.max_particles:
                    break
                
                # Random spawn offset
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                
                # Random velocity
                speed = self.particle_speed * random.uniform(0.5, 1.5)
                angle = random.uniform(0, 2 * math.pi)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                
                # Random color from palette
                color = random.choice(self.base_colors)
                
                # Create particle
                particle = Particle(
                    x=center_x + offset_x,
                    y=center_y + offset_y,
                    vx=vx,
                    vy=vy,
                    life=self.particle_life * random.uniform(0.8, 1.2),
                    max_life=self.particle_life,
                    color=color,
                    size=self.particle_size * random.uniform(0.7, 1.3)
                )
                
                self.particles.append(particle)
    
    def apply_style(self, style_config: Dict[str, Any]):
        """
        Apply style configuration to particle system
        
        Args:
            style_config: Style configuration from AI
        """
        # Colors
        if 'colors' in style_config:
            self.base_colors = style_config['colors']
        
        # Motion pattern
        if 'motion' in style_config:
            self.motion_pattern = style_config['motion']
        
        # Intensity
        if 'intensity' in style_config:
            self.intensity = style_config['intensity']
        
        # Particle parameters
        if 'particles' in style_config:
            particles = style_config['particles']
            self.spawn_rate = particles.get('count', 100) / 10  # Convert to rate
            self.particle_size = particles.get('size', 3)
            self.particle_speed = particles.get('speed', 2.0) * 10
            self.particle_life = particles.get('life', 3.0)
    
    def render(self, surface: pygame.Surface):
        """
        Render particles to surface
        
        Args:
            surface: Pygame surface to render to
        """
        for particle in self.particles:
            if particle.life <= 0:
                continue
            
            # Create color with alpha
            color = (*particle.color, particle.alpha)
            
            # Create temporary surface for alpha blending
            temp_surface = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                temp_surface, 
                color, 
                (particle.size, particle.size), 
                particle.size
            )
            
            # Blit to main surface
            surface.blit(
                temp_surface, 
                (particle.x - particle.size, particle.y - particle.size),
                special_flags=pygame.BLEND_ALPHA_SDL2
            )
    
    def get_particle_count(self) -> int:
        """Get current particle count"""
        return len(self.particles)
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()


class VisualEffectsEngine:
    """Main visual effects engine"""
    
    def __init__(self, screen_size: Tuple[int, int] = (800, 600)):
        """
        Initialize visual effects engine
        
        Args:
            screen_size: Screen dimensions
        """
        self.screen_size = screen_size
        self.particle_system = ParticleSystem()
        
        # Background effects
        self.background_color = (0, 0, 0)
        self.gradient_colors = [(0, 0, 0), (20, 20, 40)]
        
        # Performance tracking
        self.last_update = time.time()
        
    def update(self, 
               dt: float,
               motion_centers: List[Tuple[float, float]] = None,
               audio_data: Dict = None):
        """
        Update visual effects
        
        Args:
            dt: Delta time
            motion_centers: Centers of motion for particle spawning
            audio_data: Audio analysis data
        """
        # Use motion centers or audio data for spawning
        spawn_centers = motion_centers or []
        
        # If no motion centers but have audio, spawn at screen center
        if not spawn_centers and audio_data:
            if audio_data.get('beat_detected', False) or audio_data.get('amplitude', 0) > 1000:
                spawn_centers = [(self.screen_size[0] // 2, self.screen_size[1] // 2)]
        
        # Update particle system
        self.particle_system.update(dt, spawn_centers)
        
        # Adjust effects based on audio
        if audio_data:
            self._apply_audio_modulation(audio_data)
    
    def _apply_audio_modulation(self, audio_data: Dict):
        """Apply audio-reactive modulations"""
        # Modulate intensity based on volume
        volume = audio_data.get('db_norm', 0.0)
        self.particle_system.intensity = max(0.1, volume * 1.5)
        
        # Modulate spawn rate based on beats
        if audio_data.get('beat_detected', False):
            self.particle_system.spawn_rate = min(50, self.particle_system.spawn_rate * 2)
        else:
            self.particle_system.spawn_rate = max(5, self.particle_system.spawn_rate * 0.95)
        
        # Color modulation based on frequency
        frequency = audio_data.get('frequency', 0)
        if frequency > 1000:  # High frequency
            self.particle_system.base_colors = [(255, 200, 100), (255, 150, 50)]
        elif frequency > 500:  # Mid frequency
            self.particle_system.base_colors = [(100, 255, 100), (150, 255, 150)]
        else:  # Low frequency
            self.particle_system.base_colors = [(100, 100, 255), (150, 150, 255)]
    
    def apply_style(self, style_config: Dict[str, Any]):
        """Apply style configuration"""
        self.particle_system.apply_style(style_config)
        
        # Update background based on style
        if 'colors' in style_config and style_config['colors']:
            primary_color = style_config['colors'][0]
            # Darker version for background
            self.background_color = tuple(max(0, c // 4) for c in primary_color)
    
    def render(self, surface: pygame.Surface):
        """
        Render visual effects
        
        Args:
            surface: Pygame surface to render to
        """
        # Clear with background
        surface.fill(self.background_color)
        
        # Render particle system
        self.particle_system.render(surface)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance and status statistics"""
        return {
            'particle_count': self.particle_system.get_particle_count(),
            'motion_pattern': self.particle_system.motion_pattern,
            'intensity': self.particle_system.intensity,
            'spawn_rate': self.particle_system.spawn_rate
        }