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
                 channels: int = 2,
                 rate: int = 44100,
                 callback: Optional[Callable] = None,
                 input_device_index: Optional[int] = None):
        """
        Initialize the Audio Analyzer
        
        Args:
            chunk_size: Number of frames per buffer
            format: Audio format
            channels: Number of audio channels (will auto-adjust based on device capability)
            rate: Sample rate
            callback: Callback function to receive audio data
            input_device_index: Specific audio input device to use (None for default)
        """
        self.chunk_size = chunk_size
        self.format = format
        self.requested_channels = channels  # Store requested channels
        self.rate = rate
        self.callback = callback
        self.input_device_index = input_device_index
        
        # PyAudio instance
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        # Auto-detect and configure optimal channels
        self._configure_channels()
        
        # Audio data storage
        self.is_recording = False
        self.audio_data = []
        self.current_metrics = {
            'amplitude': 0.0,
            'frequency': 0.0,
            'beat_strength': 0.0,
            'energy': 0.0,
            'is_beat': False
        }
        
        # Beat detection
        self.energy_history = []
        self.beat_threshold = 1.3
        
        # Recording thread
        self.recording_thread = None
        
        # Visual mode flag
        self.visual_mode = False
        
        # Enhanced sensitivity
        self.sensitivity_multiplier = 5000
        
        # Color effects
        self.hue_offset = 0.0
        
        # Particle trails
        self.trails = []
        self.max_trail_points = 15
        
        
    def list_input_devices(self):
        try:
            print("\n Detected Audio Input Devices:")
            default_input_index = None
            try:
                default_input_index = self.p.get_default_input_device_info().get('index')
            except Exception:
                pass

            for i in range(self.p.get_device_count()):
                info = self.p.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0:
                    tag = " (Default)" if default_input_index == i else ""
                    print(
                        f" - index={i}{tag} | name={info.get('name')} | "
                        f"channels={info.get('maxInputChannels')} | "
                        f"defaultRate={info.get('defaultSampleRate')}"
                    )
            print()
        except Exception as e:
            print(f"Device enumeration failed: {e}")


    @staticmethod
    def _int_or_float_rate(x):
        try:
            r = float(x)
            return int(r)
        except Exception:
            return 44100

        
        
    def _configure_channels(self):
        """Auto-configure channels based on device capability"""
        try:
            if self.input_device_index is None:
                # Find best device and configure channels
                best_device_index = self.find_best_input_device()
                if best_device_index is not None and best_device_index != -1:
                    self.input_device_index = best_device_index
                    device_info = self.p.get_device_info_by_index(self.input_device_index)
                    max_channels = int(device_info.get('maxInputChannels', 1))
                    self.channels = min(self.requested_channels, max_channels)
                    print(f"🎵 Auto-configured: Device '{device_info['name']}' with {self.channels} channel(s)")
                else:
                    # Fallback to mono
                    self.channels = 1
                    print("⚠️ No suitable stereo device found, using mono (1 channel)")
            else:
                # Use specified device and check its capabilities
                try:
                    device_info = self.p.get_device_info_by_index(self.input_device_index)
                    max_channels = int(device_info.get('maxInputChannels', 1))
                    self.channels = min(self.requested_channels, max_channels)
                    print(f"🎵 Using device '{device_info['name']}' with {self.channels} channel(s)")
                except Exception as e:
                    print(f"⚠️ Error checking device {self.input_device_index}: {e}")
                    self.channels = 1
                    self.input_device_index = None
        except Exception as e:
            print(f"⚠️ Channel configuration error: {e}")
            self.channels = 1  # Safe fallback to mono
            self.input_device_index = None
            
        # Audio data storage
        self.is_recording = False
        self.audio_data = []
        self.current_metrics = {
            'amplitude': 0.0,
            'frequency': 0.0,
            'beat_strength': 0.0,
            'energy': 0.0,
            'is_beat': False,
            'rms': 0.0,
            'peak': 0.0,
            'db': -60.0,
            'beat_detected': False
        }
        
        # Beat detection
        self.energy_history = []
        self.beat_threshold = 1.3
        self.max_history = 50
        
        # Recording thread
        self.recording_thread = None
        
        # Visual mode flag
        self.visual_mode = False
        
        # Enhanced sensitivity
        self.sensitivity_multiplier = 5000
        
        # Color effects
        self.hue_offset = 0.0
        
        # Particle trails
        self.trails = []
        self.max_trail_points = 15
    
    def start_recording(self):
        """Start audio recording with error handling"""
        if self.is_recording:
            print("⚠️ Audio analyzer is already running")
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
        
        # Handle stereo (2-channel) audio by converting to mono for analysis
        if self.channels == 2 and len(audio_float) > 0:
            # Reshape to separate channels and take average (mono mix)
            try:
                audio_float = audio_float.reshape(-1, 2)
                audio_float = np.mean(audio_float, axis=1)  # Mix to mono
            except ValueError:
                # If reshape fails, just use the data as-is
                pass
        
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
        p = pyaudio.PyAudio()
        best = None
        try:
            try:
                default_info = p.get_default_input_device_info()
                if default_info and default_info.get('maxInputChannels', 0) > 0:
                    return int(default_info['index'])
            except Exception:
                pass

            score_best = -1
            for i in range(p.get_device_count()):
                try:
                    info = p.get_device_info_by_index(i)
                    if info.get('maxInputChannels', 0) <= 0:
                        continue
                    name = (info.get('name') or "").lower()
                    score = 0
                    if info.get('maxInputChannels', 0) >= 1:
                        score += 10
                    if info.get('maxInputChannels', 0) >= 2:
                        score += 10
                    if 'microphone' in name:
                        score += 10
                    if 'array' in name:
                        score += 5
                    if any(bad in name for bad in ['virtual', 'stream', 'stereo mix', 'loopback', 'oculus', 'steam']):
                        score -= 8
                    if score > score_best:
                        score_best = score
                        best = i
                except Exception:
                    continue
        finally:
            p.terminate()
        return best

    
    def start_visual_mode(self, effects_engine=None):
        """Start audio-only visual mode with spectrum display"""
        import pygame
        import math
        import numpy as np
        
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
                    # Flatten the most recent buffers and take last N samples
                    try:
                        buffers = self.audio_data[-4:]  # up to last ~4 buffers
                        flat = np.concatenate([np.asarray(b).astype(np.float32) for b in buffers])
                        if self.format == pyaudio.paInt16:
                            flat = flat / 32767.0
                        elif self.format == pyaudio.paInt32:
                            flat = flat / 2147483647.0
                        if self.channels == 2 and flat.size % 2 == 0:
                            flat = flat.reshape(-1, 2).mean(axis=1)
                        if flat.size >= 256:
                            segment = flat[-512:] if flat.size >= 512 else flat
                            # Calculate FFT for frequency spectrum
                            window = np.hanning(segment.size)
                            fft = np.fft.rfft(segment * window)
                            freqs = np.abs(fft)
                            # Normalize and draw spectrum
                            if freqs.size > 0:
                                max_freq = np.max(freqs) if np.max(freqs) > 0 else 1
                                freqs_normalized = freqs / max_freq
                                draw_bins = min(100, freqs_normalized.size)
                                bar_width = max(1, 600 // draw_bins)
                                for i, freq in enumerate(freqs_normalized[:draw_bins]):
                                    height = int(freq * 200)
                                    color_intensity = int(freq * 255)
                                    color = (color_intensity, 100, 255 - color_intensity)
                                    pygame.draw.rect(screen, color,
                                                     (100 + i * bar_width, 400 - height,
                                                      bar_width - 1, height))
                    except Exception:
                        pass
                
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