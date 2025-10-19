"""
Multi-Modal Creative Visualization System
Core Package Initialization
"""

__version__ = "2.0.0"
__author__ = "Creative Programming Team"
__description__ = "Professional-grade multi-modal creative visualization system"

# Import core modules for easy access
try:
    from core.vision import CameraAnalyzer
    from core.audio import AudioAnalyzer
    from core.ai import AIStyleProcessor
    from core.effects import VisualEffectsEngine
    
    __all__ = [
        'CameraAnalyzer',
        'AudioAnalyzer', 
        'AIStyleProcessor',
        'VisualEffectsEngine'
    ]
    
except ImportError as e:
    # Handle missing dependencies gracefully
    print(f"Warning: Some core modules could not be imported: {e}")
    __all__ = []