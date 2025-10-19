"""
Creative Audio Art Gallery
A reimagined gallery experience for exploring audio-visual art
"""

import pygame
import pygame_gui
import numpy as np
import math
import random
import time
from typing import Dict, List, Tuple, Optional
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.storage import DataStorage


class ArtPiece:
    """Represents a single piece of audio-visual art"""
    
    def __init__(self, x: float, y: float, width: float, height: float, 
                 title: str = "Untitled", artist: str = "Anonymous"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.artist = artist
        
        # Visual properties
        self.colors = self.generate_colors()
        self.pattern_type = random.choice(['waves', 'spirals', 'particles', 'flow', 'geometric'])
        self.animation_speed = random.uniform(0.5, 2.0)
        self.time_offset = random.uniform(0, 10)
        
        # Interaction
        self.hovered = False
        self.selected = False
        self.hover_scale = 1.0
        
    def generate_colors(self) -> List[Tuple[int, int, int]]:
        """Generate a harmonious color palette for this art piece"""
        palettes = [
            # Sunset
            [(255, 94, 77), (255, 154, 0), (255, 206, 84), (255, 255, 255)],
            # Ocean
            [(0, 119, 190), (0, 180, 216), (144, 224, 239), (255, 255, 255)],
            # Forest
            [(34, 139, 34), (0, 128, 0), (173, 255, 47), (255, 255, 255)],
            # Purple Dream
            [(138, 43, 226), (186, 85, 211), (221, 160, 221), (255, 255, 255)],
            # Fire
            [(255, 0, 0), (255, 165, 0), (255, 255, 0), (255, 255, 255)],
            # Neon
            [(57, 255, 20), (255, 20, 147), (0, 191, 255), (255, 255, 255)],
        ]
        return random.choice(palettes)
    
    def update(self, dt: float, current_time: float):
        """Update art piece animation"""
        # Smooth hover animation
        target_scale = 1.1 if self.hovered else 1.0
        self.hover_scale += (target_scale - self.hover_scale) * dt * 5
    
    def draw_waves_pattern(self, surface: pygame.Surface, time: float):
        """Draw animated wave pattern"""
        center_x, center_y = self.width // 2, self.height // 2
        
        for i in range(5):
            for angle in range(0, 360, 15):
                rad = math.radians(angle)
                wave_offset = math.sin(time * self.animation_speed + i * 0.5) * 20
                radius = 30 + i * 15 + wave_offset
                
                x = center_x + math.cos(rad) * radius
                y = center_y + math.sin(rad) * radius
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    color = self.colors[i % len(self.colors)]
                    alpha = int(255 * (1 - i / 5))
                    pygame.draw.circle(surface, (*color, alpha), (int(x), int(y)), 3)
    
    def draw_spirals_pattern(self, surface: pygame.Surface, time: float):
        """Draw animated spiral pattern"""
        center_x, center_y = self.width // 2, self.height // 2
        
        for spiral in range(3):
            points = []
            for t in range(0, 200):
                angle = t * 0.1 + time * self.animation_speed + spiral * 2
                radius = t * 0.5
                x = center_x + math.cos(angle) * radius
                y = center_y + math.sin(angle) * radius
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    points.append((x, y))
            
            if len(points) > 1:
                color = self.colors[spiral % len(self.colors)]
                for i in range(len(points) - 1):
                    pygame.draw.line(surface, color, points[i], points[i + 1], 2)
    
    def draw_particles_pattern(self, surface: pygame.Surface, time: float):
        """Draw animated particle pattern"""
        for i in range(30):
            angle = i * 0.2 + time * self.animation_speed
            radius = 50 + math.sin(time * 2 + i) * 30
            x = self.width // 2 + math.cos(angle) * radius
            y = self.height // 2 + math.sin(angle) * radius
            
            if 0 <= x < self.width and 0 <= y < self.height:
                color = self.colors[i % len(self.colors)]
                size = int(3 + math.sin(time * 3 + i) * 2)
                pygame.draw.circle(surface, color, (int(x), int(y)), size)
    
    def draw_flow_pattern(self, surface: pygame.Surface, time: float):
        """Draw animated flow pattern"""
        for y in range(10, int(self.height), 20):
            for x in range(10, int(self.width), 20):
                offset_x = math.sin(time * self.animation_speed + y * 0.01) * 10
                offset_y = math.cos(time * self.animation_speed + x * 0.01) * 10
                
                end_x = x + offset_x
                end_y = y + offset_y
                
                color_index = int((x + y) / 40) % len(self.colors)
                color = self.colors[color_index]
                
                pygame.draw.line(surface, color, (x, y), (end_x, end_y), 2)
    
    def draw_geometric_pattern(self, surface: pygame.Surface, time: float):
        """Draw animated geometric pattern"""
        center_x, center_y = self.width // 2, self.height // 2
        
        for i in range(4):
            size = 30 + i * 20 + math.sin(time * self.animation_speed + i) * 10
            rotation = time * self.animation_speed + i * 45
            
            # Calculate rectangle corners
            corners = []
            for corner in range(4):
                angle = math.radians(rotation + corner * 90)
                x = center_x + math.cos(angle) * size
                y = center_y + math.sin(angle) * size
                corners.append((x, y))
            
            color = self.colors[i % len(self.colors)]
            if len(corners) == 4:
                pygame.draw.polygon(surface, color, corners, 2)
    
    def render(self, surface: pygame.Surface, current_time: float):
        """Render the art piece"""
        # Create temporary surface for the art piece
        art_surface = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)
        art_surface.fill((20, 20, 30, 200))  # Dark background
        
        # Draw pattern based on type
        adjusted_time = current_time + self.time_offset
        
        if self.pattern_type == 'waves':
            self.draw_waves_pattern(art_surface, adjusted_time)
        elif self.pattern_type == 'spirals':
            self.draw_spirals_pattern(art_surface, adjusted_time)
        elif self.pattern_type == 'particles':
            self.draw_particles_pattern(art_surface, adjusted_time)
        elif self.pattern_type == 'flow':
            self.draw_flow_pattern(art_surface, adjusted_time)
        elif self.pattern_type == 'geometric':
            self.draw_geometric_pattern(art_surface, adjusted_time)
        
        # Apply hover scaling
        if self.hover_scale != 1.0:
            scaled_width = int(self.width * self.hover_scale)
            scaled_height = int(self.height * self.hover_scale)
            art_surface = pygame.transform.scale(art_surface, (scaled_width, scaled_height))
            
            # Center the scaled surface
            offset_x = (scaled_width - self.width) // 2
            offset_y = (scaled_height - self.height) // 2
            surface.blit(art_surface, (self.x - offset_x, self.y - offset_y))
        else:
            surface.blit(art_surface, (self.x, self.y))
        
        # Draw border
        border_color = (255, 255, 255) if self.hovered else (100, 100, 100)
        border_width = 3 if self.hovered else 1
        pygame.draw.rect(surface, border_color, 
                        (self.x, self.y, self.width, self.height), border_width)
        
        # Draw title and artist
        if self.hovered:
            font = pygame.font.Font(None, 24)
            title_text = font.render(self.title, True, (255, 255, 255))
            artist_text = font.render(f"by {self.artist}", True, (200, 200, 200))
            
            # Background for text
            text_bg = pygame.Surface((max(title_text.get_width(), artist_text.get_width()) + 10, 50))
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(180)
            
            surface.blit(text_bg, (self.x, self.y + self.height + 5))
            surface.blit(title_text, (self.x + 5, self.y + self.height + 10))
            surface.blit(artist_text, (self.x + 5, self.y + self.height + 30))
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside art piece bounds"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)


class CreativeGalleryInterface:
    """Reimagined gallery interface as an art gallery"""
    
    def __init__(self, width: int = 1600, height: int = 1000, data_dir: str = "data"):
        pygame.init()
        
        self.width = width
        self.height = height
        
        # Create window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Audio Perception Gallery - Creative Art Space")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Gallery setup
        self.art_pieces: List[ArtPiece] = []
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 300
        
        # Data storage
        self.data_storage = DataStorage(data_dir)
        
        # Visual elements
        self.background_time = 0.0
        
        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 24)
        
        # Create gallery
        self.setup_gallery()
        
    def setup_gallery(self):
        """Setup the art gallery with pieces"""
        # Load actual recordings if available
        try:
            recordings = self.data_storage.get_all_records()
            print(f"Found {len(recordings)} recordings")
        except:
            recordings = []
            print("No recordings found, creating demo gallery")
        
        # Gallery layout parameters
        cols = 4
        piece_width = 200
        piece_height = 150
        spacing_x = 250
        spacing_y = 200
        start_x = 100
        start_y = 150
        
        # Create art pieces
        piece_count = max(12, len(recordings))  # At least 12 pieces for demo
        
        for i in range(piece_count):
            row = i // cols
            col = i % cols
            
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            
            if i < len(recordings):
                # Use actual recording data
                record = recordings[i]
                title = record.title or f"Recording {i+1}"
                artist = record.user_name or "Anonymous"
            else:
                # Generate demo pieces
                titles = [
                    "Whispers of Dawn", "Electric Dreams", "Ocean Memories", 
                    "Urban Symphony", "Digital Rainfall", "Neon Nights",
                    "Cosmic Dance", "Silent Thunder", "Ethereal Winds",
                    "Mechanical Heart", "Frozen Echoes", "Liquid Light"
                ]
                artists = [
                    "SoundWave", "AudioArtist", "VoicePainter", "EchoMaster",
                    "FrequencyPoet", "VibeCreator", "AudioAlchemist", "SonicDreamer"
                ]
                
                title = titles[i % len(titles)]
                artist = artists[i % len(artists)]
            
            art_piece = ArtPiece(x, y, piece_width, piece_height, title, artist)
            self.art_pieces.append(art_piece)
        
        print(f"Gallery created with {len(self.art_pieces)} art pieces")
    
    def handle_events(self):
        """Handle input events"""
        keys = pygame.key.get_pressed()
        dt = self.clock.get_time() / 1000.0
        
        # Camera movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_x -= self.camera_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x += self.camera_speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_y -= self.camera_speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y += self.camera_speed * dt
        
        # Mouse interaction
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + self.camera_x
        world_mouse_y = mouse_y + self.camera_y
        
        # Update hover states
        for piece in self.art_pieces:
            piece.hovered = piece.contains_point(world_mouse_x, world_mouse_y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    # Regenerate gallery
                    self.art_pieces.clear()
                    self.setup_gallery()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for piece in self.art_pieces:
                        if piece.contains_point(world_mouse_x, world_mouse_y):
                            print(f"Selected: '{piece.title}' by {piece.artist}")
    
    def draw_background(self, surface: pygame.Surface):
        """Draw animated gallery background"""
        # Dark gallery background with subtle animation
        base_color = (15, 15, 25)
        surface.fill(base_color)
        
        # Animated grid pattern
        grid_spacing = 100
        grid_color = (25, 25, 35)
        
        # Calculate grid offset based on camera
        grid_offset_x = int(self.camera_x % grid_spacing)
        grid_offset_y = int(self.camera_y % grid_spacing)
        
        # Draw vertical lines
        for x in range(-grid_offset_x, self.width + grid_spacing, grid_spacing):
            pygame.draw.line(surface, grid_color, (x, 0), (x, self.height), 1)
        
        # Draw horizontal lines
        for y in range(-grid_offset_y, self.height + grid_spacing, grid_spacing):
            pygame.draw.line(surface, grid_color, (0, y), (self.width, y), 1)
        
        # Subtle floating particles for ambiance
        for i in range(20):
            x = (self.background_time * 50 + i * 123) % (self.width + 200) - 100
            y = (self.background_time * 30 + i * 456) % (self.height + 200) - 100
            alpha = int(50 + 30 * math.sin(self.background_time + i))
            color = (100, 100, 150, alpha)
            
            particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            particle_surface.fill(color)
            surface.blit(particle_surface, (x, y))
    
    def draw_ui(self, surface: pygame.Surface):
        """Draw UI elements"""
        # Gallery title
        title_text = self.title_font.render("Audio Perception Gallery", True, (255, 255, 255))
        title_bg = pygame.Surface((title_text.get_width() + 20, title_text.get_height() + 10))
        title_bg.fill((0, 0, 0))
        title_bg.set_alpha(150)
        
        surface.blit(title_bg, (20, 20))
        surface.blit(title_text, (30, 25))
        
        # Instructions
        instructions = [
            "Navigate: WASD or Arrow Keys",
            "Click on art pieces to select",
            "R - Regenerate gallery",
            "ESC - Exit gallery"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.info_font.render(instruction, True, (200, 200, 200))
            surface.blit(text, (20, self.height - 100 + i * 20))
        
        # Gallery stats
        stats_text = f"Viewing {len(self.art_pieces)} pieces"
        stats = self.info_font.render(stats_text, True, (150, 150, 200))
        surface.blit(stats, (self.width - 200, 30))
    
    def run(self):
        """Main gallery loop"""
        print("🎨 Creative Gallery Mode Started!")
        print("Navigate the gallery with WASD or arrow keys")
        print("Click on art pieces to explore them")
        print("Press ESC to exit")
        
        try:
            while self.running:
                dt = self.clock.tick(60) / 1000.0
                self.background_time += dt
                
                # Handle events
                self.handle_events()
                
                # Update art pieces
                current_time = time.time()
                for piece in self.art_pieces:
                    piece.update(dt, current_time)
                
                # Render everything
                self.draw_background(self.screen)
                
                # Create a surface for the world (affected by camera)
                world_surface = pygame.Surface((self.width * 3, self.height * 3), pygame.SRCALPHA)
                
                # Draw art pieces to world surface
                for piece in self.art_pieces:
                    piece.render(world_surface, current_time)
                
                # Blit world surface with camera offset
                self.screen.blit(world_surface, (-self.camera_x, -self.camera_y))
                
                # Draw UI (not affected by camera)
                self.draw_ui(self.screen)
                
                pygame.display.flip()
                
        except KeyboardInterrupt:
            print("\nGallery session interrupted by user")
        
        finally:
            pygame.quit()
            print("🖼️ Gallery session ended")


if __name__ == "__main__":
    gallery = CreativeGalleryInterface()
    gallery.run()