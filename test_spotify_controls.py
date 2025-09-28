#!/usr/bin/env python3
"""
Test Spotify Controls
Test different methods to control Spotify
"""

import time
import subprocess
import sys

def test_keyboard_shortcuts():
    """Test Spotify keyboard shortcuts"""
    print("Testing Spotify keyboard shortcuts...")
    
    try:
        import pyautogui
        print("✅ pyautogui available")
        
        # Test different Spotify shortcuts
        shortcuts = [
            ("Play/Pause", "ctrl+alt+space"),
            ("Next Track", "ctrl+alt+right"),
            ("Previous Track", "ctrl+alt+left"),
            ("Volume Up", "ctrl+alt+up"),
            ("Volume Down", "ctrl+alt+down")
        ]
        
        for name, shortcut in shortcuts:
            print(f"\n🎵 Testing {name} ({shortcut})")
            input("Press Enter to test this shortcut...")
            pyautogui.hotkey(*shortcut.split('+'))
            print(f"✅ Sent {shortcut}")
            
    except ImportError:
        print("❌ pyautogui not available")
        try:
            import keyboard
            print("✅ keyboard library available")
            
            shortcuts = [
                ("Play/Pause", "ctrl+alt+space"),
                ("Next Track", "ctrl+alt+right"),
                ("Previous Track", "ctrl+alt+left"),
                ("Volume Up", "ctrl+alt+up"),
                ("Volume Down", "ctrl+alt+down")
            ]
            
            for name, shortcut in shortcuts:
                print(f"\n🎵 Testing {name} ({shortcut})")
                input("Press Enter to test this shortcut...")
                keyboard.press_and_release(shortcut)
                print(f"✅ Sent {shortcut}")
                
        except ImportError:
            print("❌ keyboard library not available")

def test_media_keys():
    """Test Windows media keys"""
    print("\n" + "="*50)
    print("Testing Windows Media Keys...")
    
    try:
        import pyautogui
        
        media_keys = [
            ("Play/Pause", "playpause"),
            ("Next Track", "nexttrack"),
            ("Previous Track", "prevtrack"),
            ("Volume Up", "volumeup"),
            ("Volume Down", "volumedown")
        ]
        
        for name, key in media_keys:
            print(f"\n🎵 Testing {name} ({key})")
            input("Press Enter to test this media key...")
            pyautogui.press(key)
            print(f"✅ Sent {key}")
            
    except ImportError:
        print("❌ pyautogui not available for media keys")

def check_spotify_running():
    """Check if Spotify is running"""
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'spotify' in result.stdout.lower():
            print("✅ Spotify is running")
            return True
        else:
            print("❌ Spotify is not running")
            print("Please start Spotify and try again")
            return False
    except Exception as e:
        print(f"Error checking Spotify: {e}")
        return False

def test_alternative_shortcuts():
    """Test alternative Spotify shortcuts"""
    print("\n" + "="*50)
    print("Testing Alternative Spotify Shortcuts...")
    
    try:
        import pyautogui
        
        # Alternative shortcuts that might work
        alt_shortcuts = [
            ("Space (if Spotify focused)", "space"),
            ("Ctrl+Right (if Spotify focused)", "ctrl+right"),
            ("Ctrl+Left (if Spotify focused)", "ctrl+left"),
        ]
        
        print("Note: These require Spotify to be the active window")
        
        for name, shortcut in alt_shortcuts:
            print(f"\n🎵 Testing {name}")
            input("Make sure Spotify is active, then press Enter...")
            if '+' in shortcut:
                pyautogui.hotkey(*shortcut.split('+'))
            else:
                pyautogui.press(shortcut)
            print(f"✅ Sent {shortcut}")
            
    except ImportError:
        print("❌ pyautogui not available")

if __name__ == "__main__":
    print("🎵 Spotify Control Tester")
    print("="*50)
    
    # Check if Spotify is running
    if not check_spotify_running():
        print("\n⚠️ Please start Spotify first!")
        input("Press Enter after starting Spotify...")
    
    print("\nChoose test method:")
    print("1. Test Spotify Global Shortcuts (Ctrl+Alt+...)")
    print("2. Test Windows Media Keys")
    print("3. Test Alternative Shortcuts (requires Spotify focus)")
    print("4. Test All Methods")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_keyboard_shortcuts()
    elif choice == "2":
        test_media_keys()
    elif choice == "3":
        test_alternative_shortcuts()
    elif choice == "4":
        test_keyboard_shortcuts()
        test_media_keys()
        test_alternative_shortcuts()
    else:
        print("Invalid choice")
        
    print("\n🎵 Testing complete!")