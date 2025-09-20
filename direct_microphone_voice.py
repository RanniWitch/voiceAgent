#!/usr/bin/env py
"""
Direct microphone voice recognition - bypasses all browser audio issues.
Uses your system microphone directly with SpeechRecognition.
"""

import speech_recognition as sr
import time
import threading
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectMicrophoneRecognizer:
    """Direct microphone voice recognition."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.transcription_queue = queue.Queue()
        
        # Adjust for ambient noise
        print("🎤 Adjusting for ambient noise... (speak after this completes)")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("✅ Microphone calibrated!")
    
    def listen_continuously(self):
        """Listen continuously and transcribe speech."""
        print("🎧 Starting continuous listening...")
        print("💬 Speak now - your speech will be transcribed in real-time!")
        print("🛑 Press Ctrl+C to stop")
        print("=" * 60)
        
        def callback(recognizer, audio):
            """Callback for when audio is captured."""
            try:
                # Try to transcribe the audio
                text = recognizer.recognize_google(audio, language='en-US')
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] 🗣️  You said: {text}")
                self.transcription_queue.put(text)
                
            except sr.UnknownValueError:
                print(f"[{time.strftime('%H:%M:%S')}] 🔇 Could not understand audio")
            except sr.RequestError as e:
                print(f"[{time.strftime('%H:%M:%S')}] ❌ Error: {e}")
        
        # Start listening in the background
        stop_listening = self.recognizer.listen_in_background(
            self.microphone, 
            callback,
            phrase_time_limit=5  # Process audio every 5 seconds
        )
        
        try:
            while True:
                time.sleep(0.1)  # Keep the main thread alive
        except KeyboardInterrupt:
            print("\n🛑 Stopping voice recognition...")
            stop_listening(wait_for_stop=False)
            print("✅ Voice recognition stopped")
    
    def test_single_recognition(self):
        """Test single speech recognition."""
        print("🎤 Single speech recognition test")
        print("💬 Say something now...")
        
        try:
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
            print("🔄 Processing audio...")
            
            # Transcribe audio
            text = self.recognizer.recognize_google(audio, language='en-US')
            print(f"✅ You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("❌ No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error with speech recognition service: {e}")
            return None

def test_microphone():
    """Test if microphone is working."""
    print("🔍 Testing Microphone")
    print("=" * 30)
    
    try:
        # List available microphones
        print("Available microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {index}: {name}")
        
        # Test default microphone
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        print(f"\n🎤 Using default microphone: {sr.Microphone.list_microphone_names()[mic.device_index]}")
        
        with mic as source:
            print("🔧 Testing microphone access...")
            r.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Microphone test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def main():
    """Main function."""
    print("🎯 Direct Microphone Voice Recognition")
    print("=" * 50)
    
    # Test microphone first
    if not test_microphone():
        print("❌ Microphone test failed. Please check your microphone.")
        return
    
    print("\n" + "=" * 50)
    
    # Create recognizer
    recognizer = DirectMicrophoneRecognizer()
    
    # Ask user what they want to do
    print("\nChoose an option:")
    print("1. Single speech recognition test")
    print("2. Continuous listening mode")
    
    try:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            print("\n" + "=" * 50)
            recognizer.test_single_recognition()
        elif choice == "2":
            print("\n" + "=" * 50)
            recognizer.listen_continuously()
        else:
            print("Invalid choice. Running single test...")
            recognizer.test_single_recognition()
            
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()