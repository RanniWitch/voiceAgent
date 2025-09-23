# 🎤 Personal Voice Assistant

A customizable, always-listening voice assistant for Windows that responds to your personal wake word. Similar to Alexa or Google Assistant, but completely offline and privacy-focused.

## ✨ Features

- **Custom Wake Word Training** - Train your own wake word like "Hey Assistant" or "Computer Sarah"
- **Always Listening** - Runs in background, activates on your wake word
- **Voice Commands** - Open websites, answer questions, control your PC
- **Privacy First** - Everything runs locally, no data sent to cloud
- **Auto-Start** - Optionally start with Windows
- **Easy Setup** - Simple GUI setup process

## 🚀 Quick Start

1. **Download & Install**
   ```bash
   git clone https://github.com/yourusername/personal-voice-assistant
   cd personal-voice-assistant
   pip install -r requirements.txt
   ```

2. **Run Setup**
   ```bash
   python voice_assistant_setup.py
   ```

3. **Train Your Wake Word**
   - Enter your custom wake word (e.g., "Hey Assistant")
   - Say it 3 times to train the AI
   - Start using your assistant!

## 🎯 Voice Commands

Once your assistant is running, try these commands:

- **"[Your Wake Word], what time is it?"**
- **"[Your Wake Word], open YouTube"**
- **"[Your Wake Word], search for Python tutorials"**
- **"[Your Wake Word], what's the weather?"**
- **"[Your Wake Word], tell me a joke"**

### 🔧 Optional: Enhanced AI Responses

For smarter conversations, you can optionally add a free Gemini API key:
1. Get a free key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. The assistant will ask for it during setup (or skip for basic responses)

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

## 📁 Project Structure

```
├── voice_assistant_setup.py      # Main setup launcher
├── wake_word_assistant.py        # Core voice assistant
├── custom_wake_word_trainer.py   # Wake word training system
├── setup_windows_startup.py      # Auto-start configuration
├── src/                          # Advanced processing modules
├── examples/                     # Usage examples
└── tests/                        # Test suite
```

## 🔧 Advanced Features

The project includes advanced modules for:
- Real-time speech processing
- Multi-language translation
- Web-based subtitle display
- Audio processing pipeline
- Voice activity detection

## 🛠️ Development

Run tests:
```bash
python -m pytest tests/
```

Test microphone:
```bash
python simple_mic_test.py
```

## 📋 Requirements

- Windows 10/11
- Python 3.7+
- Microphone
- Internet connection (for speech recognition and some commands)

**No API keys required!** The assistant works out-of-the-box with free services.

## 🆘 Troubleshooting

**Assistant not responding?**
- Check microphone permissions
- Retrain your wake word
- Ensure assistant window isn't minimized

**Poor wake word recognition?**
- Train in a quiet environment
- Speak clearly during training
- Try a longer, more unique wake word

**Need help?**
- Check the built-in help in the setup GUI
- Review the examples folder
- Open an issue on GitHub

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
