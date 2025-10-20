#!/usr/bin/env python3
"""
Microphone Device Test
Test different microphone devices to find the most responsive one
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pyaudio
import numpy as np
import time
try:
    # Mark this file as a utility script; skip under pytest collection
    import pytest
    pytestmark = pytest.mark.skip("Utility script for manual microphone testing; not a unit test")
except Exception:
    pass

def test_microphone_device(device_index, duration=3):
    """Test a specific microphone device"""
    p = pyaudio.PyAudio()
    
    try:
        device_info = p.get_device_info_by_index(device_index)
        print(f"\n🎤 Testing Device {device_index}: {device_info['name']}")
        
        stream = p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            input_device_index=device_index
        )
        
        levels = []
        for i in range(int(44100 / 1024 * duration)):
            data = stream.read(1024)
            audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
            rms = np.sqrt(np.mean(audio_array ** 2))
            amplitude = np.mean(np.abs(audio_array))
            levels.append(amplitude)
            
            if i % 10 == 0:  # Print occasionally
                volume = min(1.0, amplitude * 5000.0)
                bar_length = int(volume * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                print(f"  [{bar}] {volume*100:.1f}% (amp: {amplitude:.6f})")
        
        stream.stop_stream()
        stream.close()
        
        avg_level = np.mean(levels)
        max_level = np.max(levels)
        
        print(f"  📊 Average: {avg_level:.6f}, Max: {max_level:.6f}")
        print(f"  📈 Scaled volume: {min(1.0, avg_level * 5000.0):.3f}")
        
        return max_level
        
    except Exception as e:
        print(f"  ❌ Error testing device {device_index}: {e}")
        return 0.0
    finally:
        p.terminate()

def main():
    """Test all available microphone devices"""
    print("🎵 Microphone Device Test")
    print("="*60)
    print("📢 Make some noise during each test to see which device responds best!")
    print()
    
    p = pyaudio.PyAudio()
    
    # Find all input devices
    input_devices = []
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append((i, info['name']))
        except:
            continue
    
    p.terminate()
    
    print(f"Found {len(input_devices)} input devices:")
    for idx, name in input_devices:
        print(f"  {idx}: {name}")
    
    print("\n🔍 Testing each device (3 seconds each)...")
    
    results = []
    for device_idx, device_name in input_devices:
        try:
            max_level = test_microphone_device(device_idx, duration=3)
            results.append((device_idx, device_name, max_level))
        except KeyboardInterrupt:
            print("\n⏹️ Testing stopped by user")
            break
        except Exception as e:
            print(f"❌ Failed to test device {device_idx}: {e}")
    
    # Sort by responsiveness
    results.sort(key=lambda x: x[2], reverse=True)
    
    print("\n🏆 Results (sorted by responsiveness):")
    print("-" * 60)
    for i, (idx, name, level) in enumerate(results[:5]):  # Top 5
        scaled_volume = min(1.0, level * 5000.0)
        print(f"{i+1:2d}. Device {idx:2d}: {scaled_volume*100:5.1f}% | {name}")
    
    if results:
        best_device, best_name, best_level = results[0]
        print(f"\n🎯 Best device: {best_device} ({best_name})")
        print(f"   Max level: {best_level:.6f} (scaled: {min(1.0, best_level * 5000.0)*100:.1f}%)")

if __name__ == "__main__":
    main()