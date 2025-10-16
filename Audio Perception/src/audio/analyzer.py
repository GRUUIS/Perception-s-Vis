"""
Audio Analyzer Module
Captures and analyzes audio data using PyAudio to extract:
- Amplitude
- RMS (Root Mean Square)
- Peak amplitude
- Decibel level
"""

import pyaudio
import numpy as np
import threading
import time
from typing import Dict, Callable, Optional
import math


class AudioAnalyzer:
    def __init__(self, 
                 chunk_size: int = 1024,
                 format: int = pyaudio.paInt16,
                 channels: int = 1,
                 rate: int = 44100,
                 callback: Optional[Callable] = None):
        """
        Initialize the Audio Analyzer
        
        Args:
            chunk_size: Number of frames per buffer
            format: Audio format
            channels: Number of audio channels
            rate: Sample rate
            callback: Callback function to receive audio data
        """
        self.chunk_size = chunk_size
        self.format = format
        self.channels = channels
        self.rate = rate
        self.callback = callback
        
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
            'db': -60.0,  # Start at low dB
            'frequency': 0.0
        }
        
        # Threading
        self.recording_thread = None
        self.analysis_thread = None
        
    def start_recording(self):
        """Start audio recording and analysis"""
        if self.is_recording:
            return
            
        self.is_recording = True
        
        # Open audio stream
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        print("Audio recording started...")
        
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
        if self.recording_thread:
            self.recording_thread.join()
            
        print("Audio recording stopped...")
        
    def _record_audio(self):
        """Record audio in a separate thread"""
        while self.is_recording:
            try:
                # Read audio data
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Convert to numpy array
                audio_array = np.frombuffer(data, dtype=np.int16)
                
                # Store audio data
                self.audio_data.append(audio_array)
                
                # Analyze audio data
                metrics = self._analyze_audio(audio_array)
                self.current_metrics.update(metrics)
                
                # Call callback if provided
                if self.callback:
                    self.callback(self.current_metrics.copy())
                    
            except Exception as e:
                print(f"Error in audio recording: {e}")
                
    def _analyze_audio(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Analyze audio data and extract metrics
        
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
                'frequency': 0.0
            }
            
        # Convert to float for better precision
        audio_float = audio_data.astype(np.float32)
        
        # Calculate amplitude (average absolute value)
        amplitude = np.mean(np.abs(audio_float))
        
        # Calculate RMS (Root Mean Square)
        rms = np.sqrt(np.mean(audio_float ** 2))
        
        # Calculate peak amplitude
        peak = np.max(np.abs(audio_float))
        
        # Calculate decibel level
        # Avoid log(0) by adding small epsilon
        epsilon = 1e-10
        db = 20 * np.log10(max(rms, epsilon) / 32767.0)  # 32767 is max value for int16
        db = max(db, -60.0)  # Clamp minimum dB
        
        # Calculate dominant frequency using FFT
        frequency = self._calculate_frequency(audio_float)
        
        return {
            'amplitude': float(amplitude),
            'rms': float(rms),
            'peak': float(peak),
            'db': float(db),
            'frequency': float(frequency)
        }
        
    def _calculate_frequency(self, audio_data: np.ndarray) -> float:
        """
        Calculate dominant frequency using FFT
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Dominant frequency in Hz
        """
        try:
            # Apply window function to reduce spectral leakage
            windowed = audio_data * np.hanning(len(audio_data))
            
            # Perform FFT
            fft = np.fft.rfft(windowed)
            magnitude = np.abs(fft)
            
            # Find peak frequency
            peak_bin = np.argmax(magnitude)
            frequency = peak_bin * self.rate / (2 * len(magnitude))
            
            return frequency
            
        except Exception as e:
            print(f"Error calculating frequency: {e}")
            return 0.0
            
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current audio metrics"""
        return self.current_metrics.copy()
        
    def get_normalized_metrics(self) -> Dict[str, float]:
        """
        Get normalized audio metrics (0.0 to 1.0 range)
        Useful for visualization scaling
        """
        metrics = self.current_metrics.copy()
        
        # Normalize amplitude (0-32767 to 0-1)
        metrics['amplitude_norm'] = min(metrics['amplitude'] / 5000.0, 1.0)
        
        # Normalize RMS (0-32767 to 0-1)
        metrics['rms_norm'] = min(metrics['rms'] / 5000.0, 1.0)
        
        # Normalize peak (0-32767 to 0-1)
        metrics['peak_norm'] = min(metrics['peak'] / 32767.0, 1.0)
        
        # Normalize dB (-60 to 0 dB to 0-1)
        metrics['db_norm'] = max((metrics['db'] + 60.0) / 60.0, 0.0)
        
        # Normalize frequency (0-22050 Hz to 0-1)
        metrics['frequency_norm'] = min(metrics['frequency'] / 22050.0, 1.0)
        
        return metrics
        
    def get_audio_data(self) -> list:
        """Get stored audio data"""
        return self.audio_data.copy()
        
    def clear_audio_data(self):
        """Clear stored audio data"""
        self.audio_data.clear()
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_recording()
        if hasattr(self, 'p'):
            self.p.terminate()


# Utility functions for audio processing
def db_to_linear(db: float) -> float:
    """Convert decibels to linear scale"""
    return 10 ** (db / 20.0)


def linear_to_db(linear: float) -> float:
    """Convert linear scale to decibels"""
    return 20 * math.log10(max(linear, 1e-10))


def smooth_value(current: float, target: float, smooth_factor: float = 0.1) -> float:
    """Smooth value transitions for better visual effects"""
    return current + (target - current) * smooth_factor
