"""
Enhanced Audio Analysis Module
Real-time audio processing for visual effects generation
"""

import pyaudio
import numpy as np
import threading
import time
from typing import Dict, Callable, Optional
import math


class AudioAnalyzer:
    """Advanced audio analysis for multi-modal visual effects"""
    
    def __init__(self, 
                 chunk_size: int = 1024,
                 format: int = pyaudio.paInt16,
                 channels: int = 1,
                 rate: int = 44100,
                 callback: Optional[Callable] = None,
                 input_device_index: Optional[int] = None):
        """
        Initialize the Audio Analyzer
        
        Args:
            chunk_size: Number of frames per buffer
            format: Audio format
            channels: Number of audio channels
            rate: Sample rate
            callback: Callback function to receive audio data
            input_device_index: Specific audio input device to use (None for default)
        """
        self.chunk_size = chunk_size
        self.format = format
        self.channels = channels
        self.rate = rate
        self.callback = callback
        self.input_device_index = input_device_index
        
        # PyAudio instance
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        # Audio data storage
        self.is_recording = False
        self.audio_data = []
        self.current_metrics = {
            'amplitude': 0.0,
            'rms': 0.0,
            'peak': 0.0,
            'db': -60.0,
            'frequency': 0.0,
            'beat_detected': False,
            'energy': 0.0
        }
        
        # Enhanced analysis features
        self.beat_threshold = 1.5
        self.energy_history = []
        self.max_history = 50
        
        # Threading
        self.recording_thread = None
        
    def start_recording(self):
        """Start audio recording and analysis"""
        if self.is_recording:
            return
            
        try:
            self.is_recording = True
            
            # Open audio stream
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=self.input_device_index  # Use specified device or default
            )
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
            self.recording_thread.start()
            
            print("🎵 Audio analyzer started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Audio initialization failed: {e}")
            return False
        
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=1.0)
            
        print("🎵 Audio analyzer stopped")
        
    def _record_audio(self):
        """Record audio in a separate thread"""
        while self.is_recording:
            try:
                # Read audio data
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Convert to numpy array
                audio_array = np.frombuffer(data, dtype=np.int16)
                
                # Store audio data (keep limited history)
                self.audio_data.append(audio_array)
                if len(self.audio_data) > self.max_history:
                    self.audio_data.pop(0)
                
                # Analyze audio data
                metrics = self._analyze_audio(audio_array)
                self.current_metrics.update(metrics)
                
                # Call callback if provided
                if self.callback:
                    self.callback(self.current_metrics.copy())
                    
            except Exception as e:
                print(f"Error in audio recording: {e}")
                time.sleep(0.1)  # Brief pause on error
                
    def _analyze_audio(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Enhanced audio analysis with beat detection
        
        Args:
            audio_data: Raw audio data as numpy array
            
        Returns:
            Dictionary containing audio metrics
        """
        if len(audio_data) == 0:
            return {
                'amplitude': 0.0,
                'rms': 0.0,
                'peak': 0.0,
                'db': -60.0,
                'frequency': 0.0,
                'beat_detected': False,
                'energy': 0.0
            }
            
        # Convert to float for better precision
        audio_float = audio_data.astype(np.float32)
        
        # Normalize to [-1, 1] range for consistent processing
        if self.format == pyaudio.paInt16:
            audio_float = audio_float / 32767.0
        elif self.format == pyaudio.paInt32:
            audio_float = audio_float / 2147483647.0
        
        # Basic metrics
        amplitude = np.mean(np.abs(audio_float))
        rms = np.sqrt(np.mean(audio_float ** 2))
        peak = np.max(np.abs(audio_float))
        
        # Calculate energy
        energy = np.sum(audio_float ** 2)
        
        # Decibel level (reference to full scale)
        epsilon = 1e-10
        db = 20 * np.log10(max(rms, epsilon))
        db = max(db, -60.0)
        
        # Dominant frequency
        frequency = self._calculate_frequency(audio_float)
        
        # Beat detection
        beat_detected = self._detect_beat(energy)
        
        return {
            'amplitude': float(amplitude),
            'rms': float(rms),
            'peak': float(peak),
            'db': float(db),
            'frequency': float(frequency),
            'beat_detected': beat_detected,
            'energy': float(energy)
        }
        
    def _calculate_frequency(self, audio_data: np.ndarray) -> float:
        """Calculate dominant frequency using FFT"""
        try:
            # Apply window function
            windowed = audio_data * np.hanning(len(audio_data))
            
            # Perform FFT
            fft = np.fft.rfft(windowed)
            magnitude = np.abs(fft)
            
            # Find peak frequency
            peak_bin = np.argmax(magnitude)
            frequency = peak_bin * self.rate / (2 * len(magnitude))
            
            return frequency
            
        except Exception:
            return 0.0
            
    def _detect_beat(self, current_energy: float) -> bool:
        """Simple beat detection based on energy threshold"""
        self.energy_history.append(current_energy)
        
        if len(self.energy_history) > 10:
            self.energy_history.pop(0)
            
        if len(self.energy_history) < 5:
            return False
            
        # Calculate average energy
        avg_energy = np.mean(self.energy_history[:-1])
        
        # Beat detected if current energy significantly exceeds average
        return current_energy > avg_energy * self.beat_threshold
            
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current audio metrics"""
        return self.current_metrics.copy()
        
    def get_normalized_metrics(self) -> Dict[str, float]:
        """Get normalized audio metrics (0.0 to 1.0 range)"""
        metrics = self.current_metrics.copy()
        
        # Normalize amplitude (0-5000 to 0-1)
        metrics['amplitude_norm'] = min(metrics['amplitude'] / 5000.0, 1.0)
        
        # Normalize RMS (0-5000 to 0-1)
        metrics['rms_norm'] = min(metrics['rms'] / 5000.0, 1.0)
        
        # Normalize peak (0-32767 to 0-1)
        metrics['peak_norm'] = min(metrics['peak'] / 32767.0, 1.0)
        
        # Normalize dB (-60 to 0 dB to 0-1)
        metrics['db_norm'] = max((metrics['db'] + 60.0) / 60.0, 0.0)
        
        # Normalize frequency (0-22050 Hz to 0-1)
        metrics['frequency_norm'] = min(metrics['frequency'] / 22050.0, 1.0)
        
        # Energy normalization (adaptive)
        if self.energy_history:
            max_energy = max(self.energy_history) if self.energy_history else 1.0
            metrics['energy_norm'] = min(metrics['energy'] / max(max_energy, 1000.0), 1.0)
        else:
            metrics['energy_norm'] = 0.0
        
        return metrics
        
    def get_audio_data(self) -> list:
        """Get stored audio data"""
        return self.audio_data.copy()
        
    def clear_audio_data(self):
        """Clear stored audio data"""
        self.audio_data.clear()
        self.energy_history.clear()
        
    def is_active(self) -> bool:
        """Check if audio analysis is active"""
        return self.is_recording
        
    def get_volume_level(self) -> float:
        """Get current volume level (0.0 to 1.0) - improved sensitivity"""
        metrics = self.get_current_metrics()
        # Use amplitude instead of db_norm for better responsiveness
        amplitude = metrics.get('amplitude', 0.0)
        # Scale amplitude to be more sensitive to quiet sounds
        volume = min(1.0, amplitude * 5000.0)  # Amplify by 5000x for extreme sensitivity
        return volume
    
    @staticmethod
    def find_best_input_device() -> Optional[int]:
        """Find the best microphone input device"""
        p = pyaudio.PyAudio()
        
        best_device = None
        best_score = -1
        
        try:
            for i in range(p.get_device_count()):
                try:
                    info = p.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        name = info['name'].lower()
                        score = 0
                        
                        # Prefer certain types of devices
                        if 'microphone' in name:
                            score += 10
                        if 'array' in name:
                            score += 5
                        if 'headset' in name:
                            score += 3
                        if 'soundwire' in name or 'realtek' in name:
                            score += 2
                        
                        # Avoid virtual/streaming devices for real audio
                        if any(avoid in name for avoid in ['steam', 'virtual', 'oculus']):
                            score -= 5
                        
                        if score > best_score:
                            best_score = score
                            best_device = i
                            
                except Exception:
                    continue
                    
        except Exception:
            pass
        finally:
            p.terminate()
            
        return best_device
    
    def start_visual_mode(self, effects_engine=None):
        """Start audio-only visual mode with spectrum display"""
        import pygame
        import math
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Audio Analysis Mode")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 24)
        
        # Start audio recording
        self.start_recording()
        print("🎵 Audio analysis active - Press 'Q' or ESC to quit")
        
        running = True
        spectrum_history = []
        
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_q, pygame.K_ESCAPE):
                            running = False
                
                # Clear screen with dark background
                screen.fill((10, 10, 30))
                
                # Get current audio metrics
                metrics = self.get_current_metrics()
                
                # Draw audio level bar
                level = self.get_volume_level()
                bar_width = int(level * 600)
                color = (
                    int(255 * level),
                    int(255 * (1 - level)),
                    100
                )
                pygame.draw.rect(screen, color, (100, 100, bar_width, 30))
                pygame.draw.rect(screen, (100, 100, 100), (100, 100, 600, 30), 2)
                
                # Draw beat indicator
                if metrics.get('beat_detected', False):
                    pygame.draw.circle(screen, (255, 255, 0), (50, 115), 20)
                else:
                    pygame.draw.circle(screen, (50, 50, 50), (50, 115), 20, 2)
                
                # Draw frequency spectrum visualization
                if len(self.audio_data) > 0:
                    recent_data = self.audio_data[-self.chunk_size:]
                    if len(recent_data) == self.chunk_size:
                        # Calculate FFT for frequency spectrum
                        fft = np.fft.fft(recent_data)
                        freqs = np.abs(fft[:len(fft)//2])
                        
                        # Normalize and draw spectrum
                        if len(freqs) > 0:
                            max_freq = np.max(freqs) if np.max(freqs) > 0 else 1
                            freqs_normalized = freqs / max_freq
                            
                            bar_width = 600 // len(freqs_normalized[:100])
                            for i, freq in enumerate(freqs_normalized[:100]):
                                height = int(freq * 200)
                                color_intensity = int(freq * 255)
                                color = (color_intensity, 100, 255 - color_intensity)
                                pygame.draw.rect(screen, color, 
                                               (100 + i * bar_width, 400 - height, 
                                                bar_width - 1, height))
                
                # Display metrics text
                y_offset = 200
                for key, value in metrics.items():
                    if isinstance(value, float):
                        text = f"{key}: {value:.3f}"
                    else:
                        text = f"{key}: {value}"
                    text_surface = font.render(text, True, (255, 255, 255))
                    screen.blit(text_surface, (100, y_offset))
                    y_offset += 25
                
                # Instructions
                inst_text = font.render("Press 'Q' or ESC to quit", True, (150, 150, 150))
                screen.blit(inst_text, (100, 550))
                
                pygame.display.flip()
                clock.tick(30)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_recording()
            pygame.quit()
            print("🎵 Audio mode stopped")
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_recording()
        if hasattr(self, 'p'):
            self.p.terminate()


# Utility functions
def db_to_linear(db: float) -> float:
    """Convert decibels to linear scale"""
    return 10 ** (db / 20.0)


def linear_to_db(linear: float) -> float:
    """Convert linear scale to decibels"""
    return 20 * math.log10(max(linear, 1e-10))


def smooth_value(current: float, target: float, smooth_factor: float = 0.1) -> float:
    """Smooth value transitions for better visual effects"""
    return current + (target - current) * smooth_factor