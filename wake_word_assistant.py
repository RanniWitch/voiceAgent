#!/usr/bin/env python3
"""
Wake Word Voice Assistant
Always-listening assistant that activates on wake words like "Hey Assistant"
Similar to Amazon Alexa, Google Assistant, etc.
"""

import speech_recognition as sr
import json
import os
import time
import re
from datetime import datetime
from collections import defaultdict
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import pyttsx3
import webbrowser
import queue
import numpy as np

class WakeWordAssistant:
    def __init__(self):
        # Voice recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text-to-speech setup
        try:
            self.tts_engine = pyttsx3.init()
            self.setup_tts()
            self.tts_available = True
        except:
            self.tts_available = False
            print("⚠️ Text-to-speech not available")
        
        # Wake word configuration
        self.custom_wake_word_model = None
        self.use_custom_model = False
        self.load_custom_wake_word_model()
        
        # Fallback generic wake words if no custom model
        self.generic_wake_words = [
            'hey assistant', 'computer', 'hey computer', 
            'assistant', 'hey kiro', 'kiro'
        ]
        
        # State management
        self.is_listening_for_wake_word = False
        self.is_processing_command = False
        self.wake_word_detected = False
        
        # AI configuration
        self.ai_config = {
            'gemini_api_key': '',
            'use_gemini': True,
            'use_ollama': True,
            'use_wake_word': True,
            'wake_word_sensitivity': 0.7,  # How confident we need to be
            'command_timeout': 10,  # Seconds to wait for command after wake word
        }
        
        self.load_config()
        self.setup_command_patterns()
        
        # Conversation history
        self.conversation_history = []
        self.stats = defaultdict(int)
        
        # Threading
        self.wake_word_thread = None
        self.command_queue = queue.Queue()
        
        self.setup_gui()
        
    def load_custom_wake_word_model(self):
        """Load custom trained wake word model"""
        try:
            if os.path.exists('custom_wake_word_model.pkl'):
                import pickle
                with open('custom_wake_word_model.pkl', 'rb') as f:
                    self.custom_wake_word_model = pickle.load(f)
                
                if self.custom_wake_word_model.get('trained', False):
                    self.use_custom_model = True
                    print(f"✅ Loaded custom wake word: '{self.custom_wake_word_model['word']}'")
                else:
                    print("⚠️ Custom wake word model found but not trained")
            else:
                print("ℹ️ No custom wake word model found - using generic wake words")
        except Exception as e:
            print(f"Error loading custom wake word model: {e}")
            
    def extract_audio_features(self, audio_data, sr=16000):
        """Extract acoustic features for custom wake word detection"""
        try:
            import librosa
            
            # Ensure audio data is not empty and has sufficient length
            if len(audio_data) < sr * 0.1:  # At least 0.1 seconds
                return None
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            
            # Extract additional features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            
            # Safely extract scalar values from each feature
            feature_list = []
            
            # MFCC features
            if mfccs.size > 0:
                feature_list.extend(np.mean(mfccs, axis=1).flatten())
                feature_list.extend(np.std(mfccs, axis=1).flatten())
            
            # Spectral centroid features
            if spectral_centroids.size > 0:
                feature_list.append(np.mean(spectral_centroids))
                feature_list.append(np.std(spectral_centroids))
            else:
                feature_list.extend([0.0, 0.0])
            
            # Spectral rolloff features
            if spectral_rolloff.size > 0:
                feature_list.append(np.mean(spectral_rolloff))
                feature_list.append(np.std(spectral_rolloff))
            else:
                feature_list.extend([0.0, 0.0])
            
            # Zero crossing rate features
            if zero_crossing_rate.size > 0:
                feature_list.append(np.mean(zero_crossing_rate))
                feature_list.append(np.std(zero_crossing_rate))
            else:
                feature_list.extend([0.0, 0.0])
            
            # Chroma features
            if chroma.size > 0:
                feature_list.extend(np.mean(chroma, axis=1).flatten())
                feature_list.extend(np.std(chroma, axis=1).flatten())
            
            # Convert to numpy array
            features = np.array(feature_list)
            
            return features if len(features) > 0 else None
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
            
    def detect_custom_wake_word(self, audio_data):
        """Detect custom trained wake word using acoustic features"""
        if not self.use_custom_model or not self.custom_wake_word_model:
            return False, 0.0
            
        try:
            # Extract features from audio
            features = self.extract_audio_features(audio_data)
            if features is None:
                return False, 0.0
                
            # Calculate confidence using trained model
            model = self.custom_wake_word_model['model']
            centroid = np.array(model['centroid'])
            
            # Calculate cosine similarity
            from scipy.spatial.distance import cosine
            similarity = 1 - cosine(features, centroid)
            confidence = max(0.0, min(1.0, similarity))
            
            # Check against threshold
            threshold = self.custom_wake_word_model['confidence_threshold']
            detected = confidence >= threshold
            
            return detected, confidence
            
        except Exception as e:
            print(f"Error in custom wake word detection: {e}")
            return False, 0.0
        
    def setup_tts(self):
        """Configure text-to-speech"""
        if not self.tts_available:
            return
            
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if 'english' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            self.tts_engine.setProperty('rate', 180)
            self.tts_engine.setProperty('volume', 0.8)
        except Exception as e:
            print(f"TTS setup error: {e}")
            self.tts_available = False
            
    def load_config(self):
        """Load configuration"""
        try:
            if os.path.exists('ai_config.json'):
                with open('ai_config.json', 'r') as f:
                    saved_config = json.load(f)
                    self.ai_config.update(saved_config)
        except Exception as e:
            print(f"Could not load config: {e}")
            
    def setup_command_patterns(self):
        """Setup command patterns"""
        self.local_commands = {
            # Time and date
            r'what time is it|current time|time now': self.get_current_time,
            r'what date is it|current date|today\'s date': self.get_current_date,
            
            # System commands
            r'open calculator|launch calculator': lambda: self.system_command('calc'),
            r'open notepad|launch notepad': lambda: self.system_command('notepad'),
            r'open browser|launch browser': lambda: self.system_command('start chrome'),
            r'open file explorer|open explorer': lambda: self.system_command('explorer'),
            r'open task manager|task manager': lambda: self.system_command('taskmgr'),
            
            # Website commands
            r'open youtube|go to youtube': lambda: self.open_website('https://youtube.com'),
            r'open netflix|go to netflix': lambda: self.open_website('https://netflix.com'),
            r'open google|go to google': lambda: self.open_website('https://google.com'),
            r'open facebook|go to facebook': lambda: self.open_website('https://facebook.com'),
            r'open gmail|check email': lambda: self.open_website('https://gmail.com'),
            r'open github|go to github': lambda: self.open_website('https://github.com'),
            r'open amazon|go to amazon': lambda: self.open_website('https://amazon.com'),
            r'open spotify|go to spotify': lambda: self.open_website('https://open.spotify.com'),
            
            # Built-in responses
            r'hello|hi|hey there': lambda: "Hello! I'm listening. How can I help you?",
            r'how are you|how\'s it going': lambda: "I'm doing great! Ready to help you with anything.",
            r'thank you|thanks': lambda: "You're welcome! Always happy to help.",
            r'goodbye|bye|stop listening': self.stop_wake_word_listening,
            
            # Math operations
            r'what is (\d+) plus (\d+)|(\d+) plus (\d+)': self.calculate_addition,
            r'what is (\d+) minus (\d+)|(\d+) minus (\d+)': self.calculate_subtraction,
            r'what is (\d+) times (\d+)|(\d+) times (\d+)': self.calculate_multiplication,
            
            # Entertainment
            r'tell me a joke|joke please': self.get_random_joke,
            r'random fact|tell me a fact': self.get_random_fact,
            
            # YouTube/Video Controls
            r'play|pause|play pause|pause play': self.youtube_play_pause,
            r'fullscreen|full screen|go fullscreen': self.youtube_fullscreen,
            r'skip forward|forward|skip ahead': self.youtube_skip_forward,
            r'skip back|go back|rewind': self.youtube_skip_back,
            r'skip forward 10|forward 10|skip ahead 10': self.youtube_skip_forward_10,
            r'skip back 10|go back 10|rewind 10': self.youtube_skip_back_10,
            r'volume up|louder|increase volume': self.youtube_volume_up,
            r'volume down|quieter|decrease volume': self.youtube_volume_down,
            r'mute|unmute|toggle mute': self.youtube_mute,
        }
        
        # Compile regex patterns
        self.compiled_patterns = {
            re.compile(pattern, re.IGNORECASE): handler 
            for pattern, handler in self.local_commands.items()
        }
        
        # AI trigger patterns
        self.ai_triggers = [
            r'explain|what is|how does|why does|tell me about',
            r'help me with|can you help|I need help',
            r'what do you think|your opinion|advice',
            r'write|create|generate|make me',
            r'who is|who was|when did|where is',
        ]
        
        self.ai_trigger_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.ai_triggers]
        
    def detect_wake_word(self, text, audio_data=None):
        """Detect if wake word is in the text or audio"""
        # First try custom wake word detection if available
        if self.use_custom_model and audio_data is not None:
            detected, confidence = self.detect_custom_wake_word(audio_data)
            if detected:
                wake_word = self.custom_wake_word_model['word']
                print(f"🎯 Custom wake word detected: '{wake_word}' (confidence: {confidence:.2f})")
                return True, wake_word
        
        # Fallback to generic text-based detection
        text_lower = text.lower().strip()
        
        for wake_word in self.generic_wake_words:
            if wake_word in text_lower:
                # Check if it's at the beginning or has some context
                words = text_lower.split()
                wake_word_parts = wake_word.split()
                
                # Look for the wake word sequence in the text
                for i in range(len(words) - len(wake_word_parts) + 1):
                    if words[i:i+len(wake_word_parts)] == wake_word_parts:
                        return True, wake_word
                        
        return False, None
        
    def extract_command_after_wake_word(self, text, wake_word):
        """Extract the command that comes after the wake word"""
        text_lower = text.lower().strip()
        wake_word_lower = wake_word.lower()
        
        # Find where the wake word ends
        wake_word_index = text_lower.find(wake_word_lower)
        if wake_word_index != -1:
            command_start = wake_word_index + len(wake_word_lower)
            command = text[command_start:].strip()
            
            # Remove common filler words at the beginning
            filler_words = ['please', 'can you', 'could you', 'would you', 'i want to', 'i need to']
            command_lower = command.lower()
            
            for filler in filler_words:
                if command_lower.startswith(filler):
                    command = command[len(filler):].strip()
                    break
                    
            return command if command else None
        
        return None
        
    def listen_for_wake_word(self):
        """Continuously listen for wake word"""
        print("👂 Starting wake word detection...")
        self.update_status("👂 Listening for wake word...")
        
        while self.is_listening_for_wake_word:
            try:
                with self.microphone as source:
                    # Adjust for ambient noise less frequently to improve performance
                    if self.stats['wake_word_attempts'] % 10 == 0:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Set up for wake word detection
                    self.recognizer.pause_threshold = 0.8  # Shorter pause for wake word
                    self.recognizer.energy_threshold = 400  # Higher threshold to avoid false positives
                    
                    # Listen for short phrases (wake words are usually short)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=4)
                
                # Convert audio to numpy array for custom wake word detection
                audio_data = None
                if self.use_custom_model:
                    try:
                        audio_data = np.frombuffer(audio.get_wav_data(), dtype=np.int16).astype(np.float32)
                        audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data
                    except:
                        audio_data = None
                
                # Recognize the audio
                try:
                    text = self.recognizer.recognize_google(audio)
                    self.stats['wake_word_attempts'] += 1
                    
                    print(f"🎤 Heard: '{text}'")
                    
                    # Check for wake word (both custom and generic)
                    wake_detected, wake_word = self.detect_wake_word(text, audio_data)
                    
                    if wake_detected:
                        self.stats['wake_words_detected'] += 1
                        print(f"🎯 Wake word detected: '{wake_word}'")
                        
                        # Play activation sound or speak confirmation
                        if self.tts_available:
                            self.speak_response("Yes?")
                        
                        self.update_status(f"🎯 Wake word detected! Listening for command...")
                        
                        # Check if there's a command in the same phrase
                        command = self.extract_command_after_wake_word(text, wake_word)
                        
                        if command:
                            print(f"📝 Command in same phrase: '{command}'")
                            self.process_command(command)
                        else:
                            # Listen for the actual command
                            self.listen_for_command_after_wake_word()
                            
                except sr.UnknownValueError:
                    # This is normal - lots of background noise won't be recognized
                    pass
                except sr.RequestError as e:
                    print(f"Recognition service error: {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                # This is normal - we timeout frequently to check if we should stop
                pass
            except Exception as e:
                print(f"Wake word detection error: {e}")
                time.sleep(1)
                
        print("👂 Wake word detection stopped")
        
    def listen_for_command_after_wake_word(self):
        """Listen for command after wake word is detected"""
        try:
            self.update_status("🎤 Listening for your command...")
            
            with self.microphone as source:
                # Adjust settings for command recognition
                self.recognizer.pause_threshold = 1.2
                self.recognizer.energy_threshold = 300
                
                # Listen for the command with a timeout
                audio = self.recognizer.listen(source, 
                                             timeout=self.ai_config['command_timeout'], 
                                             phrase_time_limit=15)
            
            # Recognize the command
            command = self.recognizer.recognize_google(audio)
            print(f"📝 Command received: '{command}'")
            
            self.process_command(command)
            
        except sr.WaitTimeoutError:
            self.speak_response("I didn't hear a command. Say my wake word again if you need me.")
            self.update_status("⏰ Command timeout - back to wake word listening")
        except sr.UnknownValueError:
            self.speak_response("I didn't understand that. Could you repeat?")
            self.update_status("❓ Didn't understand - back to wake word listening")
        except Exception as e:
            print(f"Command listening error: {e}")
            self.update_status("❌ Error - back to wake word listening")
            
    def process_command(self, command):
        """Process the voice command"""
        if not command:
            return
            
        self.update_status("🔍 Processing command...")
        
        # Add to conversation history
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_history.append({
            'timestamp': timestamp,
            'user': command,
            'response': None
        })
        
        # Process the command
        response = self.classify_and_execute_command(command)
        
        # Update conversation history
        self.conversation_history[-1]['response'] = response
        
        # Display in GUI
        self.update_conversation_display()
        
        # Speak the response
        if self.tts_available and response:
            self.speak_response(response)
            
        self.update_status("👂 Back to listening for wake word...")
        
    def classify_and_execute_command(self, text):
        """Classify and execute the command"""
        if not text:
            return "I didn't catch that."
        
        text_lower = text.lower().strip()
        
        # Check local command patterns first
        for pattern, handler in self.compiled_patterns.items():
            match = pattern.search(text_lower)
            if match:
                try:
                    if callable(handler):
                        if hasattr(handler, '__code__') and handler.__code__.co_argcount > 1:
                            result = handler(match)
                        else:
                            result = handler()
                        self.stats['local_commands'] += 1
                        return result
                    else:
                        self.stats['local_commands'] += 1
                        return handler
                except Exception as e:
                    return f"Error executing command: {e}"
        
        # Check if it should go to AI
        for pattern in self.ai_trigger_patterns:
            if pattern.search(text_lower):
                self.stats['ai_commands'] += 1
                return self.get_ai_response(text)
        
        # Default to AI for longer queries
        if len(text.split()) > 3:
            self.stats['ai_commands'] += 1
            return self.get_ai_response(text)
        
        # Fallback
        self.stats['fallback_responses'] += 1
        return f"I heard '{text}', but I'm not sure how to help with that. Try asking me about the time, opening websites, or general questions."
        
    def get_ai_response(self, text):
        """Get AI response (simplified version)"""
        try:
            if self.ai_config.get('use_gemini') and self.ai_config.get('gemini_api_key'):
                import google.generativeai as genai
                
                genai.configure(api_key=self.ai_config['gemini_api_key'])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"You are a helpful voice assistant. Keep responses brief and conversational (1-2 sentences max).\n\nUser: {text}"
                response = model.generate_content(prompt)
                
                return response.text.strip()
            else:
                return "AI is not configured. I can still help with local commands like opening websites and basic tasks."
                
        except Exception as e:
            return f"I'm having trouble with my AI right now, but I can still help with basic commands."
            
    # Helper methods (same as before)
    def get_current_time(self):
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}"
        
    def get_current_date(self):
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}"
        
    def system_command(self, command):
        try:
            os.system(command)
            app_name = command.replace('start ', '').replace('calc', 'Calculator').replace('notepad', 'Notepad')
            return f"Opening {app_name}"
        except Exception as e:
            return f"Couldn't execute that command: {e}"
            
    def open_website(self, url):
        try:
            webbrowser.open(url)
            site_name = url.replace('https://', '').split('.')[0].capitalize()
            if site_name == 'Open':
                site_name = 'Spotify'
            return f"Opening {site_name}"
        except Exception as e:
            return f"Couldn't open that website: {e}"
            
    def calculate_addition(self, match):
        groups = [g for g in match.groups() if g is not None]
        if len(groups) >= 2:
            a, b = int(groups[0]), int(groups[1])
            return f"{a} plus {b} equals {a + b}"
        return "Sorry, I couldn't understand those numbers"
        
    def calculate_subtraction(self, match):
        groups = [g for g in match.groups() if g is not None]
        if len(groups) >= 2:
            a, b = int(groups[0]), int(groups[1])
            return f"{a} minus {b} equals {a - b}"
        return "Sorry, I couldn't understand those numbers"
        
    def calculate_multiplication(self, match):
        groups = [g for g in match.groups() if g is not None]
        if len(groups) >= 2:
            a, b = int(groups[0]), int(groups[1])
            return f"{a} times {b} equals {a * b}"
        return "Sorry, I couldn't understand those numbers"
        
    def get_random_joke(self):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "What do you call a fake noodle? An impasta!",
            "Why don't eggs tell jokes? They'd crack each other up!",
        ]
        import random
        return random.choice(jokes)
        
    def youtube_play_pause(self):
        """Toggle play/pause on YouTube or any video player"""
        try:
            import pyautogui
            pyautogui.press('space')
            return "Play/pause toggled"
        except ImportError:
            # Fallback using keyboard module
            try:
                import keyboard
                keyboard.press_and_release('space')
                return "Play/pause toggled"
            except ImportError:
                return "Media control not available. Please install pyautogui: pip install pyautogui"
    
    def youtube_fullscreen(self):
        """Toggle fullscreen on YouTube"""
        try:
            import pyautogui
            pyautogui.press('f')
            return "Fullscreen toggled"
        except ImportError:
            try:
                import keyboard
                keyboard.press_and_release('f')
                return "Fullscreen toggled"
            except ImportError:
                return "Media control not available. Please install pyautogui: pip install pyautogui"
    
    def youtube_skip_forward(self):
        """Skip forward 5 seconds"""
        try:
            import pyautogui
            pyautogui.press('right')
            return "Skipped forward 5 seconds"
        except ImportError:
            try:
                import keyboard
                keyboard.press_and_release('right')
                return "Skipped forward 5 seconds"
            except ImportError:
                return "Media control not available. Please install pyautogui: pip install pyautogui"
    
    def youtube_skip_back(self):
        """Skip back 5 seconds"""
        try:
            import pyautogui
            pyautogui.press('left')
            return "Skipped back 5 seconds"
        except ImportError:
            try:
                import keyboard
                keyboard.press_and_release('left')
                return "Skipped back 5 seconds"
            except ImportError:
                return "Media control not available. Please install pyautogui: pip install pyautogui"
    
    def youtube_skip_forward_10(self):
        """Skip forward 10 seconds"""
        try:
            import pyautogui
            pyautogui.press('l')
            return "Skipped forward 10 seconds"
        except ImportError:
            try:
                import keyboard
                keyboard.press_and_release('l')
                return "Skipped forward 10 seconds"
            except ImportError:
                return "Media control not available. Please install pyautogui: pip install pyautogui"
    
    def youtube_skip_back_10(self):
        """Skip back 10 seconds"""
        try:
            import pyautogui
            pyautogui.press('j')
            return "Skipped back 10 seconds"
        except ImportError:
            try:
                import keyboard
                keyboard.press_and_release('j')
                return "Skipped back 10 seconds"
            except ImportError:
                return "Media control not available. Please install pyautogui: pip install pyautogui"
    
    def youtube_volume_up(self):
        """Increase volume"""
        try:
            import pyautogui
            pyautogui.press('up')
            return "Volume increased"
        except ImportError:
            try:
                import keyboard
                keyboard.press_and_release('up')
                return "Volume increased"
            except ImportError:
                return "Media control not available. Please install pyautogui: pip install pyautogui"
    
    def youtube_volume_down(self):
        """Decrease volume"""
        try:
            import pyautogui
            pyautogui.press('down')
            return "Volume decreased"
        except ImportError:
            try:
                import keyboard
                keyboard.press_and_release('down')
                return "Volume decreased"
            except ImportError:
                return "Media control not available. Please install pyautogui: pip install pyautogui"
    
    def youtube_mute(self):
        """Mute/unmute video"""
        try:
            import pyautogui
            pyautogui.press('m')
            return "Mute toggled"
        except ImportError:
            try:
                import keyboard
                keyboard.press_and_release('m')
                return "Mute toggled"
            except ImportError:
                return "Media control not available. Please install pyautogui: pip install pyautogui"
        
    def get_random_fact(self):
        facts = [
            "Honey never spoils. Archaeologists have found edible honey in ancient Egyptian tombs.",
            "A group of flamingos is called a 'flamboyance'.",
            "Bananas are berries, but strawberries aren't.",
            "Octopuses have three hearts and blue blood.",
        ]
        import random
        return random.choice(facts)
        
    def speak_response(self, text):
        """Convert text to speech"""
        if self.tts_available:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
                
    def start_wake_word_listening(self):
        """Start the wake word detection"""
        if not self.is_listening_for_wake_word:
            self.is_listening_for_wake_word = True
            self.wake_word_thread = threading.Thread(target=self.listen_for_wake_word, daemon=True)
            self.wake_word_thread.start()
            
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            if self.tts_available:
                self.speak_response("Wake word detection started. Say 'Hey Assistant' to activate me.")
                
    def stop_wake_word_listening(self):
        """Stop the wake word detection"""
        self.is_listening_for_wake_word = False
        
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        self.update_status("⏹️ Wake word detection stopped")
        
        if self.tts_available:
            self.speak_response("Wake word detection stopped. Goodbye!")
            
        return "Wake word detection stopped. Goodbye!"
        
    def update_status(self, message):
        """Update status label"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            if hasattr(self, 'root'):
                self.root.update()
                
    def update_conversation_display(self):
        """Update conversation display"""
        if hasattr(self, 'conversation_text'):
            self.conversation_text.delete(1.0, tk.END)
            
            for entry in self.conversation_history[-10:]:
                timestamp = entry['timestamp']
                user_text = entry['user']
                response = entry['response']
                
                self.conversation_text.insert(tk.END, f"[{timestamp}] You: {user_text}\n")
                if response:
                    self.conversation_text.insert(tk.END, f"Assistant: {response}\n\n")
                    
            self.conversation_text.see(tk.END)
            
    def setup_gui(self):
        """Setup the GUI"""
        self.root = tk.Tk()
        self.root.title("Wake Word Voice Assistant")
        self.root.geometry("900x600")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control section
        control_frame = ttk.LabelFrame(main_frame, text="Wake Word Assistant Control", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(control_frame, text="Ready to start wake word detection", 
                                    font=("Arial", 12))
        self.status_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Control buttons
        self.start_btn = ttk.Button(control_frame, text="🎤 Start Wake Word Detection", 
                                  command=self.start_wake_word_listening)
        self.start_btn.grid(row=1, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop Detection", 
                                 command=self.stop_wake_word_listening, state='disabled')
        self.stop_btn.grid(row=1, column=1, padx=(0, 10))
        
        ttk.Button(control_frame, text="📊 Stats", 
                  command=self.show_stats).grid(row=1, column=2)
        
        # Wake word info
        if self.use_custom_model:
            info_text = f"Custom wake word: '{self.custom_wake_word_model['word']}' (trained on your voice)"
        else:
            info_text = f"Generic wake words: {', '.join(self.generic_wake_words)}"
        ttk.Label(control_frame, text=info_text, font=("Arial", 9)).grid(row=2, column=0, columnspan=3, pady=(10, 0))
        
        # Add button to train custom wake word
        ttk.Button(control_frame, text="🎓 Train Custom Wake Word", 
                  command=self.open_wake_word_trainer).grid(row=3, column=0, columnspan=3, pady=(5, 0))
        
        # Conversation section
        conv_frame = ttk.LabelFrame(main_frame, text="Conversation History", padding="10")
        conv_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.conversation_text = scrolledtext.ScrolledText(conv_frame, width=60, height=20, 
                                                         font=("Consolas", 10))
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        
        # Commands section
        commands_frame = ttk.LabelFrame(main_frame, text="Available Commands", padding="10")
        commands_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        commands_text = scrolledtext.ScrolledText(commands_frame, width=40, height=20, 
                                                font=("Arial", 9))
        commands_text.pack(fill=tk.BOTH, expand=True)
        
        # Add command examples
        if self.use_custom_model:
            wake_word_text = f"CUSTOM WAKE WORD:\n'{self.custom_wake_word_model['word']}' (trained on your voice)"
        else:
            wake_word_text = f"GENERIC WAKE WORDS:\n{', '.join(self.generic_wake_words)}"
        
        commands = f"""{wake_word_text}

EXAMPLE USAGE:
• "Hey Assistant, what time is it?"
• "Computer, open YouTube"
• "Hey Assistant, tell me a joke"
• "Assistant, what is 5 plus 3?"

WEBSITE COMMANDS:
• "Open YouTube/Netflix/Google"
• "Go to Facebook/Gmail/GitHub"
• "Launch Amazon/Spotify"

SYSTEM COMMANDS:
• "Open calculator/notepad"
• "Launch task manager"
• "Open file explorer"

AI COMMANDS:
• "Explain quantum physics"
• "What is the capital of France?"
• "Tell me about machine learning"

BASIC COMMANDS:
• "What time is it?"
• "What date is today?"
• "Tell me a joke"
• "Random fact"

Say "goodbye" or "stop listening" to stop wake word detection."""
        
        commands_text.insert(tk.END, commands)
        commands_text.config(state=tk.DISABLED)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def show_stats(self):
        """Show usage statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Usage Statistics")
        stats_window.geometry("400x300")
        
        stats_text = scrolledtext.ScrolledText(stats_window, width=50, height=20)
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        stats_content = "WAKE WORD ASSISTANT STATISTICS:\n\n"
        
        for key, value in self.stats.items():
            stats_content += f"{key.replace('_', ' ').title()}: {value}\n"
            
        if not self.stats:
            stats_content += "No usage data yet. Start the wake word detection and try some commands!"
            
        stats_text.insert(tk.END, stats_content)
        stats_text.config(state=tk.DISABLED)
        
    def open_wake_word_trainer(self):
        """Open the wake word trainer"""
        try:
            import subprocess
            import sys
            subprocess.Popen(["py", "custom_wake_word_trainer.py"])
            messagebox.showinfo("Wake Word Trainer", 
                              "Opening Custom Wake Word Trainer in a new window.\n\n"
                              "After training, restart this assistant to use your custom wake word.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open wake word trainer: {e}")
        
    def run(self):
        """Start the assistant"""
        print("🎤 Wake Word Voice Assistant Starting...")
        if self.use_custom_model:
            print(f"Custom wake word: '{self.custom_wake_word_model['word']}'")
        else:
            print(f"Generic wake words: {', '.join(self.generic_wake_words)}")
        print("Click 'Start Wake Word Detection' to begin always-listening mode")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        assistant = WakeWordAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nWake word assistant stopped")
    except Exception as e:
        print(f"Error: {e}")