#!/usr/bin/env python3
"""
Wake Word Accuracy Tester
Test how accurately your wake word is detected vs false positives
"""

import speech_recognition as sr
import json
import os
import time
from wake_word_assistant import WakeWordAssistant

def test_wake_word_accuracy():
    """Test wake word detection accuracy"""
    print("🎯 Wake Word Accuracy Tester")
    print("="*40)
    
    # Check if custom wake word exists
    if not os.path.exists('custom_wake_word_model.pkl'):
        print("❌ No custom wake word model found!")
        print("Please train a wake word first using: py custom_wake_word_trainer.py")
        return
    
    # Load the assistant
    assistant = WakeWordAssistant()
    
    if not assistant.use_custom_model:
        print("❌ Custom wake word model not loaded!")
        return
    
    wake_word = assistant.custom_wake_word_model['word']
    threshold = assistant.custom_wake_word_model.get('confidence_threshold', 0.7)
    
    print(f"Testing wake word: '{wake_word}'")
    print(f"Current threshold: {threshold:.2f}")
    print()
    
    # Test scenarios
    print("🧪 Test Scenarios:")
    print("1. Say your wake word correctly (should detect)")
    print("2. Say random words (should NOT detect)")
    print("3. Say similar sounding words (should NOT detect)")
    print("4. Say your wake word in a sentence (should detect)")
    print()
    
    correct_detections = 0
    false_positives = 0
    missed_detections = 0
    total_tests = 0
    
    recognizer = sr.Recognizer()
    microphone = assistant.microphone
    
    try:
        while True:
            print("\n" + "-"*40)
            test_type = input("Test type (w=wake word, r=random, s=similar, q=quit): ").lower()
            
            if test_type == 'q':
                break
            elif test_type not in ['w', 'r', 's']:
                print("Invalid option. Use w, r, s, or q")
                continue
            
            expected_detection = (test_type == 'w')
            
            print(f"📢 Speak now (expecting {'DETECTION' if expected_detection else 'NO detection'})...")
            
            try:
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                
                # Get text transcription
                try:
                    text = recognizer.recognize_google(audio)
                    print(f"Heard: '{text}'")
                except sr.UnknownValueError:
                    text = "[unclear audio]"
                    print("Heard: [unclear audio]")
                except sr.RequestError:
                    text = "[network error]"
                    print("Heard: [network error]")
                
                # Test wake word detection
                detected, detected_word = assistant.detect_wake_word(text, audio.get_raw_data())
                
                print(f"Detection result: {'✅ DETECTED' if detected else '❌ NOT detected'}")
                if detected:
                    print(f"Detected word: '{detected_word}'")
                
                # Score the result
                total_tests += 1
                if expected_detection and detected:
                    correct_detections += 1
                    print("🎯 CORRECT: Expected detection and got it")
                elif not expected_detection and not detected:
                    correct_detections += 1
                    print("🎯 CORRECT: Expected no detection and got none")
                elif expected_detection and not detected:
                    missed_detections += 1
                    print("❌ MISSED: Expected detection but didn't get it")
                else:  # not expected_detection and detected
                    false_positives += 1
                    print("⚠️ FALSE POSITIVE: Didn't expect detection but got it")
                
                # Show running stats
                if total_tests > 0:
                    accuracy = (correct_detections / total_tests) * 100
                    print(f"\n📊 Running Stats:")
                    print(f"   Accuracy: {accuracy:.1f}% ({correct_detections}/{total_tests})")
                    print(f"   False Positives: {false_positives}")
                    print(f"   Missed Detections: {missed_detections}")
                
            except sr.WaitTimeoutError:
                print("⏰ No audio detected - timeout")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    
    # Final results
    if total_tests > 0:
        print("\n" + "="*40)
        print("📊 FINAL RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Correct: {correct_detections}")
        print(f"False Positives: {false_positives}")
        print(f"Missed Detections: {missed_detections}")
        print(f"Accuracy: {(correct_detections/total_tests)*100:.1f}%")
        
        if false_positives > missed_detections:
            print("\n💡 RECOMMENDATION: Your wake word is too sensitive")
            print("   Consider retraining with clearer pronunciation")
        elif missed_detections > false_positives:
            print("\n💡 RECOMMENDATION: Your wake word might be too strict")
            print("   Try speaking more clearly or retraining")
        else:
            print("\n✅ Your wake word detection looks well balanced!")

if __name__ == "__main__":
    test_wake_word_accuracy()