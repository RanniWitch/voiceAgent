#!/usr/bin/env python3
"""
Dependency installer for Advanced Voice Recognition System
Handles platform-specific installations and common issues
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def install_package(package, description=None):
    """Install a single package with error handling"""
    if description is None:
        description = f"Installing {package}"
    
    # Try different installation methods (Windows uses 'py' command)
    commands = [
        f"pip install {package}",
        f"pip install --user {package}",
        f"py -m pip install {package}",
        f"py -m pip install --user {package}",
        f"python -m pip install {package}",  # Fallback
        f"python -m pip install --user {package}"  # Fallback
    ]
    
    for cmd in commands:
        if run_command(cmd, f"{description} (using {cmd.split()[0]})"):
            return True
    
    return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required")
        return False
    
    print("✅ Python version compatible")
    return True

def install_pyaudio_windows():
    """Special handling for PyAudio on Windows"""
    print("\n🔄 Installing PyAudio for Windows...")
    
    # Try precompiled wheel first
    commands = [
        "pip install pipwin",
        "pipwin install pyaudio"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd}"):
            break
    else:
        return True
    
    # Fallback to regular pip
    return install_package("pyaudio", "Installing PyAudio (fallback)")

def main():
    """Main installation process"""
    print("🎤 Advanced Voice Recognition System - Dependency Installer")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Detect platform
    system = platform.system()
    print(f"Operating System: {system}")
    
    # Core packages that usually work
    core_packages = [
        ("numpy", "NumPy - Numerical computing"),
        ("scipy", "SciPy - Scientific computing"),
        ("matplotlib", "Matplotlib - Plotting library"),
        ("scikit-learn", "Scikit-learn - Machine learning"),
    ]
    
    print("\n📦 Installing core packages...")
    for package, description in core_packages:
        install_package(package, description)
    
    # Speech recognition
    print("\n🎤 Installing speech recognition...")
    speech_packages = [
        ("SpeechRecognition", "SpeechRecognition - Main speech library"),
    ]
    
    for package, description in speech_packages:
        install_package(package, description)
    
    # Audio packages (more complex)
    print("\n🔊 Installing audio processing packages...")
    
    # PyAudio (platform specific)
    if system == "Windows":
        install_pyaudio_windows()
    else:
        install_package("pyaudio", "PyAudio - Audio I/O")
    
    # Other audio packages
    audio_packages = [
        ("SoundFile", "SoundFile - Audio file I/O"),
        ("librosa", "Librosa - Audio analysis"),
    ]
    
    for package, description in audio_packages:
        install_package(package, description)
    
    # Test installations
    print("\n🧪 Testing installations...")
    test_imports = [
        ("speech_recognition", "SpeechRecognition"),
        ("numpy", "NumPy"),
        ("matplotlib", "Matplotlib"),
        ("sklearn", "Scikit-learn"),
        ("soundfile", "SoundFile"),
        ("librosa", "Librosa"),
        ("scipy", "SciPy"),
    ]
    
    failed_imports = []
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} - Import successful")
        except ImportError as e:
            print(f"❌ {name} - Import failed: {e}")
            failed_imports.append((module, name))
    
    # PyAudio test (optional)
    try:
        import pyaudio
        print("✅ PyAudio - Import successful")
    except ImportError:
        print("⚠️ PyAudio - Import failed (microphone input may not work)")
        print("   Try: pip install pyaudio")
        if system == "Windows":
            print("   Or download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
    
    # Summary
    print("\n" + "=" * 60)
    if failed_imports:
        print("❌ Some packages failed to install:")
        for module, name in failed_imports:
            print(f"   - {name}")
        print("\nTry installing manually:")
        for module, name in failed_imports:
            print(f"   pip install {module}")
    else:
        print("✅ All core packages installed successfully!")
        print("\n🚀 You can now run:")
        print("   python voice_system_launcher.py")
    
    print("\n💡 If you encounter issues:")
    print("   - Make sure you're in a virtual environment")
    print("   - Try: pip install --upgrade pip")
    print("   - On Windows, you might need Visual Studio Build Tools")
    print("   - For PyAudio issues, see: https://pypi.org/project/PyAudio/")

if __name__ == "__main__":
    main()