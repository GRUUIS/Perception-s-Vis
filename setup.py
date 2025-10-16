"""
Setup script for Audio Perception
Run this to install dependencies and set up the environment
"""

import subprocess
import sys
import os


def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing packages: {e}")
        return False


def check_audio_system():
    """Check if audio system is working"""
    print("Checking audio system...")
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        # Check for input devices
        input_devices = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append(info['name'])
                
        p.terminate()
        
        if input_devices:
            print(f"✓ Found {len(input_devices)} audio input device(s):")
            for device in input_devices[:3]:  # Show first 3
                print(f"  - {device}")
            if len(input_devices) > 3:
                print(f"  ... and {len(input_devices) - 3} more")
            return True
        else:
            print("✗ No audio input devices found")
            return False
            
    except Exception as e:
        print(f"✗ Error checking audio system: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("Creating data directories...")
    
    dirs = [
        "data",
        "data/recordings", 
        "data/visualizations"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        
    print("✓ Data directories created")


def main():
    """Main setup function"""
    print("Audio Perception Setup")
    print("=" * 30)
    
    # Install requirements
    if not install_requirements():
        print("\nSetup failed. Please install dependencies manually:")
        print("pip install pygame pygame-gui pyaudio numpy")
        return False
        
    # Create directories
    create_directories()
    
    # Check audio system
    audio_ok = check_audio_system()
    
    print("\nSetup Summary:")
    print("=" * 30)
    print("✓ Dependencies installed")
    print("✓ Directories created")
    
    if audio_ok:
        print("✓ Audio system working")
        print("\n🎉 Setup complete! Run 'python main.py' to start the application.")
    else:
        print("⚠ Audio system issues detected")
        print("\nPlease check:")
        print("- Microphone is connected and working")
        print("- Audio drivers are installed")
        print("- Microphone permissions are granted")
        print("\nYou can still run the application, but audio capture may not work.")
        
    return True


if __name__ == "__main__":
    main()
