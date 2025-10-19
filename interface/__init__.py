"""
Interface Package
User interface components for multi-modal visualization
"""

try:
    from .multi_modal_studio import MultiModalStudio
    
    __all__ = ['MultiModalStudio']
    
except ImportError as e:
    print(f"Warning: Interface modules could not be imported: {e}")
    __all__ = []