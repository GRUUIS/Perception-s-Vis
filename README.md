# 🎨 Creative Audio Visualization System

A dynamic real-time audio visualization application that transforms microphone input into stunning creative art through advanced particle systems and interactive galleries.

## ✨ Features

### 🎵 Creative Studio Mode
- **Real-time Audio Response**: Particles react instantly to microphone input
- **5 Dynamic Visual Themes**:
  - 🌌 **Cosmic**: Starfield particles with galaxy-like effects
  - 🔥 **Fire**: Flame-like particles with heat simulation
  - 🌊 **Ocean**: Wave particles with fluid dynamics
  - 🌲 **Forest**: Nature-inspired organic movements
  - 💜 **Neon**: Cyberpunk-style glowing effects
- **Advanced Particle System**: 2000+ particles with 4 types (spark, wave, flow, burst)
- **Beat Detection**: Particles respond to rhythm and bass
- **3D-like Effects**: Depth simulation with Z-axis movement

### 🖼️ Art Gallery Mode
- **Interactive Navigation**: WASD movement through virtual space
- **5 Art Pattern Types**:
  - Spiral designs
  - Mandala patterns
  - Wave forms
  - Geometric art
  - Fractal-like effects
- **Dynamic Generation**: Patterns evolve based on audio input
- **Smooth Camera**: Fluid movement through the gallery space
- Browse recordings by user, date, and duration
- Delete unwanted recordings

### Data Storage
- SQLite database for metadata storage
- Binary storage for audio data and visual frames
- Automatic session recording and playback
- Statistics tracking for user activity

## Installation

### Prerequisites
- Python 3.7 or higher
- Working microphone for audio input
- Audio drivers properly installed

### Step 1: Clone or Download
Download all project files to your desired directory.

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install PyAudio (if needed)
PyAudio might require additional steps on some systems:

**Windows:**
```bash
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

## Usage

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

## Troubleshooting

### Common Issues

1. **"Import pygame could not be resolved"**
   - Install pygame: `pip install pygame`

2. **"Import pyaudio could not be resolved"**
   - Follow PyAudio installation steps above
   - On Windows, try: `pip install pipwin` then `pipwin install pyaudio`

3. **No sound being captured**
   - Check microphone permissions
   - Verify microphone is working in other applications
   - Try adjusting system audio input levels

4. **Poor visualization performance**
   - Reduce the number of elements in settings
   - Disable particle effects if needed
   - Close other applications using audio

5. **Database errors**
   - Ensure write permissions in the project directory
   - Delete `data/audio_perception.db` to reset (will lose all recordings)

### Performance Optimization

- **Element Count**: Lower values (10-50) for better performance
- **Size Multiplier**: Smaller values reduce rendering load
- **Particle Effects**: Disable for lower-end systems
- **Recording Length**: Longer recordings use more memory

## Development

### Architecture

The application follows a modular design:

- **Audio Module**: Handles PyAudio capture and real-time analysis
- **Visualization Module**: Pygame-based rendering with customizable effects
- **Storage Module**: SQLite database with binary file storage
- **UI Module**: Pygame-GUI interfaces for both modes

### Key Components

1. **AudioAnalyzer**: Real-time audio capture and metric extraction
2. **VisualizationEngine**: Dynamic visual effect generation
3. **DataStorage**: Recording session management and persistence
4. **SingleModeInterface**: Real-time visualization UI
5. **MultiModeInterface**: Playback and gallery UI

### Extending the System

- **New Visual Effects**: Add to `VisualizationEngine` class
- **Additional Audio Metrics**: Extend `AudioAnalyzer._analyze_audio()`
- **New Color Palettes**: Add to `ColorPalette.PALETTES`
- **Custom Shapes**: Implement in `VisualizationEngine._render_element()`

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are properly installed
3. Verify audio hardware is working correctly
4. Check Python version compatibility (3.7+)

Enjoy creating beautiful audio visualizations!
