#!/usr/bin/env python3
"""
测试脚本来验证segmentation按钮功能
"""

import sys
import os

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_segmentation_integration():
    """测试segmentation集成"""
    print("🧪 Testing segmentation integration...")
    
    try:
        # Import the studio class
        from interface.multi_modal_studio import MultiModalStudio
        
        # Test that the new button attribute exists
        studio = MultiModalStudio(800, 600)
        
        # Check if segmentation button exists
        if hasattr(studio, 'segmentation_button'):
            print("✅ Segmentation button exists")
        else:
            print("❌ Segmentation button missing")
            return False
        
        # Check if segmentation state exists
        if hasattr(studio, 'segmentation_active'):
            print("✅ Segmentation state tracking exists")
        else:
            print("❌ Segmentation state tracking missing")
            return False
        
        # Check if toggle method exists
        if hasattr(studio, 'toggle_segmentation'):
            print("✅ Toggle segmentation method exists")
        else:
            print("❌ Toggle segmentation method missing")
            return False
        
        # Check if render method exists
        if hasattr(studio, '_render_segmentation_overlay'):
            print("✅ Render segmentation overlay method exists")
        else:
            print("❌ Render segmentation overlay method missing")
            return False
        
        print("🎉 All segmentation integration components are present!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_segmentation_integration()
    sys.exit(0 if success else 1)