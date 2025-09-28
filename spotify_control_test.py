#!/usr/bin/env python3
"""
Quick Spotify Control Test
Test media controls with Spotify
"""

import pyautogui
import time

def test_spotify_controls():
    """Test all Spotify controls"""
    print("🎵 Testing Spotify Controls")
    print("Make sure Spotify is running!")
    input("Press Enter to start testing...")
    
    controls = [
        ("Play/Pause", lambda: pyautogui.press('playpause')),
        ("Next Track", lambda: pyautogui.press('nexttrack')),
        ("Previous Track (Double Press)", lambda: (pyautogui.press('prevtrack'), time.sleep(0.3), pyautogui.press('prevtrack'))),
        ("Volume Up", lambda: pyautogui.press('volumeup')),
        ("Volume Down", lambda: pyautogui.press('volumedown')),
    ]
    
    for name, action in controls:
        print(f"\n🎵 Testing {name}...")
        action()
        time.sleep(2)  # Wait 2 seconds between commands
        print(f"✅ {name} command sent")
    
    print("\n🎵 All tests completed!")

if __name__ == "__main__":
    test_spotify_controls()