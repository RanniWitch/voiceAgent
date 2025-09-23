#!/usr/bin/env python3
"""
Simple Microphone Test
Test microphones one by one to find which one works
"""

import speech_recognition as sr
import json

def test_all_microphones():
    """Test all available microphones"""
    print("🎤 Testing All Available Microphones\n")
    
    try:
        mic_names = sr.Microphone.list_microphone_names()
        print(f"Found {len(mic_names)} microphones:\n")
        
        for index, name in enumerate(mic_names):
            print(f"{index}: {name}")
        
        print("\n" + "="*50)
        
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300  # More sensitive
        recognizer.pause_threshold = 0.5
        
        working_mics = []
        
        for index, name in enumerate(mic_names):
            print(f"\n🧪 Testing Microphone {index}: {name}")
            
            # Skip obviously problematic microphones
            if any(term in name.lower() for term in ['stereo mix', 'what u hear', 'wave out', 'speakers']):
                print("   ⚠️  SKIPPED - This might pick up system audio")
                continue
            
            try:
                # Test this microphone
                mic = sr.Microphone(device_index=index)
                
                print("   📢 Speak NOW for 3 seconds...")
                
                with mic as source:
                    # Quick calibration
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    
                    # Listen for audio
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)
                    
                print("   🔄 Processing audio...")
                
                # Try to recognize
                try:
                    text = recognizer.recognize_google(audio)
                    print(f"   ✅ SUCCESS! Heard: '{text}'")
                    working_mics.append((index, name, text))
                except sr.UnknownValueError:
                    print("   ✅ Audio detected but couldn't understand speech")
                    working_mics.append((index, name, "Audio detected"))
                except sr.RequestError as e:
                    print(f"   ⚠️  Network error: {e}")
                    working_mics.append((index, name, "Audio captured (network error)"))
                    
            except sr.WaitTimeoutError:
                print("   ❌ No audio detected")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Summary
        print("\n" + "="*50)
        print("📋 SUMMARY:")
        
        if working_mics:
            print(f"\n✅ Found {len(working_mics)} working microphone(s):")
            for index, name, result in working_mics:
                print(f"   {index}: {name} - {result}")
            
            # Auto-save the first working microphone
            best_mic = working_mics[0]
            config = {
                'microphone_index': best_mic[0],
                'microphone_name': best_mic[1]
            }
            
            try:
                with open('microphone_config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"\n💾 Auto-saved microphone {best_mic[0]} as default")
                print("   Restart your voice assistant to use this microphone")
            except Exception as e:
                print(f"\n⚠️  Could not save config: {e}")
        else:
            print("\n❌ No working microphones found!")
            print("\nTroubleshooting:")
            print("• Check Windows microphone permissions")
            print("• Make sure microphone is not muted")
            print("• Try speaking louder")
            print("• Check if another app is using the microphone")
            
    except Exception as e:
        print(f"❌ Failed to list microphones: {e}")

def test_specific_microphone():
    """Test a specific microphone by index"""
    try:
        mic_names = sr.Microphone.list_microphone_names()
        print("Available microphones:")
        for index, name in enumerate(mic_names):
            print(f"{index}: {name}")
        
        while True:
            try:
                choice = input("\nEnter microphone number to test (or 'q' to quit): ")
                if choice.lower() == 'q':
                    break
                    
                mic_index = int(choice)
                if 0 <= mic_index < len(mic_names):
                    print(f"\n🧪 Testing microphone {mic_index}: {mic_names[mic_index]}")
                    print("📢 Speak NOW for 3 seconds...")
                    
                    recognizer = sr.Recognizer()
                    recognizer.energy_threshold = 300
                    
                    mic = sr.Microphone(device_index=mic_index)
                    
                    with mic as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.2)
                        audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)
                    
                    try:
                        text = recognizer.recognize_google(audio)
                        print(f"✅ SUCCESS! Heard: '{text}'")
                        
                        save = input("Save this microphone as default? (y/n): ")
                        if save.lower() == 'y':
                            config = {
                                'microphone_index': mic_index,
                                'microphone_name': mic_names[mic_index]
                            }
                            with open('microphone_config.json', 'w') as f:
                                json.dump(config, f, indent=2)
                            print("💾 Saved!")
                            
                    except sr.UnknownValueError:
                        print("✅ Audio detected but couldn't understand speech")
                    except sr.RequestError as e:
                        print(f"⚠️  Network error: {e}")
                        
                else:
                    print("Invalid microphone number")
                    
            except ValueError:
                print("Please enter a valid number")
            except sr.WaitTimeoutError:
                print("❌ No audio detected")
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎤 Microphone Testing Tool")
    print("="*30)
    
    choice = input("1. Test all microphones automatically\n2. Test specific microphone\nChoice (1 or 2): ")
    
    if choice == "1":
        test_all_microphones()
    elif choice == "2":
        test_specific_microphone()
    else:
        print("Invalid choice")
    
    input("\nPress Enter to exit...")