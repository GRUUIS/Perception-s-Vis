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
    """Enhanced particle with beautiful visual effects"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    alpha: float = 255
    trail: List[Tuple[float, float]] = None  # Trail positions
    glow_intensity: float = 1.0
    rotation: float = 0.0
    rotation_speed: float = 0.0
    shape_type: str = "circle"  # circle, star, heart, diamond
    pulsate: bool = False
    energy: float = 1.0
    
    def __post_init__(self):
        if self.trail is None:
            self.trail = []


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
        """Update individual particles with enhanced effects"""
        current_time = time.time()
        
        for particle in self.particles:
            # Update trail (add current position before moving)
            if len(particle.trail) > 15:  # Limit trail length
                particle.trail.pop(0)
            particle.trail.append((particle.x, particle.y))
            
            # Update life
            particle.life -= dt
            if particle.life <= 0:
                continue
            
            # Calculate life ratio
            life_ratio = particle.life / particle.max_life
            
            # Update rotation
            particle.rotation += particle.rotation_speed * dt
            
            # Update energy based on life and time
            particle.energy = life_ratio * (0.8 + 0.2 * math.sin(current_time * 3 + particle.x * 0.01))
            
            # Update alpha with smooth fade
            base_alpha = int(255 * life_ratio)
            if life_ratio < 0.2:  # Fade out in last 20% of life
                fade_factor = life_ratio / 0.2
                base_alpha = int(base_alpha * fade_factor)
            particle.alpha = max(0, min(255, base_alpha))
            
            # Update glow intensity
            particle.glow_intensity = 0.5 + 0.5 * math.sin(current_time * 2 + particle.x * 0.02) * life_ratio
            
            # Apply motion patterns with more variety
            if self.motion_pattern == "spiral":
                new_x, new_y = MotionPattern.spiral(
                    1 - life_ratio, (particle.x, particle.y), 50 * self.intensity
                )
                particle.vx = (new_x - particle.x) * 2
                particle.vy = (new_y - particle.y) * 2
            
            elif self.motion_pattern == "wave":
                wave_x, wave_y = MotionPattern.wave(
                    current_time + particle.x * 0.01, (particle.x, particle.y), 
                    20 * self.intensity
                )
                particle.vx += (wave_x - particle.x) * 0.1
                particle.vy += (wave_y - particle.y) * 0.1
            
            elif self.motion_pattern == "explosion":
                # Enhanced explosion with radial acceleration
                center_x, center_y = 400, 300  # Screen center
                dx = particle.x - center_x
                dy = particle.y - center_y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    force = self.intensity * 150 * (1 + 0.5 * math.sin(current_time * 4))
                    particle.vx += (dx / distance) * force * dt
                    particle.vy += (dy / distance) * force * dt
            
            elif self.motion_pattern == "orbital":
                # New orbital motion pattern
                center_x, center_y = 400, 300
                dx = particle.x - center_x
                dy = particle.y - center_y
                distance = max(1, math.sqrt(dx*dx + dy*dy))
                
                # Orbital velocity (perpendicular to radius)
                orbital_speed = self.intensity * 50
                particle.vx += (-dy / distance) * orbital_speed * dt
                particle.vy += (dx / distance) * orbital_speed * dt
                
                # Slight inward pull
                particle.vx -= (dx / distance) * 10 * dt
                particle.vy -= (dy / distance) * 10 * dt
            
            elif self.motion_pattern == "magnetic":
                # Magnetic field-like motion
                field_strength = self.intensity * 30
                particle.vx += math.sin(particle.y * 0.02) * field_strength * dt
                particle.vy += math.cos(particle.x * 0.02) * field_strength * dt
            
            elif self.motion_pattern == "chaotic":
                # Enhanced chaotic motion
                chaos_factor = self.intensity * 80
                particle.vx += random.uniform(-chaos_factor, chaos_factor) * dt
                particle.vy += random.uniform(-chaos_factor, chaos_factor) * dt
                # More aggressive damping
                particle.vx *= 0.95
                particle.vy *= 0.95
            
            # Apply environmental forces
            particle.vx += self.wind[0] * dt
            particle.vy += self.wind[1] * dt + self.gravity * dt
            
            # Add some turbulence for organic motion
            turbulence = 10 * self.intensity
            particle.vx += math.sin(current_time * 3 + particle.x * 0.05) * turbulence * dt
            particle.vy += math.cos(current_time * 2.7 + particle.y * 0.05) * turbulence * dt
            
            # Update position
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            
            # Enhanced boundary handling - bounce instead of wrap
            if particle.x < 0:
                particle.x = 0
                particle.vx = abs(particle.vx) * 0.8
            elif particle.x > 1080:  # Adjusted for new screen size
                particle.x = 1080
                particle.vx = -abs(particle.vx) * 0.8
                
            if particle.y < 0:
                particle.y = 0
                particle.vy = abs(particle.vy) * 0.8
            elif particle.y > 750:  # Adjusted for new screen size
                particle.y = 750
                particle.vy = -abs(particle.vy) * 0.8
    
    def _spawn_particles(self, centers: List[Tuple[float, float]]):
        """Spawn beautiful enhanced particles at given centers"""
        if len(self.particles) >= self.max_particles:
            return
        
        particles_per_center = max(1, int(self.spawn_rate * self.intensity))
        
        for center_x, center_y in centers:
            for _ in range(particles_per_center):
                if len(self.particles) >= self.max_particles:
                    break
                
                # Random spawn offset with distribution
                spawn_radius = 30 * self.intensity
                spawn_angle = random.uniform(0, 2 * math.pi)
                offset_x = spawn_radius * math.cos(spawn_angle) * random.uniform(0.3, 1.0)
                offset_y = spawn_radius * math.sin(spawn_angle) * random.uniform(0.3, 1.0)
                
                # Enhanced velocity with pattern consideration
                speed = self.particle_speed * random.uniform(0.5, 1.8)
                
                if self.motion_pattern in ["spiral", "orbital"]:
                    # For circular patterns, spawn with tangential velocity
                    angle = spawn_angle + math.pi/2
                else:
                    # Random direction for other patterns
                    angle = random.uniform(0, 2 * math.pi)
                    
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                
                # Enhanced color selection with variation
                base_color = random.choice(self.base_colors)
                color_variation = 30
                color = (
                    max(0, min(255, base_color[0] + random.randint(-color_variation, color_variation))),
                    max(0, min(255, base_color[1] + random.randint(-color_variation, color_variation))),
                    max(0, min(255, base_color[2] + random.randint(-color_variation, color_variation)))
                )
                
                # Random shape selection
                shapes = ["circle", "star", "diamond", "heart"]
                shape_weights = [0.4, 0.3, 0.2, 0.1]  # Prefer circles, but mix in others
                shape_type = random.choices(shapes, weights=shape_weights)[0]
                
                # Create enhanced particle
                particle = Particle(
                    x=center_x + offset_x,
                    y=center_y + offset_y,
                    vx=vx,
                    vy=vy,
                    life=self.particle_life * random.uniform(0.6, 1.4),
                    max_life=self.particle_life,
                    color=color,
                    size=self.particle_size * random.uniform(0.5, 2.0),
                    trail=[],
                    glow_intensity=random.uniform(0.5, 1.5),
                    rotation=random.uniform(0, 2 * math.pi),
                    rotation_speed=random.uniform(-2, 2),
                    shape_type=shape_type,
                    pulsate=random.choice([True, False]),
                    energy=random.uniform(0.8, 1.2)
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
        Render beautiful particles with enhanced visual effects
        
        Args:
            surface: Pygame surface to render to
        """
        for particle in self.particles:
            if particle.life <= 0:
                continue
            
            # Calculate life-based effects
            life_ratio = particle.life / particle.max_life
            
            # Pulsation effect
            pulse_size = particle.size
            if particle.pulsate:
                pulse_factor = 1.0 + 0.3 * math.sin(time.time() * 8 + particle.x * 0.01)
                pulse_size *= pulse_factor
            
            # Size variation based on energy
            final_size = pulse_size * (0.5 + 0.5 * particle.energy)
            
            # Alpha based on life and glow
            alpha = int(particle.alpha * life_ratio * particle.glow_intensity)
            alpha = max(0, min(255, alpha))
            
            if alpha < 10:  # Skip nearly invisible particles
                continue
                
            # Render particle trail
            if len(particle.trail) > 1:
                self._render_particle_trail(surface, particle, alpha)
            
            # Main particle rendering based on shape
            if particle.shape_type == "circle":
                self._render_circle_particle(surface, particle, final_size, alpha, life_ratio)
            elif particle.shape_type == "star":
                self._render_star_particle(surface, particle, final_size, alpha, life_ratio)
            elif particle.shape_type == "diamond":
                self._render_diamond_particle(surface, particle, final_size, alpha, life_ratio)
            elif particle.shape_type == "heart":
                self._render_heart_particle(surface, particle, final_size, alpha, life_ratio)
            else:
                # Default to circle
                self._render_circle_particle(surface, particle, final_size, alpha, life_ratio)
    
    def _render_particle_trail(self, surface: pygame.Surface, particle: Particle, alpha: int):
        """Render beautiful particle trail"""
        if len(particle.trail) < 2:
            return
            
        # Draw trail as connected points with fading alpha
        trail_points = []
        for i, (tx, ty) in enumerate(particle.trail):
            trail_alpha = int(alpha * (i / len(particle.trail)) * 0.6)
            if trail_alpha > 10:
                trail_points.append((int(tx), int(ty)))
        
        if len(trail_points) > 1:
            # Create trail color (slightly dimmed)
            trail_color = (
                max(0, particle.color[0] - 50),
                max(0, particle.color[1] - 50),
                max(0, particle.color[2] - 50)
            )
            
            # Draw trail lines
            for i in range(len(trail_points) - 1):
                trail_alpha = int(alpha * ((i + 1) / len(trail_points)) * 0.4)
                if trail_alpha > 5:
                    temp_surface = pygame.Surface((abs(trail_points[i+1][0] - trail_points[i][0]) + 4,
                                                 abs(trail_points[i+1][1] - trail_points[i][1]) + 4), 
                                                pygame.SRCALPHA)
                    
                    # Calculate relative positions
                    start_pos = (2, 2)
                    end_pos = (trail_points[i+1][0] - trail_points[i][0] + 2,
                              trail_points[i+1][1] - trail_points[i][1] + 2)
                    
                    pygame.draw.line(temp_surface, (*trail_color, trail_alpha), 
                                   start_pos, end_pos, 2)
                    
                    surface.blit(temp_surface, 
                               (min(trail_points[i][0], trail_points[i+1][0]) - 2,
                                min(trail_points[i][1], trail_points[i+1][1]) - 2),
                               special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def _render_circle_particle(self, surface: pygame.Surface, particle: Particle, 
                               size: float, alpha: int, life_ratio: float):
        """Render circle particle with glow effect"""
        int_size = max(1, int(size))
        pos_x, pos_y = int(particle.x), int(particle.y)
        
        # Create glow effect
        glow_size = int(size * 2.5 * particle.glow_intensity)
        if glow_size > 0:
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            
            # Multi-layer glow
            for i in range(3):
                glow_alpha = max(1, int(alpha * (0.3 - i * 0.1) * particle.glow_intensity))
                glow_radius = int(glow_size * (1.0 - i * 0.3))
                
                if glow_radius > 0:
                    pygame.draw.circle(glow_surface, particle.color,
                                     (glow_size, glow_size), glow_radius)
                    glow_surface.set_alpha(glow_alpha)
            
            surface.blit(glow_surface, 
                        (pos_x - glow_size, pos_y - glow_size),
                        special_flags=pygame.BLEND_ADD)
        
        # Main particle
        if int_size > 0:
            particle_surface = pygame.Surface((int_size * 2, int_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle.color,
                             (int_size, int_size), int_size)
            particle_surface.set_alpha(alpha)
            
            surface.blit(particle_surface,
                        (pos_x - int_size, pos_y - int_size),
                        special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def _render_star_particle(self, surface: pygame.Surface, particle: Particle,
                             size: float, alpha: int, life_ratio: float):
        """Render star-shaped particle"""
        center_x, center_y = int(particle.x), int(particle.y)
        
        # Calculate star points
        points = []
        for i in range(10):  # 5-pointed star with inner and outer points
            angle = i * math.pi / 5 + particle.rotation
            if i % 2 == 0:  # Outer points
                radius = size
            else:  # Inner points
                radius = size * 0.5
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        
        if len(points) >= 3:
            star_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            
            # Adjust points relative to surface
            adjusted_points = [(p[0] - center_x + size * 1.5, 
                              p[1] - center_y + size * 1.5) for p in points]
            
            pygame.draw.polygon(star_surface, particle.color, adjusted_points)
            star_surface.set_alpha(alpha)
            
            surface.blit(star_surface,
                        (center_x - size * 1.5, center_y - size * 1.5),
                        special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def _render_diamond_particle(self, surface: pygame.Surface, particle: Particle,
                                size: float, alpha: int, life_ratio: float):
        """Render diamond-shaped particle"""
        center_x, center_y = int(particle.x), int(particle.y)
        
        points = [
            (center_x, center_y - size),  # Top
            (center_x + size, center_y),  # Right
            (center_x, center_y + size),  # Bottom
            (center_x - size, center_y)   # Left
        ]
        
        diamond_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        adjusted_points = [(p[0] - center_x + size * 1.5, 
                          p[1] - center_y + size * 1.5) for p in points]
        
        pygame.draw.polygon(diamond_surface, particle.color, adjusted_points)
        diamond_surface.set_alpha(alpha)
        
        surface.blit(diamond_surface,
                    (center_x - size * 1.5, center_y - size * 1.5),
                    special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def _render_heart_particle(self, surface: pygame.Surface, particle: Particle,
                              size: float, alpha: int, life_ratio: float):
        """Render heart-shaped particle"""
        center_x, center_y = int(particle.x), int(particle.y)
        
        # Simplified heart shape using circles and triangle
        heart_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        
        # Heart top circles
        left_circle_center = (size * 0.8, size * 0.8)
        right_circle_center = (size * 2.2, size * 0.8)
        circle_radius = size * 0.6
        
        pygame.draw.circle(heart_surface, particle.color,
                         left_circle_center, int(circle_radius))
        pygame.draw.circle(heart_surface, particle.color,
                         right_circle_center, int(circle_radius))
        
        # Heart bottom triangle
        triangle_points = [
            (size * 0.2, size * 1.2),
            (size * 2.8, size * 1.2),
            (size * 1.5, size * 2.6)
        ]
        
        pygame.draw.polygon(heart_surface, particle.color, triangle_points)
        heart_surface.set_alpha(alpha)
        
        surface.blit(heart_surface,
                    (center_x - size * 1.5, center_y - size * 1.5),
                    special_flags=pygame.BLEND_ALPHA_SDL2)
    
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