# Audio-Perception Multi-Modal Creative Visualization System
# Real-time Camera + Audio + AI + Selfie Segmentation Visual Effects

## See a detailed explanation
https://deepwiki.com/GRUUIS/Perception-s-Vis/1-overview
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/GRUUIS/Perception-s-Vis)

## Project Architecture

This project provides real-time visual effects generation from multiple input sources:
- **Camera Input**: Motion detection, color analysis, selfie segmentation with visual effects backgrounds
- **Audio Input**: Real-time beat detection, frequency analysis, amplitude tracking with advanced device selection
- **AI Integration**: Control via local LM Studio integration

## Features

### Camera Vision System
- **Real-time Motion Tracking**: Computer vision-based movement detection
- **Selfie Segmentation**: Real-time person segmentation with visual effects backgrounds

### Audio Analysis Engine
- **Smart Device Selection**: Automatically detects and prioritizes the best microphone input
- **Real-time Processing**: Low-latency audio capture with configurable chunk sizes
- **Beat Detection**: Intelligent rhythm recognition for dynamic visual responses

### AI Integration Hub
- **Local LLM Support**: Compatible with LM Studio and similar local AI servers

### Visual Effects
- **Multi-modal Responsiveness**: Combined audio and visual input processing
- **Color Transformations**: Color changes based on inputs

## Requirements
pip install -r requirements

## Run the main application
python main.py
```
Audio-Perception/           # Multi-Modal Creative Visualization System
├── main.py                # Main application entry point
├── requirements.txt       # Python dependencies
├── requirements-ml.txt    # ML dependencies for segmentation
├── .env.example          # Environment configuration template
├── .gitignore            # Git ignore patterns
│
├── core/                 # Core functionality modules
│   ├── __init__.py
│   ├── audio/           # Audio analysis and processing
│   │   ├── __init__.py
│   │   └── analyzer.py   # Real-time audio analysis, beat detection
│   ├── vision/          # Camera and visual processing
│   │   ├── __init__.py
│   │   ├── camera_analyzer.py      # Computer vision, motion detection
│   │   └── selfie_segmentation.py  # MediaPipe segmentation wrapper
│   ├── ai/              # AI integration and processing
│   │   ├── __init__.py
│   │   └── style_processor.py  # LM Studio integration, style control
│   └── effects/         # Visual effects engine
│       ├── __init__.py
│       └── visual_engine.py   # Dynamic visual effects generation
│
├── interface/           # User interface modules
│   ├── __init__.py
│   └── multi_modal_studio.py  # Main GUI application with segmentation
│
├── data/               # Data storage and outputs
│   ├── audio_perception.db   # Application database
│   ├── recordings/     # Audio recordings storage
│   └── visualizations/ # Generated visual outputs
│
├── tools/              # Development and diagnostic tools
│   ├── audio_diag.py           # Audio device diagnostics
│   ├── selfie_demo.py          # Segmentation demo
│   └── camera_seg_test.py      # Integration testing
│
└── legacy/             # Previous implementations and backups
    └── src/            # Legacy source code
```

## Update: Add Selfie Segmentation Feature
- **Real-time Processing**: 30 FPS segmentation with visual effects background
- **Safe Fallback**: If MediaPipe is unavailable, the system gracefully falls back to normal camera mode


### Environment Configuration
Create a `.env` file for AI integration:
```bash
LM_STUDIO_URL=http://localhost:1234
AI_MODEL_NAME=gpt-oss-20b
