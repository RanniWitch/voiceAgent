# Contributing to Personal Voice Assistant

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/personal-voice-assistant
   cd personal-voice-assistant
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Setup

### Running Tests
```bash
python -m pytest tests/
```

### Testing Individual Components
```bash
# Test microphone
python simple_mic_test.py

# Test wake word training
python custom_wake_word_trainer.py

# Test basic assistant
python wake_word_assistant.py
```

## 📝 Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Add comments for complex logic

### Example:
```python
def detect_wake_word(self, audio_data, threshold=0.7):
    """
    Detect if the wake word is present in audio data.
    
    Args:
        audio_data: Raw audio data from microphone
        threshold: Confidence threshold (0.0-1.0)
        
    Returns:
        tuple: (detected: bool, confidence: float)
    """
    # Implementation here
    pass
```

## 🎯 Areas for Contribution

### High Priority
- **Cross-platform support** (macOS, Linux)
- **Additional voice commands** (system control, file operations)
- **Better wake word accuracy** (improved training algorithms)
- **Performance optimizations** (faster response times)

### Medium Priority
- **Plugin system** (custom command extensions)
- **Voice synthesis improvements** (more natural speech)
- **Configuration GUI** (advanced settings)
- **Logging and debugging** (better error reporting)

### Low Priority
- **Themes and UI** (visual customization)
- **Additional languages** (non-English support)
- **Cloud integration** (optional online features)

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Operating System** (Windows version)
2. **Python version** (`python --version`)
3. **Steps to reproduce** the issue
4. **Expected behavior** vs **actual behavior**
5. **Error messages** (full traceback if available)
6. **Audio setup** (microphone type, drivers)

### Bug Report Template:
```
**Environment:**
- OS: Windows 11
- Python: 3.9.7
- Microphone: Built-in laptop mic

**Steps to Reproduce:**
1. Run `python wake_word_assistant.py`
2. Say wake word "hey assistant"
3. Assistant doesn't respond

**Expected:** Assistant should activate and respond
**Actual:** No response, no error messages

**Additional Info:**
- Microphone test passes
- Wake word training completed successfully
```

## ✨ Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** - why is this needed?
3. **Provide examples** of how it would work
4. **Consider implementation** - is it feasible?

## 🔄 Pull Request Process

1. **Create an issue** first (for discussion)
2. **Fork and create branch** from main
3. **Make your changes** with tests
4. **Update documentation** if needed
5. **Test thoroughly** on Windows
6. **Submit pull request** with clear description

### PR Checklist:
- [ ] Code follows project style
- [ ] Tests pass (`python -m pytest tests/`)
- [ ] New features have tests
- [ ] Documentation updated
- [ ] No breaking changes (or clearly marked)

## 🧪 Testing Guidelines

### Adding Tests
- Put tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names
- Test both success and failure cases

### Example Test:
```python
def test_wake_word_detection():
    """Test that wake word detection works correctly."""
    assistant = WakeWordAssistant()
    
    # Test positive case
    result = assistant.detect_wake_word("hey assistant")
    assert result[0] == True  # detected
    assert result[1] > 0.5    # confidence
    
    # Test negative case
    result = assistant.detect_wake_word("random speech")
    assert result[0] == False
```

## 📚 Documentation

When adding features:
- Update README.md if user-facing
- Add docstrings to new functions
- Update INSTALL.md for new dependencies
- Add examples to `examples/` folder

## 🤝 Community Guidelines

- **Be respectful** and inclusive
- **Help newcomers** get started
- **Share knowledge** and best practices
- **Give constructive feedback** on PRs
- **Stay on topic** in discussions

## 📞 Getting Help

- **GitHub Issues** - for bugs and features
- **Discussions** - for questions and ideas
- **Code Review** - ask for feedback on PRs

## 🏆 Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Given credit for their contributions

Thank you for helping make this project better! 🎉