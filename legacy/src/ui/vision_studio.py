"""
Vision-powered Creative Studio
Camera-based visualization with AI text style control
"""

import pygame
import pygame_gui
import numpy as np
import math
import random
import time
import cv2
from typing import Dict, List, Tuple, Optional
import colorsys
from dataclasses import dataclass
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.vision import VisionAnalyzer
from src.ai import StyleProcessor


@dataclass
class VisionParticle:
    """A particle generated from vision input"""
    x: float
    y: float
    z: float
    vx: float  # velocity x
    vy: float  # velocity y  
    vz: float  # velocity z
    size: float
    color: Tuple[int, int, int, int]  # RGBA
    life: float  # 0.0 to 1.0
    birth_time: float
    particle_type: str  # 'motion', 'color', 'general'
    source_area: Optional[Tuple[int, int]]  # (x, y) of motion area that spawned this particle


class VisionVisualizationEngine:
    """Vision-powered particle visualization engine"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Particle systems
        self.particles: List[VisionParticle] = []
        self.max_particles = 1500
        
        # Vision data
        self.motion_intensity = 0.0
        self.dominant_colors = []
        self.motion_areas = []
        self.visual_energy = 0.0
        
        # Style system
        self.style_processor = StyleProcessor()
        self.current_style = self.style_processor.current_style
        
        # Timing
        self.time = 0.0
        
        # Background trails
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Fonts
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def update_vision_data(self, vision_metrics: Dict):
        """Update visualization based on vision data"""
        self.motion_intensity = vision_metrics.get('motion_intensity', 0.0)
        self.dominant_colors = vision_metrics.get('dominant_colors', [])
        self.motion_areas = vision_metrics.get('motion_areas', [])
        self.visual_energy = vision_metrics.get('visual_energy', 0.0)
    
    def apply_text_style(self, text_input: str):
        """Apply style from text input"""
        result = self.style_processor.process_text_input(text_input)
        if result['style_changed']:
            self.current_style = result['style']
            print(f"🎨 Style changed: {result['detected_keywords']}")
        return result
    
    def spawn_particles(self):
        """Spawn particles based on vision data and current style"""
        if len(self.particles) >= self.max_particles:
            return
        
        # Base spawn rate from style
        base_spawn_rate = int(self.current_style.get('spawn_rate', 1.0) * 10)
        
        # Motion-based particle spawning
        if self.motion_intensity > 0.01:
            motion_spawn_count = int(self.motion_intensity * 50 * self.current_style.get('spawn_rate', 1.0))
            
            for _ in range(min(motion_spawn_count, self.max_particles - len(self.particles))):
                self._spawn_motion_particle()
        
        # Color-based ambient particles
        if self.dominant_colors and len(self.particles) < self.max_particles * 0.7:
            color_spawn_count = min(3, self.max_particles - len(self.particles))
            for _ in range(color_spawn_count):
                self._spawn_color_particle()
        
        # General ambient particles (always spawn some)
        ambient_count = min(base_spawn_rate, self.max_particles - len(self.particles))
        for _ in range(ambient_count):
            self._spawn_ambient_particle()
    
    def _spawn_motion_particle(self):
        """Spawn particle based on motion detection"""
        if not self.motion_areas:
            return
        
        # Choose a motion area
        motion_area = random.choice(self.motion_areas)
        center_x, center_y = motion_area['center']
        
        # Add some randomness around the motion center
        spread = 50
        x = center_x + random.uniform(-spread, spread)
        y = center_y + random.uniform(-spread, spread)
        
        # Ensure particle is within bounds
        x = max(0, min(self.width, x))
        y = max(0, min(self.height, y))
        
        # Motion-based velocity
        motion_direction = self.current_style.get('motion_direction', 'random')
        speed_multiplier = self.current_style.get('speed_multiplier', 1.0)
        
        if motion_direction == 'upward':
            vx = random.uniform(-50, 50) * speed_multiplier
            vy = -random.uniform(100, 200) * speed_multiplier
        elif motion_direction == 'flowing':
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150) * speed_multiplier
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
        elif motion_direction == 'chaotic':
            vx = random.uniform(-200, 200) * speed_multiplier
            vy = random.uniform(-200, 200) * speed_multiplier
        else:  # random
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 120) * speed_multiplier
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
        
        vz = random.uniform(-30, 30) * speed_multiplier
        
        # Color from style or dominant colors
        if self.dominant_colors and random.random() < 0.6:
            # Use detected color
            color_data = random.choice(self.dominant_colors)
            base_color = color_data['color']
        else:
            # Use style color
            base_color = random.choice(self.current_style['colors'])
        
        # Add some variation to color
        r, g, b = base_color
        variation = 30
        r = max(0, min(255, r + random.randint(-variation, variation)))
        g = max(0, min(255, g + random.randint(-variation, variation)))
        b = max(0, min(255, b + random.randint(-variation, variation)))
        
        # Alpha based on motion intensity
        alpha = max(100, min(255, int(self.motion_intensity * 500 + 100)))
        
        # Size and life based on style and motion
        size = random.uniform(3, 12) * self.current_style.get('size_multiplier', 1.0)
        life = random.uniform(1.0, 3.0) * self.current_style.get('life_multiplier', 1.0)
        
        particle = VisionParticle(
            x=x, y=y, z=random.uniform(0, 100),
            vx=vx, vy=vy, vz=vz,
            size=size,
            color=(r, g, b, alpha),
            life=life,
            birth_time=self.time,
            particle_type='motion',
            source_area=(center_x, center_y)
        )
        
        self.particles.append(particle)
    
    def _spawn_color_particle(self):
        """Spawn particle based on dominant colors"""
        if not self.dominant_colors:
            return
        
        # Choose dominant color
        color_data = self.dominant_colors[0]  # Most dominant
        base_color = color_data['color']
        weight = color_data['weight']
        
        # Random position
        x = random.uniform(0, self.width)
        y = random.uniform(0, self.height)
        
        # Gentle movement for color particles
        speed_multiplier = self.current_style.get('speed_multiplier', 1.0) * 0.5
        vx = random.uniform(-50, 50) * speed_multiplier
        vy = random.uniform(-50, 50) * speed_multiplier
        vz = random.uniform(-20, 20) * speed_multiplier
        
        # Size based on color weight
        size = (3 + weight * 8) * self.current_style.get('size_multiplier', 1.0)
        
        # Life based on weight
        life = (1.0 + weight * 2.0) * self.current_style.get('life_multiplier', 1.0)
        
        # Alpha based on weight
        alpha = max(80, min(200, int(weight * 400 + 80)))
        
        particle = VisionParticle(
            x=x, y=y, z=random.uniform(0, 100),
            vx=vx, vy=vy, vz=vz,
            size=size,
            color=(*base_color, alpha),
            life=life,
            birth_time=self.time,
            particle_type='color',
            source_area=None
        )
        
        self.particles.append(particle)
    
    def _spawn_ambient_particle(self):
        """Spawn general ambient particles"""
        # Random position
        x = random.uniform(0, self.width)
        y = random.uniform(0, self.height)
        
        # Style-based movement
        motion_direction = self.current_style.get('motion_direction', 'random')
        speed_multiplier = self.current_style.get('speed_multiplier', 1.0) * 0.3
        
        if motion_direction == 'upward':
            vx = random.uniform(-30, 30) * speed_multiplier
            vy = -random.uniform(20, 80) * speed_multiplier
        elif motion_direction == 'falling':
            vx = random.uniform(-20, 20) * speed_multiplier
            vy = random.uniform(20, 60) * speed_multiplier
        else:
            vx = random.uniform(-40, 40) * speed_multiplier
            vy = random.uniform(-40, 40) * speed_multiplier
        
        vz = random.uniform(-15, 15) * speed_multiplier
        
        # Style color
        base_color = random.choice(self.current_style['colors'])
        
        # Smaller, more transparent ambient particles
        size = random.uniform(2, 6) * self.current_style.get('size_multiplier', 1.0)
        life = random.uniform(2.0, 5.0) * self.current_style.get('life_multiplier', 1.0)
        alpha = random.randint(60, 120)
        
        particle = VisionParticle(
            x=x, y=y, z=random.uniform(0, 100),
            vx=vx, vy=vy, vz=vz,
            size=size,
            color=(*base_color, alpha),
            life=life,
            birth_time=self.time,
            particle_type='ambient',
            source_area=None
        )
        
        self.particles.append(particle)
    
    def update_particles(self, dt: float):
        """Update all particles"""
        self.time += dt
        
        # Update existing particles
        particles_to_remove = []
        
        for i, particle in enumerate(self.particles):
            # Update position
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.z += particle.vz * dt
            
            # Apply gravity/forces based on particle type
            if particle.particle_type == 'motion':
                particle.vy += 50 * dt  # Slight gravity
            
            # Update life
            age = self.time - particle.birth_time
            if age > particle.life:
                particles_to_remove.append(i)
                continue
            
            # Update size and alpha based on age
            life_ratio = age / particle.life
            size_factor = 1.0 - life_ratio * 0.5  # Shrink over time
            alpha_factor = 1.0 - life_ratio  # Fade out
            
            particle.size = max(1, particle.size * size_factor)
            r, g, b, _ = particle.color
            new_alpha = max(0, min(255, int(particle.color[3] * alpha_factor)))
            particle.color = (r, g, b, new_alpha)
            
            # Remove particles that go off screen or become too transparent
            if (particle.x < -100 or particle.x > self.width + 100 or
                particle.y < -100 or particle.y > self.height + 100 or
                new_alpha < 10):
                particles_to_remove.append(i)
        
        # Remove dead particles
        for i in reversed(particles_to_remove):
            self.particles.pop(i)
    
    def render(self, surface: pygame.Surface):
        """Render the visualization"""
        # Clear with style background
        bg_color = (10, 10, 15)  # Dark background
        surface.fill(bg_color)
        
        # Update trail surface (fade previous trails)
        trail_fade = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        trail_fade.fill((0, 0, 0, 5))  # Slight fade
        self.trail_surface.blit(trail_fade, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        
        # Draw particles
        for particle in self.particles:
            # 3D projection for depth effect
            depth_factor = 1.0 - (particle.z / 200.0)
            screen_size = max(1, particle.size * depth_factor)
            
            # Draw particle
            if particle.color[3] > 10:  # Only draw if visible
                try:
                    # Main particle
                    pygame.draw.circle(
                        surface,
                        particle.color[:3],
                        (int(particle.x), int(particle.y)),
                        int(screen_size)
                    )
                    
                    # Add glow effect for motion particles
                    if particle.particle_type == 'motion' and screen_size > 3:
                        glow_color = (*particle.color[:3], max(10, particle.color[3] // 3))
                        glow_surface = pygame.Surface((int(screen_size * 4), int(screen_size * 4)), pygame.SRCALPHA)
                        pygame.draw.circle(
                            glow_surface,
                            glow_color,
                            (int(screen_size * 2), int(screen_size * 2)),
                            int(screen_size * 2)
                        )
                        surface.blit(glow_surface, 
                                   (int(particle.x - screen_size * 2), int(particle.y - screen_size * 2)),
                                   special_flags=pygame.BLEND_ALPHA_SDL2)
                        
                except (ValueError, OverflowError):
                    # Skip invalid particles
                    continue
        
        # Draw motion areas (debug visualization)
        if False:  # Set to True for debugging
            for area in self.motion_areas:
                center = area['center']
                pygame.draw.circle(surface, (255, 255, 0), center, 20, 2)
        
        # Draw UI info
        self._draw_ui_info(surface)
    
    def _draw_ui_info(self, surface: pygame.Surface):
        """Draw UI information"""
        # Current style
        style_info = self.style_processor.get_current_style_info()
        style_text = self.font.render(f"Style: {style_info['name'].title()}", True, (255, 255, 255))
        surface.blit(style_text, (10, 10))
        
        # Vision stats
        stats = [
            f"Motion: {self.motion_intensity:.3f}",
            f"Energy: {self.visual_energy:.3f}",
            f"Particles: {len(self.particles)}",
            f"Colors: {len(self.dominant_colors)}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.small_font.render(stat, True, (200, 200, 200))
            surface.blit(stat_text, (10, 40 + i * 20))
        
        # Instructions
        instructions = [
            "🎥 Move in front of camera for motion particles",
            "💬 Type text commands to change style",
            "ESC - Exit  |  R - Reset particles"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, (150, 150, 150))
            surface.blit(inst_text, (10, self.height - 80 + i * 20))


class VisionCreativeStudio:
    """Main vision-powered creative studio interface"""
    
    def __init__(self, width: int = 1400, height: int = 900):
        pygame.init()
        
        self.width = width
        self.height = height
        
        # Create window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Vision AI Creative Studio")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Vision system
        self.vision_analyzer = None
        self.setup_vision()
        
        # Visualization engine
        vis_width = width - 300  # Leave space for camera feed
        self.vis_engine = VisionVisualizationEngine(vis_width, height)
        
        # Text input
        self.text_input = ""
        self.input_active = False
        self.font = pygame.font.Font(None, 32)
        
        # Camera feed display
        self.camera_surface = pygame.Surface((280, 210))
        
    def setup_vision(self):
        """Setup vision capture system"""
        try:
            self.vision_analyzer = VisionAnalyzer(callback=self.vision_callback)
            if self.vision_analyzer.start_capture():
                print("🎥 Vision system started!")
            else:
                print("❌ Failed to start camera")
        except Exception as e:
            print(f"Vision setup failed: {e}")
    
    def vision_callback(self, metrics: Dict):
        """Process vision data for visualization"""
        self.vis_engine.update_vision_data(metrics)
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    # Reset particles
                    self.vis_engine.particles.clear()
                elif event.key == pygame.K_RETURN:
                    # Process text input
                    if self.text_input.strip():
                        self.vis_engine.apply_text_style(self.text_input)
                        self.text_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.text_input = self.text_input[:-1]
                else:
                    # Add character to text input
                    if event.unicode.isprintable():
                        self.text_input += event.unicode
    
    def update_camera_display(self):
        """Update camera feed display"""
        if self.vision_analyzer:
            frame = self.vision_analyzer.get_current_frame()
            if frame is not None:
                # Resize frame for display
                frame_resized = cv2.resize(frame, (280, 210))
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                # Convert to pygame surface
                frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
                self.camera_surface.blit(frame_surface, (0, 0))
    
    def draw_ui(self):
        """Draw user interface elements"""
        # Camera feed
        camera_x = self.width - 290
        pygame.draw.rect(self.screen, (50, 50, 50), (camera_x - 5, 5, 290, 220))
        self.screen.blit(self.camera_surface, (camera_x, 10))
        
        # Camera label
        camera_label = self.font.render("Camera Feed", True, (255, 255, 255))
        self.screen.blit(camera_label, (camera_x, 230))
        
        # Text input box
        input_y = self.height - 60
        input_rect = pygame.Rect(10, input_y, self.width - 310, 40)
        pygame.draw.rect(self.screen, (30, 30, 30), input_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), input_rect, 2)
        
        # Text input content
        input_text = self.font.render(f"💬 {self.text_input}", True, (255, 255, 255))
        self.screen.blit(input_text, (input_rect.x + 10, input_rect.y + 8))
        
        # Input prompt
        prompt_text = "Type style commands like 'fire dance', 'blue water flow', 'space stars'..."
        prompt_surface = pygame.font.Font(None, 24).render(prompt_text, True, (150, 150, 150))
        self.screen.blit(prompt_surface, (10, input_y - 25))
    
    def run(self):
        """Main application loop"""
        print("🎨 Vision AI Creative Studio Started!")
        print("🎥 Point camera at yourself and move around")
        print("💬 Type text commands to change particle styles")
        print("Controls: R - Reset particles, ESC - Exit")
        
        try:
            while self.running:
                dt = self.clock.tick(60) / 1000.0
                
                # Handle events
                self.handle_events()
                
                # Update systems
                self.vis_engine.spawn_particles()
                self.vis_engine.update_particles(dt)
                self.update_camera_display()
                
                # Render
                # Create visualization surface
                vis_surface = pygame.Surface((self.width - 300, self.height))
                self.vis_engine.render(vis_surface)
                self.screen.blit(vis_surface, (0, 0))
                
                # Draw UI
                self.draw_ui()
                
                pygame.display.flip()
                
        except KeyboardInterrupt:
            print("\nSession interrupted by user")
        
        finally:
            # Cleanup
            if self.vision_analyzer:
                self.vision_analyzer.stop_capture()
            pygame.quit()
            print("🎨 Vision AI Creative Studio session ended")


if __name__ == "__main__":
    app = VisionCreativeStudio()
    app.run()