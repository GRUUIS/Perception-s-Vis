#!/usr/bin/env python3
"""
Quick test script to verify the creative application components
"""

import sys
import os
import pygame
import numpy as np

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_imports():
    """Test that all components can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from ui.creative_studio import CreativeStudioInterface
        print("✅ CreativeStudioInterface import successful")
    except Exception as e:
        print(f"❌ CreativeStudioInterface import failed: {e}")
        return False
    
    try:
        from ui.creative_gallery import CreativeGalleryInterface
        print("✅ CreativeGalleryInterface import successful")
    except Exception as e:
        print(f"❌ CreativeGalleryInterface import failed: {e}")
        return False
    
    try:
        from audio.analyzer import AudioAnalyzer
        print("✅ AudioAnalyzer import successful")
    except Exception as e:
        print(f"❌ AudioAnalyzer import failed: {e}")
        return False
    
    try:
        from storage.manager import DataStorage
        print("✅ DataStorage import successful")
    except Exception as e:
        print(f"❌ DataStorage import failed: {e}")
        return False
    
    return True

def test_audio_analyzer():
    """Test audio analyzer functionality"""
    print("\n🎵 Testing audio analyzer...")
    
    try:
        from audio.analyzer import AudioAnalyzer
        analyzer = AudioAnalyzer()
        
        # Test with fake audio data
        fake_audio = np.random.random(1024) * 0.1
        analyzer.process_audio_data(fake_audio)
        
        # Check if we get valid frequency data
        freqs = analyzer.get_frequency_bins()
        if len(freqs) > 0:
            print("✅ Audio processing working")
            print(f"   - Got {len(freqs)} frequency bins")
            print(f"   - Beat detected: {analyzer.is_beat()}")
            print(f"   - Energy level: {analyzer.get_energy():.3f}")
            return True
        else:
            print("❌ No frequency data returned")
            return False
            
    except Exception as e:
        print(f"❌ Audio analyzer test failed: {e}")
        return False

def test_creative_components():
    """Test creative components without full pygame init"""
    print("\n🎨 Testing creative components...")
    
    try:
        # Test particle system components
        from ui.creative_studio import Particle, ParticleType
        
        # Create test particle
        particle = Particle(
            x=100.0, y=100.0, z=0.0,
            vx=1.0, vy=1.0, vz=0.0,
            life=1.0, max_life=1.0,
            size=5.0, color=(255, 255, 255),
            particle_type=ParticleType.SPARK
        )
        
        print("✅ Particle system components working")
        print(f"   - Particle created: {particle.particle_type}")
        return True
        
    except Exception as e:
        print(f"❌ Creative components test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Creative Audio Visualization - Component Test")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_audio_analyzer())
    results.append(test_creative_components())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("✨ Your creative audio app is ready!")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("🔧 Check the error messages above")
    
    return passed == total

if __name__ == "__main__":
    main()