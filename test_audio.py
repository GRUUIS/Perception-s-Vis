#!/usr/bin/env python3
"""
Audio Level Test
Test the improved audio sensitivity
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.audio import AudioAnalyzer
import time

def test_audio_levels():
    """Test audio input levels with improved sensitivity"""
    print("🎵 Audio Level Test")
    print("="*50)
    
    # Find best device
    best_device = AudioAnalyzer.find_best_input_device()
    print(f"🎤 Best microphone device: {best_device}")
    
    # Create analyzer
    analyzer = AudioAnalyzer(input_device_index=best_device)
    
    if not analyzer.start_recording():
        print("❌ Failed to start audio recording")
        return
    
    print("🎯 Recording for 10 seconds... Make some noise!")
    print("Press Ctrl+C to stop early")
    
    try:
        for i in range(100):  # 10 seconds at 0.1s intervals
            time.sleep(0.1)
            
            metrics = analyzer.get_current_metrics()
            volume = analyzer.get_volume_level()
            
            # Print every 10th reading
            if i % 10 == 0:
                print(f"Volume: {volume:.3f} | RMS: {metrics['rms']:.6f} | Amplitude: {metrics['amplitude']:.6f}")
                
                # Visual bar
                bar_length = int(volume * 50)
                bar = "█" * bar_length + "░" * (50 - bar_length)
                print(f"[{bar}] {volume*100:.1f}%")
                print()
                
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    
    analyzer.stop_recording()
    print("✅ Audio test completed")

if __name__ == "__main__":
    test_audio_levels()