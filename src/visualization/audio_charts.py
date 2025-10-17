"""
Real-time Audio Visualization Charts
Creates waveform, spectrum, and meter displays for live audio feedback
"""

import pygame
import numpy as np
import math
from typing import Dict, List, Tuple, Optional
from collections import deque


class WaveformChart:
    """Real-time waveform display"""
    
    def __init__(self, width: int, height: int, max_samples: int = 1024):
        """
        Initialize waveform chart
        
        Args:
            width: Chart width in pixels
            height: Chart height in pixels
            max_samples: Maximum number of samples to display
        """
        self.width = width
        self.height = height
        self.max_samples = max_samples
        
        # Audio data buffer
        self.audio_buffer = deque(maxlen=max_samples)
        
        # Chart settings
        self.background_color = (20, 20, 30)
        self.grid_color = (40, 40, 50)
        self.waveform_color = (0, 255, 100)
        self.center_line_color = (60, 60, 80)
        
        # Initialize with zeros
        for _ in range(max_samples):
            self.audio_buffer.append(0.0)
    
    def update(self, audio_data: np.ndarray):
        """
        Update waveform with new audio data
        
        Args:
            audio_data: New audio samples
        """
        if len(audio_data) == 0:
            return
            
        # Normalize audio data to -1.0 to 1.0 range
        normalized = audio_data.astype(np.float32) / 32767.0
        
        # Add new samples to buffer
        for sample in normalized:
            self.audio_buffer.append(sample)
    
    def draw(self, surface: pygame.Surface, x: int, y: int):
        """
        Draw waveform chart
        
        Args:
            surface: Pygame surface to draw on
            x: X position of chart
            y: Y position of chart
        """
        # Create chart surface
        chart_surface = pygame.Surface((self.width, self.height))
        chart_surface.fill(self.background_color)
        
        # Draw grid lines
        self._draw_grid(chart_surface)
        
        # Draw center line
        center_y = self.height // 2
        pygame.draw.line(chart_surface, self.center_line_color, 
                        (0, center_y), (self.width, center_y), 1)
        
        # Draw waveform
        if len(self.audio_buffer) > 1:
            points = []
            for i, sample in enumerate(self.audio_buffer):
                pixel_x = int((i / len(self.audio_buffer)) * self.width)
                pixel_y = int(center_y - (sample * (self.height // 2 - 10)))
                pixel_y = max(5, min(self.height - 5, pixel_y))
                points.append((pixel_x, pixel_y))
            
            # Draw waveform line
            if len(points) > 1:
                pygame.draw.lines(chart_surface, self.waveform_color, False, points, 2)
        
        # Draw border
        pygame.draw.rect(chart_surface, (100, 100, 120), 
                        (0, 0, self.width, self.height), 2)
        
        # Blit to main surface
        surface.blit(chart_surface, (x, y))
    
    def _draw_grid(self, surface: pygame.Surface):
        """Draw grid lines on chart"""
        # Horizontal grid lines
        for i in range(1, 5):
            y = int((i / 5) * self.height)
            pygame.draw.line(surface, self.grid_color, (0, y), (self.width, y), 1)
        
        # Vertical grid lines
        for i in range(1, 10):
            x = int((i / 10) * self.width)
            pygame.draw.line(surface, self.grid_color, (x, 0), (x, self.height), 1)


class SpectrumChart:
    """Real-time frequency spectrum display"""
    
    def __init__(self, width: int, height: int, num_bins: int = 64, sample_rate: int = 44100):
        """
        Initialize spectrum chart
        
        Args:
            width: Chart width in pixels
            height: Chart height in pixels
            num_bins: Number of frequency bins to display
            sample_rate: Audio sample rate
        """
        self.width = width
        self.height = height
        self.num_bins = num_bins
        self.sample_rate = sample_rate
        
        # Spectrum data
        self.spectrum_data = np.zeros(num_bins)
        self.smoothed_spectrum = np.zeros(num_bins)
        
        # Chart settings
        self.background_color = (20, 20, 30)
        self.grid_color = (40, 40, 50)
        self.bar_colors = [(255, 100, 0), (255, 200, 0), (0, 255, 100)]
        
        # Smoothing factor for spectrum animation
        self.smooth_factor = 0.3
    
    def update(self, audio_data: np.ndarray):
        """
        Update spectrum with new audio data
        
        Args:
            audio_data: New audio samples
        """
        if len(audio_data) < 256:
            return
        
        # Apply window function
        windowed = audio_data[:1024] * np.hanning(min(len(audio_data), 1024))
        
        # Compute FFT
        fft = np.fft.rfft(windowed)
        magnitude = np.abs(fft)
        
        # Group frequencies into bins
        bin_size = len(magnitude) // self.num_bins
        for i in range(self.num_bins):
            start_idx = i * bin_size
            end_idx = (i + 1) * bin_size
            if end_idx <= len(magnitude):
                self.spectrum_data[i] = np.mean(magnitude[start_idx:end_idx])
        
        # Normalize
        if np.max(self.spectrum_data) > 0:
            self.spectrum_data = self.spectrum_data / np.max(self.spectrum_data)
        
        # Smooth the spectrum for better visual effect
        self.smoothed_spectrum = (self.smoothed_spectrum * (1 - self.smooth_factor) + 
                                 self.spectrum_data * self.smooth_factor)
    
    def draw(self, surface: pygame.Surface, x: int, y: int):
        """
        Draw spectrum chart
        
        Args:
            surface: Pygame surface to draw on
            x: X position of chart
            y: Y position of chart
        """
        # Create chart surface
        chart_surface = pygame.Surface((self.width, self.height))
        chart_surface.fill(self.background_color)
        
        # Draw grid
        self._draw_grid(chart_surface)
        
        # Draw spectrum bars
        bar_width = self.width // self.num_bins
        for i, magnitude in enumerate(self.smoothed_spectrum):
            bar_height = int(magnitude * (self.height - 20))
            bar_x = i * bar_width
            bar_y = self.height - bar_height - 10
            
            # Color based on frequency range
            if i < self.num_bins // 3:
                color = self.bar_colors[0]  # Low frequencies - red/orange
            elif i < 2 * self.num_bins // 3:
                color = self.bar_colors[1]  # Mid frequencies - yellow
            else:
                color = self.bar_colors[2]  # High frequencies - green
            
            # Draw bar with gradient effect
            for j in range(bar_height):
                alpha = 255 - int((j / bar_height) * 100) if bar_height > 0 else 255
                fade_color = (*color, alpha)
                pygame.draw.line(chart_surface, color,
                               (bar_x + 1, bar_y + j), (bar_x + bar_width - 1, bar_y + j))
        
        # Draw border
        pygame.draw.rect(chart_surface, (100, 100, 120), 
                        (0, 0, self.width, self.height), 2)
        
        # Blit to main surface
        surface.blit(chart_surface, (x, y))
    
    def _draw_grid(self, surface: pygame.Surface):
        """Draw grid lines on chart"""
        # Horizontal grid lines
        for i in range(1, 5):
            y = int((i / 5) * self.height)
            pygame.draw.line(surface, self.grid_color, (0, y), (self.width, y), 1)


class AudioMeter:
    """Audio level meters for amplitude, RMS, and dB"""
    
    def __init__(self, width: int, height: int):
        """
        Initialize audio meter
        
        Args:
            width: Meter width in pixels
            height: Meter height in pixels
        """
        self.width = width
        self.height = height
        
        # Meter values
        self.amplitude = 0.0
        self.rms = 0.0
        self.db = -60.0
        self.peak = 0.0
        
        # Visual settings
        self.background_color = (20, 20, 30)
        self.border_color = (100, 100, 120)
        self.label_color = (200, 200, 200)
        self.meter_colors = {
            'low': (0, 255, 0),      # Green
            'mid': (255, 255, 0),    # Yellow
            'high': (255, 100, 0),   # Orange
            'peak': (255, 0, 0)      # Red
        }
        
        # Font for labels
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)
    
    def update(self, metrics: Dict[str, float]):
        """
        Update meter values
        
        Args:
            metrics: Dictionary containing audio metrics
        """
        self.amplitude = metrics.get('amplitude_norm', 0.0)
        self.rms = metrics.get('rms_norm', 0.0)
        self.db = metrics.get('db', -60.0)
        self.peak = metrics.get('peak_norm', 0.0)
    
    def draw(self, surface: pygame.Surface, x: int, y: int):
        """
        Draw audio meters
        
        Args:
            surface: Pygame surface to draw on
            x: X position of meters
            y: Y position of meters
        """
        # Create meter surface
        meter_surface = pygame.Surface((self.width, self.height))
        meter_surface.fill(self.background_color)
        
        # Draw individual meters
        meter_width = (self.width - 40) // 4
        meter_height = self.height - 60
        
        meters = [
            ("AMP", self.amplitude),
            ("RMS", self.rms),
            ("PEAK", self.peak),
            ("dB", max(0, (self.db + 60) / 60))  # Normalize dB to 0-1
        ]
        
        for i, (label, value) in enumerate(meters):
            meter_x = 10 + i * (meter_width + 5)
            meter_y = 40
            
            # Draw meter background
            pygame.draw.rect(meter_surface, (40, 40, 50),
                           (meter_x, meter_y, meter_width, meter_height))
            
            # Draw meter fill
            fill_height = int(value * meter_height)
            fill_y = meter_y + meter_height - fill_height
            
            # Color based on level
            if value < 0.3:
                color = self.meter_colors['low']
            elif value < 0.6:
                color = self.meter_colors['mid']
            elif value < 0.8:
                color = self.meter_colors['high']
            else:
                color = self.meter_colors['peak']
            
            if fill_height > 0:
                pygame.draw.rect(meter_surface, color,
                               (meter_x + 2, fill_y, meter_width - 4, fill_height))
            
            # Draw meter border
            pygame.draw.rect(meter_surface, self.border_color,
                           (meter_x, meter_y, meter_width, meter_height), 2)
            
            # Draw label
            label_surface = self.font.render(label, True, self.label_color)
            label_rect = label_surface.get_rect(center=(meter_x + meter_width // 2, 20))
            meter_surface.blit(label_surface, label_rect)
            
            # Draw value
            if label == "dB":
                value_text = f"{self.db:.1f}"
            else:
                value_text = f"{value:.2f}"
            value_surface = self.font.render(value_text, True, self.label_color)
            value_rect = value_surface.get_rect(center=(meter_x + meter_width // 2, meter_y + meter_height + 15))
            meter_surface.blit(value_surface, value_rect)
        
        # Draw border around entire meter
        pygame.draw.rect(meter_surface, self.border_color, 
                        (0, 0, self.width, self.height), 2)
        
        # Blit to main surface
        surface.blit(meter_surface, (x, y))


class LiveBarChart:
    """Live updating bar chart for real-time audio visualization"""
    
    def __init__(self, width: int = 400, height: int = 300, num_bars: int = 32):
        """
        Initialize live bar chart
        
        Args:
            width: Chart width
            height: Chart height  
            num_bars: Number of frequency bars
        """
        self.width = width
        self.height = height
        self.num_bars = num_bars
        
        # Bar data
        self.bar_heights = np.zeros(num_bars)
        self.smoothed_heights = np.zeros(num_bars)
        
        # Visual settings
        self.background_color = (10, 10, 15)
        self.border_color = (60, 60, 80)
        self.smooth_factor = 0.15
        
        # Color gradients for bars
        self.bar_colors = [
            (0, 255, 100),    # Green (low)
            (100, 255, 50),   # Yellow-green
            (200, 255, 0),    # Yellow
            (255, 200, 0),    # Orange
            (255, 100, 0),    # Red-orange
            (255, 0, 0),      # Red (high)
        ]
        
        pygame.font.init()
        self.font = pygame.font.Font(None, 16)
    
    def update(self, audio_data: np.ndarray):
        """
        Update bar chart with audio data
        
        Args:
            audio_data: Raw audio samples
        """
        if len(audio_data) < 256:
            return
        
        # Convert to float and normalize to [-1, 1] range
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32767.0
        elif audio_data.dtype == np.int32:
            audio_data = audio_data.astype(np.float32) / 2147483647.0
        
        # Apply window and compute FFT
        chunk_size = min(len(audio_data), 1024)
        windowed = audio_data[:chunk_size] * np.hanning(chunk_size)
        fft = np.fft.rfft(windowed)
        magnitude = np.abs(fft)
        
        # Group into bars with improved normalization
        bar_size = max(1, len(magnitude) // self.num_bars)
        
        for i in range(self.num_bars):
            start_idx = i * bar_size
            end_idx = min((i + 1) * bar_size, len(magnitude))
            if start_idx < len(magnitude):
                # Use average magnitude in this frequency band
                bar_value = np.mean(magnitude[start_idx:end_idx])
                
                # Simple linear scaling - much more visible
                # Scale based on typical expected values
                self.bar_heights[i] = min(bar_value / 50.0, 1.0)  # Increased sensitivity
            else:
                self.bar_heights[i] = 0.0
        
        # Smooth the bars for better animation
        self.smoothed_heights = (self.smoothed_heights * (1 - self.smooth_factor) + 
                                self.bar_heights * self.smooth_factor)
    
    def get_bar_color(self, height: float, bar_index: int) -> Tuple[int, int, int]:
        """Get color for bar based on height and frequency"""
        # Color based on height
        color_idx = min(int(height * len(self.bar_colors)), len(self.bar_colors) - 1)
        base_color = self.bar_colors[color_idx]
        
        # Add some frequency-based hue shifting
        freq_shift = (bar_index / self.num_bars) * 0.3
        r, g, b = base_color
        
        # Slight color variation based on frequency
        if bar_index < self.num_bars // 3:  # Low frequencies - more red
            r = min(255, int(r * (1 + freq_shift)))
        elif bar_index > 2 * self.num_bars // 3:  # High frequencies - more blue
            b = min(255, int(b * (1 + freq_shift)))
        
        return (r, g, b)
    
    def draw(self, surface: pygame.Surface, x: int, y: int):
        """
        Draw the live bar chart
        
        Args:
            surface: Surface to draw on
            x: X position
            y: Y position
        """
        # Create chart surface
        chart_surface = pygame.Surface((self.width, self.height))
        chart_surface.fill(self.background_color)
        
        # Calculate bar dimensions
        bar_width = (self.width - 20) // self.num_bars - 2
        max_bar_height = self.height - 40
        
        # Draw bars
        for i, height in enumerate(self.smoothed_heights):
            # Calculate bar position and size
            bar_x = 10 + i * (bar_width + 2)
            bar_height = int(height * max_bar_height)
            bar_y = self.height - bar_height - 20
            
            # Get color for this bar
            color = self.get_bar_color(height, i)
            
            # Draw bar with gradient effect
            for j in range(bar_height):
                # Create gradient from bottom to top
                fade_factor = 1.0 - (j / max(bar_height, 1)) * 0.3
                fade_color = (
                    int(color[0] * fade_factor),
                    int(color[1] * fade_factor), 
                    int(color[2] * fade_factor)
                )
                pygame.draw.line(chart_surface, fade_color,
                               (bar_x, bar_y + j), (bar_x + bar_width - 1, bar_y + j))
            
            # Draw bar border
            if bar_height > 0:
                pygame.draw.rect(chart_surface, self.border_color,
                               (bar_x - 1, bar_y - 1, bar_width + 1, bar_height + 1), 1)
        
        # Draw frequency labels (simplified)
        label_positions = [0, self.num_bars // 4, self.num_bars // 2, 
                          3 * self.num_bars // 4, self.num_bars - 1]
        labels = ['Low', 'Bass', 'Mid', 'High', 'Treble']
        
        for pos, label in zip(label_positions, labels):
            label_x = 10 + pos * (bar_width + 2)
            label_surface = self.font.render(label, True, (150, 150, 150))
            chart_surface.blit(label_surface, (label_x, self.height - 15))
        
        # Draw title
        title_surface = self.font.render('Live Audio Spectrum', True, (200, 200, 200))
        chart_surface.blit(title_surface, (10, 5))
        
        # Draw border around entire chart
        pygame.draw.rect(chart_surface, self.border_color, 
                        (0, 0, self.width, self.height), 2)
        
        # Blit to main surface
        surface.blit(chart_surface, (x, y))


class RealtimeAudioVisualizer:
    """Combined real-time audio visualization display"""
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize combined visualizer
        
        Args:
            width: Total width
            height: Total height
        """
        self.width = width
        self.height = height
        
        # Create sub-components including new live bar chart
        chart_width = (width - 40) // 2
        chart_height = (height - 80) // 2
        
        self.waveform = WaveformChart(chart_width, chart_height)
        self.spectrum = SpectrumChart(chart_width, chart_height)
        self.meters = AudioMeter(180, chart_height)
        self.live_bars = LiveBarChart(chart_width, chart_height)
        
        # Background
        self.background_color = (15, 15, 25)
        
        # Font for titles
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 24)
    
    def update(self, audio_data: np.ndarray, metrics: Dict[str, float]):
        """
        Update all visualization components
        
        Args:
            audio_data: Raw audio samples
            metrics: Audio analysis metrics
        """
        self.waveform.update(audio_data)
        self.spectrum.update(audio_data)
        self.meters.update(metrics)
        self.live_bars.update(audio_data)
    
    def draw(self, surface: pygame.Surface, x: int = 0, y: int = 0):
        """
        Draw complete visualization
        
        Args:
            surface: Pygame surface to draw on
            x: X position
            y: Y position
        """
        # Create main surface
        viz_surface = pygame.Surface((self.width, self.height))
        viz_surface.fill(self.background_color)
        
        # Calculate positions for 2x2 grid layout
        chart_width = (self.width - 40) // 2
        chart_height = (self.height - 80) // 2
        
        # Positions: [top-left, top-right, bottom-left, bottom-right]
        positions = [
            (10, 30),                              # Waveform
            (chart_width + 30, 30),                # Live Bars
            (10, chart_height + 50),               # Spectrum  
            (chart_width + 30, chart_height + 50)  # Meters
        ]
        
        titles = ["Real-time Waveform", "Live Audio Bars", "Frequency Spectrum", "Audio Levels"]
        components = [self.waveform, self.live_bars, self.spectrum, self.meters]
        
        # Draw title
        main_title = self.title_font.render('Real-time Audio Visualization', True, (200, 200, 220))
        viz_surface.blit(main_title, (10, 5))
        
        # Draw each component with title
        for i, (component, title, pos) in enumerate(zip(components, titles, positions)):
            # Draw section title
            title_surface = self.title_font.render(title, True, (180, 180, 200))
            viz_surface.blit(title_surface, (pos[0], pos[1] - 20))
            
            # Draw component
            component.draw(viz_surface, pos[0], pos[1])
        
        # Blit to target surface
        surface.blit(viz_surface, (x, y))