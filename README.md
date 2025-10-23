# Creative Visualization
# Camera + Audio + Various Visual Effects

## Project Architecture

This project provides real-time visual effects generation from multiple input sources:
- **Camera Input**: Motion detection, color analysis, object recognition
- **Audio Input**: Beat detection, frequency analysis, amplitude tracking  
- **AI Integration**: Style control, effect generation

## Features

### Camera Vision
- Real-time motion tracking
- Color palette extraction

### Audio Analysis  
- Real-time amplitude monitoring

### AI Integration
- Natural language style commands
- Local LLM integration (LM Studio compatible)

## Requirements

```bash
# Core dependencies
opencv-python>=4.8.0
pygame>=2.1.0
numpy>=1.21.0
pyaudio>=0.2.11

# AI integration
requests>=2.28.0
openai>=1.0.0

# Optional enhancements
mediapipe>=0.10.0
ultralytics>=8.0.0
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Controls

- **Camera Mode**: Move in front of camera for motion-based effects
- **Audio Mode**: Play music or make sounds for audio-reactive visuals
- **Text Commands**: Type natural language to control visual styles

## Project Structure

```
core/                   # Core functionality
├── vision/            # Camera processing
├── audio/             # Audio analysis
├── ai/                # AI integration
└── effects/           # Visual effects engine

interface/             # User interfaces
├── main_studio.py     # Primary application
├── camera_mode.py     # Camera-focused interface
└── audio_mode.py      # Audio-focused interface

legacy/               # Previous implementations
```

## License

Creative Commons - Share and modify freely
- Browse recordings by user, date, and duration
- Delete unwanted recordings

### Data Storage
- SQLite database for metadata storage
- Binary storage for audio data and visual frames
- Automatic session recording and playback
- Statistics tracking for user activity

## Installation

### Prerequisites
- Python 3.7 +
- Working microphone for audio input
- Audio drivers properly installed

### Clone or Download
Download all project files to your desired directory.

### Install Dependencies
```bash
pip install -r requirements.txt
```
### Starting the Application
```bash
python main.py
```

This will launch the main launcher window where you can choose between:
- **Single Mode**: For individual recording and visualization
- **Gallery Mode**: For viewing all saved recordings

### Single Mode Operation

1. **Setup**:
   - Enter your name (optional, defaults to "Anonymous")
   - Add a title for your recording session

2. **Audio Control**:
   - Click "Start Audio" to begin capturing sound
   - Click "Stop Audio" to stop capturing

3. **Recording**:
   - Click "Start Recording" to save audio and visual data
   - Make sounds to see the visualization respond
   - Click "Stop Recording" to save the session

4. **Customization**:
   - **Palette**: Choose from different color schemes
   - **Elements**: Adjust the number of visual elements (10-200)
   - **Size**: Control the size multiplier of shapes (0.1-3.0x)
   - **Speed**: Adjust animation speed (0.1-3.0x)
   - **Effects**: Toggle particles, wave mode, and symmetry

### Gallery Mode Operation

1. **Browse Recordings**:
   - View list of all saved recordings
   - See user names, titles, and durations
   - View statistics about total recordings and users

2. **Playback**:
   - Select a recording from the list
   - Click "Play" to start playback with original visualizations
   - Use speed control to adjust playback rate
   - Seek through recordings using the progress bar

3. **Management**:
   - Delete recordings you no longer want
   - Refresh the list to see new recordings

## Audio Metrics

The system analyzes several audio characteristics:

- **Amplitude**: Average absolute value of the audio signal
- **RMS (Root Mean Square)**: Measure of the audio signal's power
- **Peak Amplitude**: Maximum amplitude value in the audio chunk
- **Decibel Level**: Logarithmic representation of audio intensity
- **Dominant Frequency**: Main frequency component using FFT analysis

These metrics drive various visual parameters:
- **Element Count**: Increases with amplitude
- **Shape Size**: Based on RMS values
- **Color Intensity**: Driven by decibel levels
- **Color Hue**: Determined by frequency content
- **Animation Speed**: Responds to audio energy

## Visual Parameters

### Shape Properties
- **Size**: Controlled by audio RMS and user multiplier
- **Color**: Based on frequency content and selected palette
- **Alpha/Transparency**: Varies with decibel levels
- **Rotation**: Speed affected by audio amplitude
- **Movement**: Velocity influenced by audio energy

### Effects
- **Particles**: Triggered by high amplitude sounds
- **Wave Mode**: Creates sinusoidal patterns based on frequency
- **Symmetry**: Mirrors visualization for enhanced patterns
- **Fade Effect**: Smooth transitions between frames

## File Structure

```
Audio Perception/
├── main.py                 # Main application launcher
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── __init__.py
│   ├── audio/             # Audio processing module
│   │   ├── __init__.py
│   │   └── analyzer.py    # PyAudio capture and analysis
│   ├── visualization/     # Visualization engine
│   │   ├── __init__.py
│   │   └── engine.py      # Pygame-based rendering
│   ├── storage/           # Data storage system
│   │   ├── __init__.py
│   │   └── manager.py     # SQLite database management
│   └── ui/                # User interfaces
│       ├── __init__.py
│       ├── single_mode.py # Individual user interface
│       └── multi_mode.py  # Gallery interface
└── data/                  # Data storage (created automatically)
    ├── audio_perception.db # SQLite database
    ├── recordings/        # Audio data files
    └── visualizations/    # Visual frame sequences
```

## License

This project is open source. Feel free to modify and distribute according to your needs.


Enjoy creating beautiful audio visualizations!
