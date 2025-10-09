# AI Voice Assistant

A powerful, always-listening voice assistant with custom wake word training, media controls, and application launching capabilities.

## Features

### Core Functionality
- **Custom Wake Word Training** - Train your own wake word (like "Hey Black")
- **Always Listening Mode** - Background operation with system tray
- **Voice Command Processing** - Natural language understanding
- **Text-to-Speech Responses** - Audio feedback for commands

### Media Controls
- **Spotify Control** - Play/pause, next/previous track, volume control
- **YouTube Control** - Play/pause, skip, fullscreen, volume, mute
- **Discord Control** - Mute mic, deafen, push-to-talk
- **Universal Media Keys** - Works with any media player

### System Integration
- **Application Launcher** - Voice-controlled app launching (200+ apps)
- **Screen Recording** - Save clips with voice commands
- **System Commands** - Open calculator, notepad, browser, etc.
- **Website Navigation** - Voice-controlled web browsing

### Visual Interface
- **Siri-like Visualizer** - Animated waveform display
- **System Tray Operation** - Minimized background operation
- **GUI Controls** - Easy configuration and monitoring

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-voice-assistant.git
cd ai-voice-assistant

# Install dependencies
pip install -r requirements.txt

# Run setup
python voice_assistant_setup.py
```

### 2. Basic Usage
```bash
# Start the voice assistant
python wake_word_assistant.py

# Or run in background mode
python background_voice_assistant.py
```

### 3. Train Custom Wake Word
```bash
# Train your own wake word
python custom_wake_word_trainer.py
```

## Voice Commands

### Wake Words
- "Hey Assistant" / "Computer" / "Hey Computer"
- Custom trained wake words (e.g., "Hey Black")

### Media Controls
```
Spotify:
- "Hey Black, spotify play" - Play/pause
- "Hey Black, next song" - Skip to next track  
- "Hey Black, previous song" - Go to previous track
- "Hey Black, spotify volume up" - Increase volume

YouTube:
- "Hey Black, play" - Play/pause video
- "Hey Black, skip forward" - Skip ahead 10 seconds
- "Hey Black, fullscreen" - Toggle fullscreen
- "Hey Black, volume up" - Increase volume

Discord:
- "Hey Black, mute mic" - Toggle microphone mute
- "Hey Black, deafen" - Toggle deafen
- "Hey Black, push to talk" - Activate PTT
```

### System Commands
```
Applications:
- "Hey Black, open calculator"
- "Hey Black, launch notepad" 
- "Hey Black, start chrome"
- "Hey Black, open [any app name]"

Websites:
- "Hey Black, open youtube"
- "Hey Black, go to netflix"
- "Hey Black, open spotify"

Screen Recording:
- "Hey Black, save last 30 seconds"
- "Hey Black, record past 2 minutes"
- "Hey Black, open recordings"
```

### Information & AI
```
AI Queries:
- "Hey Black, what time is it?"
- "Hey Black, what's the weather like?"
- "Hey Black, explain quantum physics"
- "Hey Black, help me with coding"
```

## Configuration

### Microphone Setup
```bash
# Select and configure microphone
python microphone_selector.py
```

### AI Configuration
Edit `ai_config.json` to configure:
- Gemini API key for AI responses
- Wake word sensitivity
- Command timeout settings

### Windows Startup
```bash
# Set up automatic startup
python setup_windows_startup.py
```

## Project Structure

```
ai-voice-assistant/
├── wake_word_assistant.py          # Main voice assistant
├── background_voice_assistant.py   # Background/tray mode
├── custom_wake_word_trainer.py     # Wake word training
├── app_launcher.py                 # Application launcher
├── screen_recorder.py              # Screen recording functionality
├── voice_visualizer.py             # Visual waveform interface
├── microphone_selector.py          # Microphone configuration
├── voice_assistant_setup.py        # Setup wizard
├── requirements.txt                # Python dependencies
├── INSTALL.md                      # Installation guide
└── recordings/                     # Screen recordings folder
```

## Testing

```bash
# Test wake word accuracy
python test_wake_word_accuracy.py

# Test microphone
python simple_microphone_test.py

# Test Spotify controls
python spotify_control_test.py

# Diagnostic tools
python wake_word_diagnostic.py
```

## Requirements

- **Python 3.8+**
- **Windows 10/11** (primary support)
- **Microphone** (USB or built-in)
- **Internet connection** (for AI features)

### Python Dependencies
- `speech_recognition` - Voice recognition
- `pyttsx3` - Text-to-speech
- `pyautogui` - System automation
- `tkinter` - GUI interface
- `numpy` - Audio processing
- `librosa` - Audio feature extraction
- `requests` - API communication

## Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/amazing-feature`)  
3. Commit your changes (`git commit -m 'Add amazing feature'`)  
4. Push to the branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request  

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **SpeechRecognition** library for voice recognition  
- **PyAutoGUI** for system automation  
- **Librosa** for audio processing  
- **Google Speech API** for speech-to-text  

## Troubleshooting

### Common Issues

**Microphone not detected:**
```bash
python microphone_selector.py
```

**Wake word not responding:**
```bash
python wake_word_diagnostic.py
```

**Dependencies missing:**
```bash
pip install -r requirements.txt
```

**Spotify controls not working:**
- Ensure Spotify is running
- Test with: `python spotify_control_test.py`

---

**Made with love for hands-free computing**
