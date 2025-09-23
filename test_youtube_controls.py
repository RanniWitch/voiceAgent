#!/usr/bin/env python3
"""
Test YouTube Controls
Quick test for the new media control features
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wake_word_assistant import WakeWordAssistant

def test_youtube_controls():
    """Test the YouTube control functions"""
    print("🎬 Testing YouTube Controls...")
    
    assistant = WakeWordAssistant()
    
    # Test each control
    controls = [
        ("Play/Pause", assistant.youtube_play_pause),
        ("Fullscreen", assistant.youtube_fullscreen),
        ("Skip Forward", assistant.youtube_skip_forward),
        ("Skip Back", assistant.youtube_skip_back),
        ("Volume Up", assistant.youtube_volume_up),
        ("Volume Down", assistant.youtube_volume_down),
        ("Mute", assistant.youtube_mute),
    ]
    
    print("\nAvailable YouTube Controls:")
    for name, func in controls:
        try:
            result = func()
            print(f"✅ {name}: {result}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print("\n🎯 Test Commands:")
    print("Open YouTube in your browser, then try these voice commands:")
    print("- 'Hey [your wake word], play'")
    print("- 'Hey [your wake word], fullscreen'")
    print("- 'Hey [your wake word], skip forward'")
    print("- 'Hey [your wake word], volume up'")
    
    print("\n💡 These controls work with:")
    print("- YouTube (in any browser)")
    print("- Netflix")
    print("- VLC Media Player")
    print("- Most video players that use standard keyboard shortcuts")

if __name__ == "__main__":
    test_youtube_controls()