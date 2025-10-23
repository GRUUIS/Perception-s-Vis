# Camera + Audio + Some Visual Effects

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


## Installation

### Install Dependencies
```bash
pip install -r requirements.txt
```
### Starting the Application
```bash
python main.py
```