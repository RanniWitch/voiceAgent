#!/usr/bin/env py
"""
Check what dependencies are available and identify missing ones.
"""

import sys
import importlib

def check_dependency(name, package=None):
    """Check if a dependency is available."""
    try:
        if package:
            importlib.import_module(package)
        else:
            importlib.import_module(name)
        return True, "✅ Available"
    except ImportError as e:
        return False, f"❌ Missing: {e}"

def main():
    print("🔍 Checking Dependencies for Voice Recognition AI")
    print("=" * 60)
    
    # Core dependencies
    dependencies = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("NumPy", "numpy"),
        ("AsyncIO", "asyncio"),
        ("JSON", "json"),
        ("Logging", "logging"),
        ("Time", "time"),
        ("UUID", "uuid"),
        ("Datetime", "datetime"),
        ("Typing", "typing"),
        ("Dataclasses", "dataclasses"),
        ("Collections", "collections"),
        ("Queue", "queue"),
    ]
    
    # Optional dependencies
    optional_deps = [
        ("PyAudio", "pyaudio"),
        ("SoundDevice", "sounddevice"),
        ("Whisper", "whisper"),
        ("Faster-Whisper", "faster_whisper"),
        ("Transformers", "transformers"),
        ("Torch", "torch"),
        ("Pydub", "pydub"),
        ("Librosa", "librosa"),
        ("PSUtil", "psutil"),
    ]
    
    print("CORE DEPENDENCIES:")
    core_available = 0
    for name, package in dependencies:
        available, status = check_dependency(name, package)
        print(f"  {name:15} {status}")
        if available:
            core_available += 1
    
    print(f"\nCore Dependencies: {core_available}/{len(dependencies)} available")
    
    print("\nOPTIONAL DEPENDENCIES:")
    optional_available = 0
    for name, package in optional_deps:
        available, status = check_dependency(name, package)
        print(f"  {name:15} {status}")
        if available:
            optional_available += 1
    
    print(f"\nOptional Dependencies: {optional_available}/{len(optional_deps)} available")
    
    # Check Python version
    print(f"\nPython Version: {sys.version}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if core_available < len(dependencies):
        print("❌ Missing core dependencies. Install with:")
        print("   pip install fastapi uvicorn numpy")
    
    if optional_available < 3:
        print("⚠️  Few optional dependencies available.")
        print("   For full functionality, install:")
        print("   pip install torch transformers faster-whisper pydub psutil")
    
    # Test what we can run
    print("\n🚀 WHAT YOU CAN RUN:")
    
    fastapi_available, _ = check_dependency("FastAPI", "fastapi")
    uvicorn_available, _ = check_dependency("Uvicorn", "uvicorn")
    
    if fastapi_available and uvicorn_available:
        print("✅ minimal_connection_test.py - Basic WebSocket test")
        print("✅ simple_websocket_test.py - Enhanced WebSocket test")
    else:
        print("❌ WebSocket tests require: pip install fastapi uvicorn")
    
    numpy_available, _ = check_dependency("NumPy", "numpy")
    if numpy_available:
        print("✅ Basic audio processing components")
    else:
        print("❌ Audio processing requires: pip install numpy")
    
    whisper_available, _ = check_dependency("Whisper", "whisper")
    faster_whisper_available, _ = check_dependency("Faster-Whisper", "faster_whisper")
    
    if whisper_available or faster_whisper_available:
        print("✅ Speech recognition available")
    else:
        print("❌ Speech recognition requires: pip install faster-whisper")
    
    transformers_available, _ = check_dependency("Transformers", "transformers")
    if transformers_available:
        print("✅ Translation available")
    else:
        print("❌ Translation requires: pip install transformers torch")
    
    print("\n🎯 QUICK START:")
    if fastapi_available and uvicorn_available:
        print("1. Run: py minimal_connection_test.py")
        print("2. Open: http://localhost:8008")
        print("3. Test WebSocket connection")
    else:
        print("1. Install: pip install fastapi uvicorn")
        print("2. Run: py minimal_connection_test.py")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()