"""
AI Style Processing Module
Real AI integration with LM Studio for natural language style processing
"""

import json
import requests
import time
from typing import Dict, List, Optional, Any
import threading
from dataclasses import dataclass


@dataclass
class StyleEffect:
    """Style effect configuration"""
    colors: List[tuple]
    motion: str
    intensity: float
    duration: float
    particles: Dict[str, Any]


class LMStudioClient:
    """LM Studio API client for real AI processing"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:1234",
                 model_name: str = "default",
                 timeout: int = 30):
        """
        Initialize LM Studio client
        
        Args:
            base_url: LM Studio server URL
            model_name: Model name to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.timeout = timeout
        self.is_connected = False
        
    def test_connection(self) -> bool:
        """Test connection to LM Studio server"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=2)
            self.is_connected = response.status_code == 200
            if self.is_connected:
                print("🤖 Connected to LM Studio successfully")
            return self.is_connected
        except Exception:
            # Silently fail - don't print error messages for optional AI features
            self.is_connected = False
            return False
    
    def generate_style(self, user_input: str, context: Dict = None) -> Dict:
        """
        Generate style configuration using AI
        
        Args:
            user_input: User's natural language input
            context: Current visual context (colors, motion, etc.)
            
        Returns:
            Style configuration dictionary
        """
        if not self.is_connected and not self.test_connection():
            return self._fallback_style(user_input)
        
        try:
            prompt = self._build_style_prompt(user_input, context)
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                return self._parse_ai_response(ai_response)
            else:
                print(f"LM Studio API error: {response.status_code}")
                return self._fallback_style(user_input)
                
        except Exception as e:
            print(f"AI generation error: {e}")
            return self._fallback_style(user_input)
    
    def _get_system_prompt(self) -> str:
        """Get enhanced system prompt for beautiful visual style generation"""
        return """You are an AI visual effects artist specialized in creating stunning real-time visualizations. Convert natural language descriptions into detailed visual effect parameters for an advanced particle system.

Respond with a JSON object containing:
{
    "colors": [[r,g,b], [r,g,b], ...],  // RGB color palette (3-6 colors, be creative!)
    "motion": "pattern_type",            // "spiral", "wave", "explosion", "orbital", "magnetic", "chaotic", "gentle"
    "intensity": 0.8,                   // 0.0 to 1.0 - energy level
    "duration": 5.0,                    // seconds - effect duration
    "particles": {
        "count": 150,                   // number of particles (50-500)
        "size": 4,                      // base particle size (1-10)
        "speed": 3.0,                   // movement speed (0.5-10.0)
        "life": 4.0,                    // particle lifetime (1.0-8.0)
        "glow": true,                   // enable glow effects
        "trails": true,                 // enable particle trails
        "shapes": ["circle", "star"],   // particle shapes: "circle", "star", "diamond", "heart"
        "pulsate": false               // pulsating animation
    },
    "environment": {
        "gravity": 0.0,                 // -5.0 to 5.0
        "wind": [0.0, 0.0]             // [x, y] wind force
    }
}

Enhanced Examples:
- "starry night sky" → deep blues/purples, gentle motion, star shapes, glow, trails
- "volcanic eruption" → reds/oranges/yellows, explosion motion, high intensity, large particles
- "underwater bubbles" → cyan/blue/white, gentle upward motion, circles, low gravity
- "electric storm" → purple/white/cyan, chaotic motion, high intensity, glow, fast particles
- "cherry blossoms" → pink/white, gentle spiral, heart/circle shapes, soft trails
- "disco party" → rainbow colors, orbital motion, all shapes, pulsate, high energy
- "peaceful meditation" → soft pastels, wave motion, gentle, small particles, trails

Be creative with colors and combine effects for maximum visual impact. Always respond with valid JSON only."""

    def _build_style_prompt(self, user_input: str, context: Dict = None) -> str:
        """Build prompt for style generation"""
        prompt = f"Create visual effects for: '{user_input}'"
        
        if context:
            prompt += f"\n\nCurrent context:"
            if 'dominant_colors' in context:
                prompt += f"\n- Current colors: {context['dominant_colors'][:3]}"
            if 'motion_intensity' in context:
                prompt += f"\n- Motion level: {context['motion_intensity']:.2f}"
            if 'visual_energy' in context:
                prompt += f"\n- Visual energy: {context['visual_energy']:.2f}"
        
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into style configuration"""
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start:end]
            config = json.loads(json_str)
            
            # Validate and normalize the configuration
            return self._validate_style_config(config)
            
        except Exception as e:
            print(f"Failed to parse AI response: {e}")
            return self._default_style_config()
    
    def _validate_style_config(self, config: Dict) -> Dict:
        """Validate and normalize style configuration"""
        validated = {}
        
        # Colors
        colors = config.get('colors', [[255, 255, 255]])
        validated['colors'] = []
        for color in colors[:5]:  # Max 5 colors
            if isinstance(color, list) and len(color) >= 3:
                r, g, b = [max(0, min(255, int(c))) for c in color[:3]]
                validated['colors'].append((r, g, b))
        
        if not validated['colors']:
            validated['colors'] = [(255, 255, 255)]
        
        # Motion type
        motion_types = ["spiral", "wave", "explosion", "gentle", "chaotic", "flow"]
        validated['motion'] = config.get('motion', 'gentle')
        if validated['motion'] not in motion_types:
            validated['motion'] = 'gentle'
        
        # Intensity
        validated['intensity'] = max(0.0, min(1.0, float(config.get('intensity', 0.5))))
        
        # Duration
        validated['duration'] = max(1.0, min(30.0, float(config.get('duration', 5.0))))
        
        # Particles
        particles = config.get('particles', {})
        validated['particles'] = {
            'count': max(10, min(500, int(particles.get('count', 100)))),
            'size': max(1, min(10, int(particles.get('size', 3)))),
            'speed': max(0.1, min(10.0, float(particles.get('speed', 2.0)))),
            'life': max(0.5, min(10.0, float(particles.get('life', 3.0))))
        }
        
        return validated
    
    def _fallback_style(self, user_input: str) -> Dict:
        """Fallback style generation when AI is unavailable"""
        # Simple keyword-based fallback
        keywords = user_input.lower()
        
        if any(word in keywords for word in ['fire', 'red', 'hot', 'flame']):
            return {
                'colors': [(255, 100, 50), (255, 200, 100), (255, 50, 0)],
                'motion': 'explosion',
                'intensity': 0.8,
                'duration': 4.0,
                'particles': {'count': 150, 'size': 4, 'speed': 3.0, 'life': 2.5}
            }
        elif any(word in keywords for word in ['water', 'blue', 'ocean', 'calm']):
            return {
                'colors': [(50, 150, 255), (100, 200, 255), (0, 100, 200)],
                'motion': 'wave',
                'intensity': 0.4,
                'duration': 6.0,
                'particles': {'count': 80, 'size': 2, 'speed': 1.5, 'life': 4.0}
            }
        elif any(word in keywords for word in ['green', 'forest', 'nature']):
            return {
                'colors': [(50, 200, 100), (100, 255, 150), (30, 150, 80)],
                'motion': 'gentle',
                'intensity': 0.5,
                'duration': 8.0,
                'particles': {'count': 120, 'size': 3, 'speed': 1.0, 'life': 5.0}
            }
        else:
            return self._default_style_config()
    
    def _default_style_config(self) -> Dict:
        """Default style configuration"""
        return {
            'colors': [(255, 255, 255), (200, 200, 255), (150, 150, 255)],
            'motion': 'gentle',
            'intensity': 0.5,
            'duration': 5.0,
            'particles': {'count': 100, 'size': 3, 'speed': 2.0, 'life': 3.0}
        }


class AIStyleProcessor:
    """Main AI style processing interface with enhanced model support"""
    
    def __init__(self, lm_studio_url: str = "http://localhost:1234", model_name: str = "gpt-oss-20b"):
        """
        Initialize AI Style Processor
        
        Args:
            lm_studio_url: LM Studio server URL
            model_name: Model to use (e.g., 'gpt-oss-20b', 'llama-7b', etc.)
        """
        self.client = LMStudioClient(base_url=lm_studio_url, model_name=model_name)
        self.current_style = None
        self.processing_queue = []
        self.is_processing = False
        self.model_name = model_name
        
    def connect(self) -> bool:
        """Connect to LM Studio"""
        return self.client.test_connection()
    
    def process_text_input(self, text: str, context: Dict = None) -> Dict:
        """
        Process text input and generate style
        
        Args:
            text: User's text input
            context: Current visual context
            
        Returns:
            Style configuration
        """
        if not text.strip():
            return self._get_default_style()
        
        print(f"🤖 Processing: '{text}'")
        
        # Generate style using AI
        style_config = self.client.generate_style(text, context)
        self.current_style = style_config
        
        return style_config
    
    def get_current_style(self) -> Dict:
        """Get current active style"""
        return self.current_style or self._get_default_style()
    
    def _get_default_style(self) -> Dict:
        """Get default style when no input"""
        return {
            'colors': [(100, 100, 255), (150, 150, 255), (200, 200, 255)],
            'motion': 'gentle',
            'intensity': 0.3,
            'duration': 5.0,
            'particles': {'count': 50, 'size': 2, 'speed': 1.0, 'life': 4.0}
        }
    
    def is_connected(self) -> bool:
        """Check if connected to AI service"""
        return self.client.is_connected