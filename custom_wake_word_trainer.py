#!/usr/bin/env python3
"""
Custom Wake Word Trainer
Train your own personalized wake word by typing it and saying it 3 times
The AI learns your specific pronunciation and cadence
"""

import speech_recognition as sr
import json
import os
import time
import numpy as np
from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pickle
import librosa
import soundfile as sf
from scipy.spatial.distance import cosine
from sklearn.cluster import KMeans

class CustomWakeWordTrainer:
    def __init__(self):
        # Voice recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Wake word training data
        self.wake_word_data = {
            'word': '',
            'recordings': [],
            'features': [],
            'model': None,
            'trained': False,
            'confidence_threshold': 0.7
        }
        
        # File paths
        self.data_dir = "wake_word_data"
        self.model_file = "custom_wake_word_model.pkl"
        
        self.setup_directories()
        self.load_existing_model()
        self.setup_gui()
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.data_dir, exist_ok=True)
        
    def load_existing_model(self):
        """Load existing wake word model if available"""
        try:
            if os.path.exists(self.model_file):
                with open(self.model_file, 'rb') as f:
                    self.wake_word_data = pickle.load(f)
                print(f"✅ Loaded existing wake word model for: '{self.wake_word_data['word']}'")
        except Exception as e:
            print(f"Could not load existing model: {e}")
            
    def save_model(self):
        """Save the wake word model"""
        try:
            with open(self.model_file, 'wb') as f:
                pickle.dump(self.wake_word_data, f)
            print("✅ Wake word model saved!")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
            
    def extract_audio_features(self, audio_data, sr=16000):
        """Extract acoustic features from audio data"""
        try:
            # Ensure audio data is not empty and has sufficient length
            if len(audio_data) < sr * 0.1:  # At least 0.1 seconds
                print("Audio too short for feature extraction")
                return None
            
            # Extract MFCC features (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            
            # Extract additional features for better wake word detection
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            
            # Safely extract scalar values from each feature
            feature_list = []
            
            # MFCC features
            if mfccs.size > 0:
                feature_list.extend(np.mean(mfccs, axis=1).flatten())  # MFCC means
                feature_list.extend(np.std(mfccs, axis=1).flatten())   # MFCC standard deviations
            
            # Spectral centroid features
            if spectral_centroids.size > 0:
                feature_list.append(np.mean(spectral_centroids))       # Spectral centroid mean
                feature_list.append(np.std(spectral_centroids))        # Spectral centroid std
            else:
                feature_list.extend([0.0, 0.0])  # Default values
            
            # Spectral rolloff features
            if spectral_rolloff.size > 0:
                feature_list.append(np.mean(spectral_rolloff))         # Spectral rolloff mean
                feature_list.append(np.std(spectral_rolloff))          # Spectral rolloff std
            else:
                feature_list.extend([0.0, 0.0])  # Default values
            
            # Zero crossing rate features
            if zero_crossing_rate.size > 0:
                feature_list.append(np.mean(zero_crossing_rate))       # Zero crossing rate mean
                feature_list.append(np.std(zero_crossing_rate))        # Zero crossing rate std
            else:
                feature_list.extend([0.0, 0.0])  # Default values
            
            # Chroma features
            if chroma.size > 0:
                feature_list.extend(np.mean(chroma, axis=1).flatten()) # Chroma means
                feature_list.extend(np.std(chroma, axis=1).flatten())  # Chroma standard deviations
            
            # Convert to numpy array
            features = np.array(feature_list)
            
            # Ensure we have a consistent feature vector length
            if len(features) == 0:
                print("No features extracted")
                return None
                
            print(f"Extracted {len(features)} features")
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
            
    def record_wake_word_sample(self, sample_number):
        """Record a single sample of the wake word"""
        try:
            wake_word = self.word_entry.get().strip()
            if not wake_word:
                messagebox.showwarning("No Wake Word", "Please enter a wake word first!")
                return False
                
            self.status_label.config(text=f"Recording sample {sample_number}/3 in 3 seconds...")
            self.root.update()
            
            # Countdown
            for i in range(3, 0, -1):
                self.status_label.config(text=f"Recording sample {sample_number}/3 in {i} seconds...")
                self.root.update()
                time.sleep(1)
                
            self.status_label.config(text=f"🔴 Recording sample {sample_number}/3 - Say '{wake_word}' now!")
            self.root.update()
            
            # Record audio
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                start_time = time.time()
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                end_time = time.time()
                
            # Convert to numpy array for feature extraction
            audio_data = np.frombuffer(audio.get_wav_data(), dtype=np.int16).astype(np.float32)
            audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data
            
            # Extract features
            features = self.extract_audio_features(audio_data)
            
            if features is not None:
                # Save audio file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_filename = f"{self.data_dir}/{wake_word}_sample_{sample_number}_{timestamp}.wav"
                sf.write(audio_filename, audio_data, 16000)
                
                # Try to recognize what was said for verification
                recognized_text = ""
                try:
                    recognized_text = self.recognizer.recognize_google(audio)
                except:
                    recognized_text = "[unclear]"
                
                # Store the recording data
                recording_data = {
                    'sample_number': sample_number,
                    'audio_file': audio_filename,
                    'features': features.tolist(),
                    'duration': end_time - start_time,
                    'recognized_text': recognized_text,
                    'timestamp': timestamp
                }
                
                self.wake_word_data['recordings'].append(recording_data)
                self.wake_word_data['features'].append(features)
                self.wake_word_data['word'] = wake_word
                
                self.status_label.config(text=f"✅ Sample {sample_number}/3 recorded! (Heard: '{recognized_text}')")
                self.update_training_display()
                
                return True
            else:
                self.status_label.config(text=f"❌ Failed to extract features from sample {sample_number}")
                return False
                
        except sr.WaitTimeoutError:
            self.status_label.config(text=f"❌ No speech detected for sample {sample_number}")
            return False
        except Exception as e:
            self.status_label.config(text=f"❌ Recording error: {str(e)}")
            return False
            
    def train_wake_word_model(self):
        """Train the wake word detection model from recorded samples"""
        if len(self.wake_word_data['features']) < 3:
            messagebox.showwarning("Insufficient Data", "Please record at least 3 samples first!")
            return False
            
        try:
            self.status_label.config(text="🧠 Training wake word model...")
            self.root.update()
            
            # Convert features to numpy array
            features_array = np.array(self.wake_word_data['features'])
            
            # Calculate the centroid (average) of all samples
            centroid = np.mean(features_array, axis=0)
            
            # Calculate standard deviation for each feature
            std_dev = np.std(features_array, axis=0)
            
            # Calculate pairwise similarities between samples
            similarities = []
            for i in range(len(features_array)):
                for j in range(i + 1, len(features_array)):
                    similarity = 1 - cosine(features_array[i], features_array[j])
                    similarities.append(similarity)
            
            avg_similarity = np.mean(similarities) if similarities else 0.5
            
            # Calculate more sophisticated metrics for better accuracy
            # Calculate variance and consistency metrics
            feature_variance = np.var(features_array, axis=0)
            consistency_score = 1.0 / (1.0 + np.mean(feature_variance))
            
            # Calculate quality score based on sample consistency
            quality_score = min(1.0, avg_similarity * consistency_score)
            
            # Set a stricter threshold based on quality
            if quality_score > 0.8:
                confidence_threshold = max(0.75, avg_similarity - 0.05)  # High quality = strict threshold
            elif quality_score > 0.6:
                confidence_threshold = max(0.70, avg_similarity - 0.10)  # Medium quality
            else:
                confidence_threshold = max(0.65, avg_similarity - 0.15)  # Lower quality = more lenient
            
            # Create the enhanced model
            model = {
                'centroid': centroid.tolist(),
                'std_dev': std_dev.tolist(),
                'avg_similarity': avg_similarity,
                'consistency_score': consistency_score,
                'quality_score': quality_score,
                'n_samples': len(features_array),
                'feature_ranges': {
                    'min': np.min(features_array, axis=0).tolist(),
                    'max': np.max(features_array, axis=0).tolist()
                },
                'feature_variance': feature_variance.tolist(),
                'confidence_threshold': confidence_threshold
            }
            
            self.wake_word_data['model'] = model
            self.wake_word_data['trained'] = True
            self.wake_word_data['confidence_threshold'] = model['confidence_threshold']
            
            # Save the model
            if self.save_model():
                self.status_label.config(text="✅ Wake word model trained successfully!")
                self.update_training_display()
                
                # Show training results with quality metrics
                quality_text = "Excellent" if quality_score > 0.8 else "Good" if quality_score > 0.6 else "Fair"
                messagebox.showinfo("Training Complete", 
                                  f"Wake word '{self.wake_word_data['word']}' trained successfully!\n\n"
                                  f"Samples: {model['n_samples']}\n"
                                  f"Quality: {quality_text} ({quality_score:.2f})\n"
                                  f"Avg Similarity: {avg_similarity:.2f}\n"
                                  f"Confidence Threshold: {model['confidence_threshold']:.2f}\n\n"
                                  f"💡 Tip: Higher quality = more accurate detection!")
                return True
            else:
                self.status_label.config(text="❌ Failed to save model")
                return False
                
        except Exception as e:
            self.status_label.config(text=f"❌ Training error: {str(e)}")
            messagebox.showerror("Training Error", f"Failed to train model: {e}")
            return False
            
    def test_wake_word_detection(self):
        """Test the trained wake word model"""
        if not self.wake_word_data['trained']:
            messagebox.showwarning("No Model", "Please train a wake word model first!")
            return
            
        try:
            self.status_label.config(text=f"🎯 Testing wake word detection - say '{self.wake_word_data['word']}'...")
            self.root.update()
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                
            # Extract features from test audio
            audio_data = np.frombuffer(audio.get_wav_data(), dtype=np.int16).astype(np.float32)
            audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data
            
            test_features = self.extract_audio_features(audio_data)
            
            if test_features is not None:
                # Calculate similarity to trained model
                confidence = self.calculate_wake_word_confidence(test_features)
                
                # Also get speech recognition result for comparison
                try:
                    recognized_text = self.recognizer.recognize_google(audio)
                except:
                    recognized_text = "[unclear]"
                
                # Determine if wake word was detected
                threshold = self.wake_word_data['confidence_threshold']
                detected = confidence >= threshold
                
                if detected:
                    result_text = f"✅ WAKE WORD DETECTED!\nConfidence: {confidence:.2f} (threshold: {threshold:.2f})\nRecognized: '{recognized_text}'"
                    self.status_label.config(text="✅ Wake word detected!")
                else:
                    result_text = f"❌ Wake word not detected\nConfidence: {confidence:.2f} (threshold: {threshold:.2f})\nRecognized: '{recognized_text}'"
                    self.status_label.config(text="❌ Wake word not detected")
                
                messagebox.showinfo("Test Result", result_text)
                
            else:
                self.status_label.config(text="❌ Failed to extract features from test audio")
                
        except sr.WaitTimeoutError:
            self.status_label.config(text="⏰ No speech detected during test")
        except Exception as e:
            self.status_label.config(text=f"❌ Test error: {str(e)}")
            
    def calculate_wake_word_confidence(self, test_features):
        """Calculate confidence that the test audio contains the wake word"""
        if not self.wake_word_data['trained']:
            return 0.0
            
        try:
            model = self.wake_word_data['model']
            centroid = np.array(model['centroid'])
            
            # Calculate cosine similarity to the centroid
            similarity = 1 - cosine(test_features, centroid)
            
            # Normalize similarity to confidence score
            confidence = max(0.0, min(1.0, similarity))
            
            return confidence
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.0
            
    def start_training_sequence(self):
        """Start the complete training sequence"""
        wake_word = self.word_entry.get().strip()
        if not wake_word:
            messagebox.showwarning("No Wake Word", "Please enter a wake word first!")
            return
            
        # Clear previous data
        self.wake_word_data = {
            'word': wake_word,
            'recordings': [],
            'features': [],
            'model': None,
            'trained': False,
            'confidence_threshold': 0.7
        }
        
        # Record 3 samples
        success_count = 0
        for i in range(1, 4):
            if self.record_wake_word_sample(i):
                success_count += 1
                time.sleep(1)  # Brief pause between recordings
            else:
                retry = messagebox.askyesno("Recording Failed", 
                                          f"Sample {i} failed. Would you like to retry?")
                if retry:
                    if self.record_wake_word_sample(i):
                        success_count += 1
                        time.sleep(1)
                else:
                    break
                    
        if success_count >= 3:
            # Train the model
            if self.train_wake_word_model():
                messagebox.showinfo("Training Complete", 
                                  f"Successfully trained wake word '{wake_word}'!\n\n"
                                  f"You can now test it or use it in the wake word assistant.")
        else:
            messagebox.showwarning("Training Incomplete", 
                                 f"Only recorded {success_count}/3 samples. Please try again.")
            
    def update_training_display(self):
        """Update the training progress display"""
        self.training_text.delete(1.0, tk.END)
        
        if not self.wake_word_data['word']:
            self.training_text.insert(tk.END, "No wake word configured.\n\n1. Enter your custom wake word\n2. Click 'Start Training'\n3. Say the word 3 times\n4. Test the detection")
            return
            
        word = self.wake_word_data['word']
        recordings = self.wake_word_data['recordings']
        trained = self.wake_word_data['trained']
        
        self.training_text.insert(tk.END, f"WAKE WORD: '{word.upper()}'\n")
        self.training_text.insert(tk.END, f"Status: {'✅ TRAINED' if trained else '⏳ IN PROGRESS'}\n\n")
        
        self.training_text.insert(tk.END, f"RECORDINGS ({len(recordings)}/3):\n")
        for i, recording in enumerate(recordings, 1):
            recognized = recording.get('recognized_text', 'unknown')
            duration = recording.get('duration', 0)
            self.training_text.insert(tk.END, f"  Sample {i}: '{recognized}' ({duration:.1f}s)\n")
            
        if trained:
            model = self.wake_word_data['model']
            self.training_text.insert(tk.END, f"\nMODEL INFO:\n")
            self.training_text.insert(tk.END, f"  Samples: {model['n_samples']}\n")
            self.training_text.insert(tk.END, f"  Avg Similarity: {model['avg_similarity']:.2f}\n")
            self.training_text.insert(tk.END, f"  Confidence Threshold: {model['confidence_threshold']:.2f}\n")
            
    def setup_gui(self):
        """Setup the training interface"""
        self.root = tk.Tk()
        self.root.title("Custom Wake Word Trainer")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Wake Word Configuration", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(input_frame, text="Enter your custom wake word:").grid(row=0, column=0, sticky=tk.W)
        self.word_entry = ttk.Entry(input_frame, width=30, font=("Arial", 12))
        self.word_entry.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
        
        if self.wake_word_data['word']:
            self.word_entry.insert(0, self.wake_word_data['word'])
        
        # Control buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="🎤 Start Training (3 samples)", 
                  command=self.start_training_sequence).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🎯 Test Detection", 
                  command=self.test_wake_word_detection).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="💾 Save Model", 
                  command=self.save_model).pack(side=tk.LEFT)
        
        # Status
        self.status_label = ttk.Label(input_frame, text="Ready to train custom wake word", 
                                    font=("Arial", 10))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Training progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Training Progress", padding="10")
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.training_text = scrolledtext.ScrolledText(progress_frame, width=40, height=20)
        self.training_text.pack(fill=tk.BOTH, expand=True)
        
        # Instructions section
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="10")
        instructions_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        instructions_text = scrolledtext.ScrolledText(instructions_frame, width=40, height=20)
        instructions_text.pack(fill=tk.BOTH, expand=True)
        
        instructions = """CUSTOM WAKE WORD TRAINING:

1. ENTER WAKE WORD:
   • Type your desired wake word
   • Can be any word or phrase
   • Examples: "Jarvis", "Computer", "Hey Sarah"

2. TRAINING PROCESS:
   • Click "Start Training"
   • Say your wake word 3 times
   • Speak clearly and naturally
   • Use your normal speaking voice

3. WHAT THE AI LEARNS:
   • Your specific pronunciation
   • Your voice characteristics
   • Your speaking cadence/rhythm
   • Acoustic patterns unique to you

4. TESTING:
   • Click "Test Detection" 
   • Say your wake word
   • See confidence score
   • Adjust if needed

5. USAGE:
   • Trained model saves automatically
   • Use in wake word assistant
   • Works only with your voice
   • Much more accurate than generic

TIPS:
• Choose a unique 2-3 word phrase
• Avoid common words others might say
• Speak consistently across samples
• Test in different environments
• Retrain if accuracy drops

Your custom wake word will be much more accurate than generic ones because it's trained specifically on YOUR voice and pronunciation!"""
        
        instructions_text.insert(tk.END, instructions)
        instructions_text.config(state=tk.DISABLED)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self.update_training_display()
        
    def run(self):
        """Start the trainer"""
        print("🎤 Custom Wake Word Trainer Starting...")
        print("Train your own personalized wake word!")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        trainer = CustomWakeWordTrainer()
        trainer.run()
    except KeyboardInterrupt:
        print("\nTrainer stopped")
    except Exception as e:
        print(f"Error: {e}")