#!/usr/bin/env py
"""
Simple microphone test - let's get voice recognition working!
"""

import speech_recognition as sr
import time

def simple_voice_test():
    """Simple voice recognition test."""
    print("🎤 Simple Voice Recognition Test")
    print("=" * 40)
    
    # Create recognizer and microphone
    r = sr.Recognizer()
    
    # Try to use default microphone
    try:
        mic = sr.Microphone()
        print("✅ Microphone initialized")
    except Exception as e:
        print(f"❌ Microphone initialization failed: {e}")
        return
    
    # Adjust for ambient noise
    print("🔧 Adjusting for ambient noise... (please be quiet)")
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=2)
        print("✅ Noise adjustment complete")
    except Exception as e:
        print(f"❌ Noise adjustment failed: {e}")
        return
    
    # Test speech recognition
    print("\n💬 Please say something clearly...")
    print("⏱️  You have 10 seconds to speak")
    
    try:
        with mic as source:
            # Listen for audio
            print("🎧 Listening...")
            audio = r.listen(source, timeout=10, phrase_time_limit=5)
            print("✅ Audio captured!")
        
        # Try to recognize speech
        print("🔄 Processing speech...")
        text = r.recognize_google(audio, language='en-US')
        
        print(f"\n🎉 SUCCESS! You said: '{text}'")
        return text
        
    except sr.WaitTimeoutError:
        print("❌ No speech detected - timeout")
    except sr.UnknownValueError:
        print("❌ Could not understand the audio")
    except sr.RequestError as e:
        print(f"❌ Google Speech Recognition error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return None

def continuous_listening():
    """Continuous listening mode."""
    print("🎧 Continuous Listening Mode")
    print("=" * 40)
    print("💬 Speak anytime - I'm listening!")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    # Adjust for ambient noise
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)
    
    def callback(recognizer, audio):
        try:
            text = recognizer.recognize_google(audio, language='en-US')
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] 🗣️  You said: {text}")
        except sr.UnknownValueError:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] 🔇 (unclear audio)")
        except sr.RequestError as e:
            print(f"❌ Recognition error: {e}")
    
    # Start background listening
    stop_listening = r.listen_in_background(mic, callback, phrase_time_limit=3)
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        stop_listening(wait_for_stop=False)
        print("✅ Stopped")

def main():
    print("🎯 Voice Recognition Test")
    print("Choose a test:")
    print("1. Single speech test")
    print("2. Continuous listening")
    
    try:
        choice = input("\nEnter 1 or 2: ").strip()
        print()
        
        if choice == "1":
            result = simple_voice_test()
            if result:
                print(f"\n🎉 Voice recognition is working! You said: '{result}'")
            else:
                print("\n😞 Voice recognition test failed")
        elif choice == "2":
            continuous_listening()
        else:
            print("Invalid choice, running single test...")
            simple_voice_test()
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")

if __name__ == "__main__":
    main()