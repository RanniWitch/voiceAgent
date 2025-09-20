# AI Voice Recognition Agent

A real-time voice recognition system with web interface that converts speech to text using Google Speech Recognition API.

##  Features

- **Real-time speech transcription** - Immediate speech-to-text conversion
- **Web interface** - Easy-to-use browser-based interface  
- **Direct microphone access** - Bypasses browser audio format issues
- **Multiple microphone support** - Works with various audio devices
- **WebSocket communication** - Real-time data streaming
- **No complex dependencies** - Simple setup and reliable operation

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- Microphone access
- Internet connection (for Google Speech Recognition API)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ai-voice-agent.git
   cd ai-voice-agent
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. **Run the voice recognition server:**
   ```bash
   python final_working_solution.py
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:8016
   ```

3. **Use the interface:**
   - Click "Connect" to establish WebSocket connection
   - Click "Start Listening" to begin voice recognition
   - Speak normally - your speech will be transcribed in real-time!
   - Click "Stop Listening" when done

##  Testing

### Test Voice Recognition
```bash
python simple_mic_test.py
```

### Test Dependencies
```bash
python check_dependencies.py
```

### Test WebSocket Connection
```bash
python minimal_connection_test.py
```

##  Project Structure

```
ai-voice-agent/
├── final_working_solution.py    # Main application
├── simple_mic_test.py          # Voice recognition test
├── direct_microphone_voice.py  # Command-line tool
├── check_dependencies.py       # Dependency checker
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── src/                        # Additional components
└── tests/                      # Test files
```

##  How It Works

The system uses direct microphone access instead of processing audio from the browser, which eliminates audio format conversion issues. The server listens to your system microphone and sends transcriptions to the web interface in real-time via WebSocket.

**Architecture:**
1. **Python Backend** - Handles microphone input and speech recognition
2. **Google Speech Recognition API** - Converts speech to text (free tier)
3. **WebSocket Server** - Real-time communication with web interface
4. **Web Interface** - User-friendly browser-based control panel

##  Troubleshooting

### Common Issues

**Microphone not working:**
```bash
python simple_mic_test.py
```

**Dependencies missing:**
```bash
python check_dependencies.py
```

**Connection issues:**
```bash
python minimal_connection_test.py
```

### Platform-Specific Notes

**Windows:**
- May need to install Visual C++ Build Tools for some dependencies
- Ensure microphone permissions are granted

**macOS:**
- May need to grant microphone access in System Preferences
- Install Xcode command line tools if needed

**Linux:**
- Install ALSA development headers: `sudo apt-get install libasound2-dev`
- Ensure user is in audio group: `sudo usermod -a -G audio $USER`

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Google Speech Recognition API for reliable speech-to-text conversion
- FastAPI for the excellent web framework
- SpeechRecognition library for Python audio processing

##  Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Run the test scripts to diagnose problems
3. Open an issue on GitHub with detailed information about your setup and the problem
