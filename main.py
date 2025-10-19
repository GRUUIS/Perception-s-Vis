#!/usr/bin/env python3
"""
Multi-Modal Creative Visualization System v2.0
Main Entry Point - Camera + Audio + AI Integration
"""

import sys
import os
import argparse
from pathlib import Path

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent))

def show_banner():
    """Display system banner"""
    print("🎨" + "="*60 + "🎨")
    print("   Multi-Modal Creative Visualization System v2.0")
    print("   Camera + Audio + AI Powered Visual Effects")
    print("🎨" + "="*60 + "🎨")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        ('pygame', 'pygame'),
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('pyaudio', 'pyaudio'),
        ('requests', 'requests'),
        ('pygame_gui', 'pygame-gui')
    ]
    
    missing = []
    for module, package in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing dependencies:")
        for package in missing:
            print(f"   - {package}")
        print("\n💡 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies found!")
    return True

def run_camera_mode():
    """Launch camera-only mode"""
    try:
        print("📸 Starting Camera Vision Mode...")
        from core.vision import CameraAnalyzer
        from core.effects import VisualEffectsEngine
        
        camera = CameraAnalyzer()
        effects = VisualEffectsEngine()
        
        print("🎯 Camera mode active - Press 'Q' to quit")
        camera.start_visual_mode(effects)
        
    except ImportError as e:
        print(f"❌ Camera mode error: {e}")
        print("💡 Make sure camera modules are properly set up")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_audio_mode():
    """Launch audio-only mode"""
    try:
        print("🎵 Starting Audio Analysis Mode...")
        from core.audio import AudioAnalyzer
        from core.effects import VisualEffectsEngine
        
        # Find the best microphone device
        best_device = AudioAnalyzer.find_best_input_device()
        if best_device is not None:
            print(f"🎤 Using audio device {best_device}")
        
        audio = AudioAnalyzer(input_device_index=best_device)
        effects = VisualEffectsEngine()
        
        print("🎯 Audio mode active - Press 'Q' to quit")
        print("💡 Tip: Make some noise to see the visualization!")
        audio.start_visual_mode(effects)
        
    except ImportError as e:
        print(f"❌ Audio mode error: {e}")
        print("💡 Make sure audio modules are properly set up")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_full_studio():
    """Launch full multi-modal studio"""
    try:
        print("🚀 Starting Multi-Modal Creative Studio...")
        from interface.multi_modal_studio import MultiModalStudio
        
        studio = MultiModalStudio()
        print("🎯 Full studio active - Enjoy creating!")
        studio.run()
        
    except ImportError as e:
        print(f"❌ Studio mode error: {e}")
        print("💡 Make sure all modules are properly set up")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_help():
    """Display help information"""
    print("\n📖 Usage Options:")
    print("   python main.py                    # Full multi-modal studio")
    print("   python main.py --mode=camera      # Camera-only mode")
    print("   python main.py --mode=audio       # Audio-only mode")
    print("   python main.py --help             # Show this help")
    print("\n🎯 Features:")
    print("   📸 Camera Mode: Motion tracking, color analysis, gesture detection")
    print("   � Audio Mode: Beat detection, frequency analysis, rhythm tracking")
    print("   🤖 AI Mode: Natural language style control (requires LM Studio)")
    print("   ✨ Visual Effects: Particle systems, real-time rendering")
    print("\n🔧 Setup:")
    print("   1. Install: pip install -r requirements.txt")
    print("   2. For AI features: Start LM Studio with local model")
    print("   3. Connect camera and/or microphone")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Multi-Modal Creative Visualization System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--mode', 
        choices=['camera', 'audio', 'full'],
        default='full',
        help='Run specific mode (default: full studio)'
    )
    parser.add_argument(
        '--check', 
        action='store_true',
        help='Check dependencies only'
    )
    
    args = parser.parse_args()
    
    show_banner()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    if args.check:
        print("\n✅ System ready!")
        return 0
    
    print(f"\n🎯 Running in {args.mode} mode...")
    
    try:
        if args.mode == 'camera':
            run_camera_mode()
        elif args.mode == 'audio':
            run_audio_mode()
        else:  # full mode
            run_full_studio()
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for creating with us!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Try running with --check to verify setup")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())