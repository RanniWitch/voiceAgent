# Installation Guide

## Quick Install (Recommended)

1. **Download the project:**
   ```bash
   git clone https://github.com/yourusername/personal-voice-assistant
   cd personal-voice-assistant
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the setup:**
   ```bash
   python voice_assistant_setup.py
   ```

## Manual Installation

### Prerequisites

- **Windows 10/11** (required)
- **Python 3.7+** ([Download here](https://python.org))
- **Microphone** (built-in or external)
- **Internet connection** (for some voice commands)

### Step-by-Step

1. **Install Python** (if not already installed)
   - Download from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH" during installation

2. **Download the project**
   - Download ZIP from GitHub or clone with git
   - Extract to a folder like `C:\VoiceAssistant\`

3. **Install Python packages**
   ```bash
   pip install speech_recognition pyttsx3 requests numpy librosa scikit-learn pyaudio
   ```

4. **Test your setup**
   ```bash
   python simple_mic_test.py
   ```

5. **Run the setup wizard**
   ```bash
   python voice_assistant_setup.py
   ```

## Troubleshooting Installation

### PyAudio Installation Issues

If you get errors installing PyAudio:

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Alternative:**
Download the appropriate `.whl` file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install:
```bash
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```

### Microphone Permission Issues

1. Go to **Windows Settings > Privacy > Microphone**
2. Enable "Allow apps to access your microphone"
3. Make sure Python is allowed

### Missing Visual C++ Build Tools

If you get compiler errors:
1. Download **Microsoft C++ Build Tools**
2. Or install **Visual Studio Community** with C++ workload

## Verification

After installation, verify everything works:

1. **Test microphone:**
   ```bash
   python simple_mic_test.py
   ```

2. **Check dependencies:**
   ```bash
   python check_dependencies.py
   ```

3. **Run setup:**
   ```bash
   python voice_assistant_setup.py
   ```

If all tests pass, you're ready to use your voice assistant!