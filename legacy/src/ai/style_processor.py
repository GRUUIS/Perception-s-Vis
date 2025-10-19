"""
AI Text Processing Module
Convert user text input to visual style parameters
"""

import re
from typing import Dict, List, Tuple, Optional
import colorsys


class StyleProcessor:
    """Process text input and convert to visual style parameters"""
    
    def __init__(self):
        # Predefined style library
        self.style_library = {
            # Fire/Heat styles
            'fire': {
                'colors': [(255, 69, 0), (255, 140, 0), (255, 255, 0), (255, 0, 0)],
                'particle_type': 'spark',
                'motion_direction': 'upward',
                'speed_multiplier': 1.5,
                'spawn_rate': 1.8,
                'life_multiplier': 0.8,
                'size_multiplier': 1.2,
                'description': 'Fire-like particles that rise upward'
            },
            
            # Water/Fluid styles  
            'water': {
                'colors': [(0, 191, 255), (64, 224, 208), (0, 255, 255), (30, 144, 255)],
                'particle_type': 'flow',
                'motion_direction': 'flowing',
                'speed_multiplier': 1.0,
                'spawn_rate': 1.2,
                'life_multiplier': 1.2,
                'size_multiplier': 0.9,
                'description': 'Fluid flowing particles'
            },
            
            # Space/Cosmic styles
            'space': {
                'colors': [(138, 43, 226), (75, 0, 130), (148, 0, 211), (255, 20, 147)],
                'particle_type': 'drift',
                'motion_direction': 'random',
                'speed_multiplier': 0.6,
                'spawn_rate': 0.8,
                'life_multiplier': 2.0,
                'size_multiplier': 0.7,
                'description': 'Cosmic drifting particles'
            },
            
            # Nature/Forest styles
            'nature': {
                'colors': [(34, 139, 34), (0, 128, 0), (173, 255, 47), (50, 205, 50)],
                'particle_type': 'organic',
                'motion_direction': 'growing',
                'speed_multiplier': 0.8,
                'spawn_rate': 1.0,
                'life_multiplier': 1.5,
                'size_multiplier': 1.1,
                'description': 'Organic growing particles'
            },
            
            # Energy/Electric styles
            'electric': {
                'colors': [(0, 255, 255), (255, 255, 0), (255, 0, 255), (0, 255, 0)],
                'particle_type': 'spark',
                'motion_direction': 'chaotic',
                'speed_multiplier': 2.0,
                'spawn_rate': 2.5,
                'life_multiplier': 0.5,
                'size_multiplier': 0.8,
                'description': 'Electric sparking particles'
            },
            
            # Ice/Snow styles
            'ice': {
                'colors': [(173, 216, 230), (176, 224, 230), (240, 248, 255), (255, 255, 255)],
                'particle_type': 'drift',
                'motion_direction': 'falling',
                'speed_multiplier': 0.4,
                'spawn_rate': 1.5,
                'life_multiplier': 1.8,
                'size_multiplier': 1.0,
                'description': 'Icy falling particles'
            }
        }
        
        # Keywords mapping to styles
        self.keyword_mapping = {
            # Fire related
            'fire': 'fire', 'flame': 'fire', '火': 'fire', '火焰': 'fire', 
            'burn': 'fire', 'hot': 'fire', 'heat': 'fire',
            'lava': 'fire', 'ember': 'fire', 'torch': 'fire', 'candle': 'fire',
            
            # Water related  
            'water': 'water', 'flow': 'water', '水': 'water', '流': 'water', 
            'river': 'water', 'ocean': 'water', 'sea': 'water',
            'liquid': 'water', 'fluid': 'water', 'stream': 'water', 
            'wave': 'water', 'rain': 'water',
            
            # Space related
            'space': 'space', 'star': 'space', '星': 'space', '太空': 'space', 
            'cosmic': 'space', 'galaxy': 'space',
            'universe': 'space', 'nebula': 'space', 'void': 'space', 'cosmos': 'space',
            
            # Nature related
            'nature': 'nature', 'tree': 'nature', '自然': 'nature', '树': 'nature', 
            'forest': 'nature', 'green': 'nature',
            'plant': 'nature', 'leaf': 'nature', 'grass': 'nature', 'garden': 'nature',
            
            # Electric related
            'electric': 'electric', 'lightning': 'electric', '电': 'electric', 
            '闪电': 'electric', 'spark': 'electric',
            'energy': 'electric', 'bolt': 'electric', 'charge': 'electric', 
            'power': 'electric',
            
            # Ice related
            'ice': 'ice', 'snow': 'ice', '冰': 'ice', '雪': 'ice', 
            'cold': 'ice', 'freeze': 'ice',
            'crystal': 'ice', 'frost': 'ice', 'winter': 'ice'
        }
        
        # Motion keywords
        self.motion_keywords = {
            'dance': {'motion_direction': 'dancing', 'speed_multiplier': 1.5},
            '舞蹈': {'motion_direction': 'dancing', 'speed_multiplier': 1.5},
            'dancing': {'motion_direction': 'dancing', 'speed_multiplier': 1.5},
            'float': {'motion_direction': 'floating', 'speed_multiplier': 0.6},
            '漂浮': {'motion_direction': 'floating', 'speed_multiplier': 0.6},
            'floating': {'motion_direction': 'floating', 'speed_multiplier': 0.6},
            'explode': {'spawn_rate': 3.0, 'speed_multiplier': 2.5},
            '爆炸': {'spawn_rate': 3.0, 'speed_multiplier': 2.5},
            'explosion': {'spawn_rate': 3.0, 'speed_multiplier': 2.5},
            'gentle': {'speed_multiplier': 0.7, 'life_multiplier': 1.5},
            '温柔': {'speed_multiplier': 0.7, 'life_multiplier': 1.5},
            'soft': {'speed_multiplier': 0.7, 'life_multiplier': 1.5},
            'wild': {'speed_multiplier': 2.0, 'spawn_rate': 2.0},
            '狂野': {'speed_multiplier': 2.0, 'spawn_rate': 2.0},
            'crazy': {'speed_multiplier': 2.0, 'spawn_rate': 2.0},
            'slow': {'speed_multiplier': 0.4, 'animation_speed': 0.6},
            '慢': {'speed_multiplier': 0.4, 'animation_speed': 0.6},
            'slowly': {'speed_multiplier': 0.4, 'animation_speed': 0.6},
            'fast': {'speed_multiplier': 1.8, 'animation_speed': 1.5},
            '快': {'speed_multiplier': 1.8, 'animation_speed': 1.5},
            'quickly': {'speed_multiplier': 1.8, 'animation_speed': 1.5}
        }
        
        # Color keywords
        self.color_keywords = {
            'red': (255, 0, 0), '红': (255, 0, 0), 'red色': (255, 0, 0),
            'blue': (0, 0, 255), '蓝': (0, 0, 255), 'blue色': (0, 0, 255),
            'green': (0, 255, 0), '绿': (0, 255, 0), 'green色': (0, 255, 0),
            'yellow': (255, 255, 0), '黄': (255, 255, 0), 'yellow色': (255, 255, 0),
            'purple': (128, 0, 128), '紫': (128, 0, 128), 'purple色': (128, 0, 128),
            'orange': (255, 165, 0), '橙': (255, 165, 0), 'orange色': (255, 165, 0),
            'pink': (255, 192, 203), '粉': (255, 192, 203), 'pink色': (255, 192, 203),
            'white': (255, 255, 255), '白': (255, 255, 255), 'white色': (255, 255, 255),
            'black': (0, 0, 0), '黑': (0, 0, 0), 'black色': (0, 0, 0)
        }
        
        # Current active style
        self.current_style = self.style_library['fire'].copy()
        self.current_style_name = 'fire'
    
    def process_text_input(self, text: str) -> Dict:
        """
        Process user text input and generate style parameters
        
        Args:
            text: User input text
            
        Returns:
            Dictionary with style parameters
        """
        if not text or not text.strip():
            return self.current_style
        
        text_lower = text.lower().strip()
        
        # Start with current style as base
        new_style = self.current_style.copy()
        style_changed = False
        
        # 1. Check for base style keywords
        detected_style = self._detect_base_style(text_lower)
        if detected_style and detected_style != self.current_style_name:
            new_style = self.style_library[detected_style].copy()
            self.current_style_name = detected_style
            style_changed = True
        
        # 2. Apply motion modifiers
        motion_mods = self._detect_motion_modifiers(text_lower)
        if motion_mods:
            new_style.update(motion_mods)
            style_changed = True
        
        # 3. Apply color overrides
        color_override = self._detect_color_override(text_lower)
        if color_override:
            new_style['colors'] = [color_override] * 4  # Use single color in variations
            style_changed = True
        
        # 4. Apply intensity keywords
        intensity_mods = self._detect_intensity_modifiers(text_lower)
        if intensity_mods:
            new_style.update(intensity_mods)
            style_changed = True
        
        # Update current style
        self.current_style = new_style
        
        return {
            'style': new_style,
            'style_changed': style_changed,
            'original_text': text,
            'detected_keywords': self._extract_keywords(text_lower)
        }
    
    def _detect_base_style(self, text: str) -> Optional[str]:
        """Detect base style from text"""
        for keyword, style_name in self.keyword_mapping.items():
            if keyword in text:
                return style_name
        return None
    
    def _detect_motion_modifiers(self, text: str) -> Dict:
        """Detect motion-related keywords"""
        modifiers = {}
        for keyword, params in self.motion_keywords.items():
            if keyword in text:
                modifiers.update(params)
        return modifiers
    
    def _detect_color_override(self, text: str) -> Optional[Tuple[int, int, int]]:
        """Detect specific color mentions"""
        for keyword, color in self.color_keywords.items():
            if keyword in text:
                return color
        return None
    
    def _detect_intensity_modifiers(self, text: str) -> Dict:
        """Detect intensity-related keywords"""
        modifiers = {}
        
        # Size modifiers
        if any(word in text for word in ['big', '大', 'large', 'huge']):
            modifiers['size_multiplier'] = modifiers.get('size_multiplier', 1.0) * 1.5
        elif any(word in text for word in ['small', '小', 'tiny', 'mini']):
            modifiers['size_multiplier'] = modifiers.get('size_multiplier', 1.0) * 0.6
        
        # Density modifiers
        if any(word in text for word in ['many', '多', 'lots', 'dense']):
            modifiers['spawn_rate'] = modifiers.get('spawn_rate', 1.0) * 1.8
        elif any(word in text for word in ['few', '少', 'sparse', 'light']):
            modifiers['spawn_rate'] = modifiers.get('spawn_rate', 1.0) * 0.5
        
        # Duration modifiers
        if any(word in text for word in ['long', '长', 'lasting', 'persist']):
            modifiers['life_multiplier'] = modifiers.get('life_multiplier', 1.0) * 1.8
        elif any(word in text for word in ['short', '短', 'brief', 'quick']):
            modifiers['life_multiplier'] = modifiers.get('life_multiplier', 1.0) * 0.6
        
        return modifiers
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract detected keywords from text"""
        keywords = []
        
        # Check style keywords
        for keyword, style_name in self.keyword_mapping.items():
            if keyword in text:
                keywords.append(f"style:{style_name}")
                break
        
        # Check motion keywords
        for keyword in self.motion_keywords:
            if keyword in text:
                keywords.append(f"motion:{keyword}")
        
        # Check color keywords
        for keyword in self.color_keywords:
            if keyword in text:
                keywords.append(f"color:{keyword}")
        
        return keywords
    
    def get_available_styles(self) -> List[str]:
        """Get list of available style names"""
        return list(self.style_library.keys())
    
    def get_style_description(self, style_name: str) -> str:
        """Get description of a specific style"""
        return self.style_library.get(style_name, {}).get('description', 'Unknown style')
    
    def set_style_directly(self, style_name: str) -> bool:
        """Directly set a style by name"""
        if style_name in self.style_library:
            self.current_style = self.style_library[style_name].copy()
            self.current_style_name = style_name
            return True
        return False
    
    def get_current_style_info(self) -> Dict:
        """Get current style information"""
        return {
            'name': self.current_style_name,
            'description': self.get_style_description(self.current_style_name),
            'parameters': self.current_style
        }