#!/usr/bin/env py
"""
Quick fix for FFmpeg issues in voice recognition bot.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is available."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg is installed and working!")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ FFmpeg not found or not working")
    return False

def check_ffprobe():
    """Check if FFprobe is available."""
    try:
        result = subprocess.run(['ffprobe', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFprobe is installed and working!")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ FFprobe not found or not working")
    return False

def install_ffmpeg_chocolatey():
    """Try to install FFmpeg via Chocolatey."""
    print("🍫 Attempting to install FFmpeg via Chocolatey...")
    try:
        result = subprocess.run(['choco', 'install', 'ffmpeg', '-y'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ FFmpeg installed successfully via Chocolatey!")
            return True
        else:
            print(f"❌ Chocolatey installation failed: {result.stderr}")
    except FileNotFoundError:
        print("❌ Chocolatey not found. Please install Chocolatey first.")
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out")
    return False

def install_ffmpeg_winget():
    """Try to install FFmpeg via winget."""
    print("📦 Attempting to install FFmpeg via winget...")
    try:
        result = subprocess.run(['winget', 'install', 'ffmpeg'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ FFmpeg installed successfully via winget!")
            return True
        else:
            print(f"❌ Winget installation failed: {result.stderr}")
    except FileNotFoundError:
        print("❌ Winget not found")
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out")
    return False

def test_pydub_with_ffmpeg():
    """Test if pydub works with FFmpeg."""
    try:
        from pydub import AudioSegment
        from pydub.utils import which
        
        print("\n🔍 Testing pydub FFmpeg integration...")
        
        # Check if pydub can find ffmpeg
        ffmpeg_path = which("ffmpeg")
        ffprobe_path = which("ffprobe")
        
        print(f"FFmpeg path: {ffmpeg_path or 'Not found'}")
        print(f"FFprobe path: {ffprobe_path or 'Not found'}")
        
        if ffmpeg_path and ffprobe_path:
            print("✅ Pydub should work correctly now!")
            return True
        else:
            print("❌ Pydub still can't find FFmpeg tools")
            return False
            
    except ImportError:
        print("❌ Pydub not installed")
        return False

def main():
    print("🔧 FFmpeg Fix Script for Voice Recognition Bot")
    print("=" * 60)
    
    # Check current status
    ffmpeg_ok = check_ffmpeg()
    ffprobe_ok = check_ffprobe()
    
    if ffmpeg_ok and ffprobe_ok:
        print("\n✅ FFmpeg is already working! Testing pydub integration...")
        test_pydub_with_ffmpeg()
        return
    
    print("\n🚀 Attempting to install FFmpeg...")
    
    # Try different installation methods
    success = False
    
    # Try Chocolatey first
    if install_ffmpeg_chocolatey():
        success = True
    elif install_ffmpeg_winget():
        success = True
    
    if success:
        print("\n🔄 Refreshing PATH and testing...")
        # Refresh environment
        os.system("refreshenv")
        
        # Test again
        if check_ffmpeg() and check_ffprobe():
            test_pydub_with_ffmpeg()
        else:
            print("⚠️  You may need to restart your terminal/IDE for PATH changes to take effect")
    else:
        print("\n❌ Automatic installation failed. Manual installation required:")
        print("1. Go to https://ffmpeg.org/download.html#build-windows")
        print("2. Download the Windows build")
        print("3. Extract to C:\\ffmpeg")
        print("4. Add C:\\ffmpeg\\bin to your PATH environment variable")
        print("5. Restart your terminal/IDE")

if __name__ == "__main__":
    main()